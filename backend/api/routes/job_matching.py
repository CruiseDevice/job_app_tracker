# backend/api/routes/job_matching.py (NEW FILE)

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from database.database_manager import DatabaseManager
from agent.smart_email_job_matcher import SmartEmailJobMatcher
from services.websocket_manager import manager as websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None

class BulkStatusUpdateRequest(BaseModel):
    application_ids: List[int]
    status: str
    notes: Optional[str] = None

class MergeApplicationsRequest(BaseModel):
    primary_application_id: int
    duplicate_application_ids: List[int]

class JobMatchResponse(BaseModel):
    job_id: int
    confidence: float
    match_explanation: str
    match_methods: List[str]

# Dependency to get database manager and matcher
def get_db():
    # Your existing database dependency
    pass

def get_matcher(db: DatabaseManager = Depends(get_db)):
    return SmartEmailJobMatcher(db)

# ENHANCED STATUS MANAGEMENT ENDPOINTS

@router.put("/applications/{application_id}/status")
async def update_application_status_enhanced(
    application_id: int,
    status_update: StatusUpdateRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Update job application status with enhanced tracking
    """
    try:
        logger.info(f"📝 Updating application {application_id} status to: {status_update.status}")
        
        # Get current application
        current_app = db.get_application_by_id(application_id)
        if not current_app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        old_status = current_app.get('status', '')
        
        # Update status
        updated_app = await db.update_application_status(application_id, status_update.status)
        
        if not updated_app:
            raise HTTPException(status_code=500, detail="Failed to update application")
        
        # Add notes if provided
        if status_update.notes:
            current_notes = updated_app.get('notes', '')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_notes = f"{current_notes}\n\n[{timestamp}] Status: {old_status} -> {status_update.status}\n{status_update.notes}"
            await db.update_application_notes(application_id, new_notes)
            updated_app['notes'] = new_notes
        
        # Broadcast real-time update
        await websocket_manager.broadcast({
            "type": "APPLICATION_UPDATED",
            "payload": updated_app
        })
        
        # Update statistics
        stats = await db.get_statistics()
        await websocket_manager.broadcast({
            "type": "STATISTICS_UPDATED", 
            "payload": stats
        })
        
        logger.info(f"✅ Application {application_id} updated: {old_status} -> {status_update.status}")
        
        return {
            "success": True,
            "message": f"Status updated from '{old_status}' to '{status_update.status}'",
            "application": updated_app
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating application {application_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update application")

@router.put("/applications/bulk-status")
async def bulk_update_application_status(
    bulk_update: BulkStatusUpdateRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Update multiple application statuses at once
    """
    try:
        logger.info(f"📊 Bulk updating {len(bulk_update.application_ids)} applications to: {bulk_update.status}")
        
        updated_applications = []
        failed_updates = []
        
        for app_id in bulk_update.application_ids:
            try:
                updated_app = await db.update_application_status(app_id, bulk_update.status)
                if updated_app:
                    updated_applications.append(updated_app)
                    
                    # Add bulk update notes
                    if bulk_update.notes:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                        current_notes = updated_app.get('notes', '')
                        new_notes = f"{current_notes}\n\n[{timestamp}] Bulk Status Update: {bulk_update.status}\n{bulk_update.notes}"
                        await db.update_application_notes(app_id, new_notes)
                else:
                    failed_updates.append(app_id)
                    
            except Exception as e:
                logger.error(f"Failed to update application {app_id}: {e}")
                failed_updates.append(app_id)
        
        # Broadcast updates for all successful changes
        for app in updated_applications:
            await websocket_manager.broadcast({
                "type": "APPLICATION_UPDATED",
                "payload": app
            })
        
        # Update statistics
        stats = await db.get_statistics()
        await websocket_manager.broadcast({
            "type": "STATISTICS_UPDATED",
            "payload": stats
        })
        
        success_count = len(updated_applications)
        logger.info(f"✅ Bulk update completed: {success_count} successful, {len(failed_updates)} failed")
        
        return {
            "success": True,
            "message": f"Updated {success_count} applications to '{bulk_update.status}'",
            "updated_count": success_count,
            "failed_count": len(failed_updates),
            "failed_ids": failed_updates if failed_updates else None
        }
        
    except Exception as e:
        logger.error(f"❌ Error in bulk status update: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk update")

# DUPLICATE DETECTION AND MANAGEMENT

@router.get("/applications/duplicates")
async def get_duplicate_applications(db: DatabaseManager = Depends(get_db)):
    """
    Find and return potential duplicate job applications
    """
    try:
        duplicates = db.get_duplicate_applications()
        
        logger.info(f"🔍 Found {len(duplicates)} potential duplicate groups")
        
        return {
            "success": True,
            "duplicate_groups": duplicates,
            "total_groups": len(duplicates)
        }
        
    except Exception as e:
        logger.error(f"❌ Error finding duplicates: {e}")
        raise HTTPException(status_code=500, detail="Failed to find duplicates")

@router.post("/applications/merge")
async def merge_duplicate_applications(
    merge_request: MergeApplicationsRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Merge duplicate job applications into a single primary application
    """
    try:
        primary_id = merge_request.primary_application_id
        duplicate_ids = merge_request.duplicate_application_ids
        
        logger.info(f"🔄 Merging applications: keeping {primary_id}, removing {duplicate_ids}")
        
        # Get primary application
        primary_app = db.get_application_by_id(primary_id)
        if not primary_app:
            raise HTTPException(status_code=404, detail="Primary application not found")
        
        # Merge data from duplicates into primary
        merged_notes = primary_app.get('notes', '')
        
        for dup_id in duplicate_ids:
            dup_app = db.get_application_by_id(dup_id)
            if dup_app:
                # Merge notes
                dup_notes = dup_app.get('notes', '')
                if dup_notes and dup_notes not in merged_notes:
                    merged_notes += f"\n\n[MERGED FROM APP {dup_id}]\n{dup_notes}"
                
                # Transfer any email links
                email_links = await db.get_email_job_links_for_application(dup_id)
                for link in email_links:
                    # Update link to point to primary application
                    await db.update_email_job_link_job_id(link['id'], primary_id)
                
                # Delete duplicate application
                await db.delete_application(dup_id)
        
        # Update primary application with merged notes
        if merged_notes != primary_app.get('notes', ''):
            await db.update_application_notes(primary_id, merged_notes)
        
        # Get updated primary application
        updated_primary = db.get_application_by_id(primary_id)
        
        # Broadcast updates
        await websocket_manager.broadcast({
            "type": "APPLICATIONS_MERGED",
            "payload": {
                "primary_application": updated_primary,
                "merged_ids": duplicate_ids
            }
        })
        
        logger.info(f"✅ Successfully merged {len(duplicate_ids)} applications into {primary_id}")
        
        return {
            "success": True,
            "message": f"Merged {len(duplicate_ids)} duplicate applications",
            "primary_application": updated_primary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error merging applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to merge applications")

# APPLICATION HISTORY AND PROGRESSION

@router.get("/applications/{application_id}/history")
async def get_application_history(
    application_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get the complete history and timeline for a job application
    """
    try:
        # Get application details
        application = db.get_application_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get linked emails
        email_links = await db.get_email_job_links_for_application(application_id)
        
        # Create timeline of events
        timeline = []
        
        # Application submitted
        if application.get('application_date'):
            timeline.append({
                'date': application['application_date'],
                'event': 'Application Submitted',
                'status': application.get('status', 'applied'),
                'source': 'application'
            })
        
        # Email events
        for link in email_links:
            timeline.append({
                'date': link.get('created_at'),
                'event': 'Email Received',
                'description': link.get('match_explanation', ''),
                'confidence': link.get('confidence_score', 0),
                'source': 'email'
            })
        
        # Sort timeline by date
        timeline.sort(key=lambda x: x['date'] if x['date'] else '')
        
        return {
            "success": True,
            "application": application,
            "timeline": timeline,
            "linked_emails": len(email_links)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting application history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get application history")

# MATCHING INSIGHTS AND DEBUGGING

@router.post("/debug/test-email-matching")
async def test_email_matching(
    email_data: Dict[str, Any],
    matcher: SmartEmailJobMatcher = Depends(get_matcher)
):
    """
    Test email matching for debugging purposes
    """
    try:
        matches = await matcher.find_job_matches_for_email(email_data)
        
        return {
            "success": True,
            "email_data": email_data,
            "matches_found": len(matches),
            "matches": matches[:5]  # Return top 5 matches
        }
        
    except Exception as e:
        logger.error(f"❌ Error testing email matching: {e}")
        raise HTTPException(status_code=500, detail="Failed to test email matching")

@router.get("/applications/{application_id}/potential-emails")
async def find_potential_email_matches(
    application_id: int,
    matcher: SmartEmailJobMatcher = Depends(get_matcher),
    db: DatabaseManager = Depends(get_db)
):
    """
    Find emails that might belong to this application
    """
    try:
        application = db.get_application_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # This would need an emails table to work - placeholder for now
        potential_emails = []
        
        return {
            "success": True,
            "application_id": application_id,
            "potential_emails": potential_emails
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error finding potential emails: {e}")
        raise HTTPException(status_code=500, detail="Failed to find potential email matches")