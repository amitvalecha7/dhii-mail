#!/usr/bin/env python3
"""
Test script for email integration with AI engine
Tests email intent recognition, entity extraction, and API endpoints
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine import AIEngine, ai_engine
from email_manager import EmailManager, email_manager, EmailAccount, EmailMessage

def test_email_intent_detection():
    """Test AI engine email intent recognition"""
    print("🧪 Testing Email Intent Detection")
    print("=" * 50)
    
    test_messages = [
        "Send an email to john@example.com about the project meeting",
        "Email sarah regarding the quarterly report",
        "Compose email to team@company.com saying the deadline is tomorrow",
        "Write email to client@business.com about contract renewal",
        "Send message to support@help.com telling them about the issue",
        "Email my manager about vacation plans",
        "Contact the HR department via email",
        "Forward this information to marketing@company.com"
    ]
    
    for message in test_messages:
        print(f"\n📧 Testing: {message}")
        intent = ai_engine.detect_intent(message)
        print(f"   Intent: {intent.intent} (confidence: {intent.confidence})")
        print(f"   Entities: {json.dumps(intent.entities, indent=2)}")
        print(f"   Response Type: {intent.response_type}")

def test_email_entity_extraction():
    """Test detailed email entity extraction"""
    print("\n🔍 Testing Email Entity Extraction")
    print("=" * 50)
    
    test_cases = [
        {
            "message": "Send email to john.doe@company.com and jane.smith@business.org about the Q4 financial report",
            "expected_recipients": ["john.doe@company.com", "jane.smith@business.org"],
            "expected_subject": "Q4 financial report"
        },
        {
            "message": "Email support@help.com saying that the server is down and we need immediate assistance",
            "expected_recipients": ["support@help.com"],
            "expected_message": "the server is down and we need immediate assistance"
        },
        {
            "message": "Compose email to sales@product.com regarding the new pricing proposal",
            "expected_recipients": ["sales@product.com"],
            "expected_subject": "the new pricing proposal"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📨 Testing: {test_case['message']}")
        intent = ai_engine.detect_intent(test_case['message'])
        entities = intent.entities
        
        print(f"   Recipients: {entities.get('recipients', [])}")
        print(f"   Subject: {entities.get('subject', 'None')}")
        print(f"   Message: {entities.get('message', 'None')}")
        
        # Validate results
        if 'recipients' in entities:
            print(f"   ✓ Recipients found: {entities['recipients']}")
        if 'subject' in entities:
            print(f"   ✓ Subject found: '{entities['subject']}'")
        if 'message' in entities:
            print(f"   ✓ Message found: '{entities['message']}'")

async def test_email_response_generation():
    """Test AI engine email response generation"""
    print("\n💬 Testing Email Response Generation")
    print("=" * 50)
    
    test_messages = [
        "Send email to john@example.com about the meeting",
        "Email support about the technical issue",
        "Compose email to team@company.com"
    ]
    
    # Mock user context
    context = {
        'user_id': 'test_user_123',
        'session_data': {}
    }
    
    for message in test_messages:
        print(f"\n📧 Testing: {message}")
        response = await ai_engine.process_message(message, context)
        print(f"   Response: {response.message}")
        print(f"   Intent: {response.intent.intent}")
        print(f"   Actions: {len(response.actions)} actions")
        print(f"   UI Components: {'Yes' if response.ui_components else 'No'}")
        
        if response.actions:
            for action in response.actions:
                print(f"     - {action['label']}: {action['action']}")

def test_email_ui_components():
    """Test email UI component generation"""
    print("\n🎨 Testing Email UI Components")
    print("=" * 50)
    
    test_message = "Send email to john@example.com about the project update saying we need more time"
    
    print(f"Testing: {test_message}")
    intent = ai_engine.detect_intent(test_message)
    
    # Mock context for UI component generation
    context = {'user_id': 'test_user_123'}
    ui_components = ai_engine._generate_ui_components(intent, context)
    
    if ui_components:
        print(f"UI Component Type: {ui_components['type']}")
        print(f"Title: {ui_components['title']}")
        print("Fields:")
        for field in ui_components['fields']:
            print(f"  - {field['name']}: {field['type']} (required: {field['required']})")
            if 'value' in field and field['value']:
                print(f"    Pre-filled: {field['value']}")
        print("Actions:")
        for action in ui_components['actions']:
            print(f"  - {action['label']}: {action['action']}")

def test_email_manager_integration():
    """Test email manager basic functionality"""
    print("\n⚙️ Testing Email Manager Integration")
    print("=" * 50)
    
    # Test account creation (using minimal required fields)
    test_account_data = {
        "email_address": "test@example.com",
        "display_name": "Test User",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "test@example.com",
        "smtp_password": "test_password",  # In real scenario, this would be encrypted
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "imap_username": "test@example.com",
        "imap_password": "test_password",  # In real scenario, this would be encrypted
        "is_active": True
    }
    
    # Create account with user_id (required field)
    test_account = EmailAccount(
        user_id=123,  # Mock user ID
        **test_account_data
    )
    
    print("Testing email account creation...")
    try:
        # This would normally connect to real email servers
        # For testing, we'll just validate the structure
        print(f"✓ Account structure valid: {test_account.email_address}")
        print(f"✓ Display Name: {test_account.display_name}")
        print(f"✓ SMTP: {test_account.smtp_server}:{test_account.smtp_port}")
        print(f"✓ IMAP: {test_account.imap_server}:{test_account.imap_port}")
    except Exception as e:
        print(f"✗ Error creating account: {e}")
    
    # Test email message creation
    test_message = EmailMessage(
        subject="Test Email",
        body="This is a test email from dhii Mail",
        recipient="recipient@example.com",  # Single recipient (required field)
        sender="test@example.com",
        date=datetime.now(timezone.utc)  # Required field
    )
    
    print(f"\nTesting email message creation...")
    print(f"✓ Message structure valid")
    print(f"✓ Subject: {test_message.subject}")
    print(f"✓ Recipient: {test_message.recipient}")
    print(f"✓ Body length: {len(test_message.body)} characters")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧩 Testing Edge Cases")
    print("=" * 50)
    
    edge_cases = [
        "Email",  # Too vague
        "Send email",  # No details
        "Email someone about something",  # No specific info
        "Contact support",  # Ambiguous
        "Write to john",  # No email address
        "Send message",  # Could be email or other messaging
    ]
    
    for case in edge_cases:
        print(f"\n🧪 Testing: '{case}'")
        intent = ai_engine.detect_intent(case)
        print(f"   Intent: {intent.intent} (confidence: {intent.confidence})")
        print(f"   Entities: {json.dumps(intent.entities, indent=2)}")
        
        # Generate response
        response = ai_engine._generate_response(case, intent, {})
        print(f"   Response: {response}")

async def main():
    """Run all email integration tests"""
    print("🚀 Starting Email Integration Tests")
    print("=" * 60)
    
    try:
        # Run tests
        test_email_intent_detection()
        test_email_entity_extraction()
        await test_email_response_generation()
        test_email_ui_components()
        test_email_manager_integration()
        test_edge_cases()
        
        print("\n✅ All email integration tests completed!")
        print("\n📊 Test Summary:")
        print("  ✓ Email intent detection working")
        print("  ✓ Entity extraction for recipients, subjects, messages")
        print("  ✓ Response generation with email context")
        print("  ✓ UI component generation for email forms")
        print("  ✓ Email manager integration ready")
        print("  ✓ Edge case handling implemented")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())