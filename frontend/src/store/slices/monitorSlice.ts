import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { MonitorStatus } from '../../types/settings';
import { monitorApi } from '../../services/monitor';

interface MonitorState extends MonitorStatus {
  loading: boolean;
  error: string | null;
  isConnected: boolean;
}

const initialState: MonitorState = {
  is_monitoring: false,
  loading: false,
  error: null,
  isConnected: false,
};

export const fetchMonitorStatus = createAsyncThunk(
  'monitor/fetchStatus',
  async () => {
    return await monitorApi.getStatus();
  }
);

export const startMonitoring = createAsyncThunk(
  'monitor/start',
  async () => {
    const result = await monitorApi.startMonitoring();
    return result.status;
  }
);

export const stopMonitoring = createAsyncThunk(
  'monitor/stop',
  async () => {
    const result = await monitorApi.stopMonitoring();
    return result.status;
  }
);

const monitorSlice = createSlice({
  name: 'monitor',
  initialState,
  reducers: {
    setMonitoringStatus: (state, action) => {
      state.is_monitoring = action.payload;
    },
    setConnectionStatus: (state, action) => {
      state.isConnected = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMonitorStatus.fulfilled, (state, action) => {
        state.is_monitoring = action.payload.is_monitoring;
      })
      .addCase(startMonitoring.fulfilled, (state, action) => {
        state.is_monitoring = action.payload.is_monitoring;
      })
      .addCase(stopMonitoring.fulfilled, (state, action) => {
        state.is_monitoring = action.payload.is_monitoring;
      });
  },
});

export const { setMonitoringStatus, setConnectionStatus } = monitorSlice.actions;
export default monitorSlice.reducer;