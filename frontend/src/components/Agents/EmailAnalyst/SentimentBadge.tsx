// FILE: frontend/src/components/Agents/EmailAnalyst/SentimentBadge.tsx

import React from 'react';

export type SentimentType = 'positive' | 'negative' | 'neutral';
export type UrgencyLevel = 'high' | 'medium' | 'low';

interface SentimentBadgeProps {
  sentiment: SentimentType;
  urgency?: UrgencyLevel;
  confidence?: number;
  size?: 'sm' | 'md' | 'lg';
}

const SentimentBadge: React.FC<SentimentBadgeProps> = ({
  sentiment,
  urgency,
  confidence,
  size = 'md'
}) => {
  const getSentimentConfig = (sentiment: SentimentType) => {
    switch (sentiment) {
      case 'positive':
        return {
          text: 'Positive',
          className: 'bg-green-100 text-green-800 border-green-200',
          icon: '✅'
        };
      case 'negative':
        return {
          text: 'Negative',
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: '❌'
        };
      case 'neutral':
        return {
          text: 'Neutral',
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '➖'
        };
      default:
        return {
          text: 'Unknown',
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '❓'
        };
    }
  };

  const getUrgencyConfig = (urgency: UrgencyLevel) => {
    switch (urgency) {
      case 'high':
        return {
          text: 'High Urgency',
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: '⚡'
        };
      case 'medium':
        return {
          text: 'Medium Urgency',
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: '⏰'
        };
      case 'low':
        return {
          text: 'Low Urgency',
          className: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '📅'
        };
      default:
        return {
          text: 'No Urgency',
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '🕐'
        };
    }
  };

  const getSizeClasses = (size: 'sm' | 'md' | 'lg') => {
    switch (size) {
      case 'sm':
        return 'px-2 py-0.5 text-xs';
      case 'md':
        return 'px-2.5 py-1 text-sm';
      case 'lg':
        return 'px-3 py-1.5 text-base';
      default:
        return 'px-2.5 py-1 text-sm';
    }
  };

  const sentimentConfig = getSentimentConfig(sentiment);
  const sizeClasses = getSizeClasses(size);

  return (
    <div className="flex flex-wrap gap-2 items-center">
      {/* Sentiment Badge */}
      <span
        className={`inline-flex items-center rounded-full font-medium border ${sizeClasses} ${sentimentConfig.className}`}
      >
        <span className="mr-1" role="img" aria-label={sentimentConfig.text}>
          {sentimentConfig.icon}
        </span>
        {sentimentConfig.text}
        {confidence && (
          <span className="ml-1 text-xs opacity-75">
            ({confidence}%)
          </span>
        )}
      </span>

      {/* Urgency Badge */}
      {urgency && (
        <span
          className={`inline-flex items-center rounded-full font-medium border ${sizeClasses} ${getUrgencyConfig(urgency).className}`}
        >
          <span className="mr-1" role="img" aria-label={getUrgencyConfig(urgency).text}>
            {getUrgencyConfig(urgency).icon}
          </span>
          {getUrgencyConfig(urgency).text}
        </span>
      )}
    </div>
  );
};

export default SentimentBadge;
