import { createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { JobApplication, ApplicationFilters, CreateApplicationRequest } from '../../types/application';
import { applicationsApi } from '../../services/applications';

interface ApplicationsState {
  applications: JobApplication[];
  currentApplication: JobApplication | null;
  filters: ApplicationFilters;
  loading: boolean;
  error: string | null;
}

const initialState: ApplicationsState = {
  applications: [],
  currentApplication: null,
  filters: {},
  loading: false,
  error: null,
};

// Async thunks
export const fetchApplications = createAsyncThunk(
  'applications/fetchApplications',
  async (filters?: ApplicationFilters) => {
    return await applicationsApi.getApplications(filters);
  }
);

export const fetchApplication = createAsyncThunk(
  'applications/fetchApplication',
  async (id: number) => {
    return await applicationsApi.getApplication(id);
  }
);

export const updateApplicationStatus = createAsyncThunk(
  'applications/updateStatus',
  async ({ id, status }: { id: number; status: string }) => {
    await applicationsApi.updateApplicationStatus(id, status);
    return { id, status };
  }
);

export const addApplication = createAsyncThunk(
  'applications/addApplication',
  async (applicationData: CreateApplicationRequest) => {
    const result = await applicationsApi.addManualApplication(applicationData);
    // Fetch the newly created application
    return await applicationsApi.getApplication(result.id);
  }
);

export const deleteApplication = createAsyncThunk(
  'applications/deleteApplication',
  async (id: number) => {
    await applicationsApi.deleteApplication(id);
    return id;
  }
);

const applicationsSlice = createSlice({
  name: 'applications',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<ApplicationFilters>) => {
      state.filters = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    addApplicationFromWebSocket: (state, action: PayloadAction<JobApplication>) => {
      state.applications.unshift(action.payload);
    },
    updateApplicationFromWebSocket: (state, action: PayloadAction<JobApplication>) => {
      const index = state.applications.findIndex(app => app.id === action.payload.id);
      if (index !== -1) {
        state.applications[index] = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch applications
      .addCase(fetchApplications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplications.fulfilled, (state, action) => {
        state.loading = false;
        state.applications = action.payload;
      })
      .addCase(fetchApplications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch applications';
      })
      // Fetch single application
      .addCase(fetchApplication.fulfilled, (state, action) => {
        state.currentApplication = action.payload;
      })
      // Update application status
      .addCase(updateApplicationStatus.fulfilled, (state, action) => {
        const { id, status } = action.payload;
        const application = state.applications.find(app => app.id === id);
        if (application) {
          application.status = status as any;
          application.updated_at = new Date().toISOString();
        }
      })
      // Add application
      .addCase(addApplication.fulfilled, (state, action) => {
        state.applications.unshift(action.payload);
      })
      // Delete application
      .addCase(deleteApplication.fulfilled, (state, action) => {
        state.applications = state.applications.filter(app => app.id !== action.payload);
      });
  },
});

export const { 
  setFilters, 
  clearError, 
  addApplicationFromWebSocket, 
  updateApplicationFromWebSocket 
} = applicationsSlice.actions;

export default applicationsSlice.reducer;