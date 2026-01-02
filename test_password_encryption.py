#!/usr/bin/env python3
"""
Test script for password encryption functionality in email manager
"""

import os
import sys
import tempfile
import sqlite3
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_manager import EmailManager, EmailAccount
from security_manager import security_manager

def test_password_encryption():
    """Test password encryption and decryption functionality"""
    print("Testing password encryption functionality...")
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize email manager with temporary database
        email_manager = EmailManager(db_path=temp_db_path)
        
        # Test data
        test_password = "test_password_123!@#"
        test_email = "test@example.com"
        
        # Test encryption
        print(f"Original password: {test_password}")
        encrypted_password = security_manager.encrypt_sensitive_data(test_password)
        print(f"Encrypted password: {encrypted_password[:50]}...")
        
        # Test decryption
        decrypted_password = security_manager.decrypt_sensitive_data(encrypted_password)
        print(f"Decrypted password: {decrypted_password}")
        
        # Verify encryption/decryption works correctly
        assert test_password == decrypted_password, "Password encryption/decryption failed!"
        print("✅ Password encryption/decryption test passed!")
        
        # Create test email account
        test_account = EmailAccount(
            user_id=1,
            email_address=test_email,
            display_name="Test User",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            smtp_username=test_email,
            smtp_password=test_password,
            smtp_use_tls=True,
            imap_server="imap.gmail.com",
            imap_port=993,
            imap_username=test_email,
            imap_password=test_password,
            imap_use_ssl=True,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            last_sync=None
        )
        
        # Add account to database
        account_id = email_manager.add_email_account(test_account)
        print(f"Added test account with ID: {account_id}")
        
        # Retrieve account and verify passwords are decrypted correctly
        accounts = email_manager.get_email_accounts(1)
        assert len(accounts) == 1, "Account retrieval failed!"
        
        retrieved_account = accounts[0]
        print(f"Retrieved account: {retrieved_account.email_address}")
        print(f"Retrieved SMTP password: {retrieved_account.smtp_password}")
        print(f"Retrieved IMAP password: {retrieved_account.imap_password}")
        
        # Verify passwords match
        assert retrieved_account.smtp_password == test_password, "SMTP password decryption failed!"
        assert retrieved_account.imap_password == test_password, "IMAP password decryption failed!"
        print("✅ Account password encryption/decryption test passed!")
        
        # Verify passwords are encrypted in database
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT smtp_password, imap_password FROM email_accounts WHERE id = ?", (account_id,))
        db_passwords = cursor.fetchone()
        conn.close()
        
        stored_smtp_password = db_passwords[0]
        stored_imap_password = db_passwords[1]
        
        print(f"Stored SMTP password (encrypted): {stored_smtp_password[:50]}...")
        print(f"Stored IMAP password (encrypted): {stored_imap_password[:50]}...")
        
        # Verify stored passwords are encrypted (should not match original)
        assert stored_smtp_password != test_password, "SMTP password not encrypted in database!"
        assert stored_imap_password != test_password, "IMAP password not encrypted in database!"
        
        # Verify stored passwords can be decrypted to original
        decrypted_smtp = security_manager.decrypt_sensitive_data(stored_smtp_password)
        decrypted_imap = security_manager.decrypt_sensitive_data(stored_imap_password)
        
        assert decrypted_smtp == test_password, "Stored SMTP password cannot be decrypted correctly!"
        assert decrypted_imap == test_password, "Stored IMAP password cannot be decrypted correctly!"
        
        print("✅ Database password encryption test passed!")
        print("✅ All password encryption tests passed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary database
        try:
            os.unlink(temp_db_path)
        except:
            pass

if __name__ == "__main__":
    success = test_password_encryption()
    if success:
        print("\n🎉 All tests passed! Password encryption is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)