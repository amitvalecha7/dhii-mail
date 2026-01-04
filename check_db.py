#!/usr/bin/env python3
"""
Simple debug script to check database tables
"""

import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Check database tables"""
    print("🔍 Checking database...")
    
    try:
        import database
        db = database.get_db()
        print("✅ Database connected")
        
        # Get all tables
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        print("📋 Available tables:")
        for table in tables:
            print(f"  - {table['name']}")
        
        # Check users table specifically
        users_exists = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if users_exists:
            print("✅ users table exists")
            user_count = db.execute_query("SELECT COUNT(*) as count FROM users")
            print(f"📊 Users in database: {user_count[0]['count']}")
            
            # Show first few users
            users = db.execute_query("SELECT id, email, username FROM users LIMIT 3")
            for user in users:
                print(f"  - ID {user['id']}: {user['email']} ({user['username']})")
        else:
            print("❌ users table does not exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_database()