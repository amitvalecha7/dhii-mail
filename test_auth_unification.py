#!/usr/bin/env python3
"""
Test script to verify AuthManager unification in main.py
"""

import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_unification():
    """Test that main.py properly exports auth_manager for auth.py"""
    print("🧪 Testing AuthManager unification...")
    
    try:
        # Test importing main.py
        print("📦 Importing main.py...")
        import main
        print("✅ main.py imported successfully")
        
        # Check if auth_manager is exported
        if hasattr(main, 'auth_manager'):
            print("✅ auth_manager is exported from main.py")
            auth_manager = main.auth_manager
            print(f"✅ auth_manager type: {type(auth_manager)}")
            
            # Test that it's the same instance as what auth.py uses
            print("📦 Importing auth.py...")
            import auth
            auth_manager_from_auth = auth.get_auth_manager()
            
            if auth_manager is auth_manager_from_auth:
                print("✅ main.py and auth.py use the same AuthManager instance")
            else:
                print("❌ main.py and auth.py use different AuthManager instances")
                return False
                
        else:
            print("❌ auth_manager is not exported from main.py")
            return False
        
        # Test that we can create and verify tokens
        print("🔑 Testing token functionality...")
        import database
        db = database.get_db()
        
        # Get an existing user
        existing_users = db.execute_query("SELECT * FROM users LIMIT 1")
        if existing_users:
            test_user = existing_users[0]
            print(f"👤 Using user: {test_user['email']} (ID: {test_user['id']})")
            
            # Create token using auth_manager from main.py
            token = auth_manager.create_token(test_user['id'], 'access', ['read'])
            if token:
                print(f"✅ Token created: {token[:20]}...")
                
                # Verify token using the same auth_manager
                user_data = auth_manager.verify_token(token, 'access')
                if user_data and user_data.get('token_payload', {}).get('user_id') == test_user['id']:
                    print("✅ Token verification successful")
                else:
                    print("❌ Token verification failed")
                    return False
            else:
                print("❌ Token creation failed")
                return False
        else:
            print("❌ No existing users found")
            return False
        
        print("🎉 AuthManager unification test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Auth unification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auth_unification()
    sys.exit(0 if success else 1)