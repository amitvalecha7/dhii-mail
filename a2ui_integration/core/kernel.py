"""
Core Kernel Implementation for dhii Mail A2UI System
Provides the main kernel that manages plugins and coordinates capabilities
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import asyncio

from .types import (
    KernelInterface, DomainModule, PluginConfig, PluginInfo, PluginType, 
    PluginStatus, Capability, A2UIComponent, AdjacencyOperation
)
from .shared_services import SharedServices, get_shared_services, EventType, Event
from .logging import get_logger

logger = get_logger(__name__)


class Kernel(KernelInterface):
    """Core kernel that manages plugins and coordinates capabilities using shared services"""
    
    def __init__(self, db_path: str = "kernel.db", secret_key: str = "kernel-secret-key"):
        self.db_path = db_path
        self.secret_key = secret_key
        self._plugins: Dict[str, DomainModule] = {}
        self._plugin_configs: Dict[str, PluginConfig] = {}
        self._capabilities: Dict[str, Capability] = {}
        self._capability_to_plugin: Dict[str, str] = {}
        self._initialized = False
        
        # Initialize shared services
        self._init_shared_services()
    
    def _init_shared_services(self):
        """Initialize shared services for the kernel"""
        from .shared_services import initialize_shared_services
        initialize_shared_services(self.db_path, self.secret_key)
        self.shared_services = get_shared_services()
        self._initialized = True
        logger.info("Kernel shared services initialized", extra_fields={"service": "kernel"})

    async def initialize(self):
        """Initialize kernel and load existing plugins"""
        try:
            logger.info("Initializing kernel...", extra_fields={"operation": "kernel_initialize"})
            
            # Load existing plugins
            await self._load_plugins_async()
            
            logger.info("Kernel initialization completed", extra_fields={"operation": "kernel_initialize", "status": "success"})
            
        except Exception as e:
            logger.error("Failed to initialize kernel", extra_fields={"operation": "kernel_initialize", "error": str(e)})
            raise
    
    def _load_plugins(self):
        """Load plugins from database"""
        try:
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
        except sqlite3.OperationalError as e:
            # Database tables don't exist yet, this is OK during initialization
            logger.info("Plugin tables not found, skipping plugin load during initialization")
        except Exception as e:
            logger.error(f"Error loading plugins: {e}")

    async def _load_plugins_async(self):
        """Async version of load plugins"""
        # For now, just call the sync version
        self._load_plugins()
    
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

    def install_plugin(self, plugin_id: str) -> bool:
        """
        Install a new plugin from the registry.
        
        Args:
            plugin_id: The ID of the plugin to install.
            
        Returns:
            bool: True if installed successfully, False otherwise.
        """
        logger.info(f"Requesting installation of plugin: {plugin_id}")
        if self.plugin_installer.install_plugin(plugin_id):
            logger.info(f"Plugin {plugin_id} installed. Reloading plugins...")
            # Ideally, we would reload dynamically here.
            # For now, we just log success.
            return True
        else:
            logger.error(f"Failed to install plugin {plugin_id}")
            return False
    
    async def register_plugin(self, plugin_config: PluginConfig) -> bool:
        """Register a new plugin using shared services"""
        try:
            # Use shared database service
            db = self.shared_services.database
            
            # Store plugin in database
            db.execute_update('''
                INSERT OR REPLACE INTO plugins 
                (id, name, version, description, type, author, enabled, status, config, installed_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin_config.id,
                plugin_config.name,
                plugin_config.version,
                plugin_config.description,
                plugin_config.type.value,
                plugin_config.author,
                plugin_config.enabled,
                PluginStatus.INSTALLED.value,
                json.dumps(plugin_config.config),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Store capabilities
            for capability in plugin_config.capabilities:
                db.execute_update('''
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
                db.execute_update('''
                    INSERT OR REPLACE INTO plugin_dependencies (plugin_id, dependency_id)
                    VALUES (?, ?)
                ''', (plugin_config.id, dependency))
            
            # Store in memory
            self._plugin_configs[plugin_config.id] = plugin_config
            
            # Publish event
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_registered_{plugin_config.id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_REGISTERED,
                source="kernel",
                timestamp=datetime.now(),
                data={"plugin_id": plugin_config.id, "plugin_name": plugin_config.name}
            ))
            
            logger.info(f"Plugin {plugin_config.id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_config.id}: {e}")
            return False
    
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin using shared services"""
        if plugin_id not in self._plugin_configs:
            logger.error(f"Plugin {plugin_id} not found")
            return False
        
        try:
            # Update database using shared services
            db = self.shared_services.database
            db.execute_update('''
                UPDATE plugins 
                SET status = ?, last_updated = ?
                WHERE id = ?
            ''', (PluginStatus.ENABLED.value, datetime.now().isoformat(), plugin_id))
            
            # Load capabilities
            plugin_config = self._plugin_configs[plugin_id]
            for capability in plugin_config.capabilities:
                self._capabilities[capability.id] = capability
                self._capability_to_plugin[capability.id] = plugin_id
            
            # Publish event
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_enabled_{plugin_id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_ENABLED,
                source="kernel",
                timestamp=datetime.now(),
                data={"plugin_id": plugin_id, "plugin_name": plugin_config.name}
            ))
            
            logger.info(f"Plugin {plugin_id} enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_id}: {e}")
            return False
    
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin using shared services"""
        try:
            # Update database using shared services
            db = self.shared_services.database
            db.execute_update('''
                UPDATE plugins 
                SET status = ?, last_updated = ?
                WHERE id = ?
            ''', (PluginStatus.DISABLED.value, datetime.now().isoformat(), plugin_id))
            
            # Remove capabilities
            plugin_config = self._plugin_configs.get(plugin_id)
            if plugin_config:
                for capability in plugin_config.capabilities:
                    if capability.id in self._capabilities:
                        del self._capabilities[capability.id]
                    if capability.id in self._capability_to_plugin:
                        del self._capability_to_plugin[capability.id]
                
                # Publish event
                await self.shared_services.event_bus.publish(Event(
                    id=f"plugin_disabled_{plugin_id}_{datetime.now().isoformat()}",
                    type=EventType.PLUGIN_DISABLED,
                    source="kernel",
                    timestamp=datetime.now(),
                    data={"plugin_id": plugin_id, "plugin_name": plugin_config.name}
                ))
            
            logger.info(f"Plugin {plugin_id} disabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_id}: {e}")
            return False
    
    async def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin information using shared services"""
        try:
            # Use shared database service
            db = self.shared_services.database
            results = db.execute_query('SELECT * FROM plugins WHERE id = ?', (plugin_id,))
            
            if not results:
                return None
            
            plugin_data = results[0]
            plugin_info = PluginInfo(
                id=plugin_data['id'],
                name=plugin_data['name'],
                version=plugin_data['version'],
                description=plugin_data['description'],
                type=PluginType(plugin_data['type']),
                status=PluginStatus(plugin_data['status']),
                installed_at=datetime.fromisoformat(plugin_data['installed_at']),
                last_updated=datetime.fromisoformat(plugin_data['last_updated']) if plugin_data['last_updated'] else None,
                usage_count=plugin_data['usage_count'],
                error_count=plugin_data['error_count'],
                config=json.loads(plugin_data['config']) if plugin_data['config'] else {}
            )
            
            return plugin_info
            
        except Exception as e:
            logger.error(f"Failed to get plugin {plugin_id}: {e}")
            return None
    
    async def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins or filter by type using shared services"""
        try:
            # Use shared database service
            db = self.shared_services.database
            
            if plugin_type:
                results = db.execute_query('SELECT * FROM plugins WHERE type = ?', (plugin_type.value,))
            else:
                results = db.execute_query('SELECT * FROM plugins')
            
            plugins = []
            for plugin_data in results:
                plugin_info = PluginInfo(
                    id=plugin_data['id'],
                    name=plugin_data['name'],
                    version=plugin_data['version'],
                    description=plugin_data['description'],
                    type=PluginType(plugin_data['type']),
                    status=PluginStatus(plugin_data['status']),
                    installed_at=datetime.fromisoformat(plugin_data['installed_at']),
                    last_updated=datetime.fromisoformat(plugin_data['last_updated']) if plugin_data['last_updated'] else None,
                    usage_count=plugin_data['usage_count'],
                    error_count=plugin_data['error_count'],
                    config=json.loads(plugin_data['config']) if plugin_data['config'] else {}
                )
                plugins.append(plugin_info)
            
            return plugins
            
        except Exception as e:
            logger.error(f"Failed to list plugins: {e}")
            return []
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability from any plugin using shared services"""
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
            
            # Update usage count using shared services
            db = self.shared_services.database
            db.execute_update('UPDATE plugins SET usage_count = usage_count + 1 WHERE id = ?', (plugin_id,))
            
            # Publish capability executed event
            await self.shared_services.event_bus.publish(Event(
                id=f"capability_executed_{capability_id}_{datetime.now().isoformat()}",
                type=EventType.CAPABILITY_EXECUTED,
                source=plugin_id,
                timestamp=datetime.now(),
                data={"capability_id": capability_id, "plugin_id": plugin_id, "params": params}
            ))
            
            return result
            
        except Exception as e:
            # Update error count using shared services
            db = self.shared_services.database
            db.execute_update('UPDATE plugins SET error_count = error_count + 1 WHERE id = ?', (plugin_id,))
            
            # Publish plugin error event
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_error_{plugin_id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_ERROR,
                source=plugin_id,
                timestamp=datetime.now(),
                data={"capability_id": capability_id, "error": str(e), "error_type": type(e).__name__}
            ))
            
            raise e
    
    async def get_status(self) -> Dict[str, Any]:
        """Get kernel status information"""
        try:
            plugins = await self.list_plugins()
            enabled_plugins = [p for p in plugins if p.status == PluginStatus.ENABLED]
            
            return {
                "status": "running" if self._initialized else "initializing",
                "initialized": self._initialized,
                "total_plugins": len(plugins),
                "enabled_plugins": len(enabled_plugins),
                "plugins_by_type": {
                    plugin_type.value: len([p for p in plugins if p.type == plugin_type])
                    for plugin_type in PluginType
                },
                "shared_services": {
                    "database": self.shared_services.database is not None,
                    "auth": self.shared_services.auth is not None,
                    "event_bus": self.shared_services.event_bus is not None
                }
            }
        except Exception as e:
            logger.error(f"Failed to get kernel status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "initialized": self._initialized
            }
    
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