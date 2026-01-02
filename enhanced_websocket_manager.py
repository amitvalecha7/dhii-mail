"""
Enhanced WebSocket Manager for dhii Mail
Improved connection state management and error recovery
"""

import json
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import threading

logger = logging.getLogger(__name__)

class ConnectionState(BaseModel):
    """Connection state tracking"""
    connected: bool = False
    last_heartbeat: datetime
    connection_attempts: int = 0
    last_connection_error: Optional[str] = None
    reconnect_scheduled: bool = False

class ChatMessage(BaseModel):
    """Chat message model"""
    id: str
    sender: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class EnhancedWebSocketConnection:
    """Enhanced WebSocket connection wrapper with state management and error recovery"""
    
    def __init__(self, websocket: WebSocket, client_id: str, session_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.session_id = session_id
        self.user_id: Optional[str] = None
        self.is_authenticated = False
        self.connected_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.state = ConnectionState(
            connected=True,
            last_heartbeat=datetime.now(timezone.utc)
        )
        self.message_queue: List[Dict[str, Any]] = []
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.connection_timeout = 300  # 5 minutes
        self.heartbeat_interval = 30   # 30 seconds
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 1.0
        self.reconnect_backoff = 2.0
        
    async def start_heartbeat(self):
        """Start heartbeat monitoring"""
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
    async def stop_heartbeat(self):
        """Stop heartbeat monitoring"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
    
    async def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        try:
            while self.state.connected:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Send heartbeat ping
                try:
                    await self.send_message({
                        "type": "heartbeat_ping",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
                    # Wait for pong with timeout
                    pong_received = await self._wait_for_pong(timeout=10)
                    
                    if pong_received:
                        self.state.last_heartbeat = datetime.now(timezone.utc)
                        self.last_activity = datetime.now(timezone.utc)
                    else:
                        logger.warning(f"Heartbeat timeout for client {self.client_id}")
                        await self._handle_connection_failure("Heartbeat timeout")
                        break
                        
                except Exception as e:
                    logger.error(f"Heartbeat error for client {self.client_id}: {e}")
                    await self._handle_connection_failure(f"Heartbeat error: {str(e)}")
                    break
                    
                # Check for connection timeout
                time_since_activity = datetime.now(timezone.utc) - self.last_activity
                if time_since_activity.total_seconds() > self.connection_timeout:
                    logger.warning(f"Connection timeout for client {self.client_id}")
                    await self._handle_connection_failure("Connection timeout")
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"Heartbeat loop cancelled for client {self.client_id}")
        except Exception as e:
            logger.error(f"Unexpected error in heartbeat loop for client {self.client_id}: {e}")
    
    async def _wait_for_pong(self, timeout: int = 10) -> bool:
        """Wait for heartbeat pong response"""
        try:
            # This would need to be implemented with proper message handling
            # For now, we'll assume the connection is alive if we can send the ping
            return True
        except Exception:
            return False
    
    async def _handle_connection_failure(self, error_message: str):
        """Handle connection failure"""
        self.state.connected = False
        self.state.last_connection_error = error_message
        logger.error(f"Connection failure for client {self.client_id}: {error_message}")
        
        # Schedule reconnection if attempts remaining
        if self.state.connection_attempts < self.max_reconnect_attempts:
            self.state.reconnect_scheduled = True
            self.state.connection_attempts += 1
            delay = self.reconnect_delay * (self.reconnect_backoff ** (self.state.connection_attempts - 1))
            logger.info(f"Scheduling reconnection for client {self.client_id} in {delay} seconds")
            asyncio.create_task(self._schedule_reconnection(delay))
        else:
            logger.warning(f"Max reconnection attempts reached for client {self.client_id}")
            await self.close()
    
    async def _schedule_reconnection(self, delay: float):
        """Schedule reconnection after delay"""
        try:
            await asyncio.sleep(delay)
            if self.state.reconnect_scheduled:
                logger.info(f"Attempting reconnection for client {self.client_id}")
                # Reconnection logic would be implemented here
                # For now, we'll just close the connection
                await self.close()
        except asyncio.CancelledError:
            logger.info(f"Reconnection cancelled for client {self.client_id}")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to this connection with error handling"""
        if not self.state.connected:
            logger.warning(f"Attempting to send message to disconnected client {self.client_id}")
            # Queue message for when connection is restored
            self.message_queue.append(message)
            return False
            
        try:
            await self.websocket.send_text(json.dumps(message))
            self.last_activity = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {self.client_id}: {e}")
            # Queue message for retry
            self.message_queue.append(message)
            await self._handle_connection_failure(f"Send error: {str(e)}")
            return False
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message from this connection with error handling"""
        if not self.state.connected:
            return None
            
        try:
            data = await self.websocket.receive_text()
            message = json.loads(data)
            self.last_activity = datetime.now(timezone.utc)
            
            # Handle heartbeat pong
            if message.get("type") == "heartbeat_pong":
                return message
                
            return message
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {self.client_id}: {e}")
            await self.send_message({
                "type": "error",
                "message": "Invalid message format",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return None
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for client {self.client_id}")
            await self._handle_connection_failure("Client disconnected")
            return None
        except Exception as e:
            logger.error(f"Error receiving message from {self.client_id}: {e}")
            await self._handle_connection_failure(f"Receive error: {str(e)}")
            return None
    
    async def close(self):
        """Close connection cleanly"""
        self.state.connected = False
        await self.stop_heartbeat()
        
        try:
            if self.websocket.client_state.CONNECTED:
                await self.websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket for client {self.client_id}: {e}")
    
    def update_auth_status(self, user_id: str, is_authenticated: bool):
        """Update authentication status"""
        self.user_id = user_id
        self.is_authenticated = is_authenticated
        self.last_activity = datetime.now(timezone.utc)

class EnhancedWebSocketManager:
    """Enhanced WebSocket connection manager with state management and error recovery"""
    
    def __init__(self):
        self.connections: Dict[str, EnhancedWebSocketConnection] = {}
        self.session_connections: Dict[str, List[str]] = {}  # session_id -> [client_ids]
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> [client_ids]
        self.message_history: Dict[str, List[ChatMessage]] = {}  # session_id -> messages
        self.connection_stats: Dict[str, Any] = {
            "total_connections": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "reconnections": 0,
            "connection_errors": {}
        }
        self.cleanup_interval = 300  # 5 minutes
        self.max_session_age = 3600  # 1 hour
        self.cleanup_task = None  # Will be initialized when needed
        self._initialized = False
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        if self.cleanup_task is None:
            try:
                self.cleanup_task = asyncio.create_task(self._cleanup_loop())
                self._initialized = True
            except RuntimeError:
                # No event loop running, will be initialized later
                logger.debug("No event loop available for cleanup task initialization")
    
    def ensure_initialized(self):
        """Ensure the manager is properly initialized with event loop"""
        if not self._initialized and self.cleanup_task is None:
            self.start_cleanup_task()
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if hasattr(self, 'cleanup_task'):
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_old_connections()
                await self._cleanup_old_sessions()
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_connections(self):
        """Clean up old disconnected connections"""
        current_time = datetime.now(timezone.utc)
        disconnected_clients = []
        
        for client_id, connection in self.connections.items():
            if not connection.state.connected:
                time_since_disconnect = current_time - connection.last_activity
                if time_since_disconnect.total_seconds() > 300:  # 5 minutes
                    disconnected_clients.append(client_id)
        
        for client_id in disconnected_clients:
            await self._remove_connection(client_id)
            logger.info(f"Cleaned up old connection for client {client_id}")
    
    async def _cleanup_old_sessions(self):
        """Clean up old sessions"""
        current_time = datetime.now(timezone.utc)
        old_sessions = []
        
        for session_id, messages in self.message_history.items():
            if messages:
                last_message_time = messages[-1].timestamp
                time_since_last_message = current_time - last_message_time
                if time_since_last_message.total_seconds() > self.max_session_age:
                    old_sessions.append(session_id)
        
        for session_id in old_sessions:
            if session_id in self.message_history:
                del self.message_history[session_id]
            if session_id in self.session_connections:
                del self.session_connections[session_id]
            logger.info(f"Cleaned up old session {session_id}")
    
    async def connect(self, websocket: WebSocket, client_id: str, session_id: str) -> EnhancedWebSocketConnection:
        """Accept new WebSocket connection with enhanced error handling"""
        try:
            # Ensure manager is initialized
            self.ensure_initialized()
            
            await websocket.accept()
            self.connection_stats["total_connections"] += 1
            
            connection = EnhancedWebSocketConnection(websocket, client_id, session_id)
            self.connections[client_id] = connection
            
            # Track by session
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            self.session_connections[session_id].append(client_id)
            
            # Initialize message history for new sessions
            if session_id not in self.message_history:
                self.message_history[session_id] = []
            
            # Start heartbeat monitoring
            await connection.start_heartbeat()
            
            self.connection_stats["successful_connections"] += 1
            logger.info(f"WebSocket connected: {client_id} (session: {session_id})")
            
            # Send welcome message
            await connection.send_message({
                "type": "connection_established",
                "client_id": client_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "heartbeat_interval": connection.heartbeat_interval
            })
            
            return connection
            
        except Exception as e:
            self.connection_stats["failed_connections"] += 1
            self.connection_stats["connection_errors"][str(type(e).__name__)] = (
                self.connection_stats["connection_errors"].get(str(type(e).__name__), 0) + 1
            )
            logger.error(f"Failed to establish WebSocket connection for {client_id}: {e}")
            raise
    
    async def _remove_connection(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.connections:
            connection = self.connections[client_id]
            session_id = connection.session_id
            user_id = connection.user_id
            
            # Close connection cleanly
            await connection.close()
            
            # Remove from session tracking
            if session_id in self.session_connections:
                if client_id in self.session_connections[session_id]:
                    self.session_connections[session_id].remove(client_id)
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]
            
            # Remove from user tracking
            if user_id and user_id in self.user_connections:
                if client_id in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(client_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove connection
            del self.connections[client_id]
            
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def disconnect(self, client_id: str):
        """Disconnect WebSocket connection"""
        await self._remove_connection(client_id)
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific client with error handling"""
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
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get enhanced WebSocket connection statistics"""
        current_time = datetime.now(timezone.utc)
        
        # Calculate connection durations
        connection_durations = []
        for connection in self.connections.values():
            duration = (current_time - connection.connected_at).total_seconds()
            connection_durations.append(duration)
        
        # Calculate average connection duration
        avg_duration = sum(connection_durations) / len(connection_durations) if connection_durations else 0
        
        # Count connections by state
        active_connections = sum(1 for conn in self.connections.values() if conn.state.connected)
        reconnecting_connections = sum(1 for conn in self.connections.values() if conn.state.reconnect_scheduled)
        
        return {
            "total_connections": len(self.connections),
            "active_connections": active_connections,
            "reconnecting_connections": reconnecting_connections,
            "successful_connections": self.connection_stats["successful_connections"],
            "failed_connections": self.connection_stats["failed_connections"],
            "reconnections": self.connection_stats["reconnections"],
            "connection_errors": self.connection_stats["connection_errors"],
            "active_sessions": len(self.session_connections),
            "active_users": len(self.user_connections),
            "average_connection_duration": avg_duration,
            "connections_by_session": {
                session_id: len(client_ids) 
                for session_id, client_ids in self.session_connections.items()
            },
            "connections_by_user": {
                user_id: len(client_ids)
                for user_id, client_ids in self.user_connections.items()
            }
        }
    
    async def handle_heartbeat_response(self, client_id: str, timestamp: str):
        """Handle heartbeat response from client"""
        if client_id in self.connections:
            connection = self.connections[client_id]
            connection.state.last_heartbeat = datetime.fromisoformat(timestamp)
            logger.debug(f"Heartbeat response received from client {client_id}")

# Global enhanced WebSocket manager instance
enhanced_websocket_manager = EnhancedWebSocketManager()

# Export the manager and models
__all__ = ['EnhancedWebSocketManager', 'EnhancedWebSocketConnection', 'ChatMessage', 'ConnectionState', 'enhanced_websocket_manager']