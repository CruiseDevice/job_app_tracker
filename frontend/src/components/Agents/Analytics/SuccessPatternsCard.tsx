// FILE: frontend/src/components/Agents/Analytics/SuccessPatternsCard.tsx

import React, { useState } from 'react';
import axios from 'axios';

interface SuccessPatternsCardProps {
  userId: number;
}

const SuccessPatternsCard: React.FC<SuccessPatternsCardProps> = ({ userId }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [patterns, setPatterns] = useState<any>(null);
  const [minConfidence, setMinConfidence] = useState(0.7);
  const [error, setError] = useState<string | null>(null);

  const analyzePatterns = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/agents/analytics/success-patterns', {
        user_id: userId,
        min_confidence: minConfidence
      });

      setPatterns(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to identify patterns');
      console.error('Error analyzing patterns:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Sample patterns for display
  const samplePatterns = [
    {
      id: 1,
      name: 'Optimal Application Timing',
      description: 'Applications submitted Tuesday-Thursday 9-11 AM',
      confidence: 85,
      impact: 'high',
      improvement: '+77%',
      recommendation: 'Schedule applications for Tuesday-Thursday mornings'
    },
    {
      id: 2,
      name: 'Personalized Cover Letter Effect',
      description: 'Applications with customized cover letters',
      confidence: 92,
      impact: 'very_high',
      improvement: '+200%',
      recommendation: 'Always include personalized cover letters with company research'
    },
    {
      id: 3,
      name: 'Company Size Sweet Spot',
      description: 'Medium-sized companies (201-1000 employees)',
      confidence: 78,
      impact: 'high',
      improvement: '+133%',
      recommendation: 'Prioritize medium-sized companies in target industry'
    },
    {
      id: 4,
      name: 'Follow-up Timing Optimization',
      description: 'Following up 7-10 days after application',
      confidence: 89,
      impact: 'high',
      improvement: '+100%',
      recommendation: 'Set automatic follow-up reminders for 7-10 days'
    },
    {
      id: 5,
      name: 'Referral Impact',
      description: 'Applications with employee referrals',
      confidence: 95,
      impact: 'very_high',
      improvement: '+333%',
      recommendation: 'Actively seek employee referrals through networking'
    },
    {
      id: 6,
      name: 'Skills Alignment',
      description: '70%+ keyword match between resume and job description',
      confidence: 82,
      impact: 'high',
      improvement: '+171%',
      recommendation: 'Tailor resume to match at least 70% of job requirements'
    }
  ];

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'very_high': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'moderate': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 75) return 'text-blue-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Success Pattern Recognition</h3>
        <span className="text-2xl">🔍</span>
      </div>

      {/* Confidence Threshold */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Minimum Confidence: {(minConfidence * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={minConfidence}
          onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Patterns List */}
      <div className="space-y-4 mb-6">
        {samplePatterns
          .filter(p => p.confidence >= minConfidence * 100)
          .map((pattern) => (
          <div
            key={pattern.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">{pattern.name}</h4>
                <p className="text-sm text-gray-600">{pattern.description}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(pattern.impact)}`}>
                  {pattern.impact.replace('_', ' ').toUpperCase()}
                </span>
                <span className={`text-sm font-medium ${getConfidenceColor(pattern.confidence)}`}>
                  {pattern.confidence}% confidence
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
              <div className="flex items-center gap-2">
                <span className="text-green-600 font-bold">{pattern.improvement}</span>
                <span className="text-sm text-gray-500">improvement</span>
              </div>
            </div>

            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
              <div className="text-xs font-medium text-blue-700 mb-1">💡 Recommendation</div>
              <div className="text-sm text-blue-900">{pattern.recommendation}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Pattern Summary</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">6</div>
            <div className="text-xs text-gray-600">Patterns Found</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">5</div>
            <div className="text-xs text-gray-600">High Confidence</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">+167%</div>
            <div className="text-xs text-gray-600">Avg Improvement</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600">86%</div>
            <div className="text-xs text-gray-600">Avg Confidence</div>
          </div>
        </div>
      </div>

      {/* Analyze Button */}
      <button
        onClick={analyzePatterns}
        disabled={isLoading}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyzing Patterns...
          </span>
        ) : (
          '🤖 Analyze Success Patterns'
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Analysis Result */}
      {patterns && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="font-medium text-green-900 mb-2">Pattern Analysis Complete</h4>
          <pre className="text-sm text-green-800 whitespace-pre-wrap">{patterns.patterns}</pre>
        </div>
      )}
    </div>
  );
};

export default SuccessPatternsCard;
