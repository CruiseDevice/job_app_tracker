from importlib.resources import is_resource
import logging
from contextlib import asynccontextmanager
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from api.routes import applications, statistics, settings as route_settings, monitor
from database.database_manager import db_manager
from utils.logger import setup_logger
from agent.background_service import BackgroundService

# setup logging
logger = setup_logger(__name__, logging.INFO if settings.debug else logging.WARNING)


# websocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

# global connection manager
manager = ConnectionManager()

# background service
background_service = BackgroundService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Smart Job Tracker API...")

    try:
        db_manager.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # start background service in separate thread
    try:
        threading.Thread(target=background_service.start_monitoring, daemon=True).start()
        logger.info("Background service started")
    except Exception as e:
        logger.error(f"Failed to start background service: {e}")

    yield
    logger.info("Shutting down Smart Job Tracker API...")
    # TODO: background service stop monitoring
    logger.info("Shutting down Smart Job Tracker API...")
    background_service.stop_monitoring()

app = FastAPI(
    title="Smart Job Tracker API",
    description="Backend API for Smart Job Application Tracker",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(route_settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["monitor"])


# health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Smart Job Tracker API is running",
        "monitoring": background_service.is_running
    }


# websocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "message": "Smart Job Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )