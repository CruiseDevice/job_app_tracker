from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from services.websocket_manager import manager as websocket_manager
from agent.email_monitor import EmailMonitor
from database.database_manager import DatabaseManager
from agent.email_processor import EmailProcessor
from api.routes import applications, monitor, settings, statistics, jobs_capture, agents

logger = logging.getLogger(__name__)

# Initialize core services
db_manager = DatabaseManager()
email_processor = EmailProcessor()
email_monitor = EmailMonitor(db_manager, email_processor)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("🚀 Starting Smart Job Tracker API...")
    
    # Initialize database
    db_manager.init_db()
    
    # Optionally start monitoring on startup
    # await email_monitor.start_monitoring()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Smart Job Tracker API...")
    
    # Stop monitoring
    await email_monitor.stop_monitoring()
    
    # Close database connections
    await db_manager.close()


app = FastAPI(
    title="Smart Job Tracker API",
    description="Backend API for Smart Job Application Tracker with real-time WebSocket support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["monitor"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(jobs_capture.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    connection_id = await websocket_manager.connect(websocket)
    
    try:
        # Send current monitoring status
        await websocket_manager.send_personal_message(connection_id, {
            "type": "MONITORING_STATUS",
            "payload": {"isMonitoring": email_monitor.is_running}
        })
        
        # Send current statistics
        try:
            stats = await db_manager.get_statistics()
            await websocket_manager.send_personal_message(connection_id, {
                "type": "STATISTICS_UPDATED",
                "payload": stats
            })
        except Exception as e:
            logger.error(f"❌ Error sending initial statistics: {e}")

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(connection_id, message)
            except json.JSONDecodeError:
                logger.error(f"❌ Invalid JSON received from {connection_id}: {data}")
            except Exception as e:
                logger.error(f"❌ Error handling WebSocket message: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for {connection_id}: {e}")
    finally:
        websocket_manager.disconnect(connection_id)

async def handle_websocket_message(connection_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type", "")
    payload = message.get("payload", {})
    
    logger.debug(f"📨 WebSocket message from {connection_id}: {message_type}")
    
    if message_type == "ping":
        await websocket_manager.handle_ping(connection_id)
    
    elif message_type == "start_monitoring":
        await email_monitor.start_monitoring()
    
    elif message_type == "stop_monitoring":
        await email_monitor.stop_monitoring()
    
    elif message_type == "get_stats":
        try:
            stats = await db_manager.get_statistics()
            await websocket_manager.send_personal_message(connection_id, {
                "type": "STATISTICS_UPDATED",
                "payload": stats
            })
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
    
    elif message_type == "update_application_status":
        app_id = payload.get("app_id")
        new_status = payload.get("status")
        if app_id and new_status:
            await email_monitor.update_application_status(app_id, new_status)
    
    else:
        logger.warning(f"⚠️ Unknown message type: {message_type}")

@app.get("/api/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_connection_stats()

@app.post("/api/monitoring/start")
async def start_monitoring():
    """Start email monitoring"""
    await email_monitor.start_monitoring()
    return {"message": "Email monitoring started", "status": "success"}

@app.post("/api/monitoring/stop")
async def stop_monitoring():
    """Stop email monitoring"""
    await email_monitor.stop_monitoring()
    return {"message": "Email monitoring stopped", "status": "success"}

@app.get("/api/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    return {
        "isMonitoring": email_monitor.is_running,
        "connections": len(websocket_manager.active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )