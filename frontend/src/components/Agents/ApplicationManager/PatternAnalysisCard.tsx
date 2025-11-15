import React, { useState } from 'react';

interface Application {
  status: string;
  company_type: string;
  response_days: number | null;
}

const PatternAnalysisCard: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([
    { status: 'applied', company_type: 'startup', response_days: 7 },
    { status: 'interview', company_type: 'enterprise', response_days: 3 },
    { status: 'rejected', company_type: 'medium', response_days: 14 }
  ]);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (applications.length === 0) {
      setError('Please add at least one application');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/application-manager/analyze-patterns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ applications }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze patterns');
      }

      const data = await response.json();
      setAnalysis(data.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const addApplication = () => {
    setApplications([
      ...applications,
      { status: 'applied', company_type: 'medium', response_days: null }
    ]);
  };

  const removeApplication = (index: number) => {
    setApplications(applications.filter((_, i) => i !== index));
  };

  const updateApplication = (index: number, field: keyof Application, value: any) => {
    const updated = [...applications];
    updated[index] = { ...updated[index], [field]: value };
    setApplications(updated);
  };

  const loadSample = () => {
    setApplications([
      { status: 'applied', company_type: 'startup', response_days: 7 },
      { status: 'phone_screen', company_type: 'medium', response_days: 5 },
      { status: 'technical', company_type: 'enterprise', response_days: 3 },
      { status: 'onsite', company_type: 'large', response_days: 10 },
      { status: 'rejected', company_type: 'startup', response_days: 14 },
      { status: 'applied', company_type: 'medium', response_days: null },
      { status: 'ghosted', company_type: 'startup', response_days: null },
      { status: 'offer', company_type: 'enterprise', response_days: 2 }
    ]);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Applications ({applications.length})
          </h2>
          <div className="flex gap-2">
            <button
              onClick={addApplication}
              className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-md text-sm transition-colors duration-200"
            >
              ➕ Add
            </button>
            <button
              onClick={loadSample}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1 rounded-md text-sm transition-colors duration-200"
            >
              📝 Sample
            </button>
          </div>
        </div>

        <div className="max-h-96 overflow-y-auto space-y-3 mb-4">
          {applications.map((app, index) => (
            <div key={index} className="p-3 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-medium text-gray-700">App #{index + 1}</span>
                <button
                  onClick={() => removeApplication(index)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  ❌
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Status</label>
                  <select
                    value={app.status}
                    onChange={(e) => updateApplication(index, 'status', e.target.value)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="applied">Applied</option>
                    <option value="screening">Screening</option>
                    <option value="phone_screen">Phone Screen</option>
                    <option value="technical">Technical</option>
                    <option value="onsite">Onsite</option>
                    <option value="offer">Offer</option>
                    <option value="rejected">Rejected</option>
                    <option value="ghosted">Ghosted</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-gray-600 mb-1">Company Type</label>
                  <select
                    value={app.company_type}
                    onChange={(e) => updateApplication(index, 'company_type', e.target.value)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="startup">Startup</option>
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
              </div>

              <div className="mt-2">
                <label className="block text-xs text-gray-600 mb-1">Response Days (optional)</label>
                <input
                  type="number"
                  value={app.response_days ?? ''}
                  onChange={(e) => updateApplication(index, 'response_days', e.target.value ? parseInt(e.target.value) : null)}
                  placeholder="Leave empty if no response"
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
            ❌ {error}
          </div>
        )}

        {/* Actions */}
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-4 rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin">⚙️</span>
              Analyzing Patterns...
            </>
          ) : (
            <>
              <span>🔍</span>
              Analyze Patterns
            </>
          )}
        </button>
      </div>

      {/* Results Section */}
      <div>
        {analysis ? (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Pattern Analysis Results
            </h3>
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md text-sm font-mono">
                {analysis}
              </pre>
            </div>
          </div>
        ) : (
          <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <span className="text-6xl mb-4 block">🔍</span>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Analysis Yet
            </h3>
            <p className="text-gray-600">
              Add application data and click "Analyze Patterns" to identify trends and insights
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatternAnalysisCard;
