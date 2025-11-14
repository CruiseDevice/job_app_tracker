// FILE: frontend/src/components/Agents/FollowUp/MessageDrafterCard.tsx

import React, { useState } from 'react';

interface FollowUpJob {
  jobId: number;
  company: string;
  position: string;
  status: string;
  applicationDate: string;
  daysSinceContact: number;
}

interface MessageDrafterCardProps {
  selectedJob: FollowUpJob | null;
}

const MessageDrafterCard: React.FC<MessageDrafterCardProps> = ({ selectedJob }) => {
  const [followupType, setFollowupType] = useState('initial_application');
  const [tone, setTone] = useState('professional');
  const [contextNotes, setContextNotes] = useState('');
  const [draftResult, setDraftResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const draftMessage = async () => {
    if (!selectedJob) {
      setError('Please select a job application first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/followup-agent/draft-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          followup_type: followupType,
          company: selectedJob.company,
          position: selectedJob.position,
          tone: tone,
          context_notes: contextNotes
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to draft message');
      }

      const data = await response.json();
      setDraftResult(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (draftResult && draftResult.output) {
      navigator.clipboard.writeText(draftResult.output);
      alert('Message copied to clipboard!');
    }
  };

  if (!selectedJob) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">✉️</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Message Drafter
        </h3>
        <p className="text-gray-600 mb-6">
          Select a job application to draft a personalized follow-up message
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Draft Personalized Follow-up Message
        </h3>
        <p className="text-gray-600">
          AI-generated message for {selectedJob.company} - {selectedJob.position}
        </p>
      </div>

      {/* Configuration Form */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Follow-up Type
          </label>
          <select
            value={followupType}
            onChange={(e) => setFollowupType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="initial_application">Initial Application Follow-up</option>
            <option value="post_interview">Post-Interview Thank You</option>
            <option value="checking_in">Checking In / Status Update</option>
            <option value="offer_response">Offer Response</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tone
          </label>
          <div className="grid grid-cols-3 gap-2">
            {['professional', 'casual', 'enthusiastic'].map((t) => (
              <button
                key={t}
                onClick={() => setTone(t)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  tone === t
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Context Notes (Optional)
          </label>
          <textarea
            value={contextNotes}
            onChange={(e) => setContextNotes(e.target.value)}
            placeholder="Add any specific details, interview topics, or context to personalize the message..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
          />
        </div>
      </div>

      {/* Draft Button */}
      <button
        onClick={draftMessage}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors mb-6"
      >
        {loading ? 'Drafting...' : '✉️ Draft Message'}
      </button>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <span className="text-red-600 mr-2">⚠️</span>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Results */}
      {draftResult && (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-gray-900">Generated Message</h4>
            <button
              onClick={copyToClipboard}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center"
            >
              📋 Copy to Clipboard
            </button>
          </div>

          <div className="border-l-4 border-green-500 bg-green-50 p-6 rounded-r-lg">
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm bg-white p-4 rounded border border-green-200 overflow-x-auto font-sans">
                {draftResult.output}
              </pre>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors">
              Send Email
            </button>
            <button className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-gray-700 transition-colors">
              Edit Message
            </button>
            <button
              onClick={() => setDraftResult(null)}
              className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              Start Over
            </button>
          </div>
        </div>
      )}

      {/* Tips */}
      {!draftResult && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
          <h4 className="font-semibold text-yellow-900 mb-2">💡 Message Writing Tips</h4>
          <ul className="text-sm text-yellow-800 space-y-1">
            <li>• Keep it concise (150-200 words max)</li>
            <li>• Reference specific details from the job/interview</li>
            <li>• Include a clear call-to-action</li>
            <li>• Proofread before sending</li>
            <li>• Send during business hours (9am-5pm)</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default MessageDrafterCard;
