import { api } from './api';
import type { JobApplication, ApplicationFilters, ApplicationStats, CreateApplicationRequest, PaginatedApplicationsResponse } from '../types/application';

export const applicationsApi = {
  // Get all applications with optional filtering and pagination
  getApplications: async (filters?: ApplicationFilters): Promise<PaginatedApplicationsResponse> => {
    const params = new URLSearchParams();
    
    if (filters?.status) params.append('status', filters.status);
    if (filters?.company) params.append('company', filters.company);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
    
    const response = await api.get(`/applications?${params.toString()}`);
    return response.data;
  },

  // Get single application
  getApplication: async (id: number): Promise<JobApplication> => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },

  // Update application status
  updateApplicationStatus: async (id: number, status: string): Promise<void> => {
    await api.put(`/applications/${id}/status`, { status });
  },

  // Update application
  updateApplication: async (id: number, data: Partial<JobApplication>): Promise<JobApplication> => {
    const response = await api.put(`/applications/${id}`, data);
    return response.data.application;
  },

  // Add manual application
  addManualApplication: async (data: CreateApplicationRequest): Promise<{ id: number; message: string }> => {
    const response = await api.post('/applications/manual', data);
    return response.data;
  },

  // Delete application
  deleteApplication: async (id: number): Promise<void> => {
    await api.delete(`/applications/${id}`);
  },

  // Get statistics
  getStatistics: async (): Promise<ApplicationStats> => {
    const response = await api.get('/statistics');
    return response.data;
  },
};