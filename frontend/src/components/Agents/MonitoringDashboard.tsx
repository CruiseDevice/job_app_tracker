import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Activity,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Cpu,
  Zap,
  BarChart3,
  Settings,
  RefreshCw
} from 'lucide-react';

interface AgentMetrics {
  agent_name: string;
  period_start: string;
  period_end: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  avg_execution_time: number;
  max_execution_time: number;
  min_execution_time: number;
  total_tokens_used: number;
  total_cost: number;
  avg_tokens_per_execution: number;
  avg_cost_per_execution: number;
  success_rate: number;
  error_rate: number;
  total_tool_calls: number;
  errors: string[];
}

interface CostSummary {
  agent_name: string;
  total_cost: number;
  total_calls: number;
  avg_cost_per_call: number;
  model_breakdown: Record<string, any>;
}

interface Alert {
  agent: string;
  type: string;
  severity: string;
  message: string;
  value: number;
  threshold: number;
}

const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Record<string, AgentMetrics>>({});
  const [costs, setCosts] = useState<Record<string, CostSummary>>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(24);
  const [totalCost, setTotalCost] = useState(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [metricsRes, costsRes, alertsRes, totalCostRes] = await Promise.all([
        axios.get(`/api/monitoring/performance/agents?period_hours=${selectedPeriod}`),
        axios.get(`/api/monitoring/costs/agents?period_hours=${selectedPeriod}`),
        axios.get('/api/monitoring/performance/alerts'),
        axios.get(`/api/monitoring/costs/total?period_hours=${selectedPeriod}`)
      ]);

      setMetrics(metricsRes.data);
      setCosts(costsRes.data);
      setAlerts(alertsRes.data);
      setTotalCost(totalCostRes.data.total_cost);
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [selectedPeriod]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  if (loading && Object.keys(metrics).length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
          <span className="text-gray-600">Loading monitoring data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Monitoring Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time performance and cost tracking</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value={1}>Last Hour</option>
            <option value={24}>Last 24 Hours</option>
            <option value={168}>Last Week</option>
          </select>
          <button
            onClick={fetchData}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <h2 className="text-xl font-semibold">Active Alerts</h2>
          </div>
          <div className="space-y-2">
            {alerts.map((alert, idx) => (
              <div
                key={idx}
                className={`p-4 border rounded-lg ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{alert.agent}</p>
                    <p className="text-sm">{alert.message}</p>
                  </div>
                  <div className="text-sm">
                    <span className="font-mono">{alert.value.toFixed(2)}</span>
                    <span className="text-gray-600"> / {alert.threshold}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Cost</p>
              <p className="text-2xl font-bold text-gray-900">${totalCost.toFixed(4)}</p>
            </div>
            <DollarSign className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Executions</p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.values(metrics).reduce((sum, m) => sum + m.total_executions, 0)}
              </p>
            </div>
            <Activity className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.values(metrics).length > 0
                  ? (
                      Object.values(metrics).reduce((sum, m) => sum + m.success_rate, 0) /
                      Object.values(metrics).length
                    ).toFixed(1)
                  : 0}
                %
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.values(metrics).length > 0
                  ? (
                      Object.values(metrics).reduce((sum, m) => sum + m.avg_execution_time, 0) /
                      Object.values(metrics).length
                    ).toFixed(2)
                  : 0}
                s
              </p>
            </div>
            <Clock className="w-10 h-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Agent Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(metrics).map(([agentName, metric]) => (
          <div key={agentName} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{agentName}</h3>
              <Cpu className="w-5 h-5 text-gray-400" />
            </div>

            <div className="space-y-4">
              {/* Performance Metrics */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Performance</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-600">Executions</p>
                    <p className="text-lg font-semibold">{metric.total_executions}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Success Rate</p>
                    <div className="flex items-center space-x-2">
                      <p className="text-lg font-semibold">{metric.success_rate.toFixed(1)}%</p>
                      {metric.success_rate >= 95 ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      )}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Avg Time</p>
                    <p className="text-lg font-semibold">{metric.avg_execution_time.toFixed(2)}s</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Tool Calls</p>
                    <p className="text-lg font-semibold">{metric.total_tool_calls}</p>
                  </div>
                </div>
              </div>

              {/* Cost Metrics */}
              {costs[agentName] && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Cost</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-600">Total Cost</p>
                      <p className="text-lg font-semibold">${costs[agentName].total_cost.toFixed(4)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Avg per Call</p>
                      <p className="text-lg font-semibold">
                        ${costs[agentName].avg_cost_per_call.toFixed(4)}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Token Usage */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Token Usage</h4>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-600">Total Tokens</p>
                    <p className="text-lg font-semibold">
                      {metric.total_tokens_used.toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-600">Avg per Execution</p>
                    <p className="text-lg font-semibold">
                      {metric.avg_tokens_per_execution.toFixed(0)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Error Info */}
              {metric.errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2 mb-2">
                    <XCircle className="w-4 h-4 text-red-500" />
                    <p className="text-sm font-semibold text-red-800">Recent Errors</p>
                  </div>
                  <div className="space-y-1">
                    {metric.errors.slice(0, 3).map((error, idx) => (
                      <p key={idx} className="text-xs text-red-700 truncate">
                        {error}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MonitoringDashboard;
