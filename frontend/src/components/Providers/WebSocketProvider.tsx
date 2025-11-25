import React, { useEffect, useCallback, createContext, useContext } from 'react';
import { useAppSelector } from '../../hooks/useAppSelector';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { updateApplicationFromWebSocket } from '../../store/slices/applicationsSlice';
import { updateStatisticsFromWebSocket } from '../../store/slices/statisticsSlice';
import { setMonitoringStatus } from '../../store/slices/monitorSlice';
import { webSocketService } from '../../services/websocket';
import type { WebSocketMessage } from '../../services/websocket';
import { toast } from 'react-hot-toast';

interface WebSocketContextType {
  isConnected: boolean;
  connectionState: string;
  sendMessage: (message: Record<string, unknown>) => void;
  startMonitoring: () => void;
  stopMonitoring: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const { isConnected } = useAppSelector(state => state.monitor);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'NEW_APPLICATION': {
        // Handle consolidated payload (application + statistics)
        // Note: websocket.ts already dispatches the action, but we dispatch here too as backup
        const appData = message.payload.application || message.payload;
        const stats = message.payload.statistics;
        
        toast.success(
          `New application: ${appData.company} - ${appData.position}`,
          { duration: 5000, icon: '📋' }
        );
        
        // Update statistics if included in payload
        if (stats) {
          dispatch(updateStatisticsFromWebSocket(stats));
        }
        break;
      }

      case 'APPLICATION_UPDATED':
        dispatch(updateApplicationFromWebSocket(message.payload));
        toast.success(`Application updated: ${message.payload.company}`, { icon: '📝' });
        break;

      case 'STATISTICS_UPDATED':
        dispatch(updateStatisticsFromWebSocket(message.payload));
        break;

      case 'MONITORING_STATUS': {
        dispatch(setMonitoringStatus(message.payload.isMonitoring));
        const status = message.payload.isMonitoring ? 'started' : 'stopped';
        toast.success(`Email monitoring ${status}`, { 
          icon: message.payload.isMonitoring ? '▶️' : '⏹️' 
        });
        break;
      }

      case 'CONNECTION_STATUS':
        if (message.payload.status === 'connected') {
          toast.success('Connected to server', { icon: '🔌' });
        }
        break;

      default:
        // Unknown message type - ignore silently
        break;
    }
  }, [dispatch]);

  useEffect(() => {
    // Add message listener
    const removeListener = webSocketService.addListener(handleMessage);

    // Cleanup on unmount
    return () => {
      removeListener();
    };
  }, [handleMessage]);

  const contextValue: WebSocketContextType = {
    isConnected,
    connectionState: webSocketService.getConnectionState(),
    sendMessage: (message: Record<string, unknown>) => webSocketService.send(message),
    startMonitoring: () => webSocketService.send({ type: 'start_monitoring' }),
    stopMonitoring: () => webSocketService.send({ type: 'stop_monitoring' })
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};
