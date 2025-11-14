// FILE: frontend/src/components/Dashboard/Dashboard.tsx

import React, { useEffect } from 'react';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { useAppSelector } from '../../hooks/useAppSelector';
import { fetchApplications } from '../../store/slices/applicationsSlice';
import { fetchStatistics } from '../../store/slices/statisticsSlice';
import Loading from '../common/Loading';
import StatisticsCard from './StatisticsCard';
import RecentApplications from './RecentApplications';
import QuickActions from './QuickActions';

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { applications, loading: applicationsLoading } = useAppSelector(state => state.applications);
  const { stats, loading: statsLoading } = useAppSelector(state => state.statistics);
  const { is_monitoring } = useAppSelector(state => state.monitor);

  useEffect(() => {
    // Fetch recent applications for dashboard (first 10 items)
    dispatch(fetchApplications({ skip: 0, limit: 10 }));
    dispatch(fetchStatistics());
  }, [dispatch]);

  const handleRefreshStats = () => {
    dispatch(fetchStatistics());
  };

  if (applicationsLoading || statsLoading) {
    return <Loading text="Loading dashboard..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${is_monitoring ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">
            {is_monitoring ? 'Monitoring Active' : 'Monitoring Inactive'}
          </span>
        </div>
      </div>

      {/* Manual Refresh Button */}
      <div className="flex justify-end">
        <button
          onClick={handleRefreshStats}
          disabled={statsLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {statsLoading ? 'Refreshing...' : 'Refresh Statistics'}
        </button>
      </div>
      
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatisticsCard
          title="Today"
          value={stats?.today || 0}
          icon="calendar"
          color="blue"
          trend={stats ? { value: 0, isPositive: true } : undefined}
        />
        <StatisticsCard
          title="This Week"
          value={stats?.thisWeek || 0}
          icon="week"
          color="green"
          trend={stats ? { value: 0, isPositive: true } : undefined}
        />
        <StatisticsCard
          title="This Month"
          value={stats?.thisMonth || 0}
          icon="month"
          color="purple"
          trend={stats ? { value: 0, isPositive: true } : undefined}
        />
        <StatisticsCard
          title="Total"
          value={stats?.total || 0}
          icon="total"
          color="orange"
          subtitle={`${stats?.interviewRate || 0}% interview rate`}
        />
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Applications */}
        <div className="lg:col-span-2">
          <RecentApplications 
            applications={applications} 
            loading={applicationsLoading} 
          />
        </div>

        {/* Status Overview */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Application Status</h2>
          </div>
          <div className="p-6">
            {stats?.byStatus ? (
              <div className="space-y-4">
                {Object.entries(stats.byStatus).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {status}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500">{count}</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            status === 'applied' ? 'bg-blue-500' :
                            status === 'interview' ? 'bg-yellow-500' :
                            status === 'screening' ? 'bg-teal-500' :
                            status === 'assessment' ? 'bg-purple-500' :
                            status === 'rejected' ? 'bg-red-500' :
                            'bg-green-500'
                          }`}
                          style={{ 
                            width: `${stats.total > 0 ? (count / stats.total) * 100 : 0}%` 
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;