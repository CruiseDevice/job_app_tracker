// FILE: frontend/src/components/Agents/FollowUp/StrategyPlannerCard.tsx

import React, { useState } from 'react';

interface FollowUpJob {
  jobId: number;
  company: string;
  position: string;
  status: string;
  applicationDate: string;
  daysSinceContact: number;
}

interface StrategyPlannerCardProps {
  selectedJob: FollowUpJob | null;
}

const StrategyPlannerCard: React.FC<StrategyPlannerCardProps> = ({ selectedJob }) => {
  const [responseHistory, setResponseHistory] = useState('no_response');
  const [priority, setPriority] = useState('medium');
  const [strategyResult, setStrategyResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeStrategy = async () => {
    if (!selectedJob) {
      setError('Please select a job application first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/followup-agent/analyze-strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: selectedJob.status,
          days_since_application: selectedJob.daysSinceContact,
          response_history: responseHistory,
          priority: priority
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze strategy');
      }

      const data = await response.json();
      setStrategyResult(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (!selectedJob) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🎯</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Strategy Planner
        </h3>
        <p className="text-gray-600 mb-6">
          Select a job application to create a comprehensive follow-up strategy
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Create Follow-up Strategy
        </h3>
        <p className="text-gray-600">
          Multi-step follow-up plan for {selectedJob.company} - {selectedJob.position}
        </p>
      </div>

      {/* Configuration Form */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Response History
          </label>
          <select
            value={responseHistory}
            onChange={(e) => setResponseHistory(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="no_response">No Response Yet</option>
            <option value="positive">Positive Response Received</option>
            <option value="mixed">Mixed/Neutral Response</option>
            <option value="none">First Contact</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Priority Level
          </label>
          <div className="grid grid-cols-3 gap-2">
            {['low', 'medium', 'high'].map((p) => (
              <button
                key={p}
                onClick={() => setPriority(p)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  priority === p
                    ? p === 'high'
                      ? 'bg-red-600 text-white'
                      : p === 'medium'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Status</div>
              <div className="font-semibold capitalize">{selectedJob.status}</div>
            </div>
            <div>
              <div className="text-gray-600">Days Since Contact</div>
              <div className="font-semibold">{selectedJob.daysSinceContact} days</div>
            </div>
            <div>
              <div className="text-gray-600">Application Date</div>
              <div className="font-semibold">{selectedJob.applicationDate}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Analyze Button */}
      <button
        onClick={analyzeStrategy}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors mb-6"
      >
        {loading ? 'Analyzing...' : '🎯 Generate Strategy'}
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
      {strategyResult && (
        <div className="space-y-4">
          <div className="border-l-4 border-purple-500 bg-purple-50 p-6 rounded-r-lg">
            <h4 className="font-semibold text-purple-900 mb-3">Follow-up Strategy</h4>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm bg-white p-4 rounded border border-purple-200 overflow-x-auto">
                {strategyResult.output}
              </pre>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="text-green-800 font-semibold mb-1">Expected Response Rate</div>
              <div className="text-2xl font-bold">
                {responseHistory === 'positive' ? '40-60%' :
                 responseHistory === 'no_response' ? '15-25%' : '25-35%'}
              </div>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="text-blue-800 font-semibold mb-1">Follow-up Frequency</div>
              <div className="text-lg">
                {priority === 'high' ? 'Every 5-7 days' :
                 priority === 'low' ? 'Every 10-14 days' : 'Every 7-10 days'}
              </div>
            </div>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="text-orange-800 font-semibold mb-1">Max Attempts</div>
              <div className="text-2xl font-bold">
                {priority === 'high' ? '4-5' : priority === 'low' ? '2-3' : '3-4'}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors">
              Schedule Follow-ups
            </button>
            <button
              onClick={() => setStrategyResult(null)}
              className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              Generate New Strategy
            </button>
          </div>
        </div>
      )}

      {/* Strategy Framework */}
      {!strategyResult && (
        <div className="bg-gray-50 rounded-lg p-6 mt-6">
          <h4 className="font-semibold text-gray-900 mb-4">Strategy Framework</h4>
          <div className="space-y-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <div className="font-medium text-gray-900">Progressive Persistence</div>
              <div className="text-sm text-gray-600 mt-1">
                For applications with no response: Start professional, add value in each follow-up,
                know when to move on (3-4 attempts).
              </div>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <div className="font-medium text-gray-900">Engaged Follow-through</div>
              <div className="text-sm text-gray-600 mt-1">
                For positive responses: Thank quickly, reference conversation, check-in on timeline,
                maintain momentum.
              </div>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <div className="font-medium text-gray-900">Strategic Persistence</div>
              <div className="text-sm text-gray-600 mt-1">
                For mixed responses: Provide additional value, ask specific questions,
                patient but proactive.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategyPlannerCard;
