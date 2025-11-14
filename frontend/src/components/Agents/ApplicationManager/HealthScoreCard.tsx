// FILE: frontend/src/components/Agents/ApplicationManager/HealthScoreCard.tsx

import React from 'react';

export type HealthRating = 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';

interface HealthScoreData {
  score: number;
  rating: HealthRating;
  breakdown: {
    status: number;
    timeline: number;
    engagement: number;
  };
  recommendation: string;
}

interface HealthScoreCardProps {
  data: HealthScoreData;
  applicationName?: string;
  loading?: boolean;
}

const HealthScoreCard: React.FC<HealthScoreCardProps> = ({
  data,
  applicationName,
  loading = false
}) => {
  const getRatingConfig = (rating: HealthRating) => {
    switch (rating) {
      case 'EXCELLENT':
        return {
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-300',
          emoji: '🟢',
          gradient: 'from-green-400 to-green-600'
        };
      case 'GOOD':
        return {
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-100',
          borderColor: 'border-yellow-300',
          emoji: '🟡',
          gradient: 'from-yellow-400 to-yellow-600'
        };
      case 'FAIR':
        return {
          color: 'text-orange-600',
          bgColor: 'bg-orange-100',
          borderColor: 'border-orange-300',
          emoji: '🟠',
          gradient: 'from-orange-400 to-orange-600'
        };
      case 'POOR':
        return {
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-300',
          emoji: '🔴',
          gradient: 'from-red-400 to-red-600'
        };
    }
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-24 bg-gray-200 rounded mb-4"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const config = getRatingConfig(data.rating);

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className={`${config.bgColor} border-b ${config.borderColor} p-4`}>
        <div className="flex items-center gap-2">
          <span className="text-2xl">{config.emoji}</span>
          <h3 className="text-lg font-semibold text-gray-900">
            Application Health Score
          </h3>
        </div>
        {applicationName && (
          <p className="text-sm text-gray-600 mt-1">{applicationName}</p>
        )}
      </div>

      {/* Score Display */}
      <div className="p-6">
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            {/* Circular Progress */}
            <svg className="w-32 h-32 transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="#e5e7eb"
                strokeWidth="8"
                fill="none"
              />
              {/* Progress circle */}
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke={`url(#gradient-${data.rating})`}
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - data.score / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
              {/* Gradient definition */}
              <defs>
                <linearGradient id={`gradient-${data.rating}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" className={config.gradient.split(' ')[0].replace('from-', 'stop-color-')} />
                  <stop offset="100%" className={config.gradient.split(' ')[1].replace('to-', 'stop-color-')} />
                </linearGradient>
              </defs>
            </svg>

            {/* Score text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-3xl font-bold ${config.color}`}>
                {data.score}
              </span>
              <span className="text-sm text-gray-500">/ 100</span>
            </div>
          </div>
        </div>

        {/* Rating */}
        <div className="text-center mb-6">
          <span className={`inline-block px-4 py-2 rounded-full ${config.bgColor} ${config.color} font-semibold text-lg`}>
            {data.rating}
          </span>
        </div>

        {/* Score Breakdown */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Score Breakdown</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Status Progression</span>
              <span className="font-medium text-gray-900">+{data.breakdown.status} pts</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Timeline</span>
              <span className="font-medium text-gray-900">-{data.breakdown.timeline} pts</span>
            </div>
            {data.breakdown.engagement > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Engagement</span>
                <span className="font-medium text-gray-900">+{data.breakdown.engagement} pts</span>
              </div>
            )}
          </div>
        </div>

        {/* Recommendation */}
        {data.recommendation && (
          <div className={`${config.bgColor} ${config.borderColor} border rounded-lg p-3`}>
            <div className="flex items-start gap-2">
              <span className="text-lg mt-0.5">💡</span>
              <div>
                <p className="text-sm font-medium text-gray-900 mb-1">Recommendation</p>
                <p className="text-sm text-gray-700">{data.recommendation}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthScoreCard;
