#!/usr/bin/env python3
"""
Test script to verify AuthManager functionality in auth.py
"""

import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_manager_functionality():
    """Test that auth.py AuthManager works correctly"""
    print("🧪 Testing AuthManager functionality...")
    
    try:
        # Import only auth.py (no FastAPI dependencies in core functionality)
        print("📦 Importing auth.py...")
        import auth
        
        # Test get_auth_manager function
        print("🔍 Testing get_auth_manager()...")
        manager = auth.get_auth_manager()
        if manager is not None:
            print("✅ get_auth_manager() returns a valid AuthManager instance")
        else:
            print("❌ get_auth_manager() returns None")
            return False
            
        # Test get_auth function
        print("🔍 Testing get_auth()...")
        auth_from_get_auth = auth.get_auth()
        if auth_from_get_auth is not None:
            print("✅ get_auth() returns a valid AuthManager instance")
        else:
            print("❌ get_auth() returns None")
            return False
            
        # Verify they return the same instance
        if manager is auth_from_get_auth:
            print("✅ get_auth_manager() and get_auth() return the same instance")
        else:
            print("❌ get_auth_manager() and get_auth() return different instances")
            return False
            
        # Test token creation and verification
        print("🔑 Testing token creation and verification...")
        
        # Create a test user
        test_user = {
            "user_id": 123,
            "username": "test_user",
            "email": "test@example.com"
        }
        
        # Create token using the manager
        token = manager.create_token(test_user, 'access')
        print(f"✅ Token created: {token[:20]}...")
        
        # Verify token using the same manager
        verified_user = manager.verify_token(token, 'access')
        if verified_user and verified_user.get('user_id') == test_user['user_id']:
            print("✅ Token verification works correctly")
        else:
            print("❌ Token verification failed")
            return False
            
        print("🎉 All AuthManager functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auth_manager_functionality()
    sys.exit(0 if success else 1)