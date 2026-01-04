#!/usr/bin/env python3
"""
Debug script to test database and auth functionality with proper user creation
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
        
        # Import auth manager
        print("📦 Importing auth...")
        import auth
        manager = auth.get_auth_manager()
        print("✅ AuthManager imported successfully")
        
        # Create a test user first
        print("👤 Creating test user...")
        test_user = manager.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        
        if not test_user:
            # User might already exist, try to get existing user
            print("👤 Test user might already exist, trying to get existing user...")
            existing_users = db.execute_query("SELECT * FROM users WHERE email = ?", ("test@example.com",))
            if existing_users:
                test_user = existing_users[0]
                print(f"✅ Found existing test user with ID: {test_user['id']}")
            else:
                print("❌ Failed to create or find test user")
                return False
        else:
            print(f"✅ Test user created with ID: {test_user['id']}")
        
        # Test token creation with the test user
        print("🔑 Testing token creation...")
        try:
            token = manager.create_token(test_user['id'], 'access', ['read', 'write'])
            if token:
                print(f"✅ Token created successfully: {token[:20]}...")
                
                # Test verification
                print("🔍 Testing token verification...")
                user_data = manager.verify_token(token, 'access')
                if user_data:
                    print(f"✅ Token verification successful: user_id={user_data.get('user_id')}")
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