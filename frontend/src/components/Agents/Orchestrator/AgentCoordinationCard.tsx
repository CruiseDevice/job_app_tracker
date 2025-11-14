// FILE: frontend/src/components/Agents/Orchestrator/AgentCoordinationCard.tsx

import React, { useState } from 'react';

const AgentCoordinationCard: React.FC = () => {
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCoordinate = async () => {
    if (!task.trim()) {
      setError('Please describe the task you want to accomplish');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/orchestrator/coordinate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: task,
          context: {}
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to coordinate agents');
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadExampleTask = () => {
    setTask('Help me apply to a Senior Software Engineer position at Google. I need you to search for the job, tailor my resume, generate a cover letter, and prepare me for the interview.');
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Smart Agent Coordination
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Describe what you want to accomplish, and the Orchestrator will automatically determine which agents
          to use and how to coordinate them. This is the most intelligent mode - just tell it what you want!
        </p>
      </div>

      {/* Task Input */}
      <div>
        <label htmlFor="task" className="block text-sm font-medium text-gray-700 mb-2">
          What do you want to accomplish?
        </label>
        <textarea
          id="task"
          rows={6}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          placeholder="Example: Help me apply to a Software Engineer position at Google - search for the job, tailor my resume, write a cover letter, and prepare for the interview"
          value={task}
          onChange={(e) => setTask(e.target.value)}
        />
      </div>

      {/* Actions */}
      <div className="flex space-x-3">
        <button
          onClick={handleCoordinate}
          disabled={loading}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
            loading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Coordinating Agents...
            </span>
          ) : (
            '🎭 Coordinate Agents'
          )}
        </button>
        <button
          onClick={loadExampleTask}
          disabled={loading}
          className="py-2 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Load Example
        </button>
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

      {/* Result Display */}
      {result && result.success && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            ✅ Coordination Plan
          </h4>

          {result.output && (
            <div className="prose max-w-none">
              <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap font-mono text-sm">
                {result.output}
              </div>
            </div>
          )}

          {result.workflow_id && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Workflow ID:</span> {result.workflow_id}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Use this ID to check the status of your workflow
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentCoordinationCard;
