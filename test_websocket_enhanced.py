#!/usr/bin/env python3
"""
Test script for enhanced WebSocket connection handling
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime, timezone
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketTestClient:
    def __init__(self, client_id: str, server_url: str = "ws://localhost:8000"):
        self.client_id = client_id
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.messages_received = []
        self.heartbeat_count = 0
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            uri = f"{self.server_url}/ws/{self.client_id}"
            self.websocket = await websockets.connect(uri)
            self.connected = True
            logger.info(f"Client {self.client_id} connected to {uri}")
            
            # Wait for connection acknowledgment
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5)
            message = json.loads(response)
            logger.info(f"Connection response: {message}")
            
            return True
        except Exception as e:
            logger.error(f"Connection failed for client {self.client_id}: {e}")
            return False
    
    async def send_message(self, message_type: str, content: str, session_id: str = None):
        """Send message to server"""
        if not self.connected or not self.websocket:
            logger.error(f"Cannot send message - not connected")
            return False
            
        try:
            message = {
                "type": message_type,
                "message": content,
                "session_id": session_id or f"test_session_{self.client_id}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent message: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def receive_messages(self):
        """Receive messages from server"""
        try:
            while self.connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                self.messages_received.append(data)
                
                # Handle heartbeat
                if data.get("type") == "heartbeat_ping":
                    await self.send_heartbeat_pong()
                elif data.get("type") == "heartbeat_pong":
                    self.heartbeat_count += 1
                    logger.debug(f"Heartbeat pong received (count: {self.heartbeat_count})")
                else:
                    logger.info(f"Received message: {data}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for client {self.client_id}")
            self.connected = False
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            self.connected = False
    
    async def send_heartbeat_pong(self):
        """Send heartbeat pong response"""
        try:
            pong_message = {
                "type": "heartbeat_pong",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await self.websocket.send(json.dumps(pong_message))
            logger.debug(f"Sent heartbeat pong")
        except Exception as e:
            logger.error(f"Error sending heartbeat pong: {e}")
    
    async def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info(f"Client {self.client_id} disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def get_stats(self):
        """Get client statistics"""
        return {
            "client_id": self.client_id,
            "connected": self.connected,
            "messages_received": len(self.messages_received),
            "heartbeat_count": self.heartbeat_count
        }

async def test_basic_connection():
    """Test basic WebSocket connection"""
    logger.info("=== Testing Basic Connection ===")
    
    client = WebSocketTestClient("test_client_1")
    
    try:
        # Connect
        connected = await client.connect()
        if not connected:
            logger.error("Failed to connect")
            return False
        
        # Start receiving messages in background
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Send a test message
        await client.send_message("chat", "Hello, this is a test message")
        
        # Wait a bit to receive response
        await asyncio.sleep(3)
        
        # Check stats
        stats = client.get_stats()
        logger.info(f"Client stats: {stats}")
        
        # Disconnect
        await client.disconnect()
        receive_task.cancel()
        
        return stats["messages_received"] > 0
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

async def test_multiple_clients():
    """Test multiple concurrent clients"""
    logger.info("=== Testing Multiple Clients ===")
    
    clients = []
    
    try:
        # Create multiple clients
        for i in range(3):
            client = WebSocketTestClient(f"test_client_{i+1}")
            connected = await client.connect()
            if connected:
                clients.append(client)
                logger.info(f"Client {i+1} connected successfully")
        
        if not clients:
            logger.error("No clients connected")
            return False
        
        # Start receiving messages for all clients
        tasks = []
        for client in clients:
            task = asyncio.create_task(client.receive_messages())
            tasks.append(task)
        
        # Send messages from all clients
        for i, client in enumerate(clients):
            await client.send_message("chat", f"Message from client {i+1}")
        
        # Wait for responses
        await asyncio.sleep(3)
        
        # Check stats for all clients
        all_stats = []
        for client in clients:
            stats = client.get_stats()
            all_stats.append(stats)
            logger.info(f"Client {client.client_id} stats: {stats}")
        
        # Disconnect all clients
        for client in clients:
            await client.disconnect()
        
        # Cancel receive tasks
        for task in tasks:
            task.cancel()
        
        # Check if all clients received messages
        success = all(stats["messages_received"] > 0 for stats in all_stats)
        logger.info(f"Multiple clients test: {'PASSED' if success else 'FAILED'}")
        return success
        
    except Exception as e:
        logger.error(f"Multiple clients test failed: {e}")
        return False

async def test_heartbeat_handling():
    """Test heartbeat handling"""
    logger.info("=== Testing Heartbeat Handling ===")
    
    client = WebSocketTestClient("heartbeat_test_client")
    
    try:
        # Connect
        connected = await client.connect()
        if not connected:
            return False
        
        # Start receiving messages
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Wait for heartbeats
        await asyncio.sleep(35)  # Wait for at least one heartbeat
        
        # Check heartbeat count
        stats = client.get_stats()
        logger.info(f"Heartbeat stats: {stats}")
        
        # Disconnect
        await client.disconnect()
        receive_task.cancel()
        
        return stats["heartbeat_count"] > 0
        
    except Exception as e:
        logger.error(f"Heartbeat test failed: {e}")
        return False

async def test_connection_recovery():
    """Test connection recovery after disconnection"""
    logger.info("=== Testing Connection Recovery ===")
    
    client = WebSocketTestClient("recovery_test_client")
    
    try:
        # First connection
        connected = await client.connect()
        if not connected:
            return False
        
        # Start receiving messages
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Send initial message
        await client.send_message("chat", "First message")
        await asyncio.sleep(2)
        
        # Force disconnect
        await client.disconnect()
        receive_task.cancel()
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Reconnect
        connected = await client.connect()
        if not connected:
            return False
        
        # Start receiving messages again
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Send message after reconnection
        await client.send_message("chat", "Message after reconnection")
        await asyncio.sleep(3)
        
        # Check stats
        stats = client.get_stats()
        logger.info(f"Recovery stats: {stats}")
        
        # Disconnect
        await client.disconnect()
        receive_task.cancel()
        
        return stats["messages_received"] >= 2
        
    except Exception as e:
        logger.error(f"Recovery test failed: {e}")
        return False

async def run_all_tests():
    """Run all WebSocket tests"""
    logger.info("Starting WebSocket connection handling tests...")
    
    tests = [
        test_basic_connection,
        test_multiple_clients,
        test_heartbeat_handling,
        test_connection_recovery
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
            logger.info(f"Test {test.__name__}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
        
        # Wait between tests
        await asyncio.sleep(2)
    
    # Summary
    passed = sum(results)
    total = len(results)
    logger.info(f"\n=== Test Summary ===")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Success rate: {(passed/total)*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    # Check if server is running
    import urllib.request
    import urllib.error
    
    try:
        urllib.request.urlopen("http://localhost:8000/health", timeout=2)
        logger.info("Server is running, starting tests...")
        asyncio.run(run_all_tests())
    except urllib.error.URLError:
        logger.error("Server is not running. Please start the server first:")
        logger.error("python3 main.py")
        exit(1)
    except Exception as e:
        logger.error(f"Error checking server status: {e}")
        logger.info("Assuming server is running, starting tests...")
        asyncio.run(run_all_tests())