import React from 'react';
import { useAppSelector } from '../../hooks/useAppSelector';
import { useWebSocket } from '../Providers/WebSocketProvider';
import { ConnectionStatus } from '../common/ConnectionStatus';

export const MonitoringControls: React.FC = () => {
  const { is_monitoring} = useAppSelector(state => state.monitor);
  const { startMonitoring, stopMonitoring, isConnected } = useWebSocket();

  const handleToggleMonitoring = () => {
    if (is_monitoring) {
      stopMonitoring();
    } else {
      startMonitoring();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Email Monitoring</h3>
          <p className="text-sm text-gray-600">
            Automatically scan emails for job applications every 5 minutes
          </p>
        </div>
        <ConnectionStatus />
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className={`w-3 h-3 rounded-full ${is_monitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
          <span className="font-medium text-gray-900">
            {is_monitoring ? 'Monitoring Active' : 'Monitoring Stopped'}
          </span>
        </div>

        <button
          onClick={handleToggleMonitoring}
          disabled={!isConnected}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            isConnected
              ? is_monitoring
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {is_monitoring ? 'Stop Monitoring' : 'Start Monitoring'}
        </button>
      </div>

      {!isConnected && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            ⚠️ Connection to server lost. Monitoring controls are disabled.
          </p>
        </div>
      )}
    </div>
  );
};
