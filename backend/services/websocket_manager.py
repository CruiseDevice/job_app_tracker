import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept a new WebSocket connection and return connection ID"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        logger.info(f"✅ WebSocket connected: {connection_id}")
        logger.info(f"📊 Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(connection_id, {
            "type": "CONNECTION_STATUS",
            "payload": {
                "status": "connected",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return connection_id

    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]
            logger.info(f"❌ WebSocket disconnected: {connection_id}")
            logger.info(f"📊 Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, connection_id: str, message: dict):
        """Send a message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            logger.debug("📢 No WebSocket connections to broadcast to")
            return

        # Add timestamp to message
        message["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"📢 Broadcasting to {len(self.active_connections)} connections: {message['type']}")
        
        # Send to all connections
        disconnected_connections = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Error broadcasting to {connection_id}: {e}")
                disconnected_connections.append(connection_id)

        # Clean up failed connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)

    async def handle_ping(self, connection_id: str):
        """Handle ping message and respond with pong"""
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["last_ping"] = datetime.now()
            
        await self.send_personal_message(connection_id, {
            "type": "pong",
            "payload": {"timestamp": datetime.now().isoformat()}
        })

    def get_connection_stats(self) -> dict:
        """Get statistics about current connections"""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "id": conn_id,
                    "connected_at": metadata["connected_at"].isoformat(),
                    "last_ping": metadata["last_ping"].isoformat()
                }
                for conn_id, metadata in self.connection_metadata.items()
            ]
        }

# Global connection manager instance
manager = ConnectionManager()