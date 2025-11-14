// FILE: frontend/src/components/Agents/ResumeWriter/CoverLetterCard.tsx

import React, { useState } from 'react';

interface JobListing {
  jobId: number;
  company: string;
  position: string;
  requirements: string;
  keywords: string[];
}

interface CoverLetterCardProps {
  selectedJob: JobListing | null;
}

const CoverLetterCard: React.FC<CoverLetterCardProps> = ({ selectedJob }) => {
  const [generating, setGenerating] = useState(false);
  const [coverLetter, setCoverLetter] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [motivation, setMotivation] = useState('');
  const [achievement, setAchievement] = useState('');

  const generateCoverLetter = async () => {
    if (!selectedJob) {
      setError('Please select a job listing first');
      return;
    }

    if (!motivation.trim()) {
      setError('Please describe your motivation for applying');
      return;
    }

    setGenerating(true);
    setError('');
    setCoverLetter('');

    try {
      const response = await fetch('http://localhost:8000/api/agents/resume-writer/cover-letter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company: selectedJob.company,
          position: selectedJob.position,
          motivation: motivation,
          achievement: achievement,
          metadata: { job_id: selectedJob.jobId }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setCoverLetter(data.output);
      } else {
        setError(data.error || 'Failed to generate cover letter');
      }
    } catch (err) {
      setError(`Error generating cover letter: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Cover Letter Generator</h2>
      <p className="text-gray-600 mb-6">
        Generate compelling, personalized cover letter openings with multiple style options and customization tips.
      </p>

      {/* Selected Job Info */}
      {selectedJob ? (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Applying to</h3>
          <div className="text-sm text-blue-800">
            <p><strong>{selectedJob.position}</strong> at <strong>{selectedJob.company}</strong></p>
          </div>
        </div>
      ) : (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            ⚠️ Please select a job listing from the Quick Start section above to generate a cover letter.
          </p>
        </div>
      )}

      {/* Motivation Input */}
      <div className="mb-4">
        <label htmlFor="motivation-input" className="block text-sm font-medium text-gray-700 mb-2">
          Your Motivation <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="motivation-input"
          value={motivation}
          onChange={(e) => setMotivation(e.target.value)}
          placeholder="e.g., passion for scalable systems, love for product innovation, commitment to user experience"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="mt-1 text-sm text-gray-500">
          What drives your interest in this role and company?
        </p>
      </div>

      {/* Achievement Input */}
      <div className="mb-6">
        <label htmlFor="achievement-input" className="block text-sm font-medium text-gray-700 mb-2">
          Key Achievement (Optional)
        </label>
        <textarea
          id="achievement-input"
          value={achievement}
          onChange={(e) => setAchievement(e.target.value)}
          placeholder="e.g., led a team that reduced API latency by 60%, shipped product used by 2M+ users"
          className="w-full h-24 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
        />
        <p className="mt-1 text-sm text-gray-500">
          A specific, quantified achievement relevant to this role
        </p>
      </div>

      {/* Generate Button */}
      <button
        onClick={generateCoverLetter}
        disabled={generating || !selectedJob || !motivation.trim()}
        className={`px-6 py-3 rounded-lg font-medium transition-colors ${
          generating || !selectedJob || !motivation.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {generating ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating Cover Letter...
          </span>
        ) : (
          '✉️ Generate Cover Letter'
        )}
      </button>

      {/* Error Message */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <span className="text-red-600 mr-2">❌</span>
            <div>
              <h4 className="text-sm font-semibold text-red-800">Error</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Cover Letter Output */}
      {coverLetter && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Cover Letter Options</h3>
            <button
              onClick={() => navigator.clipboard.writeText(coverLetter)}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
            >
              📋 Copy All
            </button>
          </div>

          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
              {coverLetter}
            </pre>
          </div>

          {/* Customization Tips */}
          <div className="mt-6 bg-purple-50 border border-purple-200 rounded-lg p-6">
            <h4 className="font-semibold text-purple-900 mb-3">✨ Customization Tips</h4>
            <ul className="text-sm text-purple-800 space-y-2">
              <li>• <strong>Research the company:</strong> Add specific details about their recent projects, values, or initiatives</li>
              <li>• <strong>Personalize further:</strong> Mention specific aspects of the job description that excite you</li>
              <li>• <strong>Add concrete examples:</strong> Replace placeholders with your actual achievements and skills</li>
              <li>• <strong>Match the tone:</strong> Adjust formality based on company culture (startup vs. enterprise)</li>
              <li>• <strong>Keep it concise:</strong> Opening should be 3-4 sentences, full letter 3-4 paragraphs max</li>
              <li>• <strong>End with action:</strong> Express enthusiasm and clearly state your availability for next steps</li>
            </ul>
          </div>

          {/* Format Guide */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">📝 Structure</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>1. Opening (why you're excited)</li>
                <li>2. Your qualifications</li>
                <li>3. Value you'll bring</li>
                <li>4. Call to action</li>
              </ul>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">✅ Best Practices</h4>
              <ul className="text-sm text-green-800 space-y-1">
                <li>• Address hiring manager by name</li>
                <li>• Use active voice</li>
                <li>• Show enthusiasm</li>
                <li>• Proofread carefully</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Sample Output Preview */}
      {!coverLetter && !generating && !error && selectedJob && motivation && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">You'll receive:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>3 opening paragraph options:</strong> Achievement-focused, Passion-focused, and Value proposition</li>
            <li>• <strong>Subject line suggestions</strong></li>
            <li>• <strong>Personalization checklist</strong> with company-specific tips</li>
            <li>• <strong>Content guidelines</strong> for compelling cover letters</li>
            <li>• <strong>Common mistakes to avoid</strong></li>
            <li>• <strong>Templates with placeholders</strong> for easy customization</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default CoverLetterCard;
