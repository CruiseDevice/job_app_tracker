from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

# Import the global email monitor instance
def get_email_monitor():
    from main import email_monitor
    return email_monitor

@router.get("/status")
async def get_monitoring_status(monitor = Depends(get_email_monitor)):
    """Get current monitoring status"""
    return {"is_monitoring": monitor.is_running}

@router.post("/start")
async def start_monitoring(monitor = Depends(get_email_monitor)):
    """Start email monitoring"""
    try:
        await monitor.start_monitoring()
        return {"message": "Monitoring started", "status": {"is_monitoring": monitor.is_running}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting monitoring: {str(e)}")

@router.post("/stop")
async def stop_monitoring(monitor = Depends(get_email_monitor)):
    """Stop email monitoring"""
    try:
        await monitor.stop_monitoring()
        return {"message": "Monitoring stopped", "status": {"is_monitoring": monitor.is_running}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping monitoring: {str(e)}")