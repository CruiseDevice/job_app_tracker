from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, \
    Float, Text
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    position = Column(String, nullable=False)
    application_date = Column(DateTime, nullable=False)
    status = Column(String, default="applied")  # applied, interview, assessment, rejected, offer
    job_url = Column(Text)
    job_description = Column(Text)
    salary_range = Column(String)
    location = Column(String)
    email_thread_id = Column(String, unique=True)
    email_subject = Column(String)
    email_sender = Column(String)
    calendar_event_id = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
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
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


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