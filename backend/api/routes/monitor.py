from fastapi import APIRouter, HTTPException

router = APIRouter()

# Global monitoring state (in a real app, this would be more sophisticated)
monitoring_state = {"is_monitoring": False}

@router.get("/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    return monitoring_state

@router.post("/start")
async def start_monitoring():
    """Start email monitoring"""
    try:
        monitoring_state["is_monitoring"] = True
        return {"message": "Monitoring started", "status": monitoring_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting monitoring: {str(e)}")

@router.post("/stop")
async def stop_monitoring():
    """Stop email monitoring"""
    try:
        monitoring_state["is_monitoring"] = False
        return {"message": "Monitoring stopped", "status": monitoring_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping monitoring: {str(e)}")