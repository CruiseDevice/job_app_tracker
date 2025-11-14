// FILE: frontend/src/components/Agents/Orchestrator/WorkflowStatusCard.tsx

import React, { useState } from 'react';

interface WorkflowStatus {
  workflow_id: string;
  status: string;
  task_count: number;
  completed_tasks: number;
  failed_tasks: number;
  pending_tasks: number;
  running_tasks: number;
}

const WorkflowStatusCard: React.FC = () => {
  const [workflowId, setWorkflowId] = useState('');
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckStatus = async () => {
    if (!workflowId.trim()) {
      setError('Please enter a workflow ID');
      return;
    }

    setLoading(true);
    setError(null);
    setStatus(null);

    try {
      const response = await fetch(`http://localhost:8000/api/agents/orchestrator/workflow-status/${workflowId}`);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Workflow not found');
        }
        throw new Error('Failed to fetch workflow status');
      }

      const data = await response.json();
      setStatus(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return '✅';
      case 'running':
        return '⚙️';
      case 'failed':
        return '❌';
      case 'pending':
        return '⏳';
      case 'cancelled':
        return '🚫';
      default:
        return '❓';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Workflow Status Monitor
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Check the status of a running or completed workflow using its workflow ID.
          You'll receive the workflow ID when you execute a workflow.
        </p>
      </div>

      {/* Workflow ID Input */}
      <div>
        <label htmlFor="workflow-id" className="block text-sm font-medium text-gray-700 mb-2">
          Workflow ID
        </label>
        <div className="flex space-x-3">
          <input
            id="workflow-id"
            type="text"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter workflow ID (e.g., 123e4567-e89b-12d3-a456-426614174000)"
            value={workflowId}
            onChange={(e) => setWorkflowId(e.target.value)}
          />
          <button
            onClick={handleCheckStatus}
            disabled={loading}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Checking...
              </span>
            ) : (
              'Check Status'
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Status Display */}
      {status && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-lg font-semibold text-gray-900">
              Workflow Status
            </h4>
            <div className={`px-4 py-2 rounded-full border ${getStatusColor(status.status)}`}>
              <span className="text-sm font-medium">
                {getStatusIcon(status.status)} {status.status.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{status.completed_tasks} / {status.task_count} tasks completed</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  status.failed_tasks > 0 ? 'bg-red-500' : 'bg-blue-600'
                }`}
                style={{
                  width: `${status.task_count > 0 ? (status.completed_tasks / status.task_count) * 100 : 0}%`
                }}
              ></div>
            </div>
          </div>

          {/* Task Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-xs text-gray-600 mb-1">Total Tasks</div>
              <div className="text-2xl font-bold text-gray-900">{status.task_count}</div>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-xs text-green-700 mb-1">Completed</div>
              <div className="text-2xl font-bold text-green-600">{status.completed_tasks}</div>
            </div>

            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-xs text-blue-700 mb-1">Running</div>
              <div className="text-2xl font-bold text-blue-600">{status.running_tasks}</div>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-xs text-yellow-700 mb-1">Pending</div>
              <div className="text-2xl font-bold text-yellow-600">{status.pending_tasks}</div>
            </div>
          </div>

          {status.failed_tasks > 0 && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Failed Tasks</h3>
                  <p className="text-sm text-red-700 mt-1">
                    {status.failed_tasks} task{status.failed_tasks > 1 ? 's' : ''} failed during execution
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">
          💡 How to use
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Execute a workflow using the "Build Workflow" or "Smart Coordination" tabs</li>
          <li>• Copy the workflow ID from the success message</li>
          <li>• Paste it here to monitor progress in real-time</li>
          <li>• Workflow statuses: Pending → Running → Completed/Failed</li>
        </ul>
      </div>
    </div>
  );
};

export default WorkflowStatusCard;
