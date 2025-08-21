import { createSlice } from "@reduxjs/toolkit";
import type { MonitorStatus } from '../../types/settings';

interface MonitorState extends MonitorStatus {
  loading: boolean;
  error: string | null
}

const initialState: MonitorState = {
  is_monitoring: false,
  loading: false,
  error: null
}

const monitorSlice = createSlice({
  name: 'monitor',
  initialState,
  reducers: {
    setMonitorStatus: (state, action) => {
      state.is_monitoring = action.payload
    }
  }
})

export default monitorSlice.reducer;