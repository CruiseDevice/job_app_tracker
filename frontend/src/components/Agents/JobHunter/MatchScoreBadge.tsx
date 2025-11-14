// FILE: frontend/src/components/Agents/JobHunter/MatchScoreBadge.tsx

import React from 'react';
import { TrendingUp, Target } from 'lucide-react';

interface MatchScoreBadgeProps {
  score: number;
  level?: string;
}

const MatchScoreBadge: React.FC<MatchScoreBadgeProps> = ({ score, level }) => {
  // Determine color and styling based on score
  const getScoreColor = () => {
    if (score >= 80) return 'bg-green-100 text-green-800 border-green-300';
    if (score >= 60) return 'bg-blue-100 text-blue-800 border-blue-300';
    if (score >= 40) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getScoreLabel = () => {
    if (level) return level;
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Low Match';
  };

  const getIcon = () => {
    if (score >= 80) return <Target className="h-5 w-5" />;
    return <TrendingUp className="h-5 w-5" />;
  };

  return (
    <div className="flex flex-col items-end gap-1">
      {/* Score Badge */}
      <div
        className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 ${getScoreColor()}`}
      >
        {getIcon()}
        <div className="text-right">
          <div className="text-2xl font-bold leading-none">{score}%</div>
          <div className="text-xs font-medium mt-1">{getScoreLabel()}</div>
        </div>
      </div>

      {/* Visual Score Bar */}
      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            score >= 80
              ? 'bg-green-500'
              : score >= 60
              ? 'bg-blue-500'
              : score >= 40
              ? 'bg-yellow-500'
              : 'bg-gray-400'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
};

export default MatchScoreBadge;
