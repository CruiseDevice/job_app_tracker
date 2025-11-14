// FILE: frontend/src/components/Agents/FollowUp/TimingOptimizerCard.tsx

import React, { useState } from 'react';

interface FollowUpJob {
  jobId: number;
  company: string;
  position: string;
  status: string;
  applicationDate: string;
  daysSinceContact: number;
}

interface TimingOptimizerCardProps {
  selectedJob: FollowUpJob | null;
}

const TimingOptimizerCard: React.FC<TimingOptimizerCardProps> = ({ selectedJob }) => {
  const [timingResult, setTimingResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeTiming = async () => {
    if (!selectedJob) {
      setError('Please select a job application first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/followup-agent/optimize-timing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: selectedJob.jobId,
          status: selectedJob.status,
          days_since_contact: selectedJob.daysSinceContact,
          application_date: selectedJob.applicationDate
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to optimize timing');
      }

      const data = await response.json();
      setTimingResult(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (!selectedJob) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">⏰</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Timing Optimizer
        </h3>
        <p className="text-gray-600 mb-6">
          Select a job application to optimize follow-up timing
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Optimize Follow-up Timing
        </h3>
        <p className="text-gray-600">
          AI-powered timing analysis for {selectedJob.company} - {selectedJob.position}
        </p>
      </div>

      {/* Job Details */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-500">Company</div>
            <div className="font-semibold">{selectedJob.company}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Position</div>
            <div className="font-semibold">{selectedJob.position}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Status</div>
            <div className="font-semibold capitalize">{selectedJob.status}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Days Since Contact</div>
            <div className="font-semibold">{selectedJob.daysSinceContact} days</div>
          </div>
        </div>
      </div>

      {/* Analyze Button */}
      <button
        onClick={analyzeTiming}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors mb-6"
      >
        {loading ? 'Analyzing...' : '⏰ Analyze Optimal Timing'}
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
      {timingResult && (
        <div className="space-y-4">
          <div className="border-l-4 border-blue-500 bg-blue-50 p-6 rounded-r-lg">
            <h4 className="font-semibold text-blue-900 mb-3">AI Analysis Results</h4>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm bg-white p-4 rounded border border-blue-200 overflow-x-auto">
                {timingResult.output}
              </pre>
            </div>
          </div>

          {/* Quick Recommendation */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="text-green-800 font-semibold mb-1">Recommended Action</div>
              <div className="text-2xl">
                {selectedJob.daysSinceContact >= 7 ? '✅ Follow up now' : '⏳ Wait a bit'}
              </div>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="text-purple-800 font-semibold mb-1">Best Time</div>
              <div className="text-lg">Tue-Thu, 9-11 AM</div>
            </div>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="text-orange-800 font-semibold mb-1">Expected Response</div>
              <div className="text-lg">
                {selectedJob.status === 'interview' ? '30-40%' : '15-25%'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timing Guidelines */}
      {!timingResult && (
        <div className="bg-gray-50 rounded-lg p-6 mt-6">
          <h4 className="font-semibold text-gray-900 mb-4">General Timing Guidelines</h4>
          <div className="space-y-3">
            <div className="flex items-start">
              <div className="text-green-600 font-bold mr-3">✓</div>
              <div>
                <div className="font-medium">Initial Application</div>
                <div className="text-sm text-gray-600">Wait 7 days, then follow up</div>
              </div>
            </div>
            <div className="flex items-start">
              <div className="text-green-600 font-bold mr-3">✓</div>
              <div>
                <div className="font-medium">Post-Interview</div>
                <div className="text-sm text-gray-600">Send thank you within 24 hours, check-in after 2-3 days</div>
              </div>
            </div>
            <div className="flex items-start">
              <div className="text-green-600 font-bold mr-3">✓</div>
              <div>
                <div className="font-medium">Offer Response</div>
                <div className="text-sm text-gray-600">Respond within 24 hours, even if just to acknowledge</div>
              </div>
            </div>
            <div className="flex items-start">
              <div className="text-red-600 font-bold mr-3">✗</div>
              <div>
                <div className="font-medium">Avoid</div>
                <div className="text-sm text-gray-600">Monday mornings, Friday afternoons, weekends</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimingOptimizerCard;
