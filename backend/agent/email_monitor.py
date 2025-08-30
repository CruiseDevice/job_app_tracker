# backend/agent/email_monitor.py

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from services.websocket_manager import manager as websocket_manager
from database.database_manager import DatabaseManager
from .email_processor import EmailProcessor
from .smart_email_job_matcher import SmartEmailJobMatcher

logger = logging.getLogger(__name__)

class EmailMonitor:
    def __init__(self, db_manager: DatabaseManager, email_processor: EmailProcessor):
        self.db_manager = db_manager
        self.email_processor = email_processor
        self.job_matcher = SmartEmailJobMatcher(db_manager)  # NEW: Add matcher
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Start the email monitoring process"""
        if self.is_running:
            logger.warning("⚠️ Email monitoring is already running")
            return

        self.is_running = True
        logger.info("🚀 Starting email monitoring...")
        
        # Broadcast monitoring status
        await websocket_manager.broadcast({
            "type": "MONITORING_STATUS",
            "payload": {"isMonitoring": True}
        })

        # Start the monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop the email monitoring process"""
        if not self.is_running:
            logger.warning("⚠️ Email monitoring is not running")
            return

        self.is_running = False
        logger.info("🛑 Stopping email monitoring...")

        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        # Broadcast monitoring status
        await websocket_manager.broadcast({
            "type": "MONITORING_STATUS",
            "payload": {"isMonitoring": False}
        })

    async def _monitoring_loop(self):
        """Main monitoring loop that runs every 5 minutes"""
        while self.is_running:
            try:
                logger.info("🔍 Checking for new job application emails...")
                await self._check_emails()
                
                # Wait 5 minutes before next check
                await asyncio.sleep(300)  # 5 minutes
                
            except asyncio.CancelledError:
                logger.info("✋ Email monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                # Wait 1 minute before retrying on error
                await asyncio.sleep(60)

    async def _check_emails(self):
        """Check emails and process any new job applications - WITH SMART MATCHING"""
        try:
            # Get recent emails (last 24 hours)
            emails = await self.email_processor.fetch_recent_emails(hours=24)
            
            if not emails:
                logger.debug("🔭 No new emails found")
                return

            logger.info(f"📧 Processing {len(emails)} recent emails")
            
            new_applications = 0
            updated_applications = 0
            
            for email in emails:
                try:
                    # Check if email was already processed
                    if await self._is_email_processed(email['id']):
                        continue

                    # Process the email for job application content
                    email_analysis = await self.email_processor.process_email(email)
                    
                    if email_analysis and email_analysis.get('is_job_application'):
                        # NEW LOGIC: Try to match to existing job first
                        matched_job = await self._find_matching_job(email_analysis, email)
                        
                        if matched_job:
                            # UPDATE existing job application
                            updated_app = await self._update_existing_application(matched_job, email_analysis, email)
                            updated_applications += 1
                            logger.info(f"📝 Updated existing application {matched_job['id']}: {matched_job['company']} - {matched_job['position']}")
                        else:
                            # CREATE new application (original behavior)
                            app_id = await self._create_new_application(email_analysis, email)
                            new_applications += 1
                            logger.info(f"📋 Created new application: {email_analysis['company']} - {email_analysis['position']}")

                    # Mark email as processed regardless
                    await self._mark_email_processed(email['id'])
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {email.get('id', 'unknown')}: {e}")

            if new_applications > 0 or updated_applications > 0:
                # Update and broadcast statistics
                await self._update_and_broadcast_statistics()
                logger.info(f"✅ Processed {new_applications} new applications, {updated_applications} updates")
            else:
                logger.debug("🔭 No new job applications found")

        except Exception as e:
            logger.error(f"❌ Error checking emails: {e}")

    async def _find_matching_job(self, email_analysis: dict, email: dict) -> Optional[dict]:
        """
        NEW METHOD: Find existing job application that matches this email
        """
        try:
            company = email_analysis.get('company', '').strip()
            position = email_analysis.get('position', '').strip()
            email_sender = email.get('sender', '').strip()
            
            if not company:
                logger.debug("No company found in email - cannot match")
                return None
            
            # Use the existing matcher to find potential matches
            matches = await self.job_matcher.find_job_matches_for_email({
                'company': company,
                'position': position,
                'sender': email_sender,
                'subject': email.get('subject', ''),
                'received_at': email.get('date', datetime.now().isoformat())
            })
            
            # Return best match if confidence is high enough
            if matches and matches[0]['confidence'] >= 75:  # 75% confidence threshold
                best_match = matches[0]
                logger.info(f"🎯 Found high-confidence match: {best_match['confidence']:.1f}% - Job ID {best_match['job_id']}")
                return best_match['job']
            else:
                logger.debug(f"🤷 No high-confidence match found (best: {matches[0]['confidence']:.1f}% if any)")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error finding job match: {e}")
            return None

    async def _update_existing_application(self, matched_job: dict, email_analysis: dict, email: dict) -> dict:
        """
        NEW METHOD: Update an existing job application with new status from email
        """
        try:
            job_id = matched_job['id']
            new_status = email_analysis.get('status', 'applied')
            current_status = matched_job.get('status', '')
            
            # Only update status if it's a progression (optional: you can remove this check)
            status_progression = ['captured', 'applied', 'assessment', 'interview', 'offer', 'accepted']
            rejection_statuses = ['rejected', 'withdrawn']
            
            should_update = (
                new_status in rejection_statuses or  # Always update to rejection
                current_status != new_status or      # Status changed
                new_status == 'interview' or         # Always update interviews
                new_status == 'assessment'           # Always update assessments
            )
            
            if should_update:
                # Update application status
                updated_app = await self.db_manager.update_application_status(job_id, new_status)
                
                # Add any new notes from the email
                if email_analysis.get('notes'):
                    current_notes = matched_job.get('notes', '')
                    new_notes = f"{current_notes}\n\n[{datetime.now().strftime('%Y-%m-%d')}] {email_analysis['notes']}"
                    await self.db_manager.update_application_notes(job_id, new_notes)
                
                # Create email-job link for tracking
                await self._create_email_job_link(email['id'], job_id, 85.0, "automatic")
                
                # Convert to serializable format and broadcast update
                serializable_app = self._make_serializable(updated_app)
                await websocket_manager.broadcast({
                    "type": "APPLICATION_UPDATED",
                    "payload": serializable_app
                })
                
                return updated_app
            else:
                logger.debug(f"Status unchanged for job {job_id}: {current_status} -> {new_status}")
                return matched_job
                
        except Exception as e:
            logger.error(f"❌ Error updating existing application: {e}")
            raise

    async def _create_new_application(self, email_analysis: dict, email: dict) -> int:
        """
        MODIFIED METHOD: Create new application (only when no match found)
        """
        try:
            # Create application data
            application_data = {
                'company': email_analysis['company'],
                'position': email_analysis['position'],
                'status': email_analysis.get('status', 'applied'),
                'application_date': datetime.now(),
                'job_description': email_analysis.get('job_description', ''),
                'salary_range': email_analysis.get('salary_range', ''),
                'location': email_analysis.get('location', ''),
                'job_url': email_analysis.get('job_url', ''),
                'notes': email_analysis.get('notes', ''),
                'email_sender': email.get('sender', ''),
                'email_subject': email.get('subject', ''),
            }
            
            # Save to database
            app_id = await self.db_manager.add_application(application_data)
            application_data['id'] = app_id
            
            # Convert to serializable format and broadcast
            serializable_app = self._make_serializable(application_data)
            await websocket_manager.broadcast({
                "type": "NEW_APPLICATION",
                "payload": serializable_app
            })
            
            return app_id
            
        except Exception as e:
            logger.error(f"❌ Error creating new application: {e}")
            raise

    async def _create_email_job_link(self, email_id: str, job_id: int, confidence: float, link_type: str = "automatic"):
        """
        NEW METHOD: Create link between email and job application
        """
        try:
            link_data = {
                'email_id': email_id,
                'job_id': job_id,
                'confidence_score': confidence,
                'match_methods': '["email_processing"]',
                'match_details': '{}',
                'match_explanation': f'Email matched to job application during processing',
                'link_type': link_type,
                'created_by': 'system'
            }
            
            link_id = await self.db_manager.create_email_job_link(link_data)
            logger.debug(f"🔗 Created email-job link: Email {email_id} -> Job {job_id}")
            return link_id
            
        except Exception as e:
            logger.error(f"❌ Error creating email-job link: {e}")

    # ... rest of existing methods stay the same ...

    async def _is_email_processed(self, email_id: str) -> bool:
        """Check if an email has already been processed"""
        return await self.db_manager.is_email_processed(email_id)

    async def _mark_email_processed(self, email_id: str):
        """Mark an email as processed"""
        await self.db_manager.mark_email_processed(email_id)

    async def update_application_status(self, app_id: int, new_status: str):
        """Update application status and broadcast change"""
        try:
            # Update in database
            updated_app = await self.db_manager.update_application_status(app_id, new_status)
            
            if updated_app:
                # Convert to serializable format before broadcasting
                serializable_app = self._make_serializable(updated_app)
                
                # Broadcast update via WebSocket
                await websocket_manager.broadcast({
                    "type": "APPLICATION_UPDATED",
                    "payload": serializable_app
                })
                
                # Update statistics
                await self._update_and_broadcast_statistics()
                
                logger.info(f"📝 Application {app_id} status updated to: {new_status}")
                return updated_app
            else:
                logger.warning(f"⚠️ Application {app_id} not found for status update")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error updating application status: {e}")
            return None

    def _make_serializable(self, data: Any) -> Any:
        """Convert data to JSON serializable format by converting datetime objects to strings"""
        if isinstance(data, dict):
            return {key: self._make_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data

    async def _update_and_broadcast_statistics(self):
        """Update statistics and broadcast via WebSocket"""
        try:
            stats = await self.db_manager.get_statistics()
            await websocket_manager.broadcast({
                "type": "STATISTICS_UPDATED",
                "payload": stats
            })
        except Exception as e:
            logger.error(f"❌ Error updating statistics: {e}")