import React, { useState } from 'react';

interface ProbabilityFormData {
  status: string;
  response_time: number;
  sentiment: string;
  recruiter_engagement: string;
  company_size: string;
  role_match: number;
}

const SuccessProbabilityCard: React.FC = () => {
  const [formData, setFormData] = useState<ProbabilityFormData>({
    status: 'applied',
    response_time: 7,
    sentiment: 'neutral',
    recruiter_engagement: 'medium',
    company_size: 'medium',
    role_match: 70
  });
  const [probability, setProbability] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEstimate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/application-manager/success-probability', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to estimate probability');
      }

      const data = await response.json();
      setProbability(data.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    setFormData({
      status: 'onsite',
      response_time: 3,
      sentiment: 'positive',
      recruiter_engagement: 'high',
      company_size: 'large',
      role_match: 85
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Success Indicators
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

        {/* Response Time */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Response Time (days)
          </label>
          <input
            type="number"
            value={formData.response_time}
            onChange={(e) => setFormData({ ...formData, response_time: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
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
          </select>
        </div>

        {/* Recruiter Engagement */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Recruiter Engagement
          </label>
          <select
            value={formData.recruiter_engagement}
            onChange={(e) => setFormData({ ...formData, recruiter_engagement: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="high">High - Very responsive and engaged</option>
            <option value="medium">Medium - Standard communication</option>
            <option value="low">Low - Minimal interaction</option>
          </select>
        </div>

        {/* Company Size */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Size
          </label>
          <select
            value={formData.company_size}
            onChange={(e) => setFormData({ ...formData, company_size: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="startup">Startup</option>
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </div>

        {/* Role Match */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Role Match ({formData.role_match}%)
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={formData.role_match}
            onChange={(e) => setFormData({ ...formData, role_match: parseInt(e.target.value) })}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Poor Match</span>
            <span>Perfect Match</span>
          </div>
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
            onClick={handleEstimate}
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-4 rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⚙️</span>
                Calculating...
              </>
            ) : (
              <>
                <span>🎯</span>
                Estimate Probability
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
        {probability ? (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Success Probability Estimate
            </h3>
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md text-sm font-mono">
                {probability}
              </pre>
            </div>
          </div>
        ) : (
          <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <span className="text-6xl mb-4 block">🎯</span>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Estimate Yet
            </h3>
            <p className="text-gray-600">
              Provide success indicators to estimate your application's success probability
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SuccessProbabilityCard;
