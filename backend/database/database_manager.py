from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .models import Base, JobApplication, EmailProcessingLog, ApplicationStatistics
from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def add_application(self, application_data: Dict[str, Any]) -> int:
        """Add new job application"""
        session = self.get_session()
        try:
            # Convert string date to datetime if needed
            if isinstance(application_data.get('application_date'), str):
                application_data['application_date'] = datetime.fromisoformat(
                    application_data['application_date'].replace('Z', '+00:00')
                )
            
            application = JobApplication(**application_data)
            session.add(application)
            session.commit()
            session.refresh(application)
            logger.info(f"Added application: {application.company} - {application.position}")
            return application.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding application: {e}")
            raise
        finally:
            session.close()

    def get_applications(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[JobApplication]:
        """Get job applications with filtering"""
        session = self.get_session()
        try:
            query = session.query(JobApplication)
            
            # Apply filters
            if status:
                query = query.filter(JobApplication.status == status)
            
            if company:
                query = query.filter(JobApplication.company.ilike(f"%{company}%"))
            
            if search:
                query = query.filter(
                    or_(
                        JobApplication.company.ilike(f"%{search}%"),
                        JobApplication.position.ilike(f"%{search}%"),
                        JobApplication.location.ilike(f"%{search}%")
                    )
                )
            
            # Order by creation date (newest first)
            query = query.order_by(JobApplication.created_at.desc())
            
            # Apply pagination
            applications = query.offset(skip).limit(limit).all()
            return applications
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications: {e}")
            return []
        finally:
            session.close()

    def get_application(self, application_id: int) -> Optional[JobApplication]:
        """Get single application by ID"""
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            return application
        except SQLAlchemyError as e:
            logger.error(f"Error getting application {application_id}: {e}")
            return None
        finally:
            session.close()

    def update_application_status(self, application_id: int, status: str) -> bool:
        """Update application status"""
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if application:
                application.status = status
                application.updated_at = datetime.now()
                session.commit()
                logger.info(f"Updated application {application_id} status to {status}")
                return True
            return False
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating application status: {e}")
            return False
        finally:
            session.close()

    def get_statistics(self) -> Dict[str, Any]:
        """Get application statistics"""
        session = self.get_session()
        try:
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = today_start.replace(day=1)

            # Total applications
            total = session.query(JobApplication).count()

            # Today's applications
            today = session.query(JobApplication).filter(
                JobApplication.created_at >= today_start
            ).count()

            # This week's applications
            this_week = session.query(JobApplication).filter(
                JobApplication.created_at >= week_start
            ).count()

            # This month's applications
            this_month = session.query(JobApplication).filter(
                JobApplication.created_at >= month_start
            ).count()

            # Applications by status
            status_counts = {}
            statuses = ["applied", "interview", "assessment", "rejected", "offer"]
            for status in statuses:
                count = session.query(JobApplication).filter(
                    JobApplication.status == status
                ).count()
                status_counts[status] = count

            # Calculate rates
            interview_rate = (status_counts.get("interview", 0) / total * 100) if total > 0 else 0
            response_rate = ((status_counts.get("interview", 0) + status_counts.get("rejected", 0)) / total * 100) if total > 0 else 0

            return {
                "total": total,
                "today": today,
                "thisWeek": this_week,
                "thisMonth": this_month,
                "byStatus": status_counts,
                "interviewRate": round(interview_rate, 1),
                "responseRate": round(response_rate, 1)
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total": 0,
                "today": 0,
                "thisWeek": 0,
                "thisMonth": 0,
                "byStatus": {},
                "interviewRate": 0,
                "responseRate": 0
            }
        finally:
            session.close()

    def is_email_processed(self, email_id: str) -> bool:
        """Check if email has been processed"""
        session = self.get_session()
        try:
            log = session.query(EmailProcessingLog).filter(
                EmailProcessingLog.email_id == email_id
            ).first()
            return log is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking email processing status: {e}")
            return False
        finally:
            session.close()

    def log_email_processing(self, email_id: str, is_job_related: bool, confidence_score: float = 0.0):
        """Log email processing result"""
        session = self.get_session()
        try:
            log = EmailProcessingLog(
                email_id=email_id,
                is_job_related=is_job_related,
                confidence_score=confidence_score
            )
            session.add(log)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error logging email processing: {e}")
        finally:
            session.close()

# Create global instance
db_manager = DatabaseManager()