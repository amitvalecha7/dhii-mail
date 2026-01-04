"""
Shared Services Layer for dhii Mail Kernel
Provides common infrastructure services for all plugins
"""

import logging
import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system"""
    PLUGIN_REGISTERED = "plugin_registered"
    PLUGIN_ENABLED = "plugin_enabled" 
    PLUGIN_DISABLED = "plugin_disabled"
    PLUGIN_ERROR = "plugin_error"
    CAPABILITY_EXECUTED = "capability_executed"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    EMAIL_RECEIVED = "email_received"
    EMAIL_SENT = "email_sent"
    MEETING_CREATED = "meeting_created"
    MEETING_UPDATED = "meeting_updated"
    MEETING_DELETED = "meeting_deleted"


@dataclass
class Event:
    """Event data structure"""
    id: str
    type: EventType
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None


class EventBus:
    """Central event bus for plugin communication"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, Set[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to events of a specific type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(callback)
        logger.info(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from events"""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(callback)
            logger.info(f"Unsubscribed from {event_type.value}")
    
    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Notify subscribers
        if event.type in self._subscribers:
            callbacks = list(self._subscribers[event.type])  # Copy to avoid modification during iteration
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Event callback failed: {e}")
        
        logger.info(f"Published event {event.type.value} from {event.source}")
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self._event_history if e.type == event_type]
        else:
            filtered = self._event_history
        
        return filtered[-limit:] if limit > 0 else filtered


class SharedDatabase:
    """Shared database service for all plugins"""
    
    def __init__(self, db_path: str = "kernel.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize shared database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                preferences TEXT DEFAULT '{}'
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Plugin data table (for plugin-specific data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                data_type TEXT DEFAULT 'string',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plugin_id) REFERENCES plugins (id) ON DELETE CASCADE,
                UNIQUE(plugin_id, key)
            )
        ''')
        
        # Plugins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                author TEXT NOT NULL,
                enabled BOOLEAN DEFAULT FALSE,
                status TEXT DEFAULT 'installed',
                config TEXT DEFAULT '{}',
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0
            )
        ''')
        
        # Capabilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capabilities (
                id TEXT PRIMARY KEY,
                plugin_id TEXT NOT NULL,
                domain TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                input_schema TEXT,
                output_schema TEXT,
                side_effects TEXT DEFAULT '[]',
                requires_auth BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plugin_id) REFERENCES plugins (id) ON DELETE CASCADE
            )
        ''')
        
        # Plugin dependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                dependency_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plugin_id) REFERENCES plugins (id) ON DELETE CASCADE,
                FOREIGN KEY (dependency_id) REFERENCES plugins (id) ON DELETE CASCADE,
                UNIQUE(plugin_id, dependency_id)
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_data_plugin_id ON plugin_data (plugin_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_data_key ON plugin_data (key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugins_type ON plugins (type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugins_status ON plugins (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_capabilities_plugin_id ON capabilities (plugin_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_capabilities_domain ON capabilities (domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_dependencies_plugin_id ON plugin_dependencies (plugin_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log (timestamp)')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a read query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute a write query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rowcount
    
    def get_plugin_data(self, plugin_id: str, key: str) -> Optional[Any]:
        """Get plugin-specific data"""
        results = self.execute_query(
            'SELECT value, data_type FROM plugin_data WHERE plugin_id = ? AND key = ?',
            (plugin_id, key)
        )
        
        if not results:
            return None
        
        value, data_type = results[0]['value'], results[0]['data_type']
        
        if data_type == 'json':
            return json.loads(value)
        elif data_type == 'integer':
            return int(value)
        elif data_type == 'float':
            return float(value)
        elif data_type == 'boolean':
            return value.lower() == 'true'
        else:
            return value
    
    def set_plugin_data(self, plugin_id: str, key: str, value: Any, data_type: str = 'string'):
        """Set plugin-specific data"""
        if data_type == 'json':
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        self.execute_update('''
            INSERT OR REPLACE INTO plugin_data (plugin_id, key, value, data_type, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (plugin_id, key, value_str, data_type, datetime.now().isoformat()))


class SharedAuth:
    """Shared authentication service for all plugins"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.db = SharedDatabase()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        # This would integrate with the existing AuthManager
        # For now, return a mock implementation
        results = self.db.execute_query(
            'SELECT id, email, first_name, last_name FROM users WHERE username = ? AND password_hash = ?',
            (username, password)  # In real implementation, password should be hashed
        )
        
        return results[0] if results else None
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by authentication token"""
        # This would integrate with JWT token validation
        # For now, return a mock implementation
        results = self.db.execute_query(
            'SELECT u.id, u.email, u.username, u.first_name, u.last_name FROM users u JOIN sessions s ON u.id = s.user_id WHERE s.access_token = ?',
            (token,)
        )
        
        return results[0] if results else None
    
    def log_audit_event(self, user_id: str, action: str, resource_type: str = None, resource_id: str = None, details: Dict[str, Any] = None):
        """Log audit event for security tracking"""
        self.db.execute_update('''
            INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource_type, resource_id, json.dumps(details) if details else None, datetime.now().isoformat()))


class SharedServices:
    """Central shared services manager"""
    
    def __init__(self, db_path: str = "kernel.db", secret_key: str = "kernel-secret-key"):
        self.database = SharedDatabase(db_path)
        self.auth = SharedAuth(secret_key)
        self.event_bus = EventBus()
        self._initialized = False
    
    def initialize(self):
        """Initialize shared services"""
        if self._initialized:
            return
        
        logger.info("Initializing shared services...")
        self._initialized = True
        logger.info("Shared services initialized successfully")
    
    def shutdown(self):
        """Shutdown shared services"""
        if not self._initialized:
            return
        
        logger.info("Shutting down shared services...")
        self._initialized = False
        logger.info("Shared services shut down successfully")
    
    @property
    def is_initialized(self) -> bool:
        """Check if services are initialized"""
        return self._initialized


# Global shared services instance
_shared_services: Optional[SharedServices] = None


def get_shared_services() -> SharedServices:
    """Get the global shared services instance"""
    global _shared_services
    if _shared_services is None:
        _shared_services = SharedServices()
    return _shared_services


def initialize_shared_services(db_path: str = "kernel.db", secret_key: str = "kernel-secret-key"):
    """Initialize global shared services"""
    global _shared_services
    _shared_services = SharedServices(db_path, secret_key)
    _shared_services.initialize()


def shutdown_shared_services():
    """Shutdown global shared services"""
    global _shared_services
    if _shared_services:
        _shared_services.shutdown()
        _shared_services = None