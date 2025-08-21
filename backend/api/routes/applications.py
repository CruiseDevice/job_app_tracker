from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database_manager import DatabaseManager

router = APIRouter()

def get_db():
    """Dependency to get database manager"""
    return DatabaseManager()

@router.get("/")
async def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: DatabaseManager = Depends(get_db)
):
    """Get job applications with optional filtering"""
    try:
        applications = db.get_applications(
            skip=skip, 
            limit=limit, 
            status=status, 
            company=company, 
            search=search
        )
        
        # Convert to dictionaries for JSON response
        return [app.to_dict() for app in applications]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving applications: {str(e)}")

@router.get("/{application_id}")
async def get_application(
    application_id: int, 
    db: DatabaseManager = Depends(get_db)
):
    """Get specific job application"""
    try:
        application = db.get_application(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        return application.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving application: {str(e)}")

@router.put("/{application_id}/status")
async def update_application_status(
    application_id: int, 
    status_data: Dict[str, str],
    db: DatabaseManager = Depends(get_db)
):
    """Update application status"""
    try:
        status = status_data.get("status")
        if not status:
            raise HTTPException(status_code=400, detail="Status is required")
            
        valid_statuses = ["applied", "interview", "assessment", "rejected", "offer"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        success = db.update_application_status(application_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Application not found")
            
        return {"message": "Status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")

@router.post("/manual")
async def add_manual_application(
    application_data: Dict[str, Any],
    db: DatabaseManager = Depends(get_db)
):
    """Manually add job application"""
    try:
        # Validate required fields
        required_fields = ["company", "position", "application_date"]
        for field in required_fields:
            if field not in application_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Add default status if not provided
        if "status" not in application_data:
            application_data["status"] = "applied"
            
        application_id = db.add_application(application_data)
        return {"id": application_id, "message": "Application added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding application: {str(e)}")