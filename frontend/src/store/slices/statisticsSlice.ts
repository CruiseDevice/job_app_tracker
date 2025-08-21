import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { ApplicationStats } from '../../types/application';
import { applicationsApi } from '../../services/applications';

interface StatisticsState {
  stats: ApplicationStats | null;
  loading: boolean;
  error: string | null;
}

const initialState: StatisticsState = {
  stats: null,
  loading: false,
  error: null,
};

export const fetchStatistics = createAsyncThunk(
  'statistics/fetchStatistics',
  async () => {
    return await applicationsApi.getStatistics();
  }
);

const statisticsSlice = createSlice({
  name: 'statistics',
  initialState,
  reducers: {
    updateStatisticsFromWebSocket: (state, action) => {
      state.stats = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchStatistics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStatistics.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
      })
      .addCase(fetchStatistics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch statistics';
      });
  },
});

export const { updateStatisticsFromWebSocket } = statisticsSlice.actions;
export default statisticsSlice.reducer;