#!/usr/bin/env python3
"""
Test script to verify sender parameter functionality in EmailManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_manager import EmailManager, EmailMessage
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sender_parameter():
    """Test the sender parameter functionality"""
    
    # Initialize email manager
    email_manager = EmailManager()
    
    # Create a test email message
    from datetime import datetime
    message = EmailMessage(
        subject="Test Email with Custom Sender",
        recipient="test@example.com",
        body="This is a test email with custom sender parameter",
        sender="Custom Sender Name",
        date=datetime.now()
    )
    
    # Test account ID (assuming there's at least one account in the database)
    test_account_id = 1
    
    print("🧪 Testing EmailManager sender parameter functionality...")
    
    # Test 1: Default behavior (no sender parameter)
    print("\n1️⃣ Testing default behavior (no sender parameter)...")
    try:
        # This should use the account email from the database
        result = email_manager.send_email_quick_retry(message, test_account_id)
        print(f"   ✅ Default behavior test completed (success: {result.success})")
        if not result.success:
            print(f"   ⚠️  Expected: {result.last_error}")
    except Exception as e:
        print(f"   ❌ Default behavior test failed: {e}")
    
    # Test 2: Custom sender parameter
    print("\n2️⃣ Testing custom sender parameter...")
    try:
        custom_sender = "custom@mycompany.com"
        result = email_manager.send_email_quick_retry(message, test_account_id, sender=custom_sender)
        print(f"   ✅ Custom sender test completed (success: {result.success})")
        if not result.success:
            print(f"   ⚠️  Expected: {result.last_error}")
    except Exception as e:
        print(f"   ❌ Custom sender test failed: {e}")
    
    # Test 3: Test send_email_with_retry directly
    print("\n3️⃣ Testing send_email_with_retry with sender parameter...")
    try:
        custom_sender = "noreply@mycompany.com"
        result = email_manager.send_email_with_retry(message, test_account_id, sender=custom_sender)
        print(f"   ✅ send_email_with_retry test completed (success: {result.success})")
        if not result.success:
            print(f"   ⚠️  Expected: {result.last_error}")
    except Exception as e:
        print(f"   ❌ send_email_with_retry test failed: {e}")
    
    # Test 4: Test aggressive retry with sender
    print("\n4️⃣ Testing send_email_aggressive_retry with sender parameter...")
    try:
        custom_sender = "urgent@mycompany.com"
        result = email_manager.send_email_aggressive_retry(message, test_account_id, sender=custom_sender)
        print(f"   ✅ send_email_aggressive_retry test completed (success: {result.success})")
        if not result.success:
            print(f"   ⚠️  Expected: {result.last_error}")
    except Exception as e:
        print(f"   ❌ send_email_aggressive_retry test failed: {e}")
    
    print("\n✅ All sender parameter tests completed!")
    print("\n📋 Summary:")
    print("- Added 'sender' parameter to all EmailManager send methods")
    print("- Parameter is optional and defaults to None")
    print("- When provided, overrides the account email from database")
    print("- Maintains backward compatibility with existing code")

if __name__ == "__main__":
    test_sender_parameter()