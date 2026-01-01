"""
dhii Mail - Database Configuration and Connection Manager
Handles SQLite database connections, migrations, and session management.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str = "dhii_mail.db"):
        self.db_path = db_path
        self.schema_path = Path(__file__).parent / "schema.sql"
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        if not os.path.exists(self.db_path):
            logger.info(f"Creating new database at {self.db_path}")
            self._create_database()
        else:
            logger.info(f"Using existing database at {self.db_path}")
    
    def _create_database(self):
        """Initialize database with schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Enable foreign key support
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Read and execute schema
                if self.schema_path.exists():
                    with open(self.schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    # Execute schema in transactions
                    conn.executescript(schema_sql)
                    logger.info("Database schema created successfully")
                else:
                    logger.error(f"Schema file not found at {self.schema_path}")
                    raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper settings."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
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
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries in one transaction."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table structure."""
        query = "PRAGMA table_info({})".format(table_name)
        return self.execute_query(query)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        # Get table row counts
        tables = ['users', 'email_accounts', 'email_folders', 'email_messages', 'auth_tokens']
        
        for table in tables:
            try:
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
        
        return stats
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def migrate_database(self, migration_script: str) -> bool:
        """Apply a migration script to the database."""
        try:
            with self.get_connection() as conn:
                conn.executescript(migration_script)
                conn.commit()
                logger.info("Database migration applied successfully")
                return True
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            return False

# Global database instance
db_manager = DatabaseManager()

# Utility functions
def get_db() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager

def init_database(db_path: Optional[str] = None) -> DatabaseManager:
    """Initialize a new database manager instance."""
    global db_manager
    if db_path:
        db_manager = DatabaseManager(db_path)
    return db_manager

def setup_default_data():
    """Insert default data for development/testing."""
    db = get_db()
    
    # Check if we already have data
    users = db.execute_query("SELECT COUNT(*) as count FROM users")
    if users[0]['count'] > 0:
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
    # Test the database manager
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing dhii Mail database...")
    db = init_database()
    
    print("Database stats:")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nSetting up default data...")
    setup_default_data()
    
    print("\nDatabase ready!")