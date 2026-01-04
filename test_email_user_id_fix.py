#!/usr/bin/env python3
"""
Test script to verify EmailManager user_id fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_manager import EmailManager, EmailMessage
from datetime import datetime
import sqlite3
import tempfile
import json

# Mock security manager to avoid decryption issues
class MockSecurityManager:
    def encrypt_sensitive_data(self, data):
        return f"encrypted_{data}"
    
    def decrypt_sensitive_data(self, data):
        if data.startswith("encrypted_"):
            return data[10:]  # Remove "encrypted_" prefix
        return data

# Patch the security manager
import email_manager
email_manager.security_manager = MockSecurityManager()

def test_email_user_id_fix():
    """Test that user_id is properly passed to _save_sent_message"""
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create email manager
        email_manager_obj = EmailManager(db_path)
        
        # Create test user and account
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table (simplified for test)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        
        # Insert test user
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("testuser", "test@example.com"))
        test_user_id = cursor.lastrowid
        
        # Create email accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_address TEXT NOT NULL,
                display_name TEXT,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER DEFAULT 587,
                smtp_username TEXT NOT NULL,
                smtp_password TEXT NOT NULL,
                smtp_use_tls BOOLEAN DEFAULT 1,
                imap_server TEXT NOT NULL,
                imap_port INTEGER DEFAULT 993,
                imap_username TEXT NOT NULL,
                imap_password TEXT NOT NULL,
                imap_use_ssl BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insert test account
        cursor.execute("""
            INSERT INTO email_accounts (
                user_id, email_address, display_name, smtp_server, smtp_port,
                smtp_username, smtp_password, smtp_use_tls, imap_server, imap_port,
                imap_username, imap_password, imap_use_ssl, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_user_id, "test@example.com", "Test User", "smtp.gmail.com", 587,
            "test@example.com", "encrypted_password", True, "imap.gmail.com", 993,
            "test@example.com", "encrypted_password", True, True
        ))
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Test the _save_sent_message function directly
        message = EmailMessage(
            message_id="test-123",
            subject="Test Email",
            sender="test@example.com",
            recipient="recipient@example.com",
            body="Test email body",
            html_body="<p>Test email body</p>",
            date=datetime.now(),
            attachments=[],
            headers={},
            priority="normal",
            labels=["sent"]
        )
        
        # Call _save_sent_message directly with user_id
        email_manager_obj._save_sent_message(message, account_id, test_user_id)
        
        # Check if the message was saved with correct user_id
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, sender, recipient FROM email_messages WHERE message_id = ?", ("test-123",))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            saved_user_id, saved_sender, saved_recipient = result
            print(f"✅ Message saved with user_id={saved_user_id}, sender='{saved_sender}', recipient='{saved_recipient}'")
            
            if saved_user_id == test_user_id:
                print("✅ SUCCESS: user_id correctly passed to _save_sent_message")
                return True
            else:
                print(f"❌ FAIL: Expected user_id={test_user_id}, got user_id={saved_user_id}")
                return False
        else:
            print("❌ No message saved")
            return False
            
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass

if __name__ == "__main__":
    print("Testing EmailManager user_id fix...")
    success = test_email_user_id_fix()
    if success:
        print("\n✅ Test passed - user_id fix is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Test failed - user_id fix needs more work")
        sys.exit(1)