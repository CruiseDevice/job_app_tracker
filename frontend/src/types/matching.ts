/**
 * TypeScript types for Email-Job Matching functionality
 */

export type MatchMethod = 
  | "company_exact"
  | "company_fuzzy" 
  | "domain_match"
  | "position_match"
  | "url_match"
  | "keyword_match"
  | "time_proximity"
  | "manual";

export type LinkType = "auto" | "manual" | "verified";

export type ConfidenceLevel = "very_low" | "low" | "medium" | "high" | "very_high";

export interface EmailJobLink {
  id: number;
  email_id: string;
  job_id: number;
  confidence_score: number;
  match_methods: MatchMethod[];
  match_details: Record<string, any>;
  match_explanation: string;
  link_type: LinkType;
  created_at: string;
  created_by: string;
  is_verified: boolean;
  is_rejected: boolean;
  verified_at?: string;
  verified_by?: string;
  updated_at: string;
}

export interface EmailDetails {
  email_id: string;
  subject: string;
  sender: string;
  sender_name?: string;
  date: string;
  body_text?: string;
  is_job_related?: boolean;
  job_confidence?: number;
}

export interface LinkedEmail extends EmailDetails {
  link_info: EmailJobLink;
}

export interface MatchSuggestion {
  email_id: string;
  job_id: number;
  confidence_score: number;
  match_methods: MatchMethod[];
  match_explanation: string;
  email_details: EmailDetails;
  job_details: Record<string, any>;
  created_at: string;
  is_auto_linkable: boolean;
}

export interface MatchingStatistics {
  period: {
    days: number;
    start_date: string;
    end_date: string;
  };
  totals: {
    total_links: number;
    verified_links: number;
    rejected_links: number;
    auto_links: number;
    manual_links: number;
  };
  rates: {
    verification_rate: number;
    rejection_rate: number;
    auto_link_rate: number;
  };
  confidence_distribution: {
    very_low: number;
    low: number;
    medium: number;
    high: number;
    very_high: number;
  };
  quality_metrics: {
    average_confidence: number;
    high_confidence_percentage: number;
  };
}

export interface CreateManualLinkRequest {
  email_id: string;
  job_id: number;
  user_notes?: string;
}

export interface UpdateLinkRequest {
  is_verified?: boolean;
  is_rejected?: boolean;
  user_feedback?: string;
}

export interface BulkMatchingRequest {
  job_ids?: number[];
  email_ids?: string[];
  confidence_threshold?: number;
  auto_link_threshold?: number;
  max_matches?: number;
}

export interface BulkMatchingResult {
  jobs_processed: number;
  matches_found: number;
  auto_linked: number;
  suggestions_created: number;
  errors: string[];
}

export interface MatchCriteria {
  company_exact_weight: number;
  company_fuzzy_weight: number;
  domain_match_weight: number;
  position_match_weight: number;
  url_match_weight: number;
  keyword_match_weight: number;
  time_proximity_weight: number;
  fuzzy_threshold: number;
  time_window_days: number;
  min_confidence: number;
  auto_link_confidence: number;
}

// API Response Types

export interface CreateLinkResponse {
  success: boolean;
  link_id: number;
  message: string;
  link_details: {
    email_id: string;
    job_id: number;
    confidence_score: number;
    link_type: LinkType;
    created_at: string;
  };
}

export interface UpdateLinkResponse {
  success: boolean;
  message: string;
  link: EmailJobLink;
}

export interface MatchSuggestionResponse {
  email_id: string;
  job_id: number;
  confidence_score: number;
  match_methods: string[];
  match_explanation: string;
  job_details: Record<string, any>;
  email_details: EmailDetails;
  created_at: string;
  is_auto_linkable: boolean;
}

export interface JobMatchesResponse {
  job_id: number;
  job_title: string;
  matches_found: number;
  matches: MatchSuggestionResponse[];
}

// Utility Types

export interface ConfidenceColorConfig {
  textColor: string;
  bgColor: string;
  label: string;
}

export interface MatchMethodDisplay {
  method: MatchMethod;
  label: string;
  description: string;
  color: string;
}

// WebSocket Message Types for Real-time Updates

export interface EmailJobLinkCreatedPayload {
  link_id: number;
  email_id: string;
  job_id: number;
  link_type: LinkType;
  job_title: string;
}

export interface EmailJobLinkUpdatedPayload {
  link_id: number;
  email_id: string;
  job_id: number;
  is_verified: boolean;
  is_rejected: boolean;
}

export interface EmailJobLinkDeletedPayload {
  link_id: number;
  email_id: string;
  job_id: number;
}

export interface BulkMatchingCompletePayload extends BulkMatchingResult {
  timestamp: string;
}

// Helper utility functions as types

export interface MatchingUtils {
  getConfidenceLevel: (score: number) => ConfidenceLevel;
  getConfidenceColor: (score: number) => ConfidenceColorConfig;
  getMatchMethodDisplay: (method: MatchMethod) => MatchMethodDisplay;
  formatConfidenceScore: (score: number) => string;
  isHighConfidence: (score: number) => boolean;
  isAutoLinkable: (score: number) => boolean;
}

// Form validation types

export interface LinkFormErrors {
  email_id?: string;
  job_id?: string;
  user_notes?: string;
}

export interface BulkMatchingFormData {
  job_ids: number[];
  confidence_threshold: number;
  auto_link_threshold: number;
  max_matches: number;
}

export interface BulkMatchingFormErrors {
  job_ids?: string;
  confidence_threshold?: string;
  auto_link_threshold?: string;
  max_matches?: string;
}