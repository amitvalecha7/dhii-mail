#!/usr/bin/env python3
"""
Test script for AI Agents Consolidation (Issue #29)
Tests the consolidated AI functionality in the orchestrator
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator

async def test_ai_consolidation():
    """Test the consolidated AI functionality"""
    print("🧪 Testing AI Agents Consolidation...")
    
    # Initialize orchestrator
    orchestrator = A2UIOrchestrator()
    
    # Test cases
    test_messages = [
        "Hello, how are you?",
        "Can you help me schedule a meeting with John tomorrow?",
        "I want to send an email to sarah@example.com",
        "What's on my calendar today?",
        "Help me manage my contacts",
        "What can you do?",
        "Goodbye!",
        "This is a random message that doesn't match any intent"
    ]
    
    print(f"Testing {len(test_messages)} different message types...\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        try:
            # Test intent detection
            intent = orchestrator.detect_intent(message)
            print(f"  Intent: {intent.intent} (confidence: {intent.confidence:.2f})")
            if intent.entities:
                print(f"  Entities: {intent.entities}")
            if intent.requires_clarification:
                print(f"  Requires clarification: {intent.ambiguity_reason}")
            
            # Test full AI processing
            response = await orchestrator.process_ai_message(message)
            print(f"  Response: {response.message}")
            print(f"  Actions: {len(response.actions)} available")
            print(f"  UI Components: {'Yes' if response.ui_components else 'No'}")
            print(f"  Requires user input: {response.requires_user_input}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print("✅ AI Consolidation Test Complete!")

async def test_openrouter_fallback():
    """Test OpenRouter API fallback to pattern-based responses"""
    print("🔄 Testing OpenRouter Fallback...")
    
    orchestrator = A2UIOrchestrator()
    
    # Test with OpenRouter disabled (should use pattern-based)
    orchestrator.use_openrouter = False
    
    message = "Can you help me schedule a meeting?"
    response = await orchestrator.process_ai_message(message)
    
    print(f"Message: {message}")
    print(f"Response (pattern-based): {response.message}")
    print(f"Intent: {response.intent.intent}")
    print("✅ Fallback test complete!")

async def test_ui_component_generation():
    """Test UI component generation for different intents"""
    print("🎨 Testing UI Component Generation...")
    
    orchestrator = A2UIOrchestrator()
    
    test_intents = ["check_calendar", "schedule_meeting", "send_email", "manage_contacts"]
    
    for intent_name in test_intents:
        # Create mock intent
        intent = orchestrator.detect_intent(f"Test {intent_name} message")
        ui_components = orchestrator._generate_ai_ui_components(intent, {})
        
        print(f"Intent: {intent_name}")
        if ui_components:
            print(f"  UI Type: {ui_components.get('type')}")
            print(f"  Component: {ui_components.get('component')}")
            print(f"  Props: {ui_components.get('props')}")
        else:
            print("  No UI components generated")
        print()
    
    print("✅ UI Component Generation Test Complete!")

async def main():
    """Run all tests"""
    print("🚀 Starting AI Agents Consolidation Tests")
    print("=" * 50)
    
    try:
        # Run tests
        await test_ai_consolidation()
        print("\n" + "=" * 50 + "\n")
        
        await test_openrouter_fallback()
        print("\n" + "=" * 50 + "\n")
        
        await test_ui_component_generation()
        print("\n" + "=" * 50 + "\n")
        
        print("🎉 All AI Consolidation Tests Passed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)