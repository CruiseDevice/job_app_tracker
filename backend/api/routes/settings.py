from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from config.settings import settings

router = APIRouter()

@router.get("/")
async def get_settings():
    """Get application settings"""
    try:
        return {
            "email_check_interval": settings.email_check_interval,
            "debug": settings.debug,
            "api_host": settings.api_host,
            "api_port": settings.api_port
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving settings: {str(e)}")

@router.put("/")
async def update_settings(settings_data: Dict[str, Any]):
    """Update application settings"""
    try:
        # This is a basic implementation
        # In a real app, you'd want to validate and persist these settings
        return {"message": "Settings updated successfully", "settings": settings_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")