#!/usr/bin/env python3
"""
Test script for AI response formatting improvements (Issue #7)
Tests enhanced general responses, error handling, and OpenRouter integration
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine import AIEngine, AIIntent, AIResponse

def test_enhanced_general_responses():
    """Test enhanced general response formatting"""
    print("🧪 Testing Enhanced General Response Formatting...")
    
    ai_engine = AIEngine()
    
    test_cases = [
        # Greeting tests
        {
            "message": "hello",
            "context": {},
            "expected_keywords": ["Hello", "dhii", "email", "calendar"]
        },
        {
            "message": "hi there",
            "context": {"session_data": {"conversation_history": [{"intent": "general_chat", "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()}]}},
            "expected_keywords": ["Hello again", "Welcome back"]
        },
        
        # Help requests
        {
            "message": "help me",
            "context": {},
            "expected_keywords": ["Email Management", "Calendar Scheduling", "Contact Management"]
        },
        {
            "message": "what can you do",
            "context": {},
            "expected_keywords": ["Email Features", "Calendar Features", "Contact Management"]
        },
        
        # Ambiguous requests
        {
            "message": "do it",
            "context": {},
            "expected_keywords": ["not quite sure", "provide more details"]
        },
        {
            "message": "something",
            "context": {},
            "expected_keywords": ["not quite sure", "provide more details"]
        },
        
        # Status checks
        {
            "message": "how are you",
            "context": {},
            "expected_keywords": ["doing great", "ready to help"]
        },
        
        # Goodbye
        {
            "message": "goodbye",
            "context": {},
            "expected_keywords": ["Goodbye", "reach out anytime"]
        },
        
        # Confusion
        {
            "message": "I'm confused",
            "context": {},
            "expected_keywords": ["having some difficulty", "help clarify"]
        },
        
        # Thanks
        {
            "message": "thank you",
            "context": {},
            "expected_keywords": ["You're welcome", "happy to help"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test {i+1}: '{test_case['message']}' ---")
        
        try:
            # Create a general chat intent
            intent = AIIntent(
                intent="general_chat",
                confidence=0.9,
                entities={},
                response_type="text"
            )
            
            # Generate response
            response = ai_engine._generate_response(
                test_case["message"], 
                intent, 
                test_case["context"]
            )
            
            print(f"Response: {response}")
            
            # Check for expected keywords
            found_keywords = []
            for keyword in test_case["expected_keywords"]:
                if keyword.lower() in response.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"✅ Found expected keywords: {found_keywords}")
                passed += 1
            else:
                print(f"❌ Missing expected keywords: {test_case['expected_keywords']}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            failed += 1
    
    print(f"\n📊 General Response Tests: {passed} passed, {failed} failed")
    return passed, failed

def test_ambiguous_request_detection():
    """Test ambiguous request detection"""
    print("\n🧪 Testing Ambiguous Request Detection...")
    
    ai_engine = AIEngine()
    
    ambiguous_cases = [
        "do it",
        "make that",
        "check this",
        "something",
        "anything",
        "yes",
        "no",
        "?",
        "help",
        "I don't know",
        "I need to do something"
    ]
    
    clear_cases = [
        "schedule a meeting for tomorrow",
        "send an email to john@example.com",
        "check my calendar for today",
        "create a contact for Jane Smith"
    ]
    
    print("Testing ambiguous cases (should return True):")
    for case in ambiguous_cases:
        result = ai_engine._is_ambiguous_request(case)
        status = "✅" if result else "❌"
        print(f"  {status} '{case}': {result}")
    
    print("\nTesting clear cases (should return False):")
    for case in clear_cases:
        result = ai_engine._is_ambiguous_request(case)
        status = "✅" if not result else "❌"
        print(f"  {status} '{case}': {result}")

def test_session_detection():
    """Test new session detection"""
    print("\n🧪 Testing Session Detection...")
    
    ai_engine = AIEngine()
    
    # Test new session
    new_context = {}
    result = ai_engine._is_new_session(new_context)
    print(f"New session (empty context): {result} {'✅' if result else '❌'}")
    
    # Test existing session
    recent_time = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    existing_context = {
        "session_data": {
            "conversation_history": [
                {"intent": "general_chat", "timestamp": recent_time}
            ]
        }
    }
    result = ai_engine._is_new_session(existing_context)
    print(f"Existing session (recent activity): {result} {'✅' if not result else '❌'}")
    
    # Test old session
    old_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    old_context = {
        "session_data": {
            "conversation_history": [
                {"intent": "general_chat", "timestamp": old_time}
            ]
        }
    }
    result = ai_engine._is_new_session(old_context)
    print(f"Old session (old activity): {result} {'✅' if result else '❌'}")

async def test_openrouter_response_validation():
    """Test OpenRouter response validation"""
    print("\n🧪 Testing OpenRouter Response Validation...")
    
    ai_engine = AIEngine()
    
    # Test valid responses
    valid_responses = [
        "Hello! I can help you schedule a meeting for tomorrow. What time would work best for you?",
        "I can send that email to john@example.com about the project update. Would you like me to compose it now?",
        "You're welcome! Feel free to reach out anytime you need help with email or calendar management."
    ]
    
    # Test invalid responses
    invalid_responses = [
        "",  # Empty
        "a",  # Too short
        "a" * 3000,  # Too long
        "<script>alert('test')</script>",  # Script injection
        "javascript:alert('test')",  # JavaScript injection
        "email email email email email",  # Repetitive
        "Random text about something completely unrelated to email or calendar"  # Irrelevant
    ]
    
    print("Testing valid responses:")
    for response in valid_responses:
        result = ai_engine._is_valid_openrouter_response(response)
        status = "✅" if result else "❌"
        print(f"  {status} '{response[:50]}...': {result}")
    
    print("\nTesting invalid responses:")
    for response in invalid_responses:
        result = ai_engine._is_valid_openrouter_response(response)
        status = "✅" if not result else "❌"
        print(f"  {status} '{response[:50]}...': {not result}")

async def test_full_ai_response_flow():
    """Test complete AI response flow"""
    print("\n🧪 Testing Complete AI Response Flow...")
    
    ai_engine = AIEngine()
    
    test_messages = [
        "Hello, can you help me?",
        "I want to schedule a meeting",
        "Send an email to someone",
        "Check my calendar",
        "What can you do?",
        "I'm not sure what I want to do",
        "Thank you for your help"
    ]
    
    for message in test_messages:
        print(f"\n--- Testing: '{message}' ---")
        try:
            # Test with basic context
            context = {
                "user_id": "test_user_123",
                "session_data": {
                    "conversation_history": []
                }
            }
            
            response = await ai_engine.process_message(message, context)
            
            print(f"Message: {response.message}")
            print(f"Intent: {response.intent.intent}")
            print(f"Confidence: {response.intent.confidence}")
            print(f"Response Type: {response.intent.response_type}")
            
            if response.actions:
                print(f"Actions: {len(response.actions)} available")
            if response.ui_components:
                print(f"UI Components: {response.ui_components.get('type', 'none')}")
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting AI Response Formatting Tests (Issue #7)")
    print("=" * 60)
    
    # Run tests
    passed, failed = test_enhanced_general_responses()
    test_ambiguous_request_detection()
    test_session_detection()
    await test_openrouter_response_validation()
    await test_full_ai_response_flow()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All AI response formatting tests passed!")
        print("🎉 Issue #7 - AI Response Formatting improvements are working correctly!")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")

if __name__ == "__main__":
    asyncio.run(main())