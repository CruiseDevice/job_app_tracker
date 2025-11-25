import { api } from './api';

export interface SettingsData {
  theme?: 'light' | 'dark';
  notifications?: boolean;
  autoRefresh?: boolean;
  email_check_interval?: number;
}

export const settingsApi = {
  getSettings: async (): Promise<SettingsData> => {
    const response = await api.get('/settings');
    return response.data;
  },

  updateSettings: async (settings: SettingsData): Promise<{ message: string; settings: SettingsData }> => {
    const response = await api.put('/settings', settings);
    return response.data;
  },
};

