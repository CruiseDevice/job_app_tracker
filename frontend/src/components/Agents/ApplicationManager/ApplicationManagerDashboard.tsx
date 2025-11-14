import React, { useState } from 'react';
import LifecyclePredictionCard from './LifecyclePredictionCard';
import NextActionsCard from './NextActionsCard';
import SuccessProbabilityCard from './SuccessProbabilityCard';
import PatternAnalysisCard from './PatternAnalysisCard';

const ApplicationManagerDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'lifecycle' | 'actions' | 'probability' | 'patterns'>('lifecycle');

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-4xl">📊</span>
            <h1 className="text-3xl font-bold text-gray-900">
              Application Manager Agent
            </h1>
          </div>
          <p className="text-gray-600">
            Intelligent application lifecycle management with predictions and recommendations
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('lifecycle')}
                className={`${
                  activeTab === 'lifecycle'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200`}
              >
                📈 Lifecycle Prediction
              </button>
              <button
                onClick={() => setActiveTab('actions')}
                className={`${
                  activeTab === 'actions'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200`}
              >
                📋 Next Actions
              </button>
              <button
                onClick={() => setActiveTab('probability')}
                className={`${
                  activeTab === 'probability'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200`}
              >
                🎯 Success Probability
              </button>
              <button
                onClick={() => setActiveTab('patterns')}
                className={`${
                  activeTab === 'patterns'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200`}
              >
                🔍 Pattern Analysis
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {activeTab === 'lifecycle' && <LifecyclePredictionCard />}
          {activeTab === 'actions' && <NextActionsCard />}
          {activeTab === 'probability' && <SuccessProbabilityCard />}
          {activeTab === 'patterns' && <PatternAnalysisCard />}
        </div>

        {/* Agent Statistics */}
        <div className="mt-8 bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Agent Statistics
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-3">
              <p className="text-xs text-gray-600 mb-1">Predictions Run</p>
              <p className="text-2xl font-bold text-blue-600">0</p>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <p className="text-xs text-gray-600 mb-1">Tools Available</p>
              <p className="text-2xl font-bold text-green-600">5</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <p className="text-xs text-gray-600 mb-1">Memory Size</p>
              <p className="text-2xl font-bold text-purple-600">0</p>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <p className="text-xs text-gray-600 mb-1">Avg Response</p>
              <p className="text-2xl font-bold text-orange-600">1.8s</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApplicationManagerDashboard;
