"""
Plugin Manager for A2UI Integration
Manages plugin registration, lifecycle, and analytics for Skill Store
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class PluginType(Enum):
    """Plugin types for categorization"""
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    SECURITY = "security"
    INTEGRATION = "integration"
    CUSTOM = "custom"

class PluginStatus(Enum):
    """Plugin status for lifecycle management"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

@dataclass
class PluginConfig:
    """Plugin configuration data"""
    plugin_id: str
    name: str
    description: str
    plugin_type: PluginType
    version: str
    author: str
    requires_auth: bool = False
    auth_config: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    icon: Optional[str] = None
    documentation_url: Optional[str] = None
    support_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['plugin_type'] = self.plugin_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfig':
        """Create from dictionary"""
        if 'plugin_type' in data and isinstance(data['plugin_type'], str):
            data['plugin_type'] = PluginType(data['plugin_type'])
        return cls(**data)

@dataclass
class PluginInfo:
    """Complete plugin information including runtime data"""
    config: PluginConfig
    status: PluginStatus
    last_updated: datetime
    install_date: datetime
    usage_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "config": self.config.to_dict(),
            "status": self.status.value,
            "last_updated": self.last_updated.isoformat(),
            "install_date": self.install_date.isoformat(),
            "usage_count": self.usage_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginInfo':
        """Create from dictionary"""
        config = PluginConfig.from_dict(data['config'])
        return cls(
            config=config,
            status=PluginStatus(data['status']),
            last_updated=datetime.fromisoformat(data['last_updated']),
            install_date=datetime.fromisoformat(data['install_date']),
            usage_count=data.get('usage_count', 0),
            error_count=data.get('error_count', 0),
            last_error=data.get('last_error'),
            error_message=data.get('error_message')
        )

class PluginManager:
    """Plugin management system for A2UI Skill Store"""
    
    def __init__(self, db_path: str = "plugins.db"):
        self.db_path = db_path
        self.plugins: Dict[str, PluginInfo] = {}
        self.init_database()
        self.load_plugins()
    
    def init_database(self):
        """Initialize SQLite database for plugin storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugins (
                        plugin_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        plugin_type TEXT NOT NULL,
                        version TEXT NOT NULL,
                        author TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'inactive',
                        requires_auth BOOLEAN DEFAULT FALSE,
                        auth_config TEXT,
                        settings TEXT,
                        capabilities TEXT,
                        dependencies TEXT,
                        icon TEXT,
                        documentation_url TEXT,
                        support_url TEXT,
                        privacy_policy_url TEXT,
                        install_date TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        error_message TEXT
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_plugin_type ON plugins(plugin_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_plugin_status ON plugins(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_plugin_name ON plugins(name)")
                
                conn.commit()
                logger.info("Plugin database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize plugin database: {e}")
            raise
    
    def load_plugins(self):
        """Load all plugins from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM plugins")
                
                for row in cursor:
                    plugin_data = dict(row)
                    
                    # Convert JSON strings back to objects
                    if plugin_data['auth_config']:
                        plugin_data['auth_config'] = json.loads(plugin_data['auth_config'])
                    if plugin_data['settings']:
                        plugin_data['settings'] = json.loads(plugin_data['settings'])
                    if plugin_data['capabilities']:
                        plugin_data['capabilities'] = json.loads(plugin_data['capabilities'])
                    if plugin_data['dependencies']:
                        plugin_data['dependencies'] = json.loads(plugin_data['dependencies'])
                    
                    # Convert datetime strings
                    plugin_data['install_date'] = datetime.fromisoformat(plugin_data['install_date'])
                    plugin_data['last_updated'] = datetime.fromisoformat(plugin_data['last_updated'])
                    
                    # Create PluginConfig and PluginInfo
                    config = PluginConfig.from_dict(plugin_data)
                    plugin_info = PluginInfo.from_dict({
                        'config': config.to_dict(),
                        'status': plugin_data['status'],
                        'last_updated': plugin_data['last_updated'].isoformat(),
                        'install_date': plugin_data['install_date'].isoformat(),
                        'usage_count': plugin_data['usage_count'],
                        'error_count': plugin_data['error_count'],
                        'last_error': plugin_data['last_error'],
                        'error_message': plugin_data['error_message']
                    })
                    
                    self.plugins[config.plugin_id] = plugin_info
                
                logger.info(f"Loaded {len(self.plugins)} plugins from database")
                
        except Exception as e:
            logger.error(f"Failed to load plugins from database: {e}")
            self.plugins = {}
    
    def register_plugin(self, plugin_config: PluginConfig) -> bool:
        """Register a new plugin or update existing one"""
        try:
            # Validate plugin configuration
            if not plugin_config.plugin_id:
                plugin_config.plugin_id = str(uuid.uuid4())
            
            if not plugin_config.name or not plugin_config.plugin_type:
                raise ValueError("Plugin name and type are required")
            
            # Create plugin info
            now = datetime.now()
            plugin_info = PluginInfo(
                config=plugin_config,
                status=PluginStatus.INACTIVE,
                last_updated=now,
                install_date=now
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO plugins 
                    (plugin_id, name, description, plugin_type, version, author, 
                     status, requires_auth, auth_config, settings, capabilities, 
                     dependencies, icon, documentation_url, support_url, privacy_policy_url,
                     install_date, last_updated, usage_count, error_count, last_error, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    plugin_config.plugin_id,
                    plugin_config.name,
                    plugin_config.description,
                    plugin_config.plugin_type.value,
                    plugin_config.version,
                    plugin_config.author,
                    plugin_info.status.value,
                    plugin_config.requires_auth,
                    json.dumps(plugin_config.auth_config) if plugin_config.auth_config else None,
                    json.dumps(plugin_config.settings) if plugin_config.settings else None,
                    json.dumps(plugin_config.capabilities) if plugin_config.capabilities else None,
                    json.dumps(plugin_config.dependencies) if plugin_config.dependencies else None,
                    plugin_config.icon,
                    plugin_config.documentation_url,
                    plugin_config.support_url,
                    plugin_config.privacy_policy_url,
                    plugin_info.install_date.isoformat(),
                    plugin_info.last_updated.isoformat(),
                    plugin_info.usage_count,
                    plugin_info.error_count,
                    plugin_info.last_error,
                    plugin_info.error_message
                ))
                
                conn.commit()
            
            # Update in-memory cache
            self.plugins[plugin_config.plugin_id] = plugin_info
            
            logger.info(f"Plugin registered successfully: {plugin_config.plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_config.plugin_id}: {e}")
            return False
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        try:
            if plugin_id not in self.plugins:
                logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            plugin_info = self.plugins[plugin_id]
            plugin_info.status = PluginStatus.ACTIVE
            plugin_info.last_updated = datetime.now()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE plugins 
                    SET status = ?, last_updated = ?, error_message = NULL
                    WHERE plugin_id = ?
                """, (plugin_info.status.value, plugin_info.last_updated.isoformat(), plugin_id))
                
                conn.commit()
            
            logger.info(f"Plugin enabled: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_id}: {e}")
            return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        try:
            if plugin_id not in self.plugins:
                logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            plugin_info = self.plugins[plugin_id]
            plugin_info.status = PluginStatus.INACTIVE
            plugin_info.last_updated = datetime.now()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE plugins 
                    SET status = ?, last_updated = ?
                    WHERE plugin_id = ?
                """, (plugin_info.status.value, plugin_info.last_updated.isoformat(), plugin_id))
                
                conn.commit()
            
            logger.info(f"Plugin disabled: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_id}: {e}")
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin information by ID"""
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all plugins"""
        return list(self.plugins.values())
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """Get plugins by type"""
        return [plugin for plugin in self.plugins.values() 
                if plugin.config.plugin_type == plugin_type]
    
    def get_active_plugins(self) -> List[PluginInfo]:
        """Get all active plugins"""
        return [plugin for plugin in self.plugins.values() 
                if plugin.status == PluginStatus.ACTIVE]
    
    def record_plugin_usage(self, plugin_id: str) -> bool:
        """Record plugin usage for analytics"""
        try:
            if plugin_id not in self.plugins:
                return False
            
            plugin_info = self.plugins[plugin_id]
            plugin_info.usage_count += 1
            plugin_info.last_updated = datetime.now()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE plugins 
                    SET usage_count = usage_count + 1, last_updated = ?
                    WHERE plugin_id = ?
                """, (plugin_info.last_updated.isoformat(), plugin_id))
                
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record plugin usage for {plugin_id}: {e}")
            return False
    
    def record_plugin_error(self, plugin_id: str, error_message: str) -> bool:
        """Record plugin error for monitoring"""
        try:
            if plugin_id not in self.plugins:
                return False
            
            plugin_info = self.plugins[plugin_id]
            plugin_info.error_count += 1
            plugin_info.last_error = datetime.now().isoformat()
            plugin_info.error_message = error_message
            plugin_info.status = PluginStatus.ERROR
            plugin_info.last_updated = datetime.now()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE plugins 
                    SET error_count = error_count + 1, 
                        last_error = ?, 
                        error_message = ?, 
                        status = ?, 
                        last_updated = ?
                    WHERE plugin_id = ?
                """, (plugin_info.last_error, error_message, PluginStatus.ERROR.value, 
                      plugin_info.last_updated.isoformat(), plugin_id))
                
                conn.commit()
            
            logger.error(f"Plugin error recorded for {plugin_id}: {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record plugin error for {plugin_id}: {e}")
            return False
    
    def get_plugin_analytics(self) -> Dict[str, Any]:
        """Get plugin usage analytics"""
        try:
            total_plugins = len(self.plugins)
            active_plugins = len(self.get_active_plugins())
            
            total_usage = sum(plugin.usage_count for plugin in self.plugins.values())
            total_errors = sum(plugin.error_count for plugin in self.plugins.values())
            
            # Plugin type distribution
            type_distribution = {}
            for plugin_type in PluginType:
                count = len(self.get_plugins_by_type(plugin_type))
                type_distribution[plugin_type.value] = count
            
            # Most used plugins
            most_used = sorted(self.plugins.values(), 
                             key=lambda x: x.usage_count, reverse=True)[:10]
            
            # Recent errors
            recent_errors = []
            for plugin in self.plugins.values():
                if plugin.last_error and plugin.error_message:
                    recent_errors.append({
                        "plugin_id": plugin.config.plugin_id,
                        "plugin_name": plugin.config.name,
                        "error_time": plugin.last_error,
                        "error_message": plugin.error_message
                    })
            
            recent_errors.sort(key=lambda x: x["error_time"], reverse=True)
            recent_errors = recent_errors[:10]  # Top 10 recent errors
            
            return {
                "total_plugins": total_plugins,
                "active_plugins": active_plugins,
                "inactive_plugins": total_plugins - active_plugins,
                "total_usage": total_usage,
                "total_errors": total_errors,
                "error_rate": total_errors / max(1, total_usage),
                "type_distribution": type_distribution,
                "most_used_plugins": [
                    {
                        "plugin_id": plugin.config.plugin_id,
                        "name": plugin.config.name,
                        "usage_count": plugin.usage_count,
                        "error_count": plugin.error_count
                    }
                    for plugin in most_used
                ],
                "recent_errors": recent_errors,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate plugin analytics: {e}")
            return {}
    
    def delete_plugin(self, plugin_id: str) -> bool:
        """Delete a plugin completely"""
        try:
            if plugin_id not in self.plugins:
                return False
            
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM plugins WHERE plugin_id = ?", (plugin_id,))
                conn.commit()
            
            # Remove from memory
            del self.plugins[plugin_id]
            
            logger.info(f"Plugin deleted: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete plugin {plugin_id}: {e}")
            return False

# Global plugin manager instance
plugin_manager = PluginManager()