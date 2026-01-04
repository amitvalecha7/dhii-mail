#!/usr/bin/env python3
"""
Detailed test to debug token verification issue
"""

import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_token_verification():
    """Debug token verification in detail"""
    print("🔍 Debugging token verification...")
    
    try:
        # Import main to get auth_manager
        import main
        auth_manager = main.auth_manager
        print("✅ Got auth_manager from main.py")
        
        # Get an existing user
        import database
        db = database.get_db()
        existing_users = db.execute_query("SELECT * FROM users LIMIT 1")
        if not existing_users:
            print("❌ No existing users found")
            return False
            
        test_user = existing_users[0]
        print(f"👤 Using user: {test_user['email']} (ID: {test_user['id']})")
        
        # Create token
        print("🔑 Creating token...")
        token = auth_manager.create_token(test_user['id'], 'access', ['read'])
        if not token:
            print("❌ Token creation failed")
            return False
            
        print(f"✅ Token created: {token[:50]}...")
        
        # Verify token step by step
        print("🔍 Verifying token...")
        
        # Check if token exists in database first
        print("📋 Checking if token exists in database...")
        import pyseto
        import json
        from datetime import datetime, timezone
        
        # Decode token to get token_id
        key = pyseto.Key.new(4, 'local', auth_manager.secret_key.encode('utf-8'))
        decoded = pyseto.decode(key, token.encode('utf-8'))
        payload = json.loads(decoded.payload.decode('utf-8'))
        token_id = payload['token_id']
        print(f"✅ Token payload: {payload}")
        print(f"✅ Token ID: {token_id}")
        
        # Check database for token
        db_token = db.execute_query(
            "SELECT * FROM auth_tokens WHERE token_id = ?",
            (token_id,)
        )
        if db_token:
            print(f"✅ Token found in database: {db_token[0]}")
        else:
            print("❌ Token not found in database")
            return False
        
        # Now try the actual verification
        print("🔍 Calling verify_token method...")
        user_data = auth_manager.verify_token(token, 'access')
        print(f"✅ verify_token returned: {user_data}")
        
        if user_data:
            print(f"✅ Token verification successful!")
            print(f"✅ User data: {user_data}")
            return True
        else:
            print("❌ Token verification returned None")
            return False
            
    except Exception as e:
        print(f"❌ Token verification debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_token_verification()
    sys.exit(0 if success else 1)