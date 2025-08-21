from fastapi import APIRouter

router = APIRouter()


# global monitoring state (in a real app, this would be more sophisticated)
monitoring_state = {"is_monitoring": False}


@router.get("/status")
async def get_monitor_status():
    """Get monitoring status"""
    return {"message": "Monitor endpoint - not yet implemented"}


@router.get("/start")
async def start_monitoring():
    """Start email monitoring"""
    return {"message": "Start email monitoring - not yet implemented"}


@router.post("/stop")
async def stop_monitoring():
    """Stop email monitoring"""
    return {"message": "Stop email monitoring - not yet implemented"}
