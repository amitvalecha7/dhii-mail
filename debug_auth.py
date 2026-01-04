#!/usr/bin/env python3
"""
Debug script to test database and auth functionality
"""

import os
import sys
import json

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_auth_and_db():
    """Debug auth and database functionality"""
    print("🔍 Debugging auth and database...")
    
    try:
        # Import database first
        print("📦 Importing database...")
        import database
        db = database.get_db()
        print("✅ Database imported successfully")
        
        # Test database connection
        print("🔍 Testing database connection...")
        result = db.execute_query("SELECT 1")
        print(f"✅ Database connection works: {result}")
        
        # Check if auth_tokens table exists
        print("🔍 Checking auth_tokens table...")
        try:
            result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_tokens'")
            if result:
                print("✅ auth_tokens table exists")
                
                # Check table schema
                schema = db.execute_query("PRAGMA table_info(auth_tokens)")
                print("📋 auth_tokens schema:")
                for column in schema:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("❌ auth_tokens table does not exist")
                return False
        except Exception as e:
            print(f"❌ Error checking auth_tokens table: {e}")
            return False
        
        # Test JSON storage
        print("🔍 Testing JSON storage...")
        test_scopes = json.dumps(['read', 'write'])
        print(f"Test scopes JSON: {test_scopes}")
        
        # Try to insert a test record
        print("🔍 Testing token insertion...")
        try:
            from datetime import datetime, timezone, timedelta
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            
            result = db.execute_update(
                """INSERT INTO auth_tokens 
                   (user_id, token_id, token_hash, purpose, scopes, expires_at) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (999, 'test_token_id', 'test_hash', 'access', test_scopes, expires_at)
            )
            print(f"✅ Test token insertion successful, rows affected: {result}")
            
            # Clean up
            db.execute_update("DELETE FROM auth_tokens WHERE user_id = 999")
            print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Token insertion failed: {e}")
            return False
        
        # Now test auth manager
        print("📦 Importing auth...")
        import auth
        manager = auth.get_auth_manager()
        print("✅ AuthManager imported successfully")
        
        # Test token creation with a simple user
        print("🔍 Testing token creation...")
        try:
            token = manager.create_token(999, 'access', ['read', 'write'])
            if token:
                print(f"✅ Token created successfully: {token[:20]}...")
                
                # Test verification
                print("🔍 Testing token verification...")
                user_data = manager.verify_token(token, 'access')
                if user_data:
                    print(f"✅ Token verification successful: {user_data}")
                else:
                    print("❌ Token verification failed")
                    return False
                    
            else:
                print("❌ Token creation failed")
                return False
                
        except Exception as e:
            print(f"❌ Token creation/verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("🎉 All debug tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_auth_and_db()
    sys.exit(0 if success else 1)