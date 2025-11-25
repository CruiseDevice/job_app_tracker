import { store } from '../store';
import { addApplicationFromWebSocket, updateApplicationFromWebSocket } from '../store/slices/applicationsSlice';
import { updateStatisticsFromWebSocket } from '../store/slices/statisticsSlice';
import { setMonitoringStatus, setConnectionStatus } from '../store/slices/monitorSlice';
import type { ApplicationStatus } from '../types/application';

export interface WebSocketMessage {
  type: 'NEW_APPLICATION' | 'APPLICATION_UPDATED' | 'STATISTICS_UPDATED' | 'MONITORING_STATUS' | 'CONNECTION_STATUS';
  payload: any;
  timestamp?: string;
}

export interface ApplicationPayload {
  id: number;
  company: string;
  position: string;
  status: ApplicationStatus;
  application_date: string;
  job_url?: string;
  job_description?: string;
  salary_range?: string;
  location?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface StatisticsPayload {
  today: number;
  thisWeek: number;
  thisMonth: number;
  total: number;
  avgPerDay: number;
  topCompanies: Array<{ company: string; count: number }>;
  statusDistribution: Record<string, number>;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;
  private listeners: Set<(message: WebSocketMessage) => void> = new Set();
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;

  constructor() {
    // Auto-connect on service creation
    this.connect();
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
        return;
      }

      this.isConnecting = true;

      try {
        this.ws = new WebSocket('ws://localhost:8000/ws');

        this.ws.onopen = () => {
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          // Update connection status in store
          store.dispatch(setConnectionStatus(true));
          
          // Start heartbeat
          this.startHeartbeat();
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
            this.resetHeartbeat();
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          this.isConnecting = false;
          this.stopHeartbeat();
          
          // Update connection status in store
          store.dispatch(setConnectionStatus(false));
          
          // Attempt to reconnect if not a manual close
          if (event.code !== 1000) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        // Timeout for connection
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);

      } catch (error) {
        this.isConnecting = false;
        console.error('❌ Failed to create WebSocket connection:', error);
        this.scheduleReconnect();
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage) {
    // Handle system messages
    switch (message.type) {
      case 'NEW_APPLICATION':
        // Handle consolidated payload (application + statistics)
        const appData = message.payload.application || message.payload;
        const stats = message.payload.statistics;
        
        store.dispatch(addApplicationFromWebSocket(appData as ApplicationPayload));
        this.showNotification('New Application', `${appData.company} - ${appData.position}`);
        
        // If statistics are included, update them too
        if (stats) {
          store.dispatch(updateStatisticsFromWebSocket(stats as StatisticsPayload));
        }
        break;

      case 'APPLICATION_UPDATED':
        store.dispatch(updateApplicationFromWebSocket(message.payload as ApplicationPayload));
        break;

      case 'STATISTICS_UPDATED':
        store.dispatch(updateStatisticsFromWebSocket(message.payload as StatisticsPayload));
        break;

      case 'MONITORING_STATUS':
        store.dispatch(setMonitoringStatus(message.payload.isMonitoring));
        break;

      case 'CONNECTION_STATUS':
        // Connection status update handled by store
        break;

      default:
        console.warn('⚠️ Unknown message type:', message.type);
    }

    // Notify all listeners
    this.listeners.forEach(listener => {
      try {
        listener(message);
      } catch (error) {
        console.error('❌ Error in WebSocket listener:', error);
      }
    });
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
      
      setTimeout(() => {
        if (!this.isConnected()) {
          this.connect().catch(error => {
            console.error('❌ Reconnection failed:', error);
          });
        }
      }, delay);
    } else {
      console.error('❌ Max reconnection attempts reached. Please refresh the page.');
      store.dispatch(setConnectionStatus(false));
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' });
        
        // Set timeout for pong response
        this.heartbeatTimer = setTimeout(() => {
          console.warn('⚠️ Heartbeat timeout - reconnecting...');
          this.disconnect();
          this.scheduleReconnect();
        }, 5000);
      }
    }, 30000); // Send ping every 30 seconds
  }

  private resetHeartbeat() {
    if (this.heartbeatTimer) {
      clearTimeout(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    this.resetHeartbeat();
  }

  private showNotification(title: string, body: string) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body,
        icon: '/favicon.ico',
        tag: 'job-application'
      });
    }
  }

  // Public methods
  send(message: any) {
    if (this.isConnected()) {
      try {
        this.ws!.send(JSON.stringify(message));
      } catch (error) {
        console.error('❌ Error sending WebSocket message:', error);
      }
    } else {
      console.warn('⚠️ Cannot send message - WebSocket not connected');
    }
  }

  addListener(listener: (message: WebSocketMessage) => void) {
    this.listeners.add(listener);
    return () => this.removeListener(listener);
  }

  removeListener(listener: (message: WebSocketMessage) => void) {
    this.listeners.delete(listener);
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'CONNECTED';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'CLOSED';
      default: return 'UNKNOWN';
    }
  }

  disconnect() {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    
    this.listeners.clear();
    store.dispatch(setConnectionStatus(false));
  }

  // Request browser notification permission
  static async requestNotificationPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();

// Export the class for static method access
export { WebSocketService };

// Note: Notification permissions should be requested from user interactions
// (e.g., when toggling notifications in Settings)

export default webSocketService;