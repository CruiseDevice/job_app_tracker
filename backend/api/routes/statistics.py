from fastapi import APIRouter
from database.database_manager import DatabaseManager

router = APIRouter()


def get_db():
    """Dependency to get database manager"""
    return DatabaseManager()


@router.get("/")
async def get_statistics():
    """Get application statistics"""
    return {"message": "Statistics endpoint - not yet implemented"}