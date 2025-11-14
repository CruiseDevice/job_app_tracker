// FILE: frontend/src/components/Agents/Analytics/PerformanceMetricsCard.tsx

import React from 'react';

interface PerformanceMetricsCardProps {
  userId: number;
}

const PerformanceMetricsCard: React.FC<PerformanceMetricsCardProps> = ({ userId }) => {
  // Sample metrics data
  const metrics = [
    {
      name: 'Application Velocity',
      value: 12,
      unit: 'apps/week',
      benchmark: 10,
      performance: 'Above average',
      percentile: 65,
      color: 'blue'
    },
    {
      name: 'Response Rate',
      value: 73,
      unit: '%',
      benchmark: 60,
      performance: 'Good',
      percentile: 70,
      color: 'green'
    },
    {
      name: 'Interview Conversion',
      value: 27,
      unit: '%',
      benchmark: 22,
      performance: 'Above average',
      percentile: 68,
      color: 'purple'
    },
    {
      name: 'Offer Conversion',
      value: 6.7,
      unit: '%',
      benchmark: 15,
      performance: 'Below average',
      percentile: 35,
      color: 'red'
    },
    {
      name: 'Time to Offer',
      value: 28.3,
      unit: 'days',
      benchmark: 24.0,
      performance: 'Slightly slow',
      percentile: 45,
      color: 'orange'
    },
    {
      name: 'Application Quality',
      value: 7.8,
      unit: '/10',
      benchmark: 7.0,
      performance: 'Good',
      percentile: 72,
      color: 'teal'
    }
  ];

  const getColorClasses = (color: string) => {
    const colors: any = {
      blue: 'bg-blue-100 text-blue-700',
      green: 'bg-green-100 text-green-700',
      purple: 'bg-purple-100 text-purple-700',
      red: 'bg-red-100 text-red-700',
      orange: 'bg-orange-100 text-orange-700',
      teal: 'bg-teal-100 text-teal-700'
    };
    return colors[color] || colors.blue;
  };

  const getPerformanceColor = (percentile: number) => {
    if (percentile >= 75) return 'text-green-600';
    if (percentile >= 50) return 'text-blue-600';
    if (percentile >= 25) return 'text-orange-600';
    return 'text-red-600';
  };

  const overallScore = Math.round(
    metrics.reduce((sum, m) => sum + m.percentile, 0) / metrics.length
  );

  const getGrade = (score: number) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B+';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C+';
    if (score >= 50) return 'C';
    return 'D';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Performance Metrics</h3>
        <span className="text-2xl">📈</span>
      </div>

      {/* Overall Score */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="text-sm text-gray-600 mb-1">Overall Performance Score</div>
            <div className="text-4xl font-bold text-blue-600">{overallScore}</div>
            <div className="text-sm text-gray-500 mt-1">
              Grade: <span className="font-bold text-blue-700">{getGrade(overallScore)}</span> - Good performance with room for improvement
            </div>
          </div>
          <div className="w-32 h-32">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="#E5E7EB"
                strokeWidth="10"
                fill="none"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="#3B82F6"
                strokeWidth="10"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - overallScore / 100)}`}
                className="transition-all duration-1000"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Individual Metrics */}
      <div className="space-y-4 mb-6">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{metric.name}</h4>
                <div className="flex items-baseline gap-3 mt-1">
                  <span className="text-2xl font-bold text-gray-900">
                    {metric.value}
                  </span>
                  <span className="text-sm text-gray-500">{metric.unit}</span>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getColorClasses(metric.color)}`}>
                {metric.performance}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span>vs Benchmark ({metric.benchmark}{metric.unit})</span>
                <span className={getPerformanceColor(metric.percentile)}>
                  {metric.percentile}th percentile
                </span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    metric.percentile >= 75 ? 'bg-green-500' :
                    metric.percentile >= 50 ? 'bg-blue-500' :
                    metric.percentile >= 25 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${metric.percentile}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Strengths and Areas for Improvement */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-green-900 mb-3">✓ Strengths</h4>
          <ul className="space-y-2 text-sm text-green-800">
            <li>• High application velocity - staying active</li>
            <li>• Strong response rate - good targeting</li>
            <li>• Above-average application quality</li>
          </ul>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-orange-900 mb-3">⚠ Areas for Improvement</h4>
          <ul className="space-y-2 text-sm text-orange-800">
            <li>• Offer conversion rate below benchmark</li>
            <li>• Time to offer slightly high</li>
            <li>• Need more interview preparation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetricsCard;
