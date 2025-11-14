// FILE: frontend/src/components/Agents/ApplicationManager/LifecyclePrediction.tsx

import React from 'react';

interface PredictedStage {
  stage: string;
  typical_days: string;
  probability: number;
}

interface LifecyclePredictionData {
  current_stage: string;
  days_since_application: number;
  health: string;
  next_stages: PredictedStage[];
  warning?: string;
}

interface LifecyclePredictionProps {
  data: LifecyclePredictionData;
  applicationName?: string;
  loading?: boolean;
}

const LifecyclePrediction: React.FC<LifecyclePredictionProps> = ({
  data,
  applicationName,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const getHealthColor = (health: string) => {
    const healthLower = health.toLowerCase();
    if (healthLower.includes('excellent')) return 'text-green-600 bg-green-100';
    if (healthLower.includes('healthy') || healthLower.includes('promising')) return 'text-blue-600 bg-blue-100';
    if (healthLower.includes('needs_followup') || healthLower.includes('at_risk')) return 'text-orange-600 bg-orange-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 60) return 'text-green-600 bg-green-100';
    if (probability >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📊</span>
          <h3 className="text-lg font-semibold text-gray-900">
            Lifecycle Prediction
          </h3>
        </div>
        {applicationName && (
          <p className="text-sm text-gray-600 mt-1">{applicationName}</p>
        )}
      </div>

      <div className="p-6">
        {/* Current Status */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Current Stage</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthColor(data.health)}`}>
              {data.health.toUpperCase()}
            </span>
          </div>
          <p className="text-lg font-semibold text-gray-900">{data.current_stage}</p>
          <p className="text-sm text-gray-600 mt-1">
            {data.days_since_application} days since application
          </p>
        </div>

        {/* Predicted Next Stages */}
        {data.next_stages && data.next_stages.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Predicted Next Stages</h4>
            <div className="space-y-3">
              {data.next_stages.map((stage, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h5 className="font-medium text-gray-900">{stage.stage}</h5>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProbabilityColor(stage.probability)}`}>
                      {stage.probability}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>⏰</span>
                    <span>Timeline: {stage.typical_days}</span>
                  </div>
                  {/* Probability bar */}
                  <div className="mt-3 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                      style={{ width: `${stage.probability}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Warning */}
        {data.warning && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <span className="text-lg">⚠️</span>
              <div>
                <p className="text-sm font-medium text-orange-900 mb-1">Warning</p>
                <p className="text-sm text-orange-700">{data.warning}</p>
              </div>
            </div>
          </div>
        )}

        {data.next_stages.length === 0 && (
          <div className="text-center py-6 text-gray-500">
            <p className="text-sm">Application has reached a terminal state.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LifecyclePrediction;
