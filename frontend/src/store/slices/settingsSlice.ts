import { createSlice } from '@reduxjs/toolkit';

interface SettingsState {
  theme: 'light' | 'dark';
  notifications: boolean;
  autoRefresh: boolean;
}

const initialState: SettingsState = {
  theme: 'light',
  notifications: true,
  autoRefresh: true,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    toggleNotifications: (state) => {
      state.notifications = !state.notifications;
    },
    toggleAutoRefresh: (state) => {
      state.autoRefresh = !state.autoRefresh;
    },
  },
});

export const { setTheme, toggleNotifications, toggleAutoRefresh } = settingsSlice.actions;
export default settingsSlice.reducer;