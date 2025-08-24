from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
import logging
import json
import re
import os
from datetime import datetime
from pydantic import BaseModel, field_validator

from database.database_manager import DatabaseManager
from services.websocket_manager import manager as websocket_manager
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client
try:
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    logger.warning(f"OpenAI client initialization failed: {e}")
    openai_client = None


def get_db():
    return DatabaseManager()


async def extract_salary_from_description(job_description: str) -> Optional[str]:
    """
    Extract salary information from job description using LLM
    
    Args:
        job_description: The job description text
        
    Returns:
        Extracted salary range as string, or None if no salary found
    """
    if not openai_client or not job_description or len(job_description.strip()) < 50:
        return None
        
    try:
        prompt = f"""
Extract the salary or compensation information from the following job description. 

Job Description:
{job_description}

Instructions:
- Look for salary ranges, hourly rates, annual compensation, etc.
- Include currency symbols and time periods (e.g., "$80,000 - $100,000 per year", "$50/hour")
- If no specific salary is mentioned, look for compensation ranges or levels
- If no salary information is found, respond with "Not specified"
- Be concise and extract only the relevant salary information

Respond with just the salary information, nothing else.
"""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts salary information from job descriptions. Respond only with the salary information or 'Not specified'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.2
        )
        
        salary_info = response.choices[0].message.content.strip()
        
        # Clean up the response
        if salary_info and salary_info.lower() not in ['not specified', 'none', 'n/a', '']:
            logger.info(f"💰 Extracted salary: {salary_info}")
            return salary_info
        else:
            logger.debug("💰 No salary information found in job description")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error extracting salary from description: {e}")
        return None


# Pydantic models for request validation
class JobCaptureRequest(BaseModel):
    """Schema for job capture requests from browser extension"""
    company: str
    position: str
    job_url: str
    job_board: Optional[str] = "unknown"
    location: Optional[str] = None
    job_description: Optional[str] = None
    salary_range: Optional[str] = None
    captured_at: Optional[str] = None
    extraction_data: Optional[str] = None  # JSON string of raw extracted data

    @field_validator('company')
    @classmethod
    def company_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Company name is required')
        return v.strip()
    
    @field_validator('position')
    @classmethod
    def position_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Position title is required')
        return v.strip()
    
    @field_validator('job_url')
    @classmethod
    def job_url_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Job URL is required')
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Job URL must be a valid HTTP/HTTPS URL')
        return v.strip()
    
    @field_validator('captured_at')
    @classmethod
    def parse_captured_at(cls, v):
        if v:
            try:
                # Validate ISO format datetime
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('captured_at must be in ISO format')
        return v
    
    @field_validator('extraction_data')
    @classmethod
    def validate_extraction_data(cls, v):
        if v:
            try:
                # Validate that it's valid JSON
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('extraction_data must be valid JSON string')
        return v


class JobCaptureResponse(BaseModel):
    """Schema for job capture response"""
    success: bool
    job_id: int
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/capture", response_model=JobCaptureResponse)
async def capture_job_data(
    job_request: JobCaptureRequest,
    request: Request,
    db: DatabaseManager = Depends(get_db)
):
    """
    Capture job data from browser extension

    This endpoint receives job posting data extracted by the browser extension,
    validates it, stores it in the database, and broadcasts real-time updates.
    """
    try:
        logger.info(f"📥 Receiving job capture request for: {job_request.company} - {job_request.position}")
        
        # log request details for debugging
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        logger.debug(f"📡 Request from {client_host}, User-Agent: {user_agent}")

        # Extract salary from job description if not provided and description exists
        salary_range = job_request.salary_range
        if not salary_range and job_request.job_description:
            logger.info("💰 Attempting to extract salary from job description...")
            extracted_salary = await extract_salary_from_description(job_request.job_description)
            if extracted_salary:
                salary_range = extracted_salary

        # prepare application data for database
        application_data = {
            "company": job_request.company,
            "position": job_request.position,
            "job_url": job_request.job_url,
            "location": job_request.location,
            "job_description": job_request.job_description,
            "salary_range": salary_range,
            "status": "applied",  # Extension-captured jobs are considered as applied
            "application_date": datetime.now(),  # Use current time as capture time
            "notes": f"Captured via browser extension from {job_request.job_board}",
            
            # Extension-specific fields
            "job_board": job_request.job_board,
            "captured_at": datetime.fromisoformat(job_request.captured_at.replace('Z', '+00:00')) if job_request.captured_at else datetime.now(),
            "extraction_data": job_request.extraction_data,
            "email_sender": f"extension@{job_request.job_board}.com",  # Fake email for consistency
            "email_subject": f"Job captured: {job_request.position} at {job_request.company}",
        
        }

        # check for duplicates
        existing_job = await check_duplicate_job(db, job_request.job_url, job_request.company, job_request.position)
        if existing_job:
            logger.warning(f"⚠️ Duplicate job detected: {job_request.company} - {job_request.position}")
            raise HTTPException(
                status_code=409, 
                detail=f"Job already exists: {job_request.company} - {job_request.position}"
            )
        
        # Save to database
        logger.info(f"💾 Saving job to database: {job_request.company} - {job_request.position}")
        job_id = await db.add_application(application_data)
        # Get the saved application for response
        saved_application = db.get_application(job_id)
        if not saved_application:
            raise HTTPException(status_code=500, detail="Failed to retrieve saved job")
        
        logger.info(f"✅ Job saved successfully with ID: {job_id}")
        
        # Prepare response data
        response_data = {
            "id": job_id,
            "company": saved_application.company,
            "position": saved_application.position,
            "status": saved_application.status,
            "job_url": saved_application.job_url,
            "captured_at": saved_application.created_at.isoformat() if saved_application.created_at else None
        }

        # Broadcast real-time update via WebSocket
        try:
            await websocket_manager.broadcast({
                "type": "NEW_APPLICATION",
                "payload": saved_application.to_dict()
            })
            logger.info("📡 WebSocket broadcast sent for new job capture")
        except Exception as ws_error:
            logger.error(f"❌ WebSocket broadcast failed: {ws_error}")
            # Don't fail the request if WebSocket fails
        
        # Update statistics and broadcast
        try:
            stats = await db.get_statistics()
            await websocket_manager.broadcast({
                "type": "STATISTICS_UPDATED", 
                "payload": stats
            })
            logger.info("📊 Statistics updated and broadcast")
        except Exception as stats_error:
            logger.error(f"❌ Statistics update failed: {stats_error}")
            # Don't fail the request if stats update fails

        return JobCaptureResponse(
            success=True,
            job_id=job_id,
            message="Job captured successfully",
            data=response_data
        )
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"❌ Validation error: {ve}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        # Unexpected errors
        logger.error(f"❌ Unexpected error capturing job: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while capturing job"
        )


async def check_duplicate_job(
    db: DatabaseManager, 
    job_url: str, 
    company: str, 
    position: str
) -> bool:
    """
    Check if a job already exists in the database
    
    Args:
        db: Database manager instance
        job_url: URL of the job posting
        company: Company name
        position: Position title
        
    Returns:
        bool: True if duplicate exists, False otherwise
    """
    try:
        # Search for existing jobs with same URL
        existing_jobs = db.get_applications(limit=1000)  # Get all for duplicate check
        
        for job in existing_jobs:
            # Check exact URL match first
            if job.job_url and job.job_url.strip() == job_url.strip():
                logger.info(f"🔍 Found duplicate by URL: {job_url}")
                return True
            
            # Check company + position match (fuzzy)
            if (job.company.lower().strip() == company.lower().strip() and 
                job.position.lower().strip() == position.lower().strip()):
                logger.info(f"🔍 Found duplicate by company + position: {company} - {position}")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error checking for duplicates: {e}")
        # If duplicate check fails, allow the job to be saved (better safe than sorry)
        return False