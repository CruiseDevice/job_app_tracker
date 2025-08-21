import { configureStore } from "@reduxjs/toolkit";
import monitorSlice from './slices/monitorSlice';

export const store = configureStore({
  reducer: {
    monitor: monitorSlice
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;