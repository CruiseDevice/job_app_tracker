// FILE: frontend/src/components/Agents/Orchestrator/QuickTaskRouter.tsx

import React, { useState } from 'react';

interface QuickTaskRouterProps {
  availableAgents: string[];
}

const QuickTaskRouter: React.FC<QuickTaskRouterProps> = ({ availableAgents }) => {
  const [selectedAgent, setSelectedAgent] = useState(availableAgents[0] || '');
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRouteTask = async () => {
    if (!task.trim() || !selectedAgent) {
      setError('Please select an agent and provide a task description');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/orchestrator/route-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_name: selectedAgent,
          task: task,
          context: {}
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to route task');
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const agentExamples: Record<string, string> = {
    'Email Analyst': 'Analyze an interview invitation email I received from Google',
    'Job Hunter': 'Search for Senior Software Engineer positions in San Francisco',
    'Resume Writer': 'Analyze my resume and provide improvement suggestions',
    'Follow-up Agent': 'Draft a follow-up email for a job I applied to 2 weeks ago',
    'Interview Prep': 'Help me prepare for a technical interview at Microsoft'
  };

  const loadExample = () => {
    if (selectedAgent && agentExamples[selectedAgent]) {
      setTask(agentExamples[selectedAgent]);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Quick Task Routing
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          When you know exactly which agent should handle your task, use this quick routing feature
          to send the task directly to that agent without creating a full workflow.
        </p>
      </div>

      {/* Agent Selection */}
      <div>
        <label htmlFor="agent" className="block text-sm font-medium text-gray-700 mb-2">
          Select Agent
        </label>
        <select
          id="agent"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
        >
          {availableAgents.map(agent => (
            <option key={agent} value={agent}>{agent}</option>
          ))}
        </select>
      </div>

      {/* Task Input */}
      <div>
        <label htmlFor="task" className="block text-sm font-medium text-gray-700 mb-2">
          Task Description
        </label>
        <textarea
          id="task"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          placeholder={`What do you want the ${selectedAgent} to do?`}
          value={task}
          onChange={(e) => setTask(e.target.value)}
        />
      </div>

      {/* Actions */}
      <div className="flex space-x-3">
        <button
          onClick={handleRouteTask}
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
              Routing Task...
            </span>
          ) : (
            '📨 Route Task'
          )}
        </button>
        <button
          onClick={loadExample}
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
            ✅ Task Completed by {selectedAgent}
          </h4>

          {result.output && (
            <div className="prose max-w-none">
              <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap">
                {result.output}
              </div>
            </div>
          )}

          {result.metadata && Object.keys(result.metadata).length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-semibold text-blue-900 mb-2">Metadata:</p>
              <pre className="text-xs text-blue-800 overflow-auto">
                {JSON.stringify(result.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuickTaskRouter;
