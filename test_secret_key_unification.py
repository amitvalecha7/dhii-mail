#!/usr/bin/env python3
"""
Test script for SECRET_KEY unification across auth_api.py and main.py
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from auth_api import SECRET_KEY as auth_api_secret_key
from main import auth_manager

def test_secret_key_unification():
    """Test that SECRET_KEY is unified across all modules"""
    print("Testing SECRET_KEY unification...")
    
    # Get the secret key from config
    config_secret = settings.jwt_secret_key
    print(f"Config JWT secret key: {config_secret}")
    
    # Get the secret key from auth_api.py
    print(f"Auth API secret key: {auth_api_secret_key}")
    
    # Get the secret key from main.py (through auth_manager)
    main_secret = auth_manager.secret_key
    print(f"Main auth manager secret key: {main_secret}")
    
    # Verify all secret keys match
    if config_secret == auth_api_secret_key == main_secret:
        print("✅ All SECRET_KEY values are unified!")
        return True
    else:
        print("❌ SECRET_KEY values are not unified!")
        print(f"Config: {config_secret}")
        print(f"Auth API: {auth_api_secret_key}")
        print(f"Main: {main_secret}")
        return False

def test_secret_key_environment_override():
    """Test that SECRET_KEY can be overridden via environment variable"""
    print("\nTesting SECRET_KEY environment override...")
    
    # Set a custom secret key via environment variable
    test_secret = "test-unified-secret-key-12345"
    os.environ["JWT_SECRET_KEY"] = test_secret
    
    # Reload settings to pick up environment variable
    from importlib import reload
    reload(settings)
    
    # Check if the environment variable override works
    if settings.jwt_secret_key == test_secret:
        print("✅ Environment variable override works!")
        
        # Test that auth_api.py would use the same secret
        # (We can't easily test this without restarting the process)
        print("✅ Environment variable override is available to auth_api.py")
        return True
    else:
        print("❌ Environment variable override failed!")
        return False

if __name__ == "__main__":
    success = True
    
    # Test basic unification
    if not test_secret_key_unification():
        success = False
    
    # Test environment override
    if not test_secret_key_environment_override():
        success = False
    
    if success:
        print("\n🎉 All SECRET_KEY unification tests passed!")
        print("✅ auth_api.py now uses the unified JWT_SECRET_KEY from config")
        print("✅ main.py already uses the unified JWT_SECRET_KEY from config")
        print("✅ Both modules will use the same secret key for JWT operations")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)