from sqlalchemy import create_engine, and_, or_, func
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

    async def add_application(self, application_data: Dict[str, Any]) -> int:
        """Add new job application"""
        session = self.get_session()
        try:
            # Convert string date to datetime if needed
            if isinstance(application_data.get('application_date'), str):
                date_str = application_data['application_date']
                try:
                    # Try ISO format first
                    if 'T' in date_str or 'Z' in date_str:
                        application_data['application_date'] = datetime.fromisoformat(
                            date_str.replace('Z', '+00:00')
                        )
                    else:
                        # Try common date formats
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                            try:
                                application_data['application_date'] = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            # If all formats fail, use current date
                            logger.warning(f"Could not parse date '{date_str}', using current date")
                            application_data['application_date'] = datetime.now()
                except Exception as e:
                    logger.warning(f"Date parsing failed for '{date_str}': {e}, using current date")
                    application_data['application_date'] = datetime.now()
            
            # Ensure we have a valid date
            if not application_data.get('application_date'):
                application_data['application_date'] = datetime.now()
            
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

    async def update_application_status(self, application_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Update application status and return updated application data"""
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if application:
                application.status = status
                application.updated_at = datetime.now()
                session.commit()
                session.refresh(application)
                logger.info(f"Updated application {application_id} status to {status}")
                
                # Return the updated application data
                return application.to_dict()
            return None
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating application status: {e}")
            return None
        finally:
            session.close()

    async def update_application(self, application_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update application with provided data and return updated application data"""
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()

            if not application:
                return None

            # List of updatable fields
            updatable_fields = [
                'company', 'position', 'application_date', 'status',
                'job_url', 'job_description', 'salary_range', 'location', 'notes'
            ]

            # Update only provided fields
            for field, value in update_data.items():
                if field in updatable_fields and hasattr(application, field):
                    # Special handling for date fields
                    if field == 'application_date' and isinstance(value, str):
                        try:
                            # Parse date string to datetime object
                            from datetime import datetime as dt
                            parsed_date = dt.strptime(value, '%Y-%m-%d').date()
                            setattr(application, field, parsed_date)
                        except ValueError:
                            logger.error(f"Invalid date format for {field}: {value}")
                            continue
                    else:
                        setattr(application, field, value)

            application.updated_at = datetime.now()
            session.commit()
            session.refresh(application)
            logger.info(f"Updated application {application_id}")

            # Return the updated application data
            return application.to_dict()

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating application: {e}")
            return None
        finally:
            session.close()

    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive application statistics"""
        session = self.get_session()
        try:
            now = datetime.now()
            today = now.date()
            this_week_start = today - timedelta(days=today.weekday())
            this_month_start = today.replace(day=1)
            
            # Get total applications
            total = session.query(JobApplication).count()
            
            # Get today's applications
            today = session.query(JobApplication).filter(
                func.date(JobApplication.created_at) == today
            ).count()
            
            # Get this week's applications
            this_week = session.query(JobApplication).filter(
                JobApplication.created_at >= this_week_start
            ).count()
            
            # Get this month's applications
            this_month = session.query(JobApplication).filter(
                JobApplication.created_at >= this_month_start
            ).count()
            
            # Get status distribution
            status_counts = {}
            for status in ["applied", "interview", "offer", "rejected", "assessment"]:
                count = session.query(JobApplication).filter(
                    JobApplication.status == status
                ).count()
                status_counts[status] = count

            # Calculate rates
            interview_rate = (status_counts.get("interview", 0) / total * 100) if total > 0 else 0
            response_rate = ((status_counts.get("interview", 0) + status_counts.get("rejected", 0)) / total * 100) if total > 0 else 0

            # Calculate average per day (last 30 days)
            thirty_days_ago = now - timedelta(days=30)
            recent_applications = session.query(JobApplication).filter(
                JobApplication.created_at >= thirty_days_ago
            ).count()
            avg_per_day = recent_applications / 30 if recent_applications > 0 else 0

            # Get top companies
            top_companies_query = session.query(
                JobApplication.company,
                func.count(JobApplication.id).label('count')
            ).group_by(JobApplication.company).order_by(func.count(JobApplication.id).desc()).limit(5)
            
            top_companies = []
            for company, count in top_companies_query:
                top_companies.append({"company": company, "count": count})

            # Create status distribution (same as byStatus but with different key names)
            status_distribution = {status: count for status, count in status_counts.items()}

            return {
                "total": total,
                "today": today,
                "thisWeek": this_week,
                "thisMonth": this_month,
                "avgPerDay": round(avg_per_day, 1),
                "topCompanies": top_companies,
                "statusDistribution": status_distribution,
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
                "avgPerDay": 0,
                "topCompanies": [],
                "statusDistribution": {},
                "byStatus": {},
                "interviewRate": 0,
                "responseRate": 0
            }
        finally:
            session.close()

    async def is_email_processed(self, email_id: str) -> bool:
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

    async def mark_email_processed(self, email_id: str):
        """Mark email as processed"""
        session = self.get_session()
        try:
            # Check if already logged
            existing_log = session.query(EmailProcessingLog).filter(
                EmailProcessingLog.email_id == email_id
            ).first()
            
            if not existing_log:
                log = EmailProcessingLog(
                    email_id=email_id,
                    is_job_related=True,  # Assume it was processed for job-related content
                    confidence_score=1.0
                )
                session.add(log)
                session.commit()
                logger.info(f"Marked email {email_id} as processed")
            else:
                logger.debug(f"Email {email_id} already marked as processed")
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error marking email as processed: {e}")
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

    async def delete_application(self, application_id: int) -> bool:
        """Delete job application"""
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if application:
                session.delete(application)
                session.commit()
                logger.info(f"Deleted application {application_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting application: {e}")
            return False
        finally:
            session.close()

    async def close(self):
        """Close database connections"""
        try:
            if hasattr(self, 'engine'):
                self.engine.dispose()
                logger.info("Database connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Create global instance
db_manager = DatabaseManager()