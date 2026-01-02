#!/usr/bin/env python3
"""
Simple test to verify SECRET_KEY unification across modules
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_secret_key_unification():
    """Test that all modules use the same SECRET_KEY from config"""
    print("🧪 Testing SECRET_KEY unification...")
    
    # Test 1: Check that config provides the unified secret key
    try:
        from config import settings
        config_secret = settings.jwt_secret_key
        print(f"✅ Config provides JWT secret key: {config_secret[:10]}...")
    except Exception as e:
        print(f"❌ Failed to get JWT secret from config: {e}")
        return False
    
    # Test 2: Check that auth_api.py uses the config secret
    try:
        # Import auth_api module
        import auth_api
        auth_api_secret = auth_api.SECRET_KEY
        
        if auth_api_secret == config_secret:
            print(f"✅ auth_api.py uses unified secret key: {auth_api_secret[:10]}...")
        else:
            print(f"❌ auth_api.py uses different secret key!")
            print(f"   Config: {config_secret[:10]}...")
            print(f"   auth_api: {auth_api_secret[:10]}...")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check auth_api.py secret: {e}")
        return False
    
    # Test 3: Verify token creation uses the unified secret
    try:
        from auth_api import create_access_token
        import jwt
        from datetime import timedelta
        
        # Create a test token
        test_data = {"sub": "test_user", "exp": 1234567890}
        token = create_access_token(test_data)
        
        # Decode the token to verify it was created with the unified secret
        decoded = jwt.decode(token, config_secret, algorithms=["HS256"], options={"verify_exp": False})
        
        if decoded["sub"] == "test_user":
            print("✅ Token creation uses unified secret key")
        else:
            print("❌ Token creation doesn't use unified secret key")
            return False
            
    except Exception as e:
        print(f"❌ Failed to verify token creation: {e}")
        return False
    
    print("\n🎉 All SECRET_KEY unification tests passed!")
    return True

if __name__ == "__main__":
    success = test_secret_key_unification()
    sys.exit(0 if success else 1)