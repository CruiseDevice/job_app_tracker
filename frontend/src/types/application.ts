export interface JobApplication {
    id: number;
    company: string;
    position: string;
    application_date: string;
    status: ApplicationStatus;
    job_url?: string;
    job_description?: string;
    salary_range?: string;
    location?: string;
    email_thread_id?: string;
    email_subject?: string;
    email_sender?: string;
    calendar_event_id?: string;
    notes?: string;
    created_at: string;
    updated_at: string;
  }
  
  export type ApplicationStatus = 
    | "applied" 
    | "interview" 
    | "assessment" 
    | "rejected" 
    | "offer"
    | "screening";
  
  export interface ApplicationFilters {
    status?: ApplicationStatus;
    company?: string;
    dateRange?: {
      start: string;
      end: string;
    };
    search?: string;
  }
  
  export interface ApplicationStats {
  total: number;
  today: number;
  thisWeek: number;
  thisMonth: number;
  avgPerDay: number;
  topCompanies: Array<{ company: string; count: number }>;
  statusDistribution: Record<string, number>;
  byStatus: Record<ApplicationStatus, number>;
  interviewRate: number;
  responseRate: number;
}
  
  export interface CreateApplicationRequest {
    company: string;
    position: string;
    application_date: string;
    status?: ApplicationStatus;
    job_url?: string;
    job_description?: string;
    salary_range?: string;
    location?: string;
    notes?: string;
  }