// FILE: frontend/src/components/Settings/Settings.tsx

import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { useAppSelector } from '../../hooks/useAppSelector';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { setTheme, toggleNotifications, toggleAutoRefresh } from '../../store/slices/settingsSlice';
import { Save, Bell, RefreshCw, Palette, Mail, Database, Shield } from 'lucide-react';
import { WebSocketService } from '../../services/websocket';
import { settingsApi } from '../../services/settings';

// Type definitions for settings
type SettingToggle = {
  label: string;
  type: 'toggle';
  value: boolean;
  onChange: () => void;
};

type SettingSelect = {
  label: string;
  type: 'select';
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
};

type SettingNumber = {
  label: string;
  type: 'number';
  value: number;
  onChange: (value: number) => void;
};

type SettingButton = {
  label: string;
  type: 'button';
  value: string;
  onClick: () => void;
  danger?: boolean;
};

type Setting = SettingToggle | SettingSelect | SettingNumber | SettingButton;

const Settings: React.FC = () => {
  const dispatch = useAppDispatch();
  const settings = useAppSelector(state => state.settings);
  const [isSaving, setIsSaving] = useState(false);
  const [emailCheckInterval, setEmailCheckInterval] = useState(5);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await settingsApi.updateSettings({
        theme: settings.theme,
        notifications: settings.notifications,
        autoRefresh: settings.autoRefresh,
        email_check_interval: emailCheckInterval,
      });
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleNotificationToggle = async () => {
    if (!settings.notifications) {
      // User is enabling notifications, request permission
      try {
        const granted = await WebSocketService.requestNotificationPermission();
        if (granted) {
          dispatch(toggleNotifications());
        } else {
          // Permission denied, show user feedback
          toast.error('Notification permission denied');
        }
      } catch (error) {
        console.error('Error requesting notification permission:', error);
      }
    } else {
      // User is disabling notifications, just toggle
      dispatch(toggleNotifications());
    }
  };

  const settingsGroups: Array<{
    title: string;
    icon: React.ComponentType<{ className?: string }>;
    settings: Setting[];
  }> = [
    {
      title: 'Appearance',
      icon: Palette,
      settings: [
        {
          label: 'Theme',
          type: 'select' as const,
          value: settings.theme,
          options: [
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' }
          ],
          onChange: (value: string) => dispatch(setTheme(value as 'light' | 'dark'))
        }
      ]
    },
    {
      title: 'Notifications',
      icon: Bell,
      settings: [
        {
          label: 'Enable notifications',
          type: 'toggle' as const,
          value: settings.notifications,
          onChange: handleNotificationToggle
        }
      ]
    },
    {
      title: 'Data & Sync',
      icon: RefreshCw,
      settings: [
        {
          label: 'Auto-refresh data',
          type: 'toggle' as const,
          value: settings.autoRefresh,
          onChange: () => dispatch(toggleAutoRefresh())
        }
      ]
    },
    {
      title: 'Email Monitoring',
      icon: Mail,
      settings: [
        {
          label: 'Check interval (minutes)',
          type: 'number' as const,
          value: emailCheckInterval,
          onChange: (value: number) => setEmailCheckInterval(value)
        }
      ]
    },
    {
      title: 'Database',
      icon: Database,
      settings: [
        {
          label: 'Export data',
          type: 'button' as const,
          value: 'Export',
          onClick: () => {
            toast('Export functionality coming soon', { icon: 'ℹ️' });
          }
        },
        {
          label: 'Import data',
          type: 'button' as const,
          value: 'Import',
          onClick: () => {
            toast('Import functionality coming soon', { icon: 'ℹ️' });
          }
        }
      ]
    },
    {
      title: 'Privacy & Security',
      icon: Shield,
      settings: [
        {
          label: 'Clear all data',
          type: 'button' as const,
          value: 'Clear Data',
          danger: true,
          onClick: () => {
            if (window.confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
              toast('Clear data functionality coming soon', { icon: 'ℹ️' });
            }
          }
        }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-600 mt-1">
            Configure your job tracking preferences
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className={`w-4 h-4 mr-2 ${isSaving ? 'animate-spin' : ''}`} />
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {settingsGroups.map((group, groupIndex) => {
          const Icon = group.icon;
          return (
            <div key={groupIndex} className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center">
                  <Icon className="w-5 h-5 text-gray-500 mr-2" />
                  <h2 className="text-lg font-medium text-gray-900">{group.title}</h2>
                </div>
              </div>
              <div className="p-6 space-y-4">
                {group.settings.map((setting, settingIndex) => (
                  <div key={settingIndex} className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700">
                      {setting.label}
                    </label>
                    
                    {setting.type === 'toggle' && (
                      <button
                        onClick={setting.onChange}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          setting.value ? 'bg-blue-600' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            setting.value ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    )}
                    
                    {setting.type === 'select' && (
                      <select
                        value={setting.value}
                        onChange={(e) => setting.onChange(e.target.value)}
                        className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        {setting.options?.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    )}
                    
                    {setting.type === 'number' && (
                      <input
                        type="number"
                        value={setting.value}
                        onChange={(e) => setting.onChange(Number(e.target.value))}
                        className="block w-24 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    )}
                    
                    {setting.type === 'button' && (
                      <button
                        onClick={setting.onClick}
                        className={`px-4 py-2 text-sm font-medium rounded-md ${
                          (setting as SettingButton).danger
                            ? 'text-red-700 bg-red-100 hover:bg-red-200'
                            : 'text-blue-700 bg-blue-100 hover:bg-blue-200'
                        }`}
                      >
                        {setting.value}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Status Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">Active</div>
            <div className="text-sm text-gray-500">Monitoring Status</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">v1.0.0</div>
            <div className="text-sm text-gray-500">Application Version</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">SQLite</div>
            <div className="text-sm text-gray-500">Database Type</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;