// FILE: frontend/src/components/Agents/Analytics/StrategyRecommendationsCard.tsx

import React, { useState } from 'react';
import axios from 'axios';

const StrategyRecommendationsCard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [strategy, setStrategy] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    successRate: 0.067,
    applicationsPerWeek: 10,
    targetRole: 'Software Engineer'
  });

  const generateStrategy = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/agents/analytics/strategy', {
        current_stats: {
          success_rate: formData.successRate,
          applications_per_week: formData.applicationsPerWeek
        },
        target_role: formData.targetRole
      });

      setStrategy(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate strategy');
      console.error('Error generating strategy:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Sample recommendations for display
  const sampleRecommendations = [
    {
      priority: 'critical',
      category: 'application_quality',
      title: 'Improve Application Quality',
      description: 'Current success rate below 10% indicates quality issues',
      actions: [
        'Get professional resume review',
        'Customize each application to job description',
        'Use Resume Writer Agent for tailoring',
        'Improve cover letter personalization'
      ],
      impact: '+5-8% success rate'
    },
    {
      priority: 'high',
      category: 'networking',
      title: 'Leverage Networking and Referrals',
      description: 'Referrals increase success rate by 300%',
      actions: [
        'Connect with employees at target companies on LinkedIn',
        'Attend industry events and meetups',
        'Engage in online communities',
        'Request informational interviews'
      ],
      impact: '+20-30% with referrals'
    },
    {
      priority: 'high',
      category: 'targeting',
      title: 'Refine Job Targeting',
      description: 'Focus on roles that better match your profile',
      actions: [
        'Apply only to positions with 70%+ skills match',
        'Target companies with culture fit',
        'Focus on medium-sized companies',
        'Leverage Job Hunter Agent for better matches'
      ],
      impact: '+3-5% success rate'
    },
    {
      priority: 'medium',
      category: 'follow_up',
      title: 'Implement Systematic Follow-up',
      description: 'Follow-ups double response rates',
      actions: [
        'Follow up 7-10 days after each application',
        'Use Follow-up Agent for optimal timing',
        'Send personalized follow-up messages',
        'Track all follow-up interactions'
      ],
      impact: '+100% response rate'
    }
  ];

  const tacticalActions = [
    { timeframe: 'This Week', action: 'Review and optimize resume', effort: '2 hours' },
    { timeframe: 'This Week', action: 'Identify 5 target companies', effort: '3 hours' },
    { timeframe: 'Next Week', action: 'Submit 10 personalized applications', effort: '5 hours' },
    { timeframe: 'Next Week', action: 'Connect with 10 employees', effort: '2 hours' },
    { timeframe: 'Ongoing', action: 'Follow up on all applications', effort: '1 hour/week' }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-300';
      case 'high': return 'text-orange-600 bg-orange-100 border-orange-300';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      default: return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Job Search Optimization Strategy</h3>
        <span className="text-2xl">🎯</span>
      </div>

      {/* Current Performance */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Success Rate: {(formData.successRate * 100).toFixed(1)}%
          </label>
          <input
            type="range"
            min="0"
            max="0.5"
            step="0.01"
            value={formData.successRate}
            onChange={(e) => setFormData({ ...formData, successRate: parseFloat(e.target.value) })}
            className="w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Applications per Week
          </label>
          <input
            type="number"
            min="0"
            max="50"
            value={formData.applicationsPerWeek}
            onChange={(e) => setFormData({ ...formData, applicationsPerWeek: parseInt(e.target.value) })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Role
          </label>
          <input
            type="text"
            value={formData.targetRole}
            onChange={(e) => setFormData({ ...formData, targetRole: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Performance vs Benchmark */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-blue-900 mb-3">Performance vs Industry Average</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <div className="text-xs text-gray-600 mb-1">Your Success Rate</div>
            <div className="text-2xl font-bold text-blue-600">{(formData.successRate * 100).toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-xs text-gray-600 mb-1">Industry Average</div>
            <div className="text-2xl font-bold text-gray-600">15%</div>
          </div>
          <div>
            <div className="text-xs text-gray-600 mb-1">vs Average</div>
            <div className={`text-2xl font-bold ${formData.successRate >= 0.15 ? 'text-green-600' : 'text-red-600'}`}>
              {((formData.successRate / 0.15 - 1) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Strategic Recommendations */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Strategic Recommendations</h4>
        <div className="space-y-4">
          {sampleRecommendations.map((rec, index) => (
            <div
              key={index}
              className={`border-2 rounded-lg p-4 ${getPriorityColor(rec.priority)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase">{rec.priority} Priority</span>
                    <span className="text-xs px-2 py-0.5 bg-white rounded">{rec.category}</span>
                  </div>
                  <h5 className="font-semibold text-gray-900 mb-1">{rec.title}</h5>
                  <p className="text-sm">{rec.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-xs font-medium">Expected Impact</div>
                  <div className="text-sm font-bold">{rec.impact}</div>
                </div>
              </div>

              <div className="mt-3 p-3 bg-white rounded">
                <div className="text-xs font-medium text-gray-700 mb-2">Action Items:</div>
                <ul className="space-y-1">
                  {rec.actions.map((action, actionIndex) => (
                    <li key={actionIndex} className="text-sm flex items-start gap-2">
                      <span className="text-green-600 mt-0.5">✓</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tactical Actions Timeline */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Tactical Actions Timeline</h4>
        <div className="space-y-3">
          {tacticalActions.map((action, index) => (
            <div
              key={index}
              className="flex items-center gap-4 p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all"
            >
              <div className="w-24 text-sm font-medium text-blue-600">
                {action.timeframe}
              </div>
              <div className="flex-1 text-sm text-gray-900">
                {action.action}
              </div>
              <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {action.effort}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resource Allocation */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Recommended Resource Allocation</h4>
        <div className="space-y-2">
          {[
            { category: 'Application Preparation', percentage: 40, color: 'bg-blue-500' },
            { category: 'Networking & Referrals', percentage: 30, color: 'bg-green-500' },
            { category: 'Skill Development', percentage: 15, color: 'bg-purple-500' },
            { category: 'Follow-up & Tracking', percentage: 15, color: 'bg-orange-500' }
          ].map((item, index) => (
            <div key={index}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-700">{item.category}</span>
                <span className="text-sm font-medium text-gray-900">{item.percentage}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className={`${item.color} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Expected Outcomes */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Expected Outcomes</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">4 Weeks</div>
            <div className="text-lg font-bold text-blue-600">3-5</div>
            <div className="text-xs text-gray-500">Interview Invitations</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">8 Weeks</div>
            <div className="text-lg font-bold text-green-600">8-12</div>
            <div className="text-xs text-gray-500">Interviews, 1-2 Offers</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">12 Weeks</div>
            <div className="text-lg font-bold text-purple-600">3-5</div>
            <div className="text-xs text-gray-500">Job Offers</div>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={generateStrategy}
        disabled={isLoading}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating Strategy...
          </span>
        ) : (
          '🤖 Generate Optimization Strategy'
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Strategy Result */}
      {strategy && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="font-medium text-green-900 mb-2">Strategy Generated</h4>
          <pre className="text-sm text-green-800 whitespace-pre-wrap">{strategy.strategy}</pre>
        </div>
      )}
    </div>
  );
};

export default StrategyRecommendationsCard;
