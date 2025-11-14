// FILE: frontend/src/components/Agents/Orchestrator/OrchestratorDashboard.tsx

import React, { useState, useEffect } from 'react';
import WorkflowBuilder from './WorkflowBuilder';
import WorkflowStatusCard from './WorkflowStatusCard';
import AgentCoordinationCard from './AgentCoordinationCard';
import QuickTaskRouter from './QuickTaskRouter';

interface OrchestratorStats {
  name: string;
  execution_count: number;
  tools_count: number;
  memory_size: number;
  registered_agents: string[];
  workflow_stats: {
    active_workflows: number;
    total_workflows_executed: number;
  };
  communication_stats: {
    registered_agents: string[];
    agent_count: number;
    total_messages_sent: number;
  };
}

const OrchestratorDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'workflow' | 'coordinate' | 'route' | 'status'>('coordinate');
  const [stats, setStats] = useState<OrchestratorStats | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/orchestrator/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch orchestrator stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎭 Orchestrator Agent
          </h1>
          <p className="text-gray-600">
            Coordinate multiple specialized agents to handle complex multi-step tasks
          </p>
        </div>

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Registered Agents</div>
              <div className="text-2xl font-bold text-blue-600">
                {stats.registered_agents.length}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                {stats.registered_agents.join(', ')}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Active Workflows</div>
              <div className="text-2xl font-bold text-green-600">
                {stats.workflow_stats.active_workflows}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                Currently running
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Total Executions</div>
              <div className="text-2xl font-bold text-purple-600">
                {stats.execution_count}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                All-time workflows
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Messages Sent</div>
              <div className="text-2xl font-bold text-orange-600">
                {stats.communication_stats.total_messages_sent}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                Inter-agent communication
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('coordinate')}
                className={`${
                  activeTab === 'coordinate'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                🎯 Smart Coordination
              </button>
              <button
                onClick={() => setActiveTab('workflow')}
                className={`${
                  activeTab === 'workflow'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                🔧 Build Workflow
              </button>
              <button
                onClick={() => setActiveTab('route')}
                className={`${
                  activeTab === 'route'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                📨 Quick Route
              </button>
              <button
                onClick={() => setActiveTab('status')}
                className={`${
                  activeTab === 'status'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                📊 Status Monitor
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'coordinate' && <AgentCoordinationCard />}
            {activeTab === 'workflow' && <WorkflowBuilder />}
            {activeTab === 'route' && <QuickTaskRouter availableAgents={stats?.registered_agents || []} />}
            {activeTab === 'status' && <WorkflowStatusCard />}
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              💡 What is the Orchestrator?
            </h3>
            <p className="text-blue-800 text-sm">
              The Orchestrator Agent coordinates multiple specialized agents to handle complex tasks.
              It can intelligently route simple tasks to the right agent or create multi-step workflows
              for complex operations. Think of it as a conductor leading an orchestra of AI agents.
            </p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-900 mb-3">
              🚀 Example Use Cases
            </h3>
            <ul className="text-green-800 text-sm space-y-2">
              <li>• Complete job application workflow (search → tailor resume → cover letter → prep)</li>
              <li>• Email analysis with automatic follow-up drafting</li>
              <li>• Multi-platform job search with automatic application tracking</li>
              <li>• Interview preparation combined with company research</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrchestratorDashboard;
