// FILE: frontend/src/components/Agents/ApplicationManager/NextActionsCard.tsx

import React from 'react';

type Priority = 'critical' | 'high' | 'medium' | 'low';

interface Action {
  action: string;
  priority: Priority;
  timeline: string;
}

interface NextActionsData {
  short_term: Action[];
  long_term?: Action[];
}

interface NextActionsCardProps {
  data: NextActionsData;
  applicationName?: string;
  onActionClick?: (action: Action) => void;
  loading?: boolean;
}

const NextActionsCard: React.FC<NextActionsCardProps> = ({
  data,
  applicationName,
  onActionClick,
  loading = false
}) => {
  const getPriorityConfig = (priority: Priority) => {
    switch (priority) {
      case 'critical':
        return { emoji: '🔴', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' };
      case 'high':
        return { emoji: '🟠', color: 'text-orange-600', bgColor: 'bg-orange-50', borderColor: 'border-orange-200' };
      case 'medium':
        return { emoji: '🟡', color: 'text-yellow-600', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' };
      case 'low':
        return { emoji: '🟢', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' };
    }
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📋</span>
          <h3 className="text-lg font-semibold text-gray-900">
            Recommended Next Actions
          </h3>
        </div>
        {applicationName && (
          <p className="text-sm text-gray-600 mt-1">{applicationName}</p>
        )}
      </div>

      <div className="p-6">
        {/* Short-term actions */}
        {data.short_term && data.short_term.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <span>⚡</span>
              Immediate Actions (Next 7 Days)
            </h4>
            <div className="space-y-3">
              {data.short_term.map((action, index) => {
                const config = getPriorityConfig(action.priority);
                return (
                  <div
                    key={index}
                    className={`border ${config.borderColor} ${config.bgColor} rounded-lg p-4 ${
                      onActionClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
                    }`}
                    onClick={() => onActionClick?.(action)}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xl flex-shrink-0">{config.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 mb-1">
                          {action.action}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <span className="flex items-center gap-1">
                            <span>⏰</span>
                            {action.timeline}
                          </span>
                          <span className={`px-2 py-0.5 rounded-full ${config.color} font-medium`}>
                            {action.priority.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Long-term actions */}
        {data.long_term && data.long_term.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <span>📅</span>
              Long-term Actions
            </h4>
            <div className="space-y-3">
              {data.long_term.map((action, index) => {
                const config = getPriorityConfig(action.priority);
                return (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xl flex-shrink-0">{config.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 mb-1">
                          {action.action}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <span className="flex items-center gap-1">
                            <span>⏰</span>
                            {action.timeline}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {!data.short_term?.length && !data.long_term?.length && (
          <div className="text-center py-6 text-gray-500">
            <p className="text-sm">No actions recommended at this time.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NextActionsCard;
