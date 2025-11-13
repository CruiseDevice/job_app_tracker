// FILE: frontend/src/components/Agents/EmailAnalyst/FollowupRecommendations.tsx

import React from 'react';

interface FollowupStep {
  text: string;
  completed?: boolean;
}

interface FollowupRecommendation {
  action: string;
  timeline: string;
  steps: string[] | FollowupStep[];
  priority?: 'high' | 'medium' | 'low';
}

interface FollowupRecommendationsProps {
  recommendation: FollowupRecommendation;
  onStartAction?: () => void;
}

const FollowupRecommendations: React.FC<FollowupRecommendationsProps> = ({
  recommendation,
  onStartAction
}) => {
  const getPriorityConfig = (priority?: string) => {
    switch (priority) {
      case 'high':
        return {
          className: 'bg-red-50 border-red-200',
          badgeClass: 'bg-red-100 text-red-800',
          icon: '🔴'
        };
      case 'medium':
        return {
          className: 'bg-yellow-50 border-yellow-200',
          badgeClass: 'bg-yellow-100 text-yellow-800',
          icon: '🟡'
        };
      case 'low':
        return {
          className: 'bg-blue-50 border-blue-200',
          badgeClass: 'bg-blue-100 text-blue-800',
          icon: '🔵'
        };
      default:
        return {
          className: 'bg-gray-50 border-gray-200',
          badgeClass: 'bg-gray-100 text-gray-800',
          icon: '⚪'
        };
    }
  };

  const priorityConfig = getPriorityConfig(recommendation.priority);

  const normalizedSteps: FollowupStep[] = recommendation.steps.map(step =>
    typeof step === 'string' ? { text: step, completed: false } : step
  );

  return (
    <div className={`border rounded-lg p-4 ${priorityConfig.className}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-gray-900 mb-1 flex items-center gap-2">
            <span className="text-lg">💡</span>
            Recommended Follow-up
            {recommendation.priority && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${priorityConfig.badgeClass}`}>
                {priorityConfig.icon} {recommendation.priority.toUpperCase()}
              </span>
            )}
          </h3>
        </div>
      </div>

      {/* Action */}
      <div className="mb-3">
        <div className="bg-white border border-gray-200 rounded-md p-3">
          <p className="font-semibold text-gray-900 text-base">
            {recommendation.action}
          </p>
        </div>
      </div>

      {/* Timeline */}
      <div className="mb-4">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-600">⏰ Timeline:</span>
          <span className="font-medium text-gray-900">
            {recommendation.timeline}
          </span>
        </div>
      </div>

      {/* Steps */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-2">
          Steps to Follow:
        </h4>
        <ol className="space-y-2">
          {normalizedSteps.map((step, index) => (
            <li
              key={index}
              className={`flex items-start gap-2 text-sm ${
                step.completed ? 'text-gray-500' : 'text-gray-700'
              }`}
            >
              <span className={`flex-shrink-0 font-medium ${
                step.completed ? 'line-through' : ''
              }`}>
                {index + 1}.
              </span>
              <span className={step.completed ? 'line-through' : ''}>
                {step.text}
              </span>
            </li>
          ))}
        </ol>
      </div>

      {/* Action Button */}
      {onStartAction && (
        <div className="mt-4 pt-3 border-t border-gray-200">
          <button
            onClick={onStartAction}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <span>🚀</span>
            Start This Action
          </button>
        </div>
      )}
    </div>
  );
};

export default FollowupRecommendations;
