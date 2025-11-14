from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, \
    Float, Text, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
import json

Base = declarative_base()


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    position = Column(String, nullable=False)
    application_date = Column(DateTime, nullable=False)
    status = Column(String, default="applied")  # applied, interview, assessment, rejected, offer, captured
    job_url = Column(Text)
    job_description = Column(Text)
    salary_range = Column(String)
    location = Column(String)
    email_thread_id = Column(String, unique=False)
    email_subject = Column(String)
    email_sender = Column(String)
    calendar_event_id = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Extension-specific fields
    job_board = Column(String, default="unknown")
    captured_at = Column(DateTime)
    applied_at = Column(DateTime)
    extraction_data = Column(Text)
    source_type = Column(String, default="email")

    def to_dict(self):
        """Convert model to dictionary with enhanced fields"""
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "status": self.status,
            "job_url": self.job_url,
            "job_description": self.job_description,
            "salary_range": self.salary_range,
            "location": self.location,
            "email_thread_id": self.email_thread_id,
            "email_subject": self.email_subject,
            "email_sender": self.email_sender,
            "calendar_event_id": self.calendar_event_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "job_board": self.job_board,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "extraction_data": self.extraction_data,
            "source_type": self.source_type,
            "is_extension_captured": self.source_type == "extension",
            "is_email_captured": self.source_type == "email",
        }
    
    def is_extension_job(self) -> bool:
        """Check if this job was captured via browser extension"""
        return self.source_type == "extension" or self.status == "captured"
    
    def is_email_job(self) -> bool:
        """Check if this job was captured from email monitoring"""
        return self.source_type == "email" and self.status != "captured"
    
    def get_capture_source(self) -> str:
        """Get human-readable capture source"""
        if self.is_extension_job():
            return f"Browser Extension ({self.job_board})"
        elif self.is_email_job():
            return "Email Monitoring"
        else:
            return "Manual Entry"


class EmailProcessingLog(Base):
    __tablename__ = "email_processing_log"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True)
    processed_at = Column(DateTime, server_default=func.now())
    is_job_related = Column(Boolean)
    confidence_score = Column(Float)


class ApplicationStatistics(Base):
    __tablename__ = "application_statistics"
    
    date = Column(DateTime, primary_key=True)
    applications_count = Column(Integer, default=0)
    interviews_count = Column(Integer, default=0)


class ExtensionCaptureLog(Base):
    """Track extension capture events and quality"""
    __tablename__ = "extension_capture_log"
    
    id = Column(Integer, primary_key=True, index=True)
    job_application_id = Column(Integer, index=True)
    job_url = Column(Text, nullable=False)
    job_board = Column(String, nullable=False)
    extraction_quality = Column(String, default="unknown")
    fields_extracted = Column(Text)
    extraction_time_ms = Column(Integer)
    user_agent = Column(Text)
    page_title = Column(Text)
    captured_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "job_application_id": self.job_application_id,
            "job_url": self.job_url,
            "job_board": self.job_board,
            "extraction_quality": self.extraction_quality,
            "fields_extracted": self.fields_extracted,
            "extraction_time_ms": self.extraction_time_ms,
            "user_agent": self.user_agent,
            "page_title": self.page_title,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None
        }


# NEW MODELS FOR EMAIL-JOB MATCHING

class EmailJobLink(Base):
    """
    Links between emails and job applications with confidence scoring
    """
    __tablename__ = "email_job_links"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, nullable=False, index=True)  # Reference to email
    job_id = Column(Integer, ForeignKey('job_applications.id'), nullable=False, index=True)
    
    # Matching details
    confidence_score = Column(Float, nullable=False)  # 0-100% confidence
    match_methods = Column(Text)  # JSON array of matching methods used
    match_details = Column(Text)  # JSON of detailed matching information
    match_explanation = Column(Text)  # Human-readable explanation
    
    # Link metadata
    link_type = Column(String, default="auto")  # "auto", "manual", "verified"
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, default="system")  # "system" or user identifier
    
    # Verification and quality
    is_verified = Column(Boolean, default=False)  # User has verified this match
    is_rejected = Column(Boolean, default=False)  # User has rejected this match
    verified_at = Column(DateTime)
    verified_by = Column(String)
    
    # Update tracking
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "email_id": self.email_id,
            "job_id": self.job_id,
            "confidence_score": self.confidence_score,
            "match_methods": json.loads(self.match_methods) if self.match_methods else [],
            "match_details": json.loads(self.match_details) if self.match_details else {},
            "match_explanation": self.match_explanation,
            "link_type": self.link_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "is_verified": self.is_verified,
            "is_rejected": self.is_rejected,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verified_by": self.verified_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_confidence_level(self) -> str:
        """Get human-readable confidence level"""
        if self.confidence_score >= 90:
            return "Very High"
        elif self.confidence_score >= 75:
            return "High"
        elif self.confidence_score >= 60:
            return "Medium"
        elif self.confidence_score >= 40:
            return "Low"
        else:
            return "Very Low"
    
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence match"""
        return self.confidence_score >= 75.0
    
    def is_auto_linkable(self) -> bool:
        """Check if this match is good enough for auto-linking"""
        return self.confidence_score >= 85.0 and not self.is_rejected


class EmailRecord(Base):
    """
    Store email records for matching purposes
    This extends the basic email processing to store more details needed for matching
    """
    __tablename__ = "email_records"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, nullable=False, index=True)  # Original email ID from IMAP
    
    # Email headers and metadata
    subject = Column(Text)
    sender_email = Column(String, index=True)
    sender_name = Column(String)
    recipient_email = Column(String)
    date_sent = Column(DateTime, index=True)
    date_received = Column(DateTime, server_default=func.now())
    
    # Email content
    body_text = Column(Text)  # Plain text version
    body_html = Column(Text)  # HTML version (optional)
    
    # Processing status
    is_job_related = Column(Boolean, default=False, index=True)
    job_confidence = Column(Float)  # How likely this is job-related (0-1)
    processing_status = Column(String, default="pending")  # pending, processed, matched
    
    # Matching status
    has_matches = Column(Boolean, default=False, index=True)
    match_count = Column(Integer, default=0)
    best_match_confidence = Column(Float)  # Highest confidence match
    
    # Analysis results
    extracted_companies = Column(Text)  # JSON array of company names found
    extracted_positions = Column(Text)  # JSON array of job positions found
    extracted_urls = Column(Text)  # JSON array of URLs found
    keywords_found = Column(Text)  # JSON array of job-related keywords
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "email_id": self.email_id,
            "subject": self.subject,
            "sender_email": self.sender_email,
            "sender_name": self.sender_name,
            "recipient_email": self.recipient_email,
            "date_sent": self.date_sent.isoformat() if self.date_sent else None,
            "date_received": self.date_received.isoformat() if self.date_received else None,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "is_job_related": self.is_job_related,
            "job_confidence": self.job_confidence,
            "processing_status": self.processing_status,
            "has_matches": self.has_matches,
            "match_count": self.match_count,
            "best_match_confidence": self.best_match_confidence,
            "extracted_companies": json.loads(self.extracted_companies) if self.extracted_companies else [],
            "extracted_positions": json.loads(self.extracted_positions) if self.extracted_positions else [],
            "extracted_urls": json.loads(self.extracted_urls) if self.extracted_urls else [],
            "keywords_found": json.loads(self.keywords_found) if self.keywords_found else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_searchable_content(self) -> str:
        """Get combined searchable content from email"""
        content_parts = []
        if self.subject:
            content_parts.append(self.subject)
        if self.body_text:
            content_parts.append(self.body_text[:2000])  # Limit to avoid performance issues
        if self.sender_email:
            content_parts.append(self.sender_email)
        return ' '.join(content_parts)


class MatchingSuggestion(Base):
    """
    Store matching suggestions for user review
    """
    __tablename__ = "matching_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, nullable=False, index=True)
    job_id = Column(Integer, ForeignKey('job_applications.id'), nullable=False, index=True)
    
    # Suggestion details
    confidence_score = Column(Float, nullable=False)
    match_reasons = Column(Text)  # JSON array of reasons for match
    suggestion_type = Column(String, default="auto")  # "auto", "user_requested"
    
    # User actions
    status = Column(String, default="pending")  # pending, accepted, rejected, ignored
    user_action = Column(String)  # "accept", "reject", "ignore"
    user_action_at = Column(DateTime)
    user_feedback = Column(Text)  # Optional user feedback
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)  # When this suggestion expires
    priority = Column(Integer, default=0)  # Higher priority suggestions shown first
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "email_id": self.email_id,
            "job_id": self.job_id,
            "confidence_score": self.confidence_score,
            "match_reasons": json.loads(self.match_reasons) if self.match_reasons else [],
            "suggestion_type": self.suggestion_type,
            "status": self.status,
            "user_action": self.user_action,
            "user_action_at": self.user_action_at.isoformat() if self.user_action_at else None,
            "user_feedback": self.user_feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "priority": self.priority,
        }
    
    def is_expired(self) -> bool:
        """Check if this suggestion has expired"""
        return self.expires_at and datetime.now() > self.expires_at
    
    def is_pending(self) -> bool:
        """Check if this suggestion is still pending user action"""
        return self.status == "pending" and not self.is_expired()


class MatchingStatistics(Base):
    """
    Store matching statistics and analytics
    """
    __tablename__ = "matching_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Daily statistics
    emails_processed = Column(Integer, default=0)
    job_related_emails = Column(Integer, default=0)
    matches_found = Column(Integer, default=0)
    high_confidence_matches = Column(Integer, default=0)
    auto_linked_matches = Column(Integer, default=0)
    manual_links_created = Column(Integer, default=0)
    links_verified = Column(Integer, default=0)
    links_rejected = Column(Integer, default=0)
    
    # Quality metrics
    average_confidence = Column(Float)
    matching_accuracy = Column(Float)  # Based on user feedback
    
    # Performance metrics
    processing_time_ms = Column(Integer)  # Average processing time
    
    created_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "emails_processed": self.emails_processed,
            "job_related_emails": self.job_related_emails,
            "matches_found": self.matches_found,
            "high_confidence_matches": self.high_confidence_matches,
            "auto_linked_matches": self.auto_linked_matches,
            "manual_links_created": self.manual_links_created,
            "links_verified": self.links_verified,
            "links_rejected": self.links_rejected,
            "average_confidence": self.average_confidence,
            "matching_accuracy": self.matching_accuracy,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FollowUpRecord(Base):
    """
    Track follow-up actions for job applications
    """
    __tablename__ = "followup_records"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('job_applications.id'), nullable=False, index=True)

    # Follow-up details
    followup_type = Column(String, nullable=False)  # "initial_application", "post_interview", "offer_response", "checking_in"
    status = Column(String, default="scheduled")  # scheduled, sent, responded, expired, cancelled
    priority = Column(String, default="medium")  # high, medium, low

    # Timing
    scheduled_date = Column(DateTime, nullable=False, index=True)
    sent_date = Column(DateTime)
    response_date = Column(DateTime)
    optimal_send_time = Column(DateTime)  # AI-recommended optimal time

    # Message content
    subject_line = Column(Text)
    message_body = Column(Text)
    message_tone = Column(String, default="professional")  # professional, casual, enthusiastic
    personalization_data = Column(Text)  # JSON with personalization details

    # Strategy
    strategy_used = Column(String)  # "timing_optimized", "pattern_based", "manual"
    confidence_score = Column(Float)  # How confident we are in this approach
    expected_response_rate = Column(Float)  # Predicted response likelihood

    # Tracking
    email_sent = Column(Boolean, default=False)
    email_opened = Column(Boolean, default=False)
    email_clicked = Column(Boolean, default=False)
    response_received = Column(Boolean, default=False)
    response_sentiment = Column(String)  # positive, negative, neutral

    # Agent metadata
    created_by_agent = Column(Boolean, default=True)
    agent_reasoning = Column(Text)  # Why the agent suggested this follow-up
    user_modified = Column(Boolean, default=False)
    user_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "followup_type": self.followup_type,
            "status": self.status,
            "priority": self.priority,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "response_date": self.response_date.isoformat() if self.response_date else None,
            "optimal_send_time": self.optimal_send_time.isoformat() if self.optimal_send_time else None,
            "subject_line": self.subject_line,
            "message_body": self.message_body,
            "message_tone": self.message_tone,
            "personalization_data": json.loads(self.personalization_data) if self.personalization_data else {},
            "strategy_used": self.strategy_used,
            "confidence_score": self.confidence_score,
            "expected_response_rate": self.expected_response_rate,
            "email_sent": self.email_sent,
            "email_opened": self.email_opened,
            "email_clicked": self.email_clicked,
            "response_received": self.response_received,
            "response_sentiment": self.response_sentiment,
            "created_by_agent": self.created_by_agent,
            "agent_reasoning": self.agent_reasoning,
            "user_modified": self.user_modified,
            "user_notes": self.user_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_overdue(self) -> bool:
        """Check if follow-up is overdue"""
        return self.status == "scheduled" and self.scheduled_date < datetime.now()

    def is_pending(self) -> bool:
        """Check if follow-up is pending"""
        return self.status == "scheduled"

    def days_until_scheduled(self) -> int:
        """Calculate days until scheduled follow-up"""
        if not self.scheduled_date:
            return 0
        delta = self.scheduled_date - datetime.now()
        return delta.days


class FollowUpTemplate(Base):
    """
    Store reusable follow-up message templates
    """
    __tablename__ = "followup_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template details
    name = Column(String, nullable=False)
    description = Column(Text)
    followup_type = Column(String, nullable=False)  # matches FollowUpRecord.followup_type

    # Template content
    subject_template = Column(Text, nullable=False)
    body_template = Column(Text, nullable=False)
    tone = Column(String, default="professional")

    # Personalization variables
    variables = Column(Text)  # JSON array of variables like {company}, {position}, etc.

    # Effectiveness
    times_used = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)
    positive_responses = Column(Integer, default=0)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(String, default="system")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "followup_type": self.followup_type,
            "subject_template": self.subject_template,
            "body_template": self.body_template,
            "tone": self.tone,
            "variables": json.loads(self.variables) if self.variables else [],
            "times_used": self.times_used,
            "response_rate": self.response_rate,
            "positive_responses": self.positive_responses,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_effectiveness_rating(self) -> str:
        """Get human-readable effectiveness rating"""
        if self.times_used < 5:
            return "Insufficient Data"
        elif self.response_rate >= 0.4:
            return "Highly Effective"
        elif self.response_rate >= 0.25:
            return "Effective"
        elif self.response_rate >= 0.15:
            return "Moderately Effective"
        else:
            return "Low Effectiveness"


class FollowUpStatistics(Base):
    """
    Track follow-up performance and analytics
    """
    __tablename__ = "followup_statistics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)

    # Daily metrics
    followups_scheduled = Column(Integer, default=0)
    followups_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    positive_responses = Column(Integer, default=0)
    negative_responses = Column(Integer, default=0)

    # Performance metrics
    response_rate = Column(Float, default=0.0)
    average_response_time_hours = Column(Float)
    optimal_send_time_accuracy = Column(Float)  # How accurate our timing predictions are

    # By type
    post_application_followups = Column(Integer, default=0)
    post_interview_followups = Column(Integer, default=0)
    checking_in_followups = Column(Integer, default=0)

    # Agent performance
    agent_suggestions_accepted = Column(Integer, default=0)
    agent_suggestions_modified = Column(Integer, default=0)
    agent_suggestions_rejected = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "followups_scheduled": self.followups_scheduled,
            "followups_sent": self.followups_sent,
            "responses_received": self.responses_received,
            "positive_responses": self.positive_responses,
            "negative_responses": self.negative_responses,
            "response_rate": self.response_rate,
            "average_response_time_hours": self.average_response_time_hours,
            "optimal_send_time_accuracy": self.optimal_send_time_accuracy,
            "post_application_followups": self.post_application_followups,
            "post_interview_followups": self.post_interview_followups,
            "checking_in_followups": self.checking_in_followups,
            "agent_suggestions_accepted": self.agent_suggestions_accepted,
            "agent_suggestions_modified": self.agent_suggestions_modified,
            "agent_suggestions_rejected": self.agent_suggestions_rejected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def calculate_response_rate(self) -> float:
        """Calculate response rate"""
        if self.followups_sent == 0:
            return 0.0
        return self.responses_received / self.followups_sent


# INTERVIEW PREP AGENT MODELS

class InterviewPrepRecord(Base):
    """
    Track interview preparation sessions for job applications
    """
    __tablename__ = "interview_prep_records"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('job_applications.id'), nullable=False, index=True)

    # Interview details
    interview_date = Column(DateTime, index=True)
    interview_type = Column(String)  # phone, video, in-person, technical, behavioral, panel, final
    interview_round = Column(Integer, default=1)  # 1st round, 2nd round, etc.
    interviewer_name = Column(String)
    interviewer_title = Column(String)
    interviewer_linkedin = Column(Text)

    # Preparation status
    preparation_status = Column(String, default="in_progress")  # in_progress, completed, interview_done
    preparation_level = Column(String)  # basic, intermediate, advanced
    confidence_level = Column(Integer, default=5)  # 1-10 scale

    # Content prepared
    company_research_completed = Column(Boolean, default=False)
    questions_prepared_count = Column(Integer, default=0)
    star_stories_prepared_count = Column(Integer, default=0)
    mock_interviews_completed = Column(Integer, default=0)

    # Research notes
    company_research_notes = Column(Text)  # Company background, culture, values
    role_analysis_notes = Column(Text)  # Key responsibilities, required skills
    interviewer_research_notes = Column(Text)  # Interviewer background from LinkedIn

    # Preparation plan
    preparation_checklist = Column(Text)  # JSON array of checklist items
    focus_areas = Column(Text)  # JSON array of key areas to focus on
    questions_to_ask = Column(Text)  # JSON array of questions to ask interviewer

    # Outcomes (after interview)
    interview_completed = Column(Boolean, default=False)
    interview_completion_date = Column(DateTime)
    actual_questions_asked = Column(Text)  # JSON array of actual questions asked
    performance_notes = Column(Text)  # How the interview went
    follow_up_required = Column(Boolean, default=False)

    # Agent metadata
    created_by_agent = Column(Boolean, default=True)
    agent_preparation_plan = Column(Text)  # Full preparation plan from agent
    times_practiced = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "interview_date": self.interview_date.isoformat() if self.interview_date else None,
            "interview_type": self.interview_type,
            "interview_round": self.interview_round,
            "interviewer_name": self.interviewer_name,
            "interviewer_title": self.interviewer_title,
            "interviewer_linkedin": self.interviewer_linkedin,
            "preparation_status": self.preparation_status,
            "preparation_level": self.preparation_level,
            "confidence_level": self.confidence_level,
            "company_research_completed": self.company_research_completed,
            "questions_prepared_count": self.questions_prepared_count,
            "star_stories_prepared_count": self.star_stories_prepared_count,
            "mock_interviews_completed": self.mock_interviews_completed,
            "company_research_notes": self.company_research_notes,
            "role_analysis_notes": self.role_analysis_notes,
            "interviewer_research_notes": self.interviewer_research_notes,
            "preparation_checklist": json.loads(self.preparation_checklist) if self.preparation_checklist else [],
            "focus_areas": json.loads(self.focus_areas) if self.focus_areas else [],
            "questions_to_ask": json.loads(self.questions_to_ask) if self.questions_to_ask else [],
            "interview_completed": self.interview_completed,
            "interview_completion_date": self.interview_completion_date.isoformat() if self.interview_completion_date else None,
            "actual_questions_asked": json.loads(self.actual_questions_asked) if self.actual_questions_asked else [],
            "performance_notes": self.performance_notes,
            "follow_up_required": self.follow_up_required,
            "created_by_agent": self.created_by_agent,
            "agent_preparation_plan": self.agent_preparation_plan,
            "times_practiced": self.times_practiced,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_upcoming(self) -> bool:
        """Check if interview is upcoming"""
        return self.interview_date and self.interview_date > datetime.now()

    def days_until_interview(self) -> int:
        """Calculate days until interview"""
        if not self.interview_date:
            return 0
        delta = self.interview_date - datetime.now()
        return max(0, delta.days)

    def is_well_prepared(self) -> bool:
        """Check if candidate is well prepared"""
        return (
            self.company_research_completed and
            self.questions_prepared_count >= 5 and
            self.star_stories_prepared_count >= 3 and
            self.mock_interviews_completed >= 1
        )


class InterviewQuestion(Base):
    """
    Store generated or encountered interview questions
    """
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    prep_record_id = Column(Integer, ForeignKey('interview_prep_records.id'), index=True)
    job_id = Column(Integer, ForeignKey('job_applications.id'), index=True)

    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # behavioral, technical, situational, company-fit
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    question_category = Column(String)  # leadership, teamwork, problem-solving, etc.

    # Answer preparation
    has_prepared_answer = Column(Boolean, default=False)
    star_situation = Column(Text)  # Situation part of STAR answer
    star_task = Column(Text)  # Task part
    star_action = Column(Text)  # Action part
    star_result = Column(Text)  # Result part
    full_answer_notes = Column(Text)  # Complete answer notes

    # Metadata
    focus_area = Column(String)  # Key skill this question tests
    tips_for_answering = Column(Text)  # Tips for answering this question
    example_answer = Column(Text)  # Example/template answer

    # Practice tracking
    times_practiced = Column(Integer, default=0)
    confidence_rating = Column(Integer, default=5)  # 1-10 how confident in answer

    # Actual interview
    was_asked_in_interview = Column(Boolean, default=False)
    actual_answer_given = Column(Text)  # What was actually said
    answer_went_well = Column(Boolean)

    # Source
    generated_by_agent = Column(Boolean, default=True)
    source = Column(String, default="agent")  # agent, user, actual_interview

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "prep_record_id": self.prep_record_id,
            "job_id": self.job_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "difficulty_level": self.difficulty_level,
            "question_category": self.question_category,
            "has_prepared_answer": self.has_prepared_answer,
            "star_situation": self.star_situation,
            "star_task": self.star_task,
            "star_action": self.star_action,
            "star_result": self.star_result,
            "full_answer_notes": self.full_answer_notes,
            "focus_area": self.focus_area,
            "tips_for_answering": self.tips_for_answering,
            "example_answer": self.example_answer,
            "times_practiced": self.times_practiced,
            "confidence_rating": self.confidence_rating,
            "was_asked_in_interview": self.was_asked_in_interview,
            "actual_answer_given": self.actual_answer_given,
            "answer_went_well": self.answer_went_well,
            "generated_by_agent": self.generated_by_agent,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_star_answer(self) -> str:
        """Get formatted STAR answer"""
        parts = []
        if self.star_situation:
            parts.append(f"SITUATION: {self.star_situation}")
        if self.star_task:
            parts.append(f"TASK: {self.star_task}")
        if self.star_action:
            parts.append(f"ACTION: {self.star_action}")
        if self.star_result:
            parts.append(f"RESULT: {self.star_result}")
        return "\n\n".join(parts) if parts else self.full_answer_notes or ""

    def is_well_prepared(self) -> bool:
        """Check if question has a good prepared answer"""
        return (
            self.has_prepared_answer and
            self.confidence_rating >= 7 and
            (self.star_situation or self.full_answer_notes)
        )


class MockInterviewSession(Base):
    """
    Track mock interview practice sessions
    """
    __tablename__ = "mock_interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    prep_record_id = Column(Integer, ForeignKey('interview_prep_records.id'), index=True)
    job_id = Column(Integer, ForeignKey('job_applications.id'), index=True)

    # Session details
    session_date = Column(DateTime, nullable=False, server_default=func.now())
    session_duration_minutes = Column(Integer)
    session_type = Column(String)  # solo_practice, with_friend, recorded, live_agent
    focus_area = Column(String)  # behavioral, technical, company-fit, general
    difficulty_level = Column(String, default="medium")  # entry, medium, senior

    # Questions asked
    questions_asked_count = Column(Integer, default=0)
    questions_asked = Column(Text)  # JSON array of question IDs or texts

    # Performance
    overall_performance = Column(String)  # excellent, good, needs_improvement, poor
    performance_score = Column(Integer)  # 1-10
    strengths_identified = Column(Text)  # JSON array of strengths
    areas_for_improvement = Column(Text)  # JSON array of improvement areas

    # Detailed feedback
    feedback_notes = Column(Text)
    specific_questions_struggled = Column(Text)  # JSON array
    questions_answered_well = Column(Text)  # JSON array

    # Practice metrics
    average_answer_length_seconds = Column(Integer)
    used_star_format = Column(Boolean, default=False)
    examples_were_specific = Column(Boolean, default=False)
    maintained_good_pace = Column(Boolean, default=False)

    # Next steps
    recommended_next_practice = Column(DateTime)
    recommended_focus = Column(Text)  # What to focus on next

    # Recording/notes
    has_recording = Column(Boolean, default=False)
    recording_url = Column(Text)
    practice_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "prep_record_id": self.prep_record_id,
            "job_id": self.job_id,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "session_duration_minutes": self.session_duration_minutes,
            "session_type": self.session_type,
            "focus_area": self.focus_area,
            "difficulty_level": self.difficulty_level,
            "questions_asked_count": self.questions_asked_count,
            "questions_asked": json.loads(self.questions_asked) if self.questions_asked else [],
            "overall_performance": self.overall_performance,
            "performance_score": self.performance_score,
            "strengths_identified": json.loads(self.strengths_identified) if self.strengths_identified else [],
            "areas_for_improvement": json.loads(self.areas_for_improvement) if self.areas_for_improvement else [],
            "feedback_notes": self.feedback_notes,
            "specific_questions_struggled": json.loads(self.specific_questions_struggled) if self.specific_questions_struggled else [],
            "questions_answered_well": json.loads(self.questions_answered_well) if self.questions_answered_well else [],
            "average_answer_length_seconds": self.average_answer_length_seconds,
            "used_star_format": self.used_star_format,
            "examples_were_specific": self.examples_were_specific,
            "maintained_good_pace": self.maintained_good_pace,
            "recommended_next_practice": self.recommended_next_practice.isoformat() if self.recommended_next_practice else None,
            "recommended_focus": self.recommended_focus,
            "has_recording": self.has_recording,
            "recording_url": self.recording_url,
            "practice_notes": self.practice_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def is_recent(self) -> bool:
        """Check if session was in last 7 days"""
        if not self.session_date:
            return False
        delta = datetime.now() - self.session_date
        return delta.days <= 7

    def performance_rating(self) -> str:
        """Get human-readable performance rating"""
        if not self.performance_score:
            return "Not Rated"
        if self.performance_score >= 8:
            return "Excellent"
        elif self.performance_score >= 6:
            return "Good"
        elif self.performance_score >= 4:
            return "Needs Improvement"
        else:
            return "Poor"


class InterviewTip(Base):
    """
    Store interview tips and best practices
    """
    __tablename__ = "interview_tips"

    id = Column(Integer, primary_key=True, index=True)

    # Tip details
    tip_category = Column(String, nullable=False, index=True)  # preparation, during_interview, after_interview, body_language, etc.
    interview_stage = Column(String, index=True)  # phone-screen, technical, behavioral, panel, final, general
    role_level = Column(String)  # entry, mid, senior, executive

    # Content
    tip_title = Column(String, nullable=False)
    tip_content = Column(Text, nullable=False)
    tip_importance = Column(String, default="medium")  # high, medium, low

    # Examples
    example_scenario = Column(Text)
    what_to_do = Column(Text)
    what_to_avoid = Column(Text)

    # Metadata
    source = Column(String, default="agent")  # agent, user, industry_best_practice
    is_verified = Column(Boolean, default=True)
    applies_to_industries = Column(Text)  # JSON array of industries

    # Usage tracking
    times_viewed = Column(Integer, default=0)
    times_helpful = Column(Integer, default=0)
    helpfulness_rating = Column(Float)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "tip_category": self.tip_category,
            "interview_stage": self.interview_stage,
            "role_level": self.role_level,
            "tip_title": self.tip_title,
            "tip_content": self.tip_content,
            "tip_importance": self.tip_importance,
            "example_scenario": self.example_scenario,
            "what_to_do": self.what_to_do,
            "what_to_avoid": self.what_to_avoid,
            "source": self.source,
            "is_verified": self.is_verified,
            "applies_to_industries": json.loads(self.applies_to_industries) if self.applies_to_industries else [],
            "times_viewed": self.times_viewed,
            "times_helpful": self.times_helpful,
            "helpfulness_rating": self.helpfulness_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_highly_rated(self) -> bool:
        """Check if tip is highly rated"""
        return self.helpfulness_rating and self.helpfulness_rating >= 4.0


class InterviewStatistics(Base):
    """
    Track interview preparation and performance statistics
    """
    __tablename__ = "interview_statistics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)

    # Preparation metrics
    prep_sessions_started = Column(Integer, default=0)
    prep_sessions_completed = Column(Integer, default=0)
    total_questions_generated = Column(Integer, default=0)
    total_star_answers_prepared = Column(Integer, default=0)
    mock_interviews_conducted = Column(Integer, default=0)

    # Interview metrics
    interviews_scheduled = Column(Integer, default=0)
    interviews_completed = Column(Integer, default=0)
    interviews_successful = Column(Integer, default=0)  # Led to next round or offer

    # Performance metrics
    average_preparation_time_hours = Column(Float)
    average_confidence_level = Column(Float)  # 1-10 scale
    average_mock_interview_score = Column(Float)  # 1-10 scale

    # Effectiveness metrics
    prepared_questions_asked_rate = Column(Float)  # How often prepared questions were actually asked
    star_format_success_rate = Column(Float)  # When using STAR, how often it worked well

    # By interview type
    phone_screens = Column(Integer, default=0)
    technical_interviews = Column(Integer, default=0)
    behavioral_interviews = Column(Integer, default=0)
    panel_interviews = Column(Integer, default=0)
    final_interviews = Column(Integer, default=0)

    # Outcomes
    offers_received = Column(Integer, default=0)
    rejections_received = Column(Integer, default=0)
    still_in_process = Column(Integer, default=0)

    # Agent usage
    agent_prep_plans_generated = Column(Integer, default=0)
    agent_tips_viewed = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "prep_sessions_started": self.prep_sessions_started,
            "prep_sessions_completed": self.prep_sessions_completed,
            "total_questions_generated": self.total_questions_generated,
            "total_star_answers_prepared": self.total_star_answers_prepared,
            "mock_interviews_conducted": self.mock_interviews_conducted,
            "interviews_scheduled": self.interviews_scheduled,
            "interviews_completed": self.interviews_completed,
            "interviews_successful": self.interviews_successful,
            "average_preparation_time_hours": self.average_preparation_time_hours,
            "average_confidence_level": self.average_confidence_level,
            "average_mock_interview_score": self.average_mock_interview_score,
            "prepared_questions_asked_rate": self.prepared_questions_asked_rate,
            "star_format_success_rate": self.star_format_success_rate,
            "phone_screens": self.phone_screens,
            "technical_interviews": self.technical_interviews,
            "behavioral_interviews": self.behavioral_interviews,
            "panel_interviews": self.panel_interviews,
            "final_interviews": self.final_interviews,
            "offers_received": self.offers_received,
            "rejections_received": self.rejections_received,
            "still_in_process": self.still_in_process,
            "agent_prep_plans_generated": self.agent_prep_plans_generated,
            "agent_tips_viewed": self.agent_tips_viewed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def calculate_success_rate(self) -> float:
        """Calculate interview success rate"""
        if self.interviews_completed == 0:
            return 0.0
        return self.interviews_successful / self.interviews_completed

    def calculate_completion_rate(self) -> float:
        """Calculate preparation completion rate"""
        if self.prep_sessions_started == 0:
            return 0.0
        return self.prep_sessions_completed / self.prep_sessions_started