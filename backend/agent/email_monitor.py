import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from services.websocket_manager import manager as websocket_manager
from database.database_manager import DatabaseManager
from .email_processor import EmailProcessor

logger = logging.getLogger(__name__)

class EmailMonitor:
    def __init__(self, db_manager: DatabaseManager, email_processor: EmailProcessor):
        self.db_manager = db_manager
        self.email_processor = email_processor
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
        """Check emails and process any new job applications"""
        try:
            # Get recent emails (last 24 hours)
            emails = await self.email_processor.fetch_recent_emails(hours=24)
            
            if not emails:
                logger.debug("📭 No new emails found")
                return

            logger.info(f"📧 Processing {len(emails)} recent emails")
            
            new_applications = 0
            for email in emails:
                try:
                    # Check if email was already processed
                    if await self._is_email_processed(email['id']):
                        continue

                    # Process the email for job application content
                    application_data = await self.email_processor.process_email(email)
                    
                    if application_data:
                        # Save to database
                        app_id = await self.db_manager.add_application(application_data)
                        application_data['id'] = app_id
                        
                        # Convert application data to serializable format before broadcasting
                        serializable_data = self._make_serializable(application_data)
                        
                        # Broadcast new application via WebSocket
                        await websocket_manager.broadcast({
                            "type": "NEW_APPLICATION",
                            "payload": serializable_data
                        })
                        
                        new_applications += 1
                        logger.info(f"📋 New application added: {application_data['company']} - {application_data['position']}")

                    # Mark email as processed
                    await self._mark_email_processed(email['id'])
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {email.get('id', 'unknown')}: {e}")

            if new_applications > 0:
                # Update and broadcast statistics
                await self._update_and_broadcast_statistics()
                logger.info(f"✅ Processed {new_applications} new job applications")
            else:
                logger.debug("📭 No new job applications found")

        except Exception as e:
            logger.error(f"❌ Error checking emails: {e}")

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

    async def _is_email_processed(self, email_id: str) -> bool:
        """Check if an email has already been processed"""
        # Implementation depends on your database schema
        # You might want to add a processed_emails table
        return await self.db_manager.is_email_processed(email_id)

    async def _mark_email_processed(self, email_id: str):
        """Mark an email as processed"""
        await self.db_manager.mark_email_processed(email_id)

    async def update_application_status(self, app_id: str, new_status: str):
        """Update application status and broadcast change"""
        try:
            # Update in database
            updated_app = await self.db_manager.update_application_status(int(app_id), new_status)
            
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
            else:
                logger.warning(f"⚠️ Application {app_id} not found for status update")
            
        except Exception as e:
            logger.error(f"❌ Error updating application status: {e}")

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
