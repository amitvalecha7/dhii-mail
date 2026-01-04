#!/usr/bin/env python3
"""
Test script to verify unified AuthManager integration in auth_api.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test that auth_api.py can import and use the unified AuthManager
try:
    # Import the auth_api module
    import auth_api
    
    # Check if auth_manager is properly initialized
    if hasattr(auth_api, 'auth_manager'):
        print("✅ auth_api.py has unified auth_manager")
        
        # Check if create_access_token function works
        if hasattr(auth_api, 'create_access_token'):
            print("✅ create_access_token function available")
            
            # Test creating a token
            test_data = {"sub": "testuser", "user_id": "123"}
            try:
                token = auth_api.create_access_token(test_data)
                if token:
                    print(f"✅ Token created successfully: {token[:50]}...")
                    
                    # Verify the token using the auth_manager
                    user_data = auth_api.auth_manager.verify_token(token, "access")
                    if user_data:
                        print(f"✅ Token verified successfully: user_id={user_data.get('user_id')}")
                        print("✅ SUCCESS: Unified AuthManager integration working correctly")
                        sys.exit(0)
                    else:
                        print("❌ Token verification failed")
                        sys.exit(1)
                else:
                    print("❌ Token creation failed")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Token creation error: {e}")
                sys.exit(1)
        else:
            print("❌ create_access_token function not found")
            sys.exit(1)
    else:
        print("❌ auth_manager not found in auth_api.py")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Failed to import auth_api.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)