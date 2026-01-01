#!/usr/bin/env python3
import imaplib
import ssl

def test_imap_auth():
    try:
        # Connect to IMAPS (secure IMAP)
        mail = imaplib.IMAP4_SSL('localhost', 993)
        
        # Try to login with test credentials
        # Note: Since we're using bcrypt, we need the actual password
        # Let's try with a known test password first
        try:
            mail.login('test@dhii.ai', 'test123')
            print("✓ Authentication successful!")
            mail.logout()
            return True
        except imaplib.IMAP4.error as e:
            print(f"✗ Authentication failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("Testing IMAP authentication...")
    test_imap_auth()