"""
dhii Mail - Database Configuration and Connection Manager
Handles SQLite database connections, migrations, and session management with connection pooling.
"""

import sqlite3
import json
import os
import threading
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, ContextManager
from datetime import datetime, timezone
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionPool:
    """Thread-safe connection pool for SQLite databases."""
    
    def __init__(self, db_path: str, max_connections: int = 10, timeout: float = 5.0):
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool = []
        self._lock = threading.Lock()
        self._connection_count = 0
        
        logger.info(f"Initializing connection pool for {db_path} (max: {max_connections})")
        
        # Pre-create a few connections
        for _ in range(min(3, max_connections)):
            try:
                conn = self._create_connection()
                self._pool.append(conn)
                self._connection_count += 1
            except Exception as e:
                logger.warning(f"Failed to pre-create connection: {e}")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimal settings."""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and performance
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache size
        conn.execute("PRAGMA temp_store = MEMORY")  # Use memory for temp tables
        conn.execute("PRAGMA mmap_size = 30000000000")  # 30GB memory map (if available)
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        logger.debug("Created new database connection")
        return conn
    
    def _acquire_connection(self) -> sqlite3.Connection:
        """Acquire a connection from the pool or create a new one."""
        with self._lock:
            # Try to get an existing connection from the pool
            if self._pool:
                conn = self._pool.pop()
                
                # Validate the connection
                try:
                    conn.execute("SELECT 1")
                    logger.debug("Reused existing connection from pool")
                    return conn
                except sqlite3.Error:
                    # Connection is invalid, close it and create a new one
                    try:
                        conn.close()
                    except:
                        pass
                    self._connection_count -= 1
            
            # Create a new connection if we haven't reached the limit
            if self._connection_count < self.max_connections:
                conn = self._create_connection()
                self._connection_count += 1
                logger.debug("Created new connection (pool exhausted)")
                return conn
            
            # Wait for a connection to become available
            logger.debug("Waiting for available connection...")
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                if self._pool:
                    conn = self._pool.pop()
                    try:
                        conn.execute("SELECT 1")
                        logger.debug("Acquired connection after waiting")
                        return conn
                    except sqlite3.Error:
                        try:
                            conn.close()
                        except:
                            pass
                        self._connection_count -= 1
                time.sleep(0.1)
            
            raise RuntimeError(f"Connection pool timeout after {self.timeout}s")
    
    def _release_connection(self, conn: sqlite3.Connection):
        """Release a connection back to the pool."""
        if conn:
            try:
                # Reset any transaction state
                conn.execute("ROLLBACK")
                
                with self._lock:
                    if len(self._pool) < self.max_connections - 1:
                        self._pool.append(conn)
                        logger.debug("Returned connection to pool")
                    else:
                        # Pool is full, close the connection
                        try:
                            conn.close()
                        except:
                            pass
                        self._connection_count -= 1
                        logger.debug("Closed connection (pool full)")
            except Exception as e:
                logger.warning(f"Error releasing connection: {e}")
                try:
                    conn.close()
                except:
                    pass
                with self._lock:
                    self._connection_count -= 1
    
    @contextmanager
    def get_connection(self) -> ContextManager[sqlite3.Connection]:
        """Get a database connection from the pool."""
        conn = None
        try:
            conn = self._acquire_connection()
            yield conn
        finally:
            if conn:
                self._release_connection(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing pooled connection: {e}")
            self._pool.clear()
            self._connection_count = 0
            logger.info("All connections closed")


class DatabaseManager:
    """Enhanced Database manager with connection pooling for better performance."""
    
    def __init__(self, db_path: str = "dhii_mail.db", max_connections: int = 10):
        self.db_path = db_path
        self.connection_pool = ConnectionPool(db_path, max_connections)
        self.email_manager = None  # Will be set later if needed
        self._ensure_database_exists()
        logger.info(f"DatabaseManager initialized with connection pool (max: {max_connections})")
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not os.path.exists(self.db_path):
            logger.info(f"Creating new database at {self.db_path}")
            self._create_database(schema_path)
        else:
            logger.info(f"Using existing database at {self.db_path}")
    
    def _create_database(self, schema_path: Path):
        """Initialize database with schema."""
        try:
            with self.connection_pool.get_connection() as conn:
                # Read and execute schema
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    # Execute schema in transactions
                    conn.executescript(schema_sql)
                    logger.info("Database schema created successfully")
                else:
                    logger.error(f"Schema file not found at {schema_path}")
                    raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results using connection pool."""
        try:
            with self.connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Convert rows to dictionaries
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    # Convert JSON strings to objects
                    for key, value in result.items():
                        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                            try:
                                result[key] = json.loads(value)
                            except json.JSONDecodeError:
                                pass  # Keep as string if not valid JSON
                    results.append(result)
                
                return results
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return []
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query using connection pool."""
        try:
            with self.connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution error: {e}")
            return 0
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries in one transaction using connection pool."""
        try:
            with self.connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Batch execution error: {e}")
            return 0
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table structure."""
        query = "PRAGMA table_info({})".format(table_name)
        return self.execute_query(query)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics including connection pool stats."""
        stats = {}
        
        # Get table row counts
        tables = ['users', 'email_accounts', 'email_folders', 'email_messages', 'auth_tokens']
        
        for table in tables:
            try:
                # Validate table name to prevent SQL injection
                if table not in tables:
                    stats[f"{table}_count"] = "Error: Invalid table name"
                    continue
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result[0]['count'] if result else 0
            except Exception as e:
                stats[f"{table}_count"] = f"Error: {e}"
        
        # Get database file size
        try:
            size_bytes = os.path.getsize(self.db_path)
            stats['database_size_bytes'] = size_bytes
            stats['database_size_mb'] = round(size_bytes / (1024 * 1024), 2)
        except Exception as e:
            stats['database_size_error'] = str(e)
        
        # Add connection pool statistics
        stats['connection_pool_stats'] = {
            "active_connections": self.connection_pool._connection_count,
            "available_connections": len(self.connection_pool._pool),
            "max_connections": self.connection_pool.max_connections
        }
        
        return stats
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            with self.connection_pool.get_connection() as conn:
                with sqlite3.connect(backup_path) as backup:
                    conn.backup(backup)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def migrate_database(self, migration_script: str) -> bool:
        """Apply a migration script to the database."""
        try:
            with self.connection_pool.get_connection() as conn:
                conn.executescript(migration_script)
                conn.commit()
                logger.info("Database migration applied successfully")
                return True
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            return False
    
    def close(self):
        """Close the database connection pool."""
        if self.connection_pool:
            self.connection_pool.close_all()
            logger.info("Database connection pool closed")


# Global database manager instance
db_manager = None

def get_db() -> DatabaseManager:
    """Get the global database manager instance with connection pooling."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_database(db_path: Optional[str] = None, max_connections: int = 10) -> DatabaseManager:
    """Initialize a new database manager instance with connection pooling."""
    global db_manager
    if db_path:
        db_manager = DatabaseManager(db_path, max_connections)
    else:
        db_manager = DatabaseManager(max_connections=max_connections)
    return db_manager

def setup_default_data():
    """Insert default data for development/testing."""
    db = get_db()
    
    # Check if we already have data
    users = db.execute_query("SELECT COUNT(*) as count FROM users")
    if users and users[0]['count'] > 0:
        logger.info("Default data already exists")
        return
    
    try:
        # Insert default tenant
        db.execute_update(
            """INSERT INTO tenants (name, slug, domain, settings) 
               VALUES (?, ?, ?, ?)""",
            ("Default Organization", "default", "localhost", json.dumps({"theme": "light"}))
        )
        
        # Get tenant ID
        tenant = db.execute_query("SELECT id FROM tenants WHERE slug = ?", ("default",))
        tenant_id = tenant[0]['id'] if tenant else None
        
        # Insert test user (password: 'test123')
        import bcrypt
        password_hash = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db.execute_update(
            """INSERT INTO users (email, username, password_hash, first_name, last_name, is_verified) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("test@dhii.ai", "testuser", password_hash, "Test", "User", True)
        )
        
        # Get user ID
        user = db.execute_query("SELECT id FROM users WHERE username = ?", ("testuser",))
        user_id = user[0]['id'] if user else None
        
        # Link user to tenant
        if user_id and tenant_id:
            db.execute_update(
                "INSERT INTO user_tenants (user_id, tenant_id, role) VALUES (?, ?, ?)",
                (user_id, tenant_id, "admin")
            )
        
        # Insert default user preferences
        default_prefs = {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "email_notifications": True,
            "ai_suggestions": True,
            "auto_sync": True
        }
        
        for key, value in default_prefs.items():
            db.execute_update(
                "INSERT INTO user_preferences (user_id, category, key, value) VALUES (?, ?, ?, ?)",
                (user_id, "general", key, str(value))
            )
        
        logger.info("Default data setup completed")
        
    except Exception as e:
        logger.error(f"Failed to setup default data: {e}")


if __name__ == "__main__":
    # Test the database manager with connection pooling
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing dhii Mail database with connection pooling...")
    db = init_database(max_connections=5)
    
    print("Database stats:")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nSetting up default data...")
    setup_default_data()
    
    print("\nDatabase ready with connection pooling!")
    
    # Test connection pooling
    print("\nTesting connection pooling...")
    import concurrent.futures
    
    def test_query(thread_id):
        stats = db.get_database_stats()
        return f"Thread {thread_id}: {stats['users_count']} users"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(test_query, i) for i in range(3)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    for result in results:
        print(f"  {result}")
    
    db.close()
    print("\nConnection pooling test completed!")