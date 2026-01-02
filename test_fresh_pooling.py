#!/usr/bin/env python3
"""
Fresh test for database connection pooling
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, '/root/dhii-mail')

# Import fresh
from database import DatabaseManager

# Test the constructor signature
import inspect
print("DatabaseManager signature:", inspect.signature(DatabaseManager.__init__))

# Test instantiation
try:
    db = DatabaseManager(db_path="test_fresh.db", max_connections=3)
    print("✅ DatabaseManager created successfully with max_connections=3")
    
    # Test basic functionality
    stats = db.get_database_stats()
    print("✅ Database stats retrieved:", stats)
    
    # Test connection pool stats
    pool_stats = stats.get('connection_pool_stats', {})
    print("✅ Connection pool stats:", pool_stats)
    
    # Close and cleanup
    db.close()
    os.remove("test_fresh.db")
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()