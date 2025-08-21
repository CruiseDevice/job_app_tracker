import { configureStore } from '@reduxjs/toolkit';
import applicationsSlice from './slices/applicationsSlice';
import statisticsSlice from './slices/statisticsSlice';
import settingsSlice from './slices/settingsSlice';
import monitorSlice from './slices/monitorSlice';

export const store = configureStore({
  reducer: {
    applications: applicationsSlice,
    statistics: statisticsSlice,
    settings: settingsSlice,
    monitor: monitorSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;