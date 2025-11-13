// FILE: frontend/src/components/Agents/EmailAnalyst/EmailAnalysisCard.tsx

import React, { useState } from 'react';
import SentimentBadge, { SentimentType, UrgencyLevel } from './SentimentBadge';
import ActionItemsList from './ActionItemsList';
import FollowupRecommendations from './FollowupRecommendations';

interface EmailAnalysisData {
  subject: string;
  sender: string;
  sentiment?: SentimentType;
  urgency?: UrgencyLevel;
  confidence?: number;
  category?: string;
  company?: string;
  position?: string;
  actionItems?: string[];
  followup?: {
    action: string;
    timeline: string;
    steps: string[];
    priority?: 'high' | 'medium' | 'low';
  };
  matchingApplications?: Array<{
    company: string;
    position: string;
    status: string;
  }>;
  analysis?: string;
}

interface EmailAnalysisCardProps {
  data: EmailAnalysisData;
  loading?: boolean;
  onReanalyze?: () => void;
}

const EmailAnalysisCard: React.FC<EmailAnalysisCardProps> = ({
  data,
  loading = false,
  onReanalyze
}) => {
  const [expanded, setExpanded] = useState(true);

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">🤖</span>
              <h3 className="text-lg font-semibold text-gray-900">
                Email Analysis
              </h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              <span className="font-medium">From:</span> {data.sender}
            </p>
            <p className="text-sm font-medium text-gray-900">
              {data.subject}
            </p>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            {expanded ? '▼' : '▶'}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="p-4 space-y-4">
          {/* Sentiment & Urgency */}
          {(data.sentiment || data.urgency) && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Sentiment & Urgency
              </h4>
              <SentimentBadge
                sentiment={data.sentiment || 'neutral'}
                urgency={data.urgency}
                confidence={data.confidence}
              />
            </div>
          )}

          {/* Category & Details */}
          {(data.category || data.company || data.position) && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {data.category && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Category</p>
                  <p className="font-medium text-gray-900">{data.category}</p>
                </div>
              )}
              {data.company && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Company</p>
                  <p className="font-medium text-gray-900">{data.company}</p>
                </div>
              )}
              {data.position && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Position</p>
                  <p className="font-medium text-gray-900">{data.position}</p>
                </div>
              )}
            </div>
          )}

          {/* Analysis Text */}
          {data.analysis && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                AI Analysis
              </h4>
              <div className="text-sm text-gray-700 whitespace-pre-wrap">
                {data.analysis}
              </div>
            </div>
          )}

          {/* Matching Applications */}
          {data.matchingApplications && data.matchingApplications.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                🎯 Matching Applications
              </h4>
              <div className="space-y-2">
                {data.matchingApplications.map((app, index) => (
                  <div
                    key={index}
                    className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div>
                      <p className="font-medium text-gray-900">
                        {app.company} - {app.position}
                      </p>
                      <p className="text-sm text-gray-600">
                        Status: {app.status}
                      </p>
                    </div>
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View →
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Items */}
          {data.actionItems && data.actionItems.length > 0 && (
            <ActionItemsList items={data.actionItems} />
          )}

          {/* Follow-up Recommendations */}
          {data.followup && (
            <FollowupRecommendations recommendation={data.followup} />
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-2 border-t border-gray-200">
            {onReanalyze && (
              <button
                onClick={onReanalyze}
                className="flex-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-md transition-colors duration-200"
              >
                🔄 Re-analyze
              </button>
            )}
            <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200">
              💾 Save Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailAnalysisCard;
