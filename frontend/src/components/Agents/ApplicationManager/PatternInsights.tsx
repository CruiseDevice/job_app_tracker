// FILE: frontend/src/components/Agents/ApplicationManager/PatternInsights.tsx

import React from 'react';

interface PatternData {
  total_applications: number;
  success_rate: number;
  status_distribution: { [key: string]: number };
  avg_response_time?: number;
  insights: string[];
}

interface PatternInsightsProps {
  data: PatternData;
  loading?: boolean;
}

const PatternInsights: React.FC<PatternInsightsProps> = ({
  data,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 30) return 'text-green-600';
    if (rate >= 15) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'offer') return 'bg-green-100 text-green-800';
    if (statusLower === 'interview') return 'bg-blue-100 text-blue-800';
    if (statusLower === 'assessment') return 'bg-purple-100 text-purple-800';
    if (statusLower === 'screening') return 'bg-yellow-100 text-yellow-800';
    if (statusLower === 'applied') return 'bg-gray-100 text-gray-800';
    if (statusLower === 'rejected') return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🔍</span>
          <h3 className="text-lg font-semibold text-gray-900">
            Success Pattern Analysis
          </h3>
        </div>
      </div>

      <div className="p-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-xs text-gray-600 mb-1">Total Applications</p>
            <p className="text-2xl font-bold text-blue-600">{data.total_applications}</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-xs text-gray-600 mb-1">Success Rate</p>
            <p className={`text-2xl font-bold ${getSuccessRateColor(data.success_rate)}`}>
              {data.success_rate.toFixed(1)}%
            </p>
          </div>
          {data.avg_response_time && (
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-xs text-gray-600 mb-1">Avg Response Time</p>
              <p className="text-2xl font-bold text-green-600">
                {data.avg_response_time.toFixed(0)}d
              </p>
            </div>
          )}
        </div>

        {/* Status Distribution */}
        {data.status_distribution && Object.keys(data.status_distribution).length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Status Distribution</h4>
            <div className="space-y-2">
              {Object.entries(data.status_distribution)
                .sort(([, a], [, b]) => b - a)
                .map(([status, count]) => {
                  const percentage = (count / data.total_applications) * 100;
                  return (
                    <div key={status} className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(status)} min-w-[80px] text-center`}>
                        {status}
                      </span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 min-w-[60px] text-right">
                        {count} ({percentage.toFixed(0)}%)
                      </span>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* Key Insights */}
        {data.insights && data.insights.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <span>💡</span>
              Key Insights
            </h4>
            <div className="space-y-2">
              {data.insights.map((insight, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-700 bg-gray-50 rounded-lg p-3"
                >
                  <span className="text-blue-600 mt-0.5">•</span>
                  <p className="flex-1">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {(!data.insights || data.insights.length === 0) && (
          <div className="text-center py-6 text-gray-500">
            <p className="text-sm">No patterns identified yet. Apply to more jobs to see insights!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatternInsights;
