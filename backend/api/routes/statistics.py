from fastapi import APIRouter, HTTPException, Depends
from database.database_manager import DatabaseManager

router = APIRouter()

def get_db():
    """Dependency to get database manager"""
    return DatabaseManager()

@router.get("/")
async def get_statistics(db: DatabaseManager = Depends(get_db)):
    """Get application statistics"""
    try:
        stats = await db.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")