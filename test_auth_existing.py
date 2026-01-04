#!/usr/bin/env python3
"""
Debug script to test auth functionality with existing user
"""

import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_auth_with_existing_user():
    """Debug auth functionality using existing user"""
    print("🔍 Testing auth with existing user...")
    
    try:
        # Import auth manager
        print("📦 Importing auth...")
        import auth
        manager = auth.get_auth_manager()
        print("✅ AuthManager imported successfully")
        
        # Get an existing user
        print("👤 Getting existing user...")
        import database
        db = database.get_db()
        
        existing_users = db.execute_query("SELECT * FROM users LIMIT 1")
        if not existing_users:
            print("❌ No existing users found")
            return False
            
        test_user = existing_users[0]
        print(f"✅ Found user: ID {test_user['id']}, email: {test_user['email']}")
        
        # Test token creation with the existing user
        print("🔑 Testing token creation...")
        try:
            token = manager.create_token(test_user['id'], 'access', ['read', 'write'])
            if token:
                print(f"✅ Token created successfully: {token[:30]}...")
                
                # Test verification
                print("🔍 Testing token verification...")
                user_data = manager.verify_token(token, 'access')
                if user_data:
                    print(f"✅ Token verification successful: user_id={user_data.get('user_id')}")
                    print(f"✅ Token data: {user_data}")
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
        
        print("🎉 All auth tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_auth_with_existing_user()
    sys.exit(0 if success else 1)