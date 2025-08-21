import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../../hooks/useAppSelector';
import { useWebSocket } from '../Providers/WebSocketProvider';

export const RealTimeStats: React.FC = () => {
  const { stats } = useAppSelector(state => state.statistics);
  const { isConnected } = useWebSocket();
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    setLastUpdate(new Date().toLocaleTimeString());
  }, [stats]);

  const StatCard: React.FC<{ 
    title: string; 
    value: number; 
    icon: string; 
    trend?: string;
    color?: string;
  }> = ({ title, value, icon, trend, color = 'blue' }) => (
    <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 border-${color}-500`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className="text-sm text-gray-500 mt-1">{trend}</p>
          )}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Application Statistics</h2>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
            <span className="text-sm font-medium">
              {isConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
          {lastUpdate && (
            <span className="text-sm text-gray-500">
              Last updated: {lastUpdate}
            </span>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Today"
          value={stats.today}
          icon="📅"
          color="green"
        />
        <StatCard
          title="This Week"
          value={stats.thisWeek}
          icon="📊"
          color="blue"
        />
        <StatCard
          title="This Month"
          value={stats.thisMonth}
          icon="📈"
          color="purple"
        />
        <StatCard
          title="Total Applications"
          value={stats.total}
          icon="🎯"
          trend={`Avg: ${stats.avgPerDay.toFixed(1)}/day`}
          color="indigo"
        />
      </div>

      {/* Top Companies */}
      {stats.topCompanies.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Companies Applied</h3>
          <div className="space-y-3">
            {stats.topCompanies.slice(0, 5).map((company, index) => (
              <div key={company.company} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                  <span className="font-medium text-gray-900">{company.company}</span>
                </div>
                <span className="text-sm text-gray-600">{company.count} applications</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status Distribution */}
      {Object.keys(stats.statusDistribution).length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.statusDistribution).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{count}</div>
                <div className="text-sm text-gray-600 capitalize">{status}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
