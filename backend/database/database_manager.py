from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .models import Base, EmailJobLink, EmailRecord, JobApplication, EmailProcessingLog, ApplicationStatistics
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
        """Add new job application with enhanced extension support"""
        session = self.get_session()
        try:
            # Determine source type
            if application_data.get('status') == 'captured':
                application_data['source_type'] = 'extension'
            elif 'source_type' not in application_data:
                application_data['source_type'] = 'email'

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
            
            # Handle captured_at field for extension jobs
            if isinstance(application_data.get('captured_at'), str):
                try:
                    application_data['captured_at'] = datetime.fromisoformat(
                        application_data['captured_at'].replace('Z', '+00:00')
                    )
                except Exception as e:
                    logger.warning(f"Could not parse captured_at: {e}")
                    application_data['captured_at'] = datetime.now()
            elif application_data.get('source_type') == 'extension' and not application_data.get('captured_at'):
                application_data['captured_at'] = datetime.now()
            
            application = JobApplication(**application_data)
            session.add(application)
            session.commit()
            session.refresh(application)
            logger.info(f"Added application: {application.company} - {application.position} (source: {application.source_type})")
            return application.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding application: {e}")
            raise
        finally:
            session.close()

    def search_applications_by_company_and_position(self, company: str, position: str = None, 
                                                  days_back: int = 45) -> List[Dict[str, Any]]:
        """
        Search for applications by company name and optionally position
        
        Args:
            company: Company name to search for
            position: Optional position title
            days_back: How many days back to search
            
        Returns:
            List of matching applications
        """
        session = self.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query = session.query(JobApplication).filter(
                JobApplication.application_date >= cutoff_date
            )
            
            # Add company filter (case-insensitive)
            if company:
                query = query.filter(JobApplication.company.ilike(f'%{company}%'))
            
            # Add position filter if provided
            if position:
                query = query.filter(JobApplication.position.ilike(f'%{position}%'))
            
            applications = query.order_by(JobApplication.application_date.desc()).all()
            
            return [app.to_dict() for app in applications]
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching applications: {e}")
            return []
        finally:
            session.close()

    def get_applications(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None,
        source_type: Optional[str] = None,
        job_board: Optional[str] = None
    ) -> List[JobApplication]:
        """Get job applications with enhanced filtering for extension jobs"""
        session = self.get_session()
        try:
            query = session.query(JobApplication)
            
            # Apply filters
            if status:
                query = query.filter(JobApplication.status == status)
            
            if company:
                query = query.filter(JobApplication.company.ilike(f"%{company}%"))
            
            if source_type:
                query = query.filter(JobApplication.source_type == source_type)
            
            if job_board:
                query = query.filter(JobApplication.job_board == job_board)
            
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

    def get_applications_count(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None,
        source_type: Optional[str] = None,
        job_board: Optional[str] = None
    ) -> int:
        """Get total count of job applications with the same filters as get_applications"""
        session = self.get_session()
        try:
            query = session.query(JobApplication)
            
            # Apply the same filters as get_applications
            if status:
                query = query.filter(JobApplication.status == status)
            
            if company:
                query = query.filter(JobApplication.company.ilike(f"%{company}%"))
            
            if source_type:
                query = query.filter(JobApplication.source_type == source_type)
            
            if job_board:
                query = query.filter(JobApplication.job_board == job_board)
            
            if search:
                query = query.filter(
                    or_(
                        JobApplication.company.ilike(f"%{search}%"),
                        JobApplication.position.ilike(f"%{search}%"),
                        JobApplication.location.ilike(f"%{search}%")
                    )
                )
            
            # Get count
            count = query.count()
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting applications: {e}")
            return 0
        finally:
            session.close()

    def get_extension_jobs(self, limit: int = 100) -> List[JobApplication]:
        """Get jobs captured via browser extension"""
        return self.get_applications(source_type="extension", limit=limit)

    def get_email_jobs(self, limit: int = 100) -> List[JobApplication]:
        """Get jobs captured via email monitoring"""  
        return self.get_applications(source_type="email", limit=limit)

    async def get_applications_since(self, cutoff_date: datetime) -> List[JobApplication]:
        """
        Get all job applications since a specific date
        
        Args:
            cutoff_date: Only return applications after this date
            
        Returns:
            List of JobApplication objects
        """
        session = self.get_session()
        try:
            applications = session.query(JobApplication).filter(
                JobApplication.application_date >= cutoff_date
            ).order_by(JobApplication.application_date.desc()).all()
            
            logger.debug(f"Found {len(applications)} applications since {cutoff_date}")
            return applications
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications since {cutoff_date}: {e}")
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
    
    def get_application_by_id(self, application_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single job application by ID
        
        Args:
            application_id: ID of the application
            
        Returns:
            Application dict or None if not found
        """
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            return application.to_dict() if application else None
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting application {application_id}: {e}")
            return None
        finally:
            session.close()

    async def update_application_notes(self, application_id: int, notes: str) -> bool:
        """
        Update the notes field for a job application
        
        Args:
            application_id: ID of the application to update
            notes: New notes content
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if application:
                application.notes = notes
                application.updated_at = datetime.now()
                session.commit()
                
                logger.info(f"📝 Updated notes for application {application_id}")
                return True
            else:
                logger.warning(f"⚠️ Application {application_id} not found for notes update")
                return False
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating application notes: {e}")
            return False
        finally:
            session.close()

    async def update_application_status(self, application_id: int, new_status: str) -> Optional[Dict[str, Any]]:
        """
        Update application status and return updated application
        
        Args:
            application_id: ID of application to update
            new_status: New status value
            
        Returns:
            Updated application dict or None if not found
        """
        session = self.get_session()
        try:
            application = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if application:
                old_status = application.status
                application.status = new_status
                application.updated_at = datetime.now()
                
                # Update status-specific dates
                if new_status == 'interview' and not application.interview_date:
                    application.interview_date = datetime.now()
                elif new_status in ['offer', 'accepted']:
                    application.offer_date = datetime.now()
                elif new_status == 'rejected':
                    application.rejection_date = datetime.now()
                
                session.commit()
                
                logger.info(f"📝 Updated application {application_id}: {old_status} -> {new_status}")
                return application.to_dict()
            else:
                logger.warning(f"⚠️ Application {application_id} not found")
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
            today_date = now.date()
            this_week_start = today_date - timedelta(days=today_date.weekday())
            this_month_start = today_date.replace(day=1)
            
            # Get total applications
            total = session.query(JobApplication).count()
            
            # Get today's applications
            today_count = session.query(JobApplication).filter(
                func.date(JobApplication.created_at) == today_date
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
            for status in ["applied", "interview", "offer", "rejected", "assessment", "screening", "captured"]:
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
                "today": today_count,
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


    async def create_email_job_link(self, link_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new email-job link
        
        Args:
            link_data: Dictionary containing link information
            
        Returns:
            Link ID if successful, None otherwise
        """
        session = self.get_session()
        try:
            # Check if link already exists
            existing_link = session.query(EmailJobLink).filter(
                EmailJobLink.email_id == link_data['email_id'],
                EmailJobLink.job_id == link_data['job_id']
            ).first()
            
            if existing_link:
                logger.debug(f"Link already exists: Email {link_data['email_id']} -> Job {link_data['job_id']}")
                return existing_link.id
            
            # Create new link
            link = EmailJobLink(
                email_id=link_data['email_id'],
                job_id=link_data['job_id'],
                confidence_score=link_data.get('confidence_score', 0.0),
                match_methods=link_data.get('match_methods', '[]'),
                match_details=link_data.get('match_details', '{}'),
                match_explanation=link_data.get('match_explanation', ''),
                link_type=link_data.get('link_type', 'automatic'),
                created_by=link_data.get('created_by', 'system'),
                is_verified=link_data.get('is_verified', False),
                is_rejected=link_data.get('is_rejected', False)
            )
            
            session.add(link)
            session.commit()
            
            logger.info(f"🔗 Created email-job link: Email {link_data['email_id']} -> Job {link_data['job_id']}")
            return link.id
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating email-job link: {e}")
            return None
        finally:
            session.close()

    def get_email_job_link(self, email_id: str, job_id: int) -> Optional[EmailJobLink]:
        """Get specific email-job link"""
        session = self.get_session()
        try:
            link = session.query(EmailJobLink).filter(
                and_(
                    EmailJobLink.email_id == email_id,
                    EmailJobLink.job_id == job_id,
                    EmailJobLink.is_rejected == False
                )
            ).first()
            return link
        except SQLAlchemyError as e:
            logger.error(f"Error getting email-job link: {e}")
            return None
        finally:
            session.close()

    def get_email_job_link_by_id(self, link_id: int) -> Optional[Dict[str, Any]]:
        """Get email-job link by ID"""
        session = self.get_session()
        try:
            link = session.query(EmailJobLink).filter(EmailJobLink.id == link_id).first()
            return link.to_dict() if link else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting email-job link {link_id}: {e}")
            return None
        finally:
            session.close()

    def get_email_job_links(
        self,
        limit: int = 100,
        job_id: Optional[int] = None,
        email_id: Optional[str] = None,
        link_type: Optional[str] = None,
        is_verified: Optional[bool] = None,
        min_confidence: Optional[float] = None
    ) -> List[EmailJobLink]:
        """Get email-job links with filtering"""
        session = self.get_session()
        try:
            query = session.query(EmailJobLink)
            
            if job_id:
                query = query.filter(EmailJobLink.job_id == job_id)
            
            if email_id:
                query = query.filter(EmailJobLink.email_id == email_id)
            
            if link_type:
                query = query.filter(EmailJobLink.link_type == link_type)
            
            if is_verified is not None:
                query = query.filter(EmailJobLink.is_verified == is_verified)
            
            if min_confidence:
                query = query.filter(EmailJobLink.confidence_score >= min_confidence)
            
            # Exclude rejected links by default
            query = query.filter(EmailJobLink.is_rejected == False)
            
            # Order by confidence and creation date
            query = query.order_by(EmailJobLink.confidence_score.desc(), EmailJobLink.created_at.desc())
            
            return query.limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting email-job links: {e}")
            return []
        finally:
            session.close()

    async def get_email_job_links_for_application(self, job_id: int) -> List[Dict[str, Any]]:
        """
        Get all email links for a specific job application
        
        Args:
            job_id: Job application ID
            
        Returns:
            List of email-job links
        """
        session = self.get_session()
        try:
            links = session.query(EmailJobLink).filter(
                EmailJobLink.job_id == job_id,
                EmailJobLink.is_rejected == False
            ).order_by(EmailJobLink.created_at.desc()).all()
            
            return [link.to_dict() for link in links]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting email links for job {job_id}: {e}")
            return []
        finally:
            session.close()

    def update_email_job_link(self, link_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an email-job link"""
        session = self.get_session()
        try:
            link = session.query(EmailJobLink).filter(EmailJobLink.id == link_id).first()
            
            if not link:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(link, field):
                    setattr(link, field, value)
            
            link.updated_at = datetime.now()
            session.commit()
            session.refresh(link)
            
            logger.info(f"Updated email-job link {link_id}")
            return link.to_dict()
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating email-job link {link_id}: {e}")
            return None
        finally:
            session.close()

    def delete_email_job_link(self, link_id: int) -> bool:
        """Delete an email-job link"""
        session = self.get_session()
        try:
            link = session.query(EmailJobLink).filter(EmailJobLink.id == link_id).first()
            
            if link:
                session.delete(link)
                session.commit()
                logger.info(f"Deleted email-job link {link_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting email-job link {link_id}: {e}")
            return False
        finally:
            session.close()

    def get_linked_emails_for_job(self, job_id: int) -> List[Dict[str, Any]]:
        """Get all emails linked to a specific job"""
        session = self.get_session()
        try:
            links = session.query(EmailJobLink).filter(
                and_(
                    EmailJobLink.job_id == job_id,
                    EmailJobLink.is_rejected == False
                )
            ).all()
            
            linked_emails = []
            for link in links:
                # Get email details - placeholder for now
                email_data = {
                    "email_id": link.email_id,
                    "subject": "Email subject placeholder",
                    "sender": "sender@example.com",
                    "date": link.created_at.isoformat(),
                    "link_info": link.to_dict()
                }
                linked_emails.append(email_data)
            
            return linked_emails
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting linked emails for job {job_id}: {e}")
            return []
        finally:
            session.close()

    def get_linked_jobs_for_email(self, email_id: str) -> List[Dict[str, Any]]:
        """Get all jobs linked to a specific email"""
        session = self.get_session()
        try:
            query = session.query(EmailJobLink, JobApplication).join(
                JobApplication, EmailJobLink.job_id == JobApplication.id
            ).filter(
                and_(
                    EmailJobLink.email_id == email_id,
                    EmailJobLink.is_rejected == False
                )
            )
            
            linked_jobs = []
            for link, job in query.all():
                job_data = job.to_dict()
                job_data["link_info"] = link.to_dict()
                linked_jobs.append(job_data)
            
            return linked_jobs
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting linked jobs for email {email_id}: {e}")
            return []
        finally:
            session.close()

    # EMAIL RECORD MANAGEMENT

    def save_email_record(self, email_data: Dict[str, Any]) -> int:
        """Save email record for matching purposes"""
        session = self.get_session()
        try:
            email_record = EmailRecord(**email_data)
            session.add(email_record)
            session.commit()
            session.refresh(email_record)
            logger.info(f"Saved email record: {email_data.get('email_id')}")
            return email_record.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving email record: {e}")
            raise
        finally:
            session.close()

    def get_email_record(self, email_id: str) -> Optional[EmailRecord]:
        """Get email record by email ID"""
        session = self.get_session()
        try:
            email = session.query(EmailRecord).filter(EmailRecord.email_id == email_id).first()
            return email
        except SQLAlchemyError as e:
            logger.error(f"Error getting email record {email_id}: {e}")
            return None
        finally:
            session.close()

    def get_unlinked_emails_count(self) -> int:
        """
        Get count of job-related emails that aren't linked to applications
        
        Returns:
            Number of unlinked emails
        """
        session = self.get_session()
        try:
            # This would require an emails table to work properly
            # For now, return 0 as placeholder
            return 0
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting unlinked emails count: {e}")
            return 0
        finally:
            session.close()

    def get_duplicate_applications(self) -> List[Dict[str, Any]]:
        """
        Find potential duplicate applications (same company + position)
        
        Returns:
            List of potential duplicates grouped by company+position
        """
        session = self.get_session()
        try:
            from sqlalchemy import func
            
            # Find applications with same company and position
            duplicates = session.query(
                JobApplication.company,
                JobApplication.position,
                func.count(JobApplication.id).label('count'),
                func.group_concat(JobApplication.id).label('ids')
            ).group_by(
                JobApplication.company, 
                JobApplication.position
            ).having(
                func.count(JobApplication.id) > 1
            ).all()
            
            duplicate_groups = []
            for dup in duplicates:
                if dup.count > 1:
                    ids = [int(id_str) for id_str in dup.ids.split(',')]
                    apps = session.query(JobApplication).filter(
                        JobApplication.id.in_(ids)
                    ).all()
                    
                    duplicate_groups.append({
                        'company': dup.company,
                        'position': dup.position,
                        'count': dup.count,
                        'applications': [app.to_dict() for app in apps]
                    })
            
            return duplicate_groups
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding duplicate applications: {e}")
            return []
        finally:
            session.close()

    def get_unmatched_emails(self, limit: int = 100) -> List[EmailRecord]:
        """Get emails that don't have matches yet"""
        session = self.get_session()
        try:
            emails = session.query(EmailRecord).filter(
                and_(
                    EmailRecord.is_job_related == True,
                    EmailRecord.has_matches == False
                )
            ).order_by(EmailRecord.date_received.desc()).limit(limit).all()
            return emails
        except SQLAlchemyError as e:
            logger.error(f"Error getting unmatched emails: {e}")
            return []
        finally:
            session.close()

    # MATCHING STATISTICS

    def count_email_job_links(
        self,
        is_verified: Optional[bool] = None,
        is_rejected: Optional[bool] = None,
        link_type: Optional[str] = None
    ) -> int:
        """Count email-job links with optional filters"""
        session = self.get_session()
        try:
            query = session.query(EmailJobLink)
            
            if is_verified is not None:
                query = query.filter(EmailJobLink.is_verified == is_verified)
            
            if is_rejected is not None:
                query = query.filter(EmailJobLink.is_rejected == is_rejected)
            
            if link_type:
                query = query.filter(EmailJobLink.link_type == link_type)
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting email-job links: {e}")
            return 0
        finally:
            session.close()

    def get_link_confidence_distribution(self) -> Dict[str, int]:
        """Get distribution of link confidence scores"""
        session = self.get_session()
        try:
            # Define confidence ranges
            ranges = {
                "very_low": (0, 30),
                "low": (30, 50),
                "medium": (50, 70),
                "high": (70, 85),
                "very_high": (85, 100)
            }
            
            distribution = {}
            for range_name, (min_conf, max_conf) in ranges.items():
                count = session.query(EmailJobLink).filter(
                    and_(
                        EmailJobLink.confidence_score >= min_conf,
                        EmailJobLink.confidence_score < max_conf,
                        EmailJobLink.is_rejected == False
                    )
                ).count()
                distribution[range_name] = count
            
            return distribution
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting confidence distribution: {e}")
            return {}
        finally:
            session.close()

    def get_average_link_confidence(self) -> float:
        """Get average confidence score of all links"""
        session = self.get_session()
        try:
            avg = session.query(func.avg(EmailJobLink.confidence_score)).filter(
                EmailJobLink.is_rejected == False
            ).scalar()
            return round(float(avg or 0), 1)
        except SQLAlchemyError as e:
            logger.error(f"Error getting average confidence: {e}")
            return 0.0
        finally:
            session.close()

    def get_high_confidence_link_percentage(self) -> float:
        """Get percentage of high confidence links (>= 75%)"""
        session = self.get_session()
        try:
            total = session.query(EmailJobLink).filter(EmailJobLink.is_rejected == False).count()
            high_conf = session.query(EmailJobLink).filter(
                and_(
                    EmailJobLink.confidence_score >= 75.0,
                    EmailJobLink.is_rejected == False
                )
            ).count()
            
            return round((high_conf / total * 100) if total > 0 else 0, 1)
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting high confidence percentage: {e}")
            return 0.0
        finally:
            session.close()

    # ENHANCED STATISTICS

    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive application statistics including matching data"""
        session = self.get_session()
        try:
            now = datetime.now()
            today_date = now.date()
            this_week_start = today_date - timedelta(days=today_date.weekday())
            this_month_start = today_date.replace(day=1)
            
            # Get basic application statistics (existing functionality)
            total = session.query(JobApplication).count()
            today_count = session.query(JobApplication).filter(
                func.date(JobApplication.created_at) == today_date
            ).count()
            this_week = session.query(JobApplication).filter(
                JobApplication.created_at >= this_week_start
            ).count()
            this_month = session.query(JobApplication).filter(
                JobApplication.created_at >= this_month_start
            ).count()
            
            # Status distribution
            status_counts = {}
            for status in ["applied", "interview", "offer", "rejected", "assessment", "screening", "captured"]:
                count = session.query(JobApplication).filter(JobApplication.status == status).count()
                status_counts[status] = count

            # Source type distribution  
            extension_count = session.query(JobApplication).filter(JobApplication.source_type == "extension").count()
            email_count = session.query(JobApplication).filter(JobApplication.source_type == "email").count()
            
            # Job board distribution
            job_board_stats = session.query(
                JobApplication.job_board,
                func.count(JobApplication.id).label('count')
            ).filter(JobApplication.source_type == "extension").group_by(JobApplication.job_board).all()
            job_board_distribution = {board: count for board, count in job_board_stats}

            # Matching statistics
            total_links = session.query(EmailJobLink).filter(EmailJobLink.is_rejected == False).count()
            verified_links = session.query(EmailJobLink).filter(
                and_(EmailJobLink.is_verified == True, EmailJobLink.is_rejected == False)
            ).count()
            high_confidence_links = session.query(EmailJobLink).filter(
                and_(EmailJobLink.confidence_score >= 75.0, EmailJobLink.is_rejected == False)
            ).count()

            # Calculate rates
            interview_rate = (status_counts.get("interview", 0) / total * 100) if total > 0 else 0
            response_rate = ((status_counts.get("interview", 0) + status_counts.get("rejected", 0)) / total * 100) if total > 0 else 0
            link_rate = (total_links / extension_count * 100) if extension_count > 0 else 0
            
            # Average per day
            thirty_days_ago = now - timedelta(days=30)
            recent_applications = session.query(JobApplication).filter(JobApplication.created_at >= thirty_days_ago).count()
            avg_per_day = recent_applications / 30 if recent_applications > 0 else 0

            # Top companies
            top_companies_query = session.query(
                JobApplication.company,
                func.count(JobApplication.id).label('count')
            ).group_by(JobApplication.company).order_by(func.count(JobApplication.id).desc()).limit(5)
            top_companies = [{"company": company, "count": count} for company, count in top_companies_query]

            return {
                # Basic statistics
                "total": total,
                "today": today_count,
                "thisWeek": this_week,
                "thisMonth": this_month,
                "avgPerDay": round(avg_per_day, 1),
                "topCompanies": top_companies,
                "statusDistribution": status_counts,
                "byStatus": status_counts,
                "interviewRate": round(interview_rate, 1),
                "responseRate": round(response_rate, 1),
                
                # Source distribution
                "sourceDistribution": {
                    "extension": extension_count,
                    "email": email_count,
                    "manual": max(0, total - extension_count - email_count)
                },
                "jobBoardDistribution": job_board_distribution,
                "extensionCaptureRate": round((extension_count / total * 100) if total > 0 else 0, 1),
                
                # NEW: Email-job matching statistics
                "matching": {
                    "total_links": total_links,
                    "verified_links": verified_links,
                    "high_confidence_links": high_confidence_links,
                    "link_rate": round(link_rate, 1),
                    "verification_rate": round((verified_links / total_links * 100) if total_links > 0 else 0, 1),
                    "average_confidence": self.get_average_link_confidence(),
                    "confidence_distribution": self.get_link_confidence_distribution()
                }
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total": 0, "today": 0, "thisWeek": 0, "thisMonth": 0,
                "avgPerDay": 0, "topCompanies": [], "statusDistribution": {},
                "byStatus": {}, "interviewRate": 0, "responseRate": 0,
                "sourceDistribution": {"extension": 0, "email": 0, "manual": 0},
                "jobBoardDistribution": {}, "extensionCaptureRate": 0,
                "matching": {
                    "total_links": 0, "verified_links": 0, "high_confidence_links": 0,
                    "link_rate": 0, "verification_rate": 0, "average_confidence": 0,
                    "confidence_distribution": {}
                }
            }
        finally:
            session.close()


# Create global instance
db_manager = DatabaseManager()