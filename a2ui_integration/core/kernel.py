"""
Core Kernel Implementation for dhii Mail A2UI System
Provides the main kernel that manages plugins and coordinates capabilities
"""

import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
from pathlib import Path

from .types import (
    KernelInterface, DomainModule, PluginConfig, PluginInfo, PluginType, 
    PluginStatus, Capability, A2UIComponent, AdjacencyOperation
)
from ..plugin_manager import PluginManager

logger = logging.getLogger(__name__)


class Kernel(KernelInterface):
    """Core kernel that manages plugins and coordinates capabilities"""
    
    def __init__(self, db_path: str = "kernel.db"):
        self.db_path = db_path
        self.plugin_manager = PluginManager()
        self._plugins: Dict[str, DomainModule] = {}
        self._plugin_configs: Dict[str, PluginConfig] = {}
        self._capabilities: Dict[str, Capability] = {}
        self._capability_to_plugin: Dict[str, str] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing plugins
        self._load_plugins()
    
    def _init_database(self):
        """Initialize the kernel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Plugins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                config TEXT,
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP,
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
                side_effects TEXT,
                requires_auth BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (plugin_id) REFERENCES plugins (id)
            )
        ''')
        
        # Plugin dependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_dependencies (
                plugin_id TEXT NOT NULL,
                dependency_id TEXT NOT NULL,
                PRIMARY KEY (plugin_id, dependency_id),
                FOREIGN KEY (plugin_id) REFERENCES plugins (id),
                FOREIGN KEY (dependency_id) REFERENCES plugins (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_plugins(self):
        """Load plugins from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM plugins WHERE status = ?', (PluginStatus.ENABLED.value,))
        plugins = cursor.fetchall()
        
        for plugin_data in plugins:
            plugin_id = plugin_data[0]
            try:
                self._load_plugin(plugin_id)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
        
        conn.close()
    
    def _load_plugin(self, plugin_id: str):
        """Load a specific plugin"""
        # This would dynamically load the plugin module
        # For now, we'll use the existing plugin manager
        pass
    
    def register_plugin_instance(self, plugin_id: str, plugin_instance: DomainModule) -> bool:
        """Register an actual plugin instance that can execute capabilities"""
        try:
            self._plugins[plugin_id] = plugin_instance
            logger.info(f"Plugin instance {plugin_id} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin instance {plugin_id}: {e}")
            return False
    
    async def register_plugin(self, plugin_config: PluginConfig) -> bool:
        """Register a new plugin"""
        try:
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO plugins 
                (id, name, version, description, type, status, config, installed_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin_config.id,
                plugin_config.name,
                plugin_config.version,
                plugin_config.description,
                plugin_config.type.value,
                PluginStatus.INSTALLED.value,
                json.dumps(plugin_config.config),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Store capabilities
            for capability in plugin_config.capabilities:
                cursor.execute('''
                    INSERT OR REPLACE INTO capabilities 
                    (id, plugin_id, domain, name, description, input_schema, output_schema, side_effects, requires_auth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    capability.id,
                    plugin_config.id,
                    capability.domain,
                    capability.name,
                    capability.description,
                    json.dumps(capability.input_schema),
                    json.dumps(capability.output_schema),
                    json.dumps(capability.side_effects),
                    capability.requires_auth
                ))
            
            # Store dependencies
            for dependency in plugin_config.dependencies:
                cursor.execute('''
                    INSERT OR REPLACE INTO plugin_dependencies (plugin_id, dependency_id)
                    VALUES (?, ?)
                ''', (plugin_config.id, dependency))
            
            conn.commit()
            conn.close()
            
            # Store in memory
            self._plugin_configs[plugin_config.id] = plugin_config
            
            logger.info(f"Plugin {plugin_config.id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_config.id}: {e}")
            return False
    
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        if plugin_id not in self._plugin_configs:
            logger.error(f"Plugin {plugin_id} not found")
            return False
        
        try:
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE plugins 
                SET status = ?, last_updated = ?
                WHERE id = ?
            ''', (PluginStatus.ENABLED.value, datetime.now().isoformat(), plugin_id))
            
            conn.commit()
            conn.close()
            
            # Load capabilities
            plugin_config = self._plugin_configs[plugin_id]
            for capability in plugin_config.capabilities:
                self._capabilities[capability.id] = capability
                self._capability_to_plugin[capability.id] = plugin_id
            
            logger.info(f"Plugin {plugin_id} enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_id}: {e}")
            return False
    
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        try:
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE plugins 
                SET status = ?, last_updated = ?
                WHERE id = ?
            ''', (PluginStatus.DISABLED.value, datetime.now().isoformat(), plugin_id))
            
            conn.commit()
            conn.close()
            
            # Remove capabilities
            plugin_config = self._plugin_configs.get(plugin_id)
            if plugin_config:
                for capability in plugin_config.capabilities:
                    if capability.id in self._capabilities:
                        del self._capabilities[capability.id]
                    if capability.id in self._capability_to_plugin:
                        del self._capability_to_plugin[capability.id]
            
            logger.info(f"Plugin {plugin_id} disabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_id}: {e}")
            return False
    
    async def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM plugins WHERE id = ?', (plugin_id,))
        plugin_data = cursor.fetchone()
        
        if not plugin_data:
            conn.close()
            return None
        
        plugin_info = PluginInfo(
            id=plugin_data[0],
            name=plugin_data[1],
            version=plugin_data[2],
            description=plugin_data[3],
            type=PluginType(plugin_data[4]),
            status=PluginStatus(plugin_data[5]),
            installed_at=datetime.fromisoformat(plugin_data[7]),
            last_updated=datetime.fromisoformat(plugin_data[8]) if plugin_data[8] else None,
            usage_count=plugin_data[9],
            error_count=plugin_data[10],
            config=json.loads(plugin_data[6]) if plugin_data[6] else {}
        )
        
        conn.close()
        return plugin_info
    
    async def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins or filter by type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if plugin_type:
            cursor.execute('SELECT * FROM plugins WHERE type = ?', (plugin_type.value,))
        else:
            cursor.execute('SELECT * FROM plugins')
        
        plugins_data = cursor.fetchall()
        plugins = []
        
        for plugin_data in plugins_data:
            plugin_info = PluginInfo(
                id=plugin_data[0],
                name=plugin_data[1],
                version=plugin_data[2],
                description=plugin_data[3],
                type=PluginType(plugin_data[4]),
                status=PluginStatus(plugin_data[5]),
                installed_at=datetime.fromisoformat(plugin_data[7]),
                last_updated=datetime.fromisoformat(plugin_data[8]) if plugin_data[8] else None,
                usage_count=plugin_data[9],
                error_count=plugin_data[10],
                config=json.loads(plugin_data[6]) if plugin_data[6] else {}
            )
            plugins.append(plugin_info)
        
        conn.close()
        return plugins
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability from any plugin"""
        if capability_id not in self._capabilities:
            raise ValueError(f"Capability {capability_id} not found")
        
        if capability_id not in self._capability_to_plugin:
            raise ValueError(f"Plugin for capability {capability_id} not found")
        
        plugin_id = self._capability_to_plugin[capability_id]
        plugin = self._plugins.get(plugin_id)
        
        if not plugin:
            raise ValueError(f"Plugin {plugin_id} not loaded")
        
        try:
            result = await plugin.execute_capability(capability_id, params)
            
            # Update usage count
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE plugins SET usage_count = usage_count + 1 WHERE id = ?', (plugin_id,))
            conn.commit()
            conn.close()
            
            return result
            
        except Exception as e:
            # Update error count
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE plugins SET error_count = error_count + 1 WHERE id = ?', (plugin_id,))
            conn.commit()
            conn.close()
            
            raise e
    
    async def search(self, query: str, domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Universal search across enabled plugins"""
        results = []
        
        # First try to search using plugin instances if available
        for plugin_id, plugin in self._plugins.items():
            # Skip if domain filter is specified and plugin doesn't match
            if domains and plugin.domain not in domains:
                continue
            
            try:
                # Look for search capability
                search_capability = None
                for capability in plugin.capabilities:
                    if 'search' in capability.id.lower():
                        search_capability = capability
                        break
                
                if search_capability:
                    search_results = await plugin.execute_capability(
                        search_capability.id, 
                        {"query": query}
                    )
                    results.extend(search_results)
                    
            except Exception as e:
                logger.error(f"Search failed for plugin {plugin_id}: {e}")
        
        # If no plugin instances are loaded, search through configurations
        if not results and self._plugin_configs:
            for plugin_id, config in self._plugin_configs.items():
                # Skip if domain filter is specified and plugin doesn't match
                if domains and config.type.value not in domains:
                    continue
                
                # Simple text search through plugin info
                search_text = f"{config.name} {config.description} {' '.join([cap.name for cap in config.capabilities])}"
                if query.lower() in search_text.lower():
                    results.append({
                        "type": "plugin",
                        "id": plugin_id,
                        "name": config.name,
                        "description": config.description,
                        "domain": config.type.value,
                        "status": "enabled" if plugin_id in [pid for pid, _ in self._plugins.items()] else "configured"
                    })
                
                # Search through capabilities
                for capability in config.capabilities:
                    cap_text = f"{capability.name} {capability.description}"
                    if query.lower() in cap_text.lower():
                        results.append({
                            "type": "capability",
                            "id": capability.id,
                            "name": capability.name,
                            "description": capability.description,
                            "domain": capability.domain,
                            "plugin_id": plugin_id
                        })
        
        return results