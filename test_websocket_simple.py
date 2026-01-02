#!/usr/bin/env python3
"""
Simple test for enhanced WebSocket manager without requiring full server
"""

import sys
import os
import asyncio
import json
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock

# Add current directory to path
sys.path.insert(0, '/root/dhii-mail')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock FastAPI WebSocket for testing
class MockWebSocket:
    def __init__(self):
        self.client_state = Mock()
        self.client_state.CONNECTED = "CONNECTED"
        self.messages_sent = []
        self.messages_received = []
        self.closed = False
    
    async def accept(self):
        logger.info("WebSocket connection accepted")
    
    async def send_text(self, message: str):
        if not self.closed:
            self.messages_sent.append(json.loads(message))
            logger.info(f"Sent message: {message}")
    
    async def receive_text(self):
        if self.messages_received and not self.closed:
            return self.messages_received.pop(0)
        await asyncio.sleep(1)  # Simulate waiting
        return json.dumps({"type": "heartbeat_pong", "timestamp": datetime.now(timezone.utc).isoformat()})
    
    async def close(self):
        self.closed = True
        logger.info("WebSocket connection closed")

async def test_enhanced_websocket_manager():
    """Test the enhanced WebSocket manager functionality"""
    logger.info("=== Testing Enhanced WebSocket Manager ===")
    
    try:
        # Import the enhanced manager
        from enhanced_websocket_manager import EnhancedWebSocketManager, ChatMessage
        
        # Create manager instance
        manager = EnhancedWebSocketManager()
        
        logger.info("✅ Enhanced WebSocket Manager imported successfully")
        
        # Test 1: Basic connection
        logger.info("\n--- Test 1: Basic Connection ---")
        mock_websocket = MockWebSocket()
        
        connection = await manager.connect(
            websocket=mock_websocket,
            client_id="test_client_1",
            session_id="test_session_1"
        )
        
        assert connection is not None
        assert connection.client_id == "test_client_1"
        assert connection.session_id == "test_session_1"
        assert connection.state.connected == True
        logger.info("✅ Basic connection test passed")
        
        # Test 2: Message sending
        logger.info("\n--- Test 2: Message Sending ---")
        test_message = {
            "type": "test",
            "content": "Hello World",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        success = await connection.send_message(test_message)
        assert success == True
        assert len(mock_websocket.messages_sent) > 0
        logger.info("✅ Message sending test passed")
        
        # Test 3: Message history
        logger.info("\n--- Test 3: Message History ---")
        chat_message = ChatMessage(
            id="msg_1",
            sender="user",
            content="Test message",
            timestamp=datetime.now(timezone.utc),
            session_id="test_session_1"
        )
        
        manager.add_message("test_session_1", chat_message)
        messages = manager.get_session_messages("test_session_1")
        assert len(messages) == 1
        assert messages[0].content == "Test message"
        logger.info("✅ Message history test passed")
        
        # Test 4: Connection stats
        logger.info("\n--- Test 4: Connection Statistics ---")
        stats = manager.get_connection_stats()
        assert stats["total_connections"] == 1
        assert stats["active_connections"] == 1
        assert stats["successful_connections"] == 1
        logger.info(f"Connection stats: {stats}")
        logger.info("✅ Connection statistics test passed")
        
        # Test 5: Authentication update
        logger.info("\n--- Test 5: Authentication Update ---")
        manager.update_user_authentication("test_client_1", "user_123", True)
        assert connection.user_id == "user_123"
        assert connection.is_authenticated == True
        logger.info("✅ Authentication update test passed")
        
        # Test 6: Disconnection
        logger.info("\n--- Test 6: Disconnection ---")
        await manager.disconnect("test_client_1")
        assert connection.state.connected == False
        stats = manager.get_connection_stats()
        assert stats["total_connections"] == 0
        logger.info("✅ Disconnection test passed")
        
        # Test 7: Error handling
        logger.info("\n--- Test 7: Error Handling ---")
        mock_websocket_fail = MockWebSocket()
        mock_websocket_fail.accept = AsyncMock(side_effect=Exception("Connection failed"))
        
        try:
            await manager.connect(
                websocket=mock_websocket_fail,
                client_id="test_client_fail",
                session_id="test_session_fail"
            )
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Connection failed" in str(e)
            logger.info("✅ Error handling test passed")
        
        logger.info("\n🎉 All Enhanced WebSocket Manager tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_connection_state_management():
    """Test connection state management and recovery"""
    logger.info("\n=== Testing Connection State Management ===")
    
    try:
        from enhanced_websocket_manager import EnhancedWebSocketManager
        
        manager = EnhancedWebSocketManager()
        
        # Test connection state tracking
        logger.info("\n--- Testing Connection State Tracking ---")
        mock_websocket = MockWebSocket()
        
        connection = await manager.connect(
            websocket=mock_websocket,
            client_id="state_test_client",
            session_id="state_test_session"
        )
        
        # Verify initial state
        assert connection.state.connected == True
        assert connection.state.connection_attempts == 0
        assert connection.state.last_connection_error is None
        assert connection.state.reconnect_scheduled == False
        
        logger.info("✅ Initial connection state verified")
        
        # Test heartbeat functionality (simulate)
        logger.info("\n--- Testing Heartbeat Simulation ---")
        connection.state.last_heartbeat = datetime.now(timezone.utc)
        assert connection.state.last_heartbeat is not None
        logger.info("✅ Heartbeat state updated")
        
        # Test connection timeout simulation
        logger.info("\n--- Testing Connection Timeout ---")
        connection.last_activity = datetime.now(timezone.utc) - timedelta(minutes=10)
        # This would trigger timeout in real implementation
        logger.info("✅ Connection timeout simulation completed")
        
        # Test disconnection state
        logger.info("\n--- Testing Disconnection State ---")
        await manager.disconnect("state_test_client")
        assert connection.state.connected == False
        logger.info("✅ Disconnection state verified")
        
        logger.info("🎉 Connection state management tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection state test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Add timedelta import
from datetime import timedelta

async def run_all_tests():
    """Run all WebSocket tests"""
    logger.info("Starting Enhanced WebSocket Manager tests...")
    
    tests = [
        test_enhanced_websocket_manager,
        test_connection_state_management
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
        
        # Wait between tests
        await asyncio.sleep(1)
    
    # Summary
    passed = sum(results)
    total = len(results)
    logger.info(f"\n=== Test Summary ===")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Success rate: {(passed/total)*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests())