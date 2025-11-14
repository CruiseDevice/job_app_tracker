// FILE: frontend/src/components/Agents/Analytics/AnalyticsDashboard.tsx

import React, { useState, useEffect } from 'react';
import DataAnalysisCard from './DataAnalysisCard';
import SuccessPatternsCard from './SuccessPatternsCard';
import OfferPredictionCard from './OfferPredictionCard';
import StrategyRecommendationsCard from './StrategyRecommendationsCard';
import SalaryAnalysisCard from './SalaryAnalysisCard';
import PerformanceMetricsCard from './PerformanceMetricsCard';

type TabType = 'overview' | 'patterns' | 'prediction' | 'strategy' | 'salary';

const AnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [userId, setUserId] = useState<number>(1);
  const [isLoading, setIsLoading] = useState(false);

  // Sample data for overview (in production, this would come from API)
  const [overviewStats, setOverviewStats] = useState({
    totalApplications: 45,
    successRate: 6.7,
    interviewRate: 26.7,
    responseRate: 73.3,
    avgTimeToOffer: 28.3,
    applicationsThisMonth: 15,
    trend: '+12%'
  });

  const tabs = [
    { id: 'overview' as TabType, label: 'Overview', icon: '📊' },
    { id: 'patterns' as TabType, label: 'Success Patterns', icon: '🔍' },
    { id: 'prediction' as TabType, label: 'Offer Prediction', icon: '🎯' },
    { id: 'strategy' as TabType, label: 'Strategy', icon: '🎯' },
    { id: 'salary' as TabType, label: 'Salary Insights', icon: '💰' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analytics & Strategy Dashboard
          </h1>
          <p className="text-gray-600">
            AI-powered insights, predictions, and recommendations for your job search
          </p>
        </div>

        {/* Key Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-medium text-gray-500">Total Applications</div>
              <span className="text-2xl">📝</span>
            </div>
            <div className="text-3xl font-bold text-gray-900">{overviewStats.totalApplications}</div>
            <div className="text-xs text-green-500 mt-1">
              {overviewStats.trend} this month
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-medium text-gray-500">Success Rate</div>
              <span className="text-2xl">🎯</span>
            </div>
            <div className="text-3xl font-bold text-blue-600">{overviewStats.successRate}%</div>
            <div className="text-xs text-gray-500 mt-1">
              Offer conversion rate
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-medium text-gray-500">Interview Rate</div>
              <span className="text-2xl">💼</span>
            </div>
            <div className="text-3xl font-bold text-purple-600">{overviewStats.interviewRate}%</div>
            <div className="text-xs text-purple-500 mt-1">
              Above industry avg
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-medium text-gray-500">Response Rate</div>
              <span className="text-2xl">📬</span>
            </div>
            <div className="text-3xl font-bold text-green-600">{overviewStats.responseRate}%</div>
            <div className="text-xs text-green-500 mt-1">
              Good targeting
            </div>
          </div>
        </div>

        {/* Performance Trends Chart */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">Performance Trends</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-4xl mb-2">📈</div>
              <p className="text-gray-500">Performance visualization would go here</p>
              <p className="text-sm text-gray-400 mt-2">
                Applications, interviews, and offers over time
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <span>{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              <DataAnalysisCard userId={userId} />
              <PerformanceMetricsCard userId={userId} />
            </>
          )}

          {activeTab === 'patterns' && (
            <SuccessPatternsCard userId={userId} />
          )}

          {activeTab === 'prediction' && (
            <OfferPredictionCard />
          )}

          {activeTab === 'strategy' && (
            <StrategyRecommendationsCard />
          )}

          {activeTab === 'salary' && (
            <SalaryAnalysisCard />
          )}
        </div>

        {/* AI Insights Summary */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow p-6">
          <div className="flex items-start gap-4">
            <div className="text-3xl">🤖</div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI Insights Summary
              </h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p>
                  <span className="font-medium">✓ Strength:</span> Your application quality score (7.8/10) is above average
                </p>
                <p>
                  <span className="font-medium">⚠ Opportunity:</span> Offer conversion rate is below benchmark - focus on interview preparation
                </p>
                <p>
                  <span className="font-medium">💡 Recommendation:</span> Applications with referrals show 300% higher success rate - prioritize networking
                </p>
                <p>
                  <span className="font-medium">📅 Action:</span> Follow up on 7 pending applications that are 7-10 days old
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
