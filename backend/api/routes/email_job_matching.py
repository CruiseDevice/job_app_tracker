"""
Email-Job Matching API Routes

Endpoints for managing smart matching between emails and job applications,
including match suggestions, manual linking, and match quality management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

from database.database_manager import DatabaseManager
from agent.email_job_matcher import SmartEmailJobMatcher, MatchCriteria
from services.websocket_manager import manager as websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    """Dependency to get database manager"""
    return DatabaseManager()

def get_matcher(db: DatabaseManager = Depends(get_db)):
    """Dependency to get email-job matcher"""
    return SmartEmailJobMatcher(db)

# Pydantic models for request/response validation

class MatchSuggestionResponse(BaseModel):
    """Response model for match suggestions"""
    email_id: str
    job_id: int
    confidence_score: float
    match_methods: List[str]
    match_explanation: str
    job_details: Dict[str, Any]
    email_details: Dict[str, Any]
    created_at: str
    is_auto_linkable: bool

class CreateManualLinkRequest(BaseModel):
    """Request model for creating manual email-job links"""
    email_id: str
    job_id: int
    user_notes: Optional[str] = None
    
    @validator('email_id')
    def email_id_required(cls, v):
        if not v or not v.strip():
            raise ValueError('Email ID is required')
        return v.strip()
    
    @validator('job_id')
    def job_id_positive(cls, v):
        if v <= 0:
            raise ValueError('Job ID must be positive')
        return v

class UpdateLinkRequest(BaseModel):
    """Request model for updating email-job links"""
    is_verified: Optional[bool] = None
    is_rejected: Optional[bool] = None
    user_feedback: Optional[str] = None

class BulkMatchingRequest(BaseModel):
    """Request model for bulk matching operations"""
    job_ids: Optional[List[int]] = None
    email_ids: Optional[List[str]] = None
    confidence_threshold: Optional[float] = 30.0
    auto_link_threshold: Optional[float] = 85.0
    max_matches: Optional[int] = 100

# MATCH DISCOVERY AND SUGGESTIONS

@router.get("/matches/suggestions", response_model=List[MatchSuggestionResponse])
async def get_match_suggestions(
    limit: int = Query(50, ge=1, le=200),
    min_confidence: float = Query(30.0, ge=0.0, le=100.0),
    include_rejected: bool = Query(False),
    job_id: Optional[int] = Query(None),
    email_id: Optional[str] = Query(None),
    db: DatabaseManager = Depends(get_db),
    matcher: SmartEmailJobMatcher = Depends(get_matcher)
):
    """
    Get match suggestions between emails and jobs
    
    Returns a list of potential matches with confidence scores and explanations.
    """
    try:
        logger.info(f"🔍 Getting match suggestions (limit: {limit}, min_confidence: {min_confidence}%)")
        
        suggestions = []
        
        if job_id:
            # Get matches for specific job
            job_matches = matcher.find_matches_for_job(job_id)
            for match in job_matches:
                if match.confidence_score >= min_confidence:
                    suggestion = await _build_match_suggestion_response(match, db)
                    if suggestion:
                        suggestions.append(suggestion)
        
        elif email_id:
            # Get matches for specific email
            # This would require email data - placeholder for now
            logger.info(f"Getting matches for email: {email_id}")
            # email_matches = matcher.find_matches_for_email(email_data)
        
        else:
            # Get general suggestions - this would require access to stored emails
            logger.info("Getting general match suggestions")
            # This would involve querying unmatched emails and jobs
            
            # For now, return existing links as examples
            existing_links = db.get_email_job_links(limit=limit)
            for link in existing_links:
                if link.confidence_score >= min_confidence:
                    suggestion = await _build_link_suggestion_response(link, db)
                    if suggestion:
                        suggestions.append(suggestion)
        
        logger.info(f"✅ Found {len(suggestions)} match suggestions")
        return suggestions
        
    except Exception as e:
        logger.error(f"❌ Error getting match suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get match suggestions")

@router.post("/matches/find-for-job/{job_id}")
async def find_matches_for_job(
    job_id: int,
    min_confidence: float = Query(30.0, ge=0.0, le=100.0),
    matcher: SmartEmailJobMatcher = Depends(get_matcher),
    db: DatabaseManager = Depends(get_db)
):
    """
    Find email matches for a specific job application
    """
    try:
        logger.info(f"🔍 Finding email matches for job {job_id}")
        
        # Verify job exists
        job = db.get_application(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Find matches
        matches = matcher.find_matches_for_job(job_id)
        
        # Filter by confidence and build response
        suggestions = []
        for match in matches:
            if match.confidence_score >= min_confidence:
                suggestion = await _build_match_suggestion_response(match, db)
                if suggestion:
                    suggestions.append(suggestion)
        
        return {
            "job_id": job_id,
            "job_title": f"{job.company} - {job.position}",
            "matches_found": len(suggestions),
            "matches": suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error finding matches for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to find job matches")

# MANUAL LINK MANAGEMENT

@router.post("/links/create")
async def create_manual_link(
    link_request: CreateManualLinkRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Create a manual link between an email and job application
    """
    try:
        logger.info(f"🔗 Creating manual link: email {link_request.email_id} → job {link_request.job_id}")
        
        # Verify job exists
        job = db.get_application(link_request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {link_request.job_id} not found")
        
        # Check if link already exists
        existing_link = db.get_email_job_link(link_request.email_id, link_request.job_id)
        if existing_link:
            raise HTTPException(status_code=409, detail="Link already exists between this email and job")
        
        # Create the link
        link_data = {
            "email_id": link_request.email_id,
            "job_id": link_request.job_id,
            "confidence_score": 100.0,  # Manual links get 100% confidence
            "match_methods": json.dumps(["manual"]),
            "match_details": json.dumps({"user_notes": link_request.user_notes}),
            "match_explanation": "Manually linked by user",
            "link_type": "manual",
            "created_by": "user",  # In production, this would be the actual user ID
            "is_verified": True,
            "verified_at": datetime.now()
        }
        
        link_id = db.create_email_job_link(link_data)
        
        # Broadcast real-time update
        await websocket_manager.broadcast({
            "type": "EMAIL_JOB_LINK_CREATED",
            "payload": {
                "link_id": link_id,
                "email_id": link_request.email_id,
                "job_id": link_request.job_id,
                "link_type": "manual",
                "job_title": f"{job.company} - {job.position}"
            }
        })
        
        logger.info(f"✅ Manual link created successfully: {link_id}")
        
        return {
            "success": True,
            "link_id": link_id,
            "message": f"Manual link created between email and {job.company} - {job.position}",
            "link_details": {
                "email_id": link_request.email_id,
                "job_id": link_request.job_id,
                "confidence_score": 100.0,
                "link_type": "manual",
                "created_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating manual link: {e}")
        raise HTTPException(status_code=500, detail="Failed to create manual link")

@router.put("/links/{link_id}")
async def update_link(
    link_id: int,
    update_request: UpdateLinkRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Update an existing email-job link (verify, reject, add feedback)
    """
    try:
        logger.info(f"🔧 Updating link {link_id}")
        
        # Get existing link
        link = db.get_email_job_link_by_id(link_id)
        if not link:
            raise HTTPException(status_code=404, detail=f"Link {link_id} not found")
        
        # Update fields
        update_data = {}
        if update_request.is_verified is not None:
            update_data["is_verified"] = update_request.is_verified
            if update_request.is_verified:
                update_data["verified_at"] = datetime.now()
                update_data["verified_by"] = "user"
        
        if update_request.is_rejected is not None:
            update_data["is_rejected"] = update_request.is_rejected
        
        if update_request.user_feedback is not None:
            update_data["user_feedback"] = update_request.user_feedback
        
        # Apply updates
        updated_link = db.update_email_job_link(link_id, update_data)
        
        if updated_link:
            # Broadcast update
            await websocket_manager.broadcast({
                "type": "EMAIL_JOB_LINK_UPDATED",
                "payload": {
                    "link_id": link_id,
                    "email_id": updated_link["email_id"],
                    "job_id": updated_link["job_id"],
                    "is_verified": updated_link["is_verified"],
                    "is_rejected": updated_link["is_rejected"]
                }
            })
            
            action = "verified" if update_request.is_verified else "rejected" if update_request.is_rejected else "updated"
            logger.info(f"✅ Link {link_id} {action} successfully")
            
            return {
                "success": True,
                "message": f"Link {action} successfully",
                "link": updated_link
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update link")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating link {link_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update link")

@router.delete("/links/{link_id}")
async def delete_link(
    link_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Delete an email-job link
    """
    try:
        logger.info(f"🗑️ Deleting link {link_id}")
        
        # Get link details before deletion
        link = db.get_email_job_link_by_id(link_id)
        if not link:
            raise HTTPException(status_code=404, detail=f"Link {link_id} not found")
        
        # Delete the link
        success = db.delete_email_job_link(link_id)
        
        if success:
            # Broadcast deletion
            await websocket_manager.broadcast({
                "type": "EMAIL_JOB_LINK_DELETED",
                "payload": {
                    "link_id": link_id,
                    "email_id": link["email_id"],
                    "job_id": link["job_id"]
                }
            })
            
            logger.info(f"✅ Link {link_id} deleted successfully")
            
            return {
                "success": True,
                "message": "Link deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete link")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting link {link_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete link")

# BULK OPERATIONS

@router.post("/matches/bulk-process")
async def bulk_match_processing(
    bulk_request: BulkMatchingRequest,
    db: DatabaseManager = Depends(get_db),
    matcher: SmartEmailJobMatcher = Depends(get_matcher)
):
    """
    Process bulk matching for multiple jobs/emails
    """
    try:
        logger.info("🔄 Starting bulk matching process")
        
        results = {
            "jobs_processed": 0,
            "matches_found": 0,
            "auto_linked": 0,
            "suggestions_created": 0,
            "errors": []
        }
        
        # Get jobs to process
        jobs_to_process = []
        if bulk_request.job_ids:
            for job_id in bulk_request.job_ids[:bulk_request.max_matches]:
                job = db.get_application(job_id)
                if job:
                    jobs_to_process.append(job)
        else:
            # Process recent extension jobs
            jobs_to_process = db.get_extension_jobs(limit=bulk_request.max_matches)
        
        logger.info(f"📋 Processing {len(jobs_to_process)} jobs for matching")
        
        for job in jobs_to_process:
            try:
                job_data = job.to_dict() if hasattr(job, 'to_dict') else job
                
                # Find matches for this job
                matches = matcher.find_matches_for_job(job_data["id"])
                
                results["jobs_processed"] += 1
                
                for match in matches:
                    if match.confidence_score >= bulk_request.confidence_threshold:
                        results["matches_found"] += 1
                        
                        # Auto-link high confidence matches
                        if match.confidence_score >= bulk_request.auto_link_threshold:
                            try:
                                link_data = {
                                    "email_id": match.email_id,
                                    "job_id": match.job_id,
                                    "confidence_score": match.confidence_score,
                                    "match_methods": json.dumps([m.value for m in match.match_methods]),
                                    "match_details": json.dumps(match.match_details),
                                    "match_explanation": matcher.get_match_explanation(match),
                                    "link_type": "auto",
                                    "created_by": "system"
                                }
                                
                                link_id = db.create_email_job_link(link_data)
                                results["auto_linked"] += 1
                                
                                logger.debug(f"Auto-linked: job {match.job_id} ↔ email {match.email_id}")
                                
                            except Exception as e:
                                results["errors"].append(f"Auto-link failed for job {match.job_id}: {str(e)}")
                        
                        else:
                            # Create suggestion for manual review
                            results["suggestions_created"] += 1
                
            except Exception as e:
                error_msg = f"Error processing job {job.get('id', 'unknown')}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Broadcast bulk update
        await websocket_manager.broadcast({
            "type": "BULK_MATCHING_COMPLETE",
            "payload": results
        })
        
        logger.info(f"✅ Bulk matching complete: {results}")
        
        return {
            "success": True,
            "message": f"Processed {results['jobs_processed']} jobs, found {results['matches_found']} matches",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Error in bulk matching: {e}")
        raise HTTPException(status_code=500, detail="Bulk matching failed")

# STATISTICS AND ANALYTICS

@router.get("/matches/statistics")
async def get_matching_statistics(
    days: int = Query(30, ge=1, le=365),
    db: DatabaseManager = Depends(get_db)
):
    """
    Get matching statistics and analytics
    """
    try:
        logger.info(f"📊 Getting matching statistics for last {days} days")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get basic counts
        total_links = db.count_email_job_links()
        verified_links = db.count_email_job_links(is_verified=True)
        rejected_links = db.count_email_job_links(is_rejected=True)
        auto_links = db.count_email_job_links(link_type="auto")
        manual_links = db.count_email_job_links(link_type="manual")
        
        # Get confidence distribution
        confidence_distribution = db.get_link_confidence_distribution()
        
        # Calculate rates
        verification_rate = (verified_links / total_links * 100) if total_links > 0 else 0
        rejection_rate = (rejected_links / total_links * 100) if total_links > 0 else 0
        auto_link_rate = (auto_links / total_links * 100) if total_links > 0 else 0
        
        statistics = {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "totals": {
                "total_links": total_links,
                "verified_links": verified_links,
                "rejected_links": rejected_links,
                "auto_links": auto_links,
                "manual_links": manual_links
            },
            "rates": {
                "verification_rate": round(verification_rate, 1),
                "rejection_rate": round(rejection_rate, 1),
                "auto_link_rate": round(auto_link_rate, 1)
            },
            "confidence_distribution": confidence_distribution,
            "quality_metrics": {
                "average_confidence": db.get_average_link_confidence(),
                "high_confidence_percentage": db.get_high_confidence_link_percentage()
            }
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"❌ Error getting matching statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get matching statistics")

# HELPER FUNCTIONS

async def _build_match_suggestion_response(match, db: DatabaseManager) -> Optional[MatchSuggestionResponse]:
    """Build response object for a match suggestion"""
    try:
        # Get job details
        job = db.get_application(match.job_id)
        if not job:
            return None
        
        # Get email details (placeholder - would need email storage)
        email_details = {
            "email_id": match.email_id,
            "subject": "Email subject placeholder",
            "sender": "sender@example.com",
            "date": datetime.now().isoformat()
        }
        
        return MatchSuggestionResponse(
            email_id=match.email_id,
            job_id=match.job_id,
            confidence_score=match.confidence_score,
            match_methods=[method.value for method in match.match_methods],
            match_explanation=match.match_details.get("explanation", "Match found"),
            job_details=job.to_dict(),
            email_details=email_details,
            created_at=match.created_at.isoformat(),
            is_auto_linkable=match.confidence_score >= 85.0
        )
        
    except Exception as e:
        logger.error(f"Error building match suggestion: {e}")
        return None

async def _build_link_suggestion_response(link, db: DatabaseManager) -> Optional[MatchSuggestionResponse]:
    """Build response object from an existing link"""
    try:
        # This is a placeholder - would build from existing EmailJobLink
        return None
        
    except Exception as e:
        logger.error(f"Error building link suggestion: {e}")
        return None