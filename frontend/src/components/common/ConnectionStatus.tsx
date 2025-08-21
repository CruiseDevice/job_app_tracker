import React from 'react';
import { useAppSelector } from '../../hooks/redux';
import { webSocketService } from '../../services/websocket';

export const ConnectionStatus: React.FC = () => {
  const { isConnected, isMonitoring } = useAppSelector(state => state.monitor);
  const connectionState = webSocketService.getConnectionState();

  const getStatusColor = () => {
    if (isConnected && isMonitoring) return 'text-green-500';
    if (isConnected) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusIcon = () => {
    if (isConnected && isMonitoring) return '🟢';
    if (isConnected) return '🟡';
    return '🔴';
  };

  const getStatusText = () => {
    if (isConnected && isMonitoring) return 'Active Monitoring';
    if (isConnected) return 'Connected';
    return connectionState;
  };

  return (
    <div className="flex items-center space-x-2 text-sm">
      <span className="text-lg">{getStatusIcon()}</span>
      <span className={`font-medium ${getStatusColor()}`}>
        {getStatusText()}
      </span>
    </div>
  );
};