// FILE: frontend/src/components/Agents/Analytics/DataAnalysisCard.tsx

import React, { useState } from 'react';
import axios from 'axios';

interface DataAnalysisCardProps {
  userId: number;
}

const DataAnalysisCard: React.FC<DataAnalysisCardProps> = ({ userId }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [timePeriod, setTimePeriod] = useState(90);
  const [error, setError] = useState<string | null>(null);

  const analyzeData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/agents/analytics/analyze-data', {
        user_id: userId,
        time_period_days: timePeriod
      });

      setAnalysis(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze data');
      console.error('Error analyzing data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Application Data Analysis</h3>
        <span className="text-2xl">📊</span>
      </div>

      {/* Time Period Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Time Period
        </label>
        <select
          value={timePeriod}
          onChange={(e) => setTimePeriod(Number(e.target.value))}
          className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={30}>Last 30 days</option>
          <option value={60}>Last 60 days</option>
          <option value={90}>Last 90 days</option>
          <option value={180}>Last 6 months</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Sample Statistics (would be replaced with real data) */}
      {!analysis && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-sm text-blue-600 font-medium mb-1">Conversion Rate</div>
            <div className="text-2xl font-bold text-blue-700">37.8%</div>
            <div className="text-xs text-blue-500 mt-1">Application → Screening</div>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-sm text-green-600 font-medium mb-1">Interview Rate</div>
            <div className="text-2xl font-bold text-green-700">61.5%</div>
            <div className="text-xs text-green-500 mt-1">Screening → Interview</div>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-sm text-purple-600 font-medium mb-1">Offer Rate</div>
            <div className="text-2xl font-bold text-purple-700">25%</div>
            <div className="text-xs text-purple-500 mt-1">Interview → Offer</div>
          </div>
        </div>
      )}

      {/* Industry Breakdown */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Industry Breakdown</h4>
        <div className="space-y-2">
          {[
            { name: 'Technology', count: 25, percentage: 56 },
            { name: 'Finance', count: 10, percentage: 22 },
            { name: 'Healthcare', count: 5, percentage: 11 },
            { name: 'Other', count: 5, percentage: 11 }
          ].map((industry) => (
            <div key={industry.name} className="flex items-center gap-3">
              <div className="w-24 text-sm text-gray-600">{industry.name}</div>
              <div className="flex-1">
                <div className="bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${industry.percentage}%` }}
                  />
                </div>
              </div>
              <div className="w-16 text-right text-sm font-medium text-gray-700">
                {industry.count}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Key Insights</h4>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">✓</span>
            <span>Application volume increased 50% in the last month</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">✓</span>
            <span>Highest conversion rate with Medium-sized companies (20%)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">ℹ</span>
            <span>Technology sector shows 40% higher response rate</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">ℹ</span>
            <span>Applications sent Tuesday-Thursday get 25% more responses</span>
          </li>
        </ul>
      </div>

      {/* Analyze Button */}
      <button
        onClick={analyzeData}
        disabled={isLoading}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyzing...
          </span>
        ) : (
          '🤖 Generate AI Analysis'
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Analysis Result */}
      {analysis && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="font-medium text-green-900 mb-2">AI Analysis Complete</h4>
          <pre className="text-sm text-green-800 whitespace-pre-wrap">{analysis.analysis}</pre>
        </div>
      )}
    </div>
  );
};

export default DataAnalysisCard;
