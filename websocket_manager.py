"""
WebSocket Manager for dhii Mail
Handles real-time connections, message routing, and chat functionality
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    """Chat message model"""
    id: str
    sender: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class WebSocketConnection:
    """Individual WebSocket connection wrapper"""
    
    def __init__(self, websocket: WebSocket, client_id: str, session_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.session_id = session_id
        self.user_id: Optional[str] = None
        self.is_authenticated = False
        self.connected_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to this connection"""
        try:
            await self.websocket.send_text(json.dumps(message))
            self.last_activity = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {self.client_id}: {e}")
            return False
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message from this connection"""
        try:
            data = await self.websocket.receive_text()
            self.last_activity = datetime.now(timezone.utc)
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {self.client_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error receiving message from {self.client_id}: {e}")
            return None
    
    def update_auth_status(self, user_id: str, is_authenticated: bool):
        """Update authentication status"""
        self.user_id = user_id
        self.is_authenticated = is_authenticated

class WebSocketManager:
    """Central WebSocket connection manager"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.session_connections: Dict[str, List[str]] = {}  # session_id -> [client_ids]
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> [client_ids]
        self.message_history: Dict[str, List[ChatMessage]] = {}  # session_id -> messages
        
    async def connect(self, websocket: WebSocket, client_id: str, session_id: str) -> WebSocketConnection:
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        connection = WebSocketConnection(websocket, client_id, session_id)
        self.connections[client_id] = connection
        
        # Track by session
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(client_id)
        
        # Initialize message history for new sessions
        if session_id not in self.message_history:
            self.message_history[session_id] = []
        
        logger.info(f"WebSocket connected: {client_id} (session: {session_id})")
        
        # Send welcome message
        await connection.send_message({
            "type": "connection_established",
            "client_id": client_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return connection
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.connections:
            connection = self.connections[client_id]
            session_id = connection.session_id
            user_id = connection.user_id
            
            # Remove from session tracking
            if session_id in self.session_connections:
                self.session_connections[session_id].remove(client_id)
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]
                    # Keep message history for session
            
            # Remove from user tracking
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].remove(client_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove connection
            del self.connections[client_id]
            
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific client"""
        if client_id in self.connections:
            return await self.connections[client_id].send_message(message)
        return False
    
    async def send_to_session(self, session_id: str, message: Dict[str, Any], exclude_client: Optional[str] = None):
        """Send message to all clients in a session"""
        if session_id in self.session_connections:
            tasks = []
            for client_id in self.session_connections[session_id]:
                if client_id != exclude_client:
                    tasks.append(self.send_to_client(client_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a user"""
        if user_id in self.user_connections:
            tasks = []
            for client_id in self.user_connections[user_id]:
                tasks.append(self.send_to_client(client_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast(self, message: Dict[str, Any], exclude_client: Optional[str] = None):
        """Send message to all connected clients"""
        tasks = []
        for client_id in self.connections:
            if client_id != exclude_client:
                tasks.append(self.send_to_client(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Get message history for a session"""
        return self.message_history.get(session_id, [])
    
    def add_message(self, session_id: str, message: ChatMessage):
        """Add message to session history"""
        if session_id not in self.message_history:
            self.message_history[session_id] = []
        
        self.message_history[session_id].append(message)
        
        # Keep only last 100 messages to prevent memory issues
        if len(self.message_history[session_id]) > 100:
            self.message_history[session_id] = self.message_history[session_id][-100:]
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.connections),
            "active_sessions": len(self.session_connections),
            "active_users": len(self.user_connections),
            "connections_by_session": {
                session_id: len(client_ids) 
                for session_id, client_ids in self.session_connections.items()
            },
            "connections_by_user": {
                user_id: len(client_ids)
                for user_id, client_ids in self.user_connections.items()
            }
        }
    
    def update_user_authentication(self, client_id: str, user_id: str, is_authenticated: bool):
        """Update authentication status for a connection"""
        if client_id in self.connections:
            connection = self.connections[client_id]
            connection.update_auth_status(user_id, is_authenticated)
            
            # Track user connections
            if is_authenticated and user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = []
                if client_id not in self.user_connections[user_id]:
                    self.user_connections[user_id].append(client_id)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# Export the manager and models
__all__ = ['WebSocketManager', 'WebSocketConnection', 'ChatMessage', 'websocket_manager']