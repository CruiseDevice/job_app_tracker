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