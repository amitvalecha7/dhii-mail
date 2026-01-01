#!/usr/bin/env python3
"""
Test script for WebSocket AI integration
Tests real-time chat with AI engine through WebSocket connection
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_ai_chat():
    """Test WebSocket AI chat functionality"""
    
    uri = "ws://localhost:8004/ws/test_client_001"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Wait for initial system message
            system_message = await websocket.recv()
            logger.info(f"System message: {json.loads(system_message)}")
            
            # Test messages
            test_messages = [
                "Hello, who are you?",
                "Can you help me schedule a meeting?",
                "I want to send an email to john@example.com",
                "What's on my calendar today?",
                "Create a video conference room for my team"
            ]
            
            for message in test_messages:
                logger.info(f"\n--- Testing message: '{message}' ---")
                
                # Send user message
                chat_request = {
                    "message": message,
                    "session_id": "test_session_001",
                    "message_type": "text",
                    "metadata": {"test": True}
                }
                
                await websocket.send(json.dumps(chat_request))
                logger.info(f"Sent: {message}")
                
                # Wait for AI response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                logger.info(f"AI Response: {response_data.get('message', 'No message')}")
                logger.info(f"Intent: {response_data.get('intent', 'unknown')}")
                logger.info(f"Confidence: {response_data.get('confidence', 0)}")
                
                if response_data.get('actions'):
                    logger.info(f"Available actions: {[action['label'] for action in response_data['actions']]}")
                
                if response_data.get('ui_components'):
                    logger.info(f"UI components: {response_data['ui_components'].get('type', 'none')}")
                
                # Small delay between messages
                await asyncio.sleep(1)
            
            logger.info("\n--- Test completed successfully ---")
            
    except websockets.exceptions.ConnectionClosed:
        logger.error("WebSocket connection closed unexpectedly")
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")

async def test_authenticated_chat():
    """Test WebSocket chat with authentication"""
    
    uri = "ws://localhost:8004/ws/authenticated_client"
    
    try:
        # First, get an access token (you'll need to modify this based on your auth system)
        # For now, we'll use a mock token
        mock_token = "mock_access_token_for_testing"
        
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server (authenticated)")
            
            # Wait for initial system message
            system_message = await websocket.recv()
            logger.info(f"System message: {json.loads(system_message)}")
            
            # Test authenticated message
            chat_request = {
                "message": "Show me my email summary",
                "session_id": "auth_session_001", 
                "access_token": mock_token,
                "message_type": "text"
            }
            
            await websocket.send(json.dumps(chat_request))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            logger.info(f"Authenticated AI Response: {response_data.get('message', 'No message')}")
            logger.info(f"Session authenticated: {response_data.get('metadata', {}).get('authenticated', False)}")
            
    except Exception as e:
        logger.error(f"Authenticated chat test failed: {e}")

async def test_error_handling():
    """Test error handling in WebSocket chat"""
    
    uri = "ws://localhost:8004/ws/error_test_client"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server (error testing)")
            
            # Wait for initial system message
            await websocket.recv()
            
            # Test invalid message format
            invalid_message = {"invalid": "format"}  # Missing required fields
            await websocket.send(json.dumps(invalid_message))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            
            logger.info(f"Error response: {response_data}")
            
            # Test empty message
            empty_message = {
                "message": "",
                "session_id": "error_session",
                "message_type": "text"
            }
            
            await websocket.send(json.dumps(empty_message))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            logger.info(f"Empty message response: {response_data.get('message', 'No message')}")
            
    except Exception as e:
        logger.error(f"Error handling test failed: {e}")

async def main():
    """Run all WebSocket AI tests"""
    logger.info("Starting WebSocket AI integration tests...")
    
    # Wait a bit for the server to be ready
    await asyncio.sleep(2)
    
    try:
        # Test basic AI chat
        logger.info("=== Test 1: Basic AI Chat ===")
        await test_websocket_ai_chat()
        
        # Test authenticated chat
        logger.info("\n=== Test 2: Authenticated Chat ===")
        await test_authenticated_chat()
        
        # Test error handling
        logger.info("\n=== Test 3: Error Handling ===")
        await test_error_handling()
        
        logger.info("\n✅ All WebSocket AI tests completed!")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())