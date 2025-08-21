import { api } from './api';
import type { MonitorStatus } from '../types/settings';

export const monitorApi = {
  getStatus: async (): Promise<MonitorStatus> => {
    const response = await api.get('/monitor/status');
    return response.data;
  },

  startMonitoring: async (): Promise<{ message: string; status: MonitorStatus }> => {
    const response = await api.post('/monitor/start');
    return response.data;
  },

  stopMonitoring: async (): Promise<{ message: string; status: MonitorStatus }> => {
    const response = await api.post('/monitor/stop');
    return response.data;
  },
};