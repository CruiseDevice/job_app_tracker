// FILE: frontend/src/components/Agents/Orchestrator/WorkflowBuilder.tsx

import React, { useState } from 'react';

interface WorkflowTask {
  id: string;
  agent_name: string;
  task_description: string;
  input_data: Record<string, any>;
  dependencies: string[];
}

interface WorkflowBuilderProps {
  availableAgents?: string[];
}

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  availableAgents = ['Email Analyst', 'Job Hunter', 'Resume Writer', 'Follow-up Agent', 'Interview Prep']
}) => {
  const [workflowName, setWorkflowName] = useState('');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [executionMode, setExecutionMode] = useState<'sequential' | 'parallel'>('sequential');
  const [tasks, setTasks] = useState<WorkflowTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const addTask = () => {
    const newTask: WorkflowTask = {
      id: `task-${Date.now()}`,
      agent_name: availableAgents[0],
      task_description: '',
      input_data: {},
      dependencies: []
    };
    setTasks([...tasks, newTask]);
  };

  const removeTask = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const updateTask = (id: string, field: keyof WorkflowTask, value: any) => {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, [field]: value } : task
    ));
  };

  const handleExecuteWorkflow = async () => {
    if (!workflowName || tasks.length === 0) {
      setError('Please provide a workflow name and at least one task');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Convert tasks to API format
      const apiTasks = tasks.map(task => ({
        agent_name: task.agent_name,
        task_description: task.task_description,
        input_data: task.input_data,
        dependencies: task.dependencies,
        metadata: {}
      }));

      const response = await fetch('http://localhost:8000/api/agents/orchestrator/execute-workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_name: workflowName,
          workflow_description: workflowDescription,
          tasks: apiTasks,
          execution_mode: executionMode,
          metadata: {}
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to execute workflow');
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadExampleWorkflow = () => {
    setWorkflowName('Complete Job Application');
    setWorkflowDescription('Search for jobs, tailor resume, and generate cover letter');
    setExecutionMode('sequential');
    setTasks([
      {
        id: 'task-1',
        agent_name: 'Job Hunter',
        task_description: 'Search for Software Engineer jobs in San Francisco',
        input_data: { keywords: 'Software Engineer', location: 'San Francisco' },
        dependencies: []
      },
      {
        id: 'task-2',
        agent_name: 'Resume Writer',
        task_description: 'Analyze my current resume and provide feedback',
        input_data: {},
        dependencies: []
      },
      {
        id: 'task-3',
        agent_name: 'Resume Writer',
        task_description: 'Generate a cover letter for the top job match',
        input_data: {},
        dependencies: []
      }
    ]);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Build Custom Workflow
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Create a multi-step workflow by defining tasks for different agents. You can execute them
          sequentially (one after another) or in parallel (all at once).
        </p>
      </div>

      {/* Workflow Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Workflow Name *
          </label>
          <input
            id="name"
            type="text"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Complete Job Application"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="mode" className="block text-sm font-medium text-gray-700 mb-2">
            Execution Mode
          </label>
          <select
            id="mode"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={executionMode}
            onChange={(e) => setExecutionMode(e.target.value as 'sequential' | 'parallel')}
          >
            <option value="sequential">Sequential (one after another)</option>
            <option value="parallel">Parallel (all at once)</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <input
          id="description"
          type="text"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Brief description of what this workflow does"
          value={workflowDescription}
          onChange={(e) => setWorkflowDescription(e.target.value)}
        />
      </div>

      {/* Tasks */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <label className="block text-sm font-medium text-gray-700">
            Tasks ({tasks.length})
          </label>
          <button
            onClick={addTask}
            className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
          >
            + Add Task
          </button>
        </div>

        <div className="space-y-4">
          {tasks.map((task, index) => (
            <div key={task.id} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <span className="text-sm font-semibold text-gray-700">Task {index + 1}</span>
                <button
                  onClick={() => removeTask(task.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  ✕ Remove
                </button>
              </div>

              <div className="grid grid-cols-1 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Agent
                  </label>
                  <select
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={task.agent_name}
                    onChange={(e) => updateTask(task.id, 'agent_name', e.target.value)}
                  >
                    {availableAgents.map(agent => (
                      <option key={agent} value={agent}>{agent}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Task Description *
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="What should this agent do?"
                    value={task.task_description}
                    onChange={(e) => updateTask(task.id, 'task_description', e.target.value)}
                  />
                </div>
              </div>
            </div>
          ))}

          {tasks.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No tasks yet. Click "Add Task" to get started.
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex space-x-3">
        <button
          onClick={handleExecuteWorkflow}
          disabled={loading || tasks.length === 0}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
            loading || tasks.length === 0
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
              Executing Workflow...
            </span>
          ) : (
            '🚀 Execute Workflow'
          )}
        </button>
        <button
          onClick={loadExampleWorkflow}
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
            ✅ Workflow Executed Successfully
          </h4>

          {result.workflow_id && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Workflow ID:</span> {result.workflow_id}
              </p>
            </div>
          )}

          {result.results && result.results.length > 0 && (
            <div className="space-y-3">
              <h5 className="font-medium text-gray-900">Task Results:</h5>
              {result.results.map((taskResult: any, index: number) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">
                      {taskResult.agent_name}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      taskResult.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : taskResult.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {taskResult.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{taskResult.task_description}</p>
                  {taskResult.error && (
                    <p className="text-sm text-red-600 mt-2">Error: {taskResult.error}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkflowBuilder;
