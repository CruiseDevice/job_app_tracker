// FILE: frontend/src/components/Dashboard/QuickActions.tsx

import React, { useState } from 'react';
import { Plus, Play, Square, Settings, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { useAppSelector } from '../../hooks/useAppSelector';
import { fetchApplications, addApplication } from '../../store/slices/applicationsSlice';
import { fetchStatistics } from '../../store/slices/statisticsSlice';
import { startMonitoring, stopMonitoring } from '../../store/slices/monitorSlice';
import AddApplicationModal from '../Applications/AddApplicationModal';
import type { CreateApplicationRequest } from '../../types/application';

const QuickActions: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { is_monitoring } = useAppSelector(state => state.monitor);
  const [isToggling, setIsToggling] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  const handleToggleMonitoring = async () => {
    setIsToggling(true);
    try {
      if (is_monitoring) {
        await dispatch(stopMonitoring()).unwrap();
        toast.success('Monitoring stopped');
      } else {
        await dispatch(startMonitoring()).unwrap();
        toast.success('Monitoring started');
      }
    } catch (error) {
      console.error('Error toggling monitoring:', error);
      toast.error('Failed to toggle monitoring');
    } finally {
      setIsToggling(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([
        dispatch(fetchApplications({ skip: 0, limit: 10 })).unwrap(),
        dispatch(fetchStatistics()).unwrap()
      ]);
      toast.success('Data refreshed');
    } catch (error) {
      console.error('Error refreshing data:', error);
      toast.error('Failed to refresh data');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleAddManualApplication = () => {
    setShowAddModal(true);
  };

  const handleSaveApplication = async (data: CreateApplicationRequest) => {
    try {
      await dispatch(addApplication(data)).unwrap();
      // Refresh the statistics after adding
      await dispatch(fetchStatistics()).unwrap();
    } catch (error) {
      console.error('Error adding application:', error);
      throw error; // Re-throw to let the modal handle the error
    }
  };

  const actions = [
    {
      title: 'Add Application',
      description: 'Manually add a job application',
      icon: Plus,
      color: 'bg-blue-500 hover:bg-blue-600',
      onClick: handleAddManualApplication
    },
    {
      title: is_monitoring ? 'Stop Monitoring' : 'Start Monitoring',
      description: is_monitoring 
        ? 'Stop checking emails for job applications' 
        : 'Start monitoring emails for job applications',
      icon: is_monitoring ? Square : Play,
      color: is_monitoring 
        ? 'bg-red-500 hover:bg-red-600' 
        : 'bg-green-500 hover:bg-green-600',
      onClick: handleToggleMonitoring,
      loading: isToggling
    },
    {
      title: 'Refresh Data',
      description: 'Reload applications and statistics',
      icon: RefreshCw,
      color: 'bg-gray-500 hover:bg-gray-600',
      onClick: handleRefresh,
      loading: isRefreshing
    },
    {
      title: 'Settings',
      description: 'Configure monitoring and preferences',
      icon: Settings,
      color: 'bg-purple-500 hover:bg-purple-600',
      onClick: () => {
        navigate('/settings');
      }
    }
  ];

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <button
              key={index}
              onClick={action.onClick}
              disabled={action.loading}
              className={`${action.color} text-white p-4 rounded-lg shadow hover:shadow-md transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none`}
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <Icon 
                    className={`w-6 h-6 ${action.loading ? 'animate-spin' : ''}`} 
                  />
                </div>
                <div className="text-left">
                  <h3 className="text-sm font-medium">{action.title}</h3>
                  <p className="text-xs opacity-90 mt-1">{action.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Add Application Modal */}
      <AddApplicationModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSave={handleSaveApplication}
      />
    </>
  );
};

export default QuickActions;