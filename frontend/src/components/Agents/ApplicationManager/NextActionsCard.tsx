import React, { useState } from 'react';

interface NextActionsFormData {
  status: string;
  days_since_activity: number;
  last_interaction_type: string;
  sentiment: string;
}

const NextActionsCard: React.FC = () => {
  const [formData, setFormData] = useState<NextActionsFormData>({
    status: 'applied',
    days_since_activity: 7,
    last_interaction_type: 'application_submission',
    sentiment: 'neutral'
  });
  const [actions, setActions] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRecommend = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/application-manager/next-actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations');
      }

      const data = await response.json();
      setActions(data.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    setFormData({
      status: 'technical',
      days_since_activity: 3,
      last_interaction_type: 'interview',
      sentiment: 'positive'
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Application Context
        </h2>

        {/* Status */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Status
          </label>
          <select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="applied">Applied</option>
            <option value="screening">Screening</option>
            <option value="phone_screen">Phone Screen</option>
            <option value="technical">Technical Interview</option>
            <option value="onsite">Onsite Interview</option>
            <option value="final_round">Final Round</option>
            <option value="offer">Offer</option>
          </select>
        </div>

        {/* Days Since Activity */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Days Since Last Activity
          </label>
          <input
            type="number"
            value={formData.days_since_activity}
            onChange={(e) => setFormData({ ...formData, days_since_activity: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Last Interaction Type */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Last Interaction Type
          </label>
          <select
            value={formData.last_interaction_type}
            onChange={(e) => setFormData({ ...formData, last_interaction_type: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="application_submission">Application Submission</option>
            <option value="email">Email</option>
            <option value="interview">Interview</option>
            <option value="phone_call">Phone Call</option>
            <option value="assessment">Assessment</option>
            <option value="rejection">Rejection</option>
          </select>
        </div>

        {/* Sentiment */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Overall Sentiment
          </label>
          <select
            value={formData.sentiment}
            onChange={(e) => setFormData({ ...formData, sentiment: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="very positive">Very Positive</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
            <option value="concerning">Concerning</option>
          </select>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
            ❌ {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleRecommend}
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-4 rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⚙️</span>
                Analyzing...
              </>
            ) : (
              <>
                <span>📋</span>
                Get Recommendations
              </>
            )}
          </button>
          <button
            onClick={loadSample}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-3 px-4 rounded-md transition-colors duration-200"
          >
            📝 Sample
          </button>
        </div>
      </div>

      {/* Results Section */}
      <div>
        {actions ? (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Recommended Next Actions
            </h3>
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md text-sm font-mono">
                {actions}
              </pre>
            </div>
          </div>
        ) : (
          <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <span className="text-6xl mb-4 block">📋</span>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Recommendations Yet
            </h3>
            <p className="text-gray-600">
              Provide application context to get personalized action recommendations
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NextActionsCard;
