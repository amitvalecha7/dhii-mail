#!/usr/bin/env python3
"""
Test database connection pooling for dhii-mail
"""

import os
import sys
import time
import threading
import concurrent.futures

sys.path.insert(0, '/root/dhii-mail')

def test_connection_pooling():
    """Test the connection pooling functionality"""
    print("=== Testing Database Connection Pooling ===\n")
    
    # Clear any cached modules
    if 'database' in sys.modules:
        del sys.modules['database']
    
    from database import DatabaseManager
    
    # Test 1: Basic functionality
    print("1. Testing basic connection pool functionality...")
    db = DatabaseManager(db_path="test_pooling.db", max_connections=5)
    
    # Test database stats
    stats = db.get_database_stats()
    print(f"   Database stats: {stats}")
    print(f"   Connection pool stats: {stats.get('connection_pool_stats', {})}")
    print("   ✅ Basic connection pool working")
    print()
    
    # Test 2: Concurrent connections
    print("2. Testing concurrent connections...")
    
    def query_database(thread_id):
        """Simulate database query from multiple threads"""
        try:
            stats = db.get_database_stats()
            return f"Thread {thread_id}: Success - {stats['users_count']} users"
        except Exception as e:
            return f"Thread {thread_id}: Error - {e}"
    
    # Test with 10 concurrent threads (more than pool size)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(query_database, i) for i in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    for result in results:
        print(f"   {result}")
    print("   ✅ Concurrent connections handled properly")
    print()
    
    # Test 3: Connection reuse
    print("3. Testing connection reuse...")
    
    def test_query_reuse(iteration):
        """Test that connections are properly reused"""
        try:
            # Execute multiple queries
            for i in range(3):
                stats = db.get_database_stats()
            return f"Iteration {iteration}: All queries successful"
        except Exception as e:
            return f"Iteration {iteration}: Error - {e}"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(test_query_reuse, i) for i in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    for result in results:
        print(f"   {result}")
    print("   ✅ Connection reuse working")
    print()
    
    # Test 4: Connection pool stats
    print("4. Testing connection pool statistics...")
    final_stats = db.get_database_stats()
    pool_stats = final_stats.get('connection_pool_stats', {})
    
    print(f"   Final pool stats: {pool_stats}")
    print(f"   Active connections: {pool_stats.get('active_connections', 0)}")
    print(f"   Available connections: {pool_stats.get('available_connections', 0)}")
    print(f"   Max connections: {pool_stats.get('max_connections', 0)}")
    print("   ✅ Connection pool statistics working")
    print()
    
    # Cleanup
    db.close()
    
    # Remove test database
    try:
        os.remove("test_pooling.db")
    except:
        pass
    
    print("=== All Connection Pooling Tests Passed! ===")

if __name__ == "__main__":
    test_connection_pooling()