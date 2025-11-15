import React, { useState } from 'react';

interface LifecycleFormData {
  job_id: number;
  current_status: string;
  days_elapsed: number;
  last_activity: string;
  company_type: string;
}

const LifecyclePredictionCard: React.FC = () => {
  const [formData, setFormData] = useState<LifecycleFormData>({
    job_id: 1,
    current_status: 'applied',
    days_elapsed: 7,
    last_activity: 'submitted application',
    company_type: 'medium'
  });
  const [prediction, setPrediction] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/application-manager/predict-lifecycle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to predict lifecycle');
      }

      const data = await response.json();
      setPrediction(data.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    setFormData({
      job_id: 123,
      current_status: 'phone_screen',
      days_elapsed: 5,
      last_activity: 'interview completed',
      company_type: 'startup'
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Application Details
        </h2>

        {/* Job ID */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Application ID
          </label>
          <input
            type="number"
            value={formData.job_id}
            onChange={(e) => setFormData({ ...formData, job_id: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Current Status */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Status
          </label>
          <select
            value={formData.current_status}
            onChange={(e) => setFormData({ ...formData, current_status: e.target.value })}
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

        {/* Days Elapsed */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Days Elapsed
          </label>
          <input
            type="number"
            value={formData.days_elapsed}
            onChange={(e) => setFormData({ ...formData, days_elapsed: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Last Activity */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Last Activity
          </label>
          <input
            type="text"
            value={formData.last_activity}
            onChange={(e) => setFormData({ ...formData, last_activity: e.target.value })}
            placeholder="e.g., completed phone screen"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Company Type */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Type/Size
          </label>
          <select
            value={formData.company_type}
            onChange={(e) => setFormData({ ...formData, company_type: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="startup">Startup</option>
            <option value="small">Small (1-50)</option>
            <option value="medium">Medium (51-500)</option>
            <option value="large">Large (501-5000)</option>
            <option value="enterprise">Enterprise (5000+)</option>
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
            onClick={handlePredict}
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-4 rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⚙️</span>
                Predicting...
              </>
            ) : (
              <>
                <span>📈</span>
                Predict Lifecycle
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
        {prediction ? (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Lifecycle Prediction
            </h3>
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md text-sm font-mono">
                {prediction}
              </pre>
            </div>
          </div>
        ) : (
          <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <span className="text-6xl mb-4 block">📈</span>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Prediction Yet
            </h3>
            <p className="text-gray-600">
              Fill in application details and click "Predict Lifecycle" to get AI-powered insights
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LifecyclePredictionCard;
