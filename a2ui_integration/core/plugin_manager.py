"""
Framework 2.0: Plugin Manager
Standardized plugin lifecycle management - handles loading, validation, and execution
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
import importlib.util
import sys

from .plugin_contract import (
    PluginInterface, PluginManifest, PluginCapability, PluginType, 
    CapabilityType, register_plugin
)
from .sandbox import PluginSandbox
from .plugin_api import PluginAPIBuilder

logger = logging.getLogger(__name__)

class PluginLoadError(Exception):
    """Raised when plugin loading fails"""
    pass

class PluginValidationError(Exception):
    """Raised when plugin validation fails"""
    pass

class PluginManager:
    """
    Standardized plugin manager - handles all plugin lifecycle operations
    Never touches kernel core directly
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self._loaded_plugins: Dict[str, PluginInterface] = {}
        self._plugin_manifests: Dict[str, PluginManifest] = {}
        self._capabilities: Dict[str, PluginCapability] = {}
        self._capability_handlers: Dict[str, Any] = {}
        self._sandbox_cache: Dict[str, PluginSandbox] = {}
        
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in plugins directory"""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist")
            return []
            
        plugins = []
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "manifest.json").exists():
                plugins.append(item.name)
                
        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins
    
    def load_manifest(self, plugin_id: str) -> PluginManifest:
        """Load and validate plugin manifest"""
        manifest_path = self.plugins_dir / plugin_id / "manifest.json"
        
        if not manifest_path.exists():
            raise PluginValidationError(f"Plugin {plugin_id} missing manifest.json")
            
        try:
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
                
            # Convert to PluginManifest
            capabilities = []
            for cap_data in manifest_data.get("capabilities", []):
                capability = PluginCapability(
                    id=cap_data["id"],
                    name=cap_data["name"],
                    description=cap_data["description"],
                    capability_type=CapabilityType(cap_data["capability_type"]),
                    input_schema=cap_data.get("input_schema", {}),
                    output_schema=cap_data.get("output_schema", {}),
                    requires_auth=cap_data.get("requires_auth", False),
                    rate_limit=cap_data.get("rate_limit"),
                    timeout_seconds=cap_data.get("timeout_seconds", 30)
                )
                capabilities.append(capability)
            
            manifest = PluginManifest(
                id=manifest_data["id"],
                name=manifest_data["name"],
                version=manifest_data["version"],
                plugin_type=PluginType(manifest_data["plugin_type"]),
                author=manifest_data["author"],
                description=manifest_data["description"],
                capabilities=capabilities,
                dependencies=manifest_data.get("dependencies", []),
                sandbox_config=manifest_data.get("sandbox_config", {})
            )
            
            # Validate manifest
            errors = manifest.validate()
            if errors:
                raise PluginValidationError(f"Plugin {plugin_id} manifest validation failed: {errors}")
                
            return manifest
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise PluginValidationError(f"Plugin {plugin_id} invalid manifest: {e}")
    
    def create_plugin_api(self, plugin_id: str) -> Dict[str, Any]:
        """Create standardized API for plugin"""
        
        def register_capability(capability_id: str, capability: PluginCapability, handler: Any) -> None:
            """Register a capability with the manager"""
            if capability_id in self._capabilities:
                logger.warning(f"Capability {capability_id} already registered, overwriting")
                
            self._capabilities[capability_id] = capability
            self._capability_handlers[capability_id] = handler
            logger.info(f"Registered capability {capability_id} for plugin {plugin_id}")
        
        def log(message: str, level: str = "info") -> None:
            """Standardized logging"""
            getattr(logger, level)(f"Plugin {plugin_id}: {message}")
        
        def error(message: str, error: Optional[Exception] = None) -> None:
            """Standardized error logging"""
            logger.error(f"Plugin {plugin_id}: {message}")
            if error:
                logger.exception(error)
        
        # Build API using PluginAPIBuilder
        api_builder = PluginAPIBuilder(plugin_id)
        api_builder.with_function("log", log)
        api_builder.with_function("error", error)
        api_builder.with_register_capability(register_capability)
        
        return api_builder.build()
    
    def load_plugin(self, plugin_id: str) -> PluginInterface:
        """Load a plugin using standardized process"""
        logger.info(f"Loading plugin {plugin_id}")
        
        # Load manifest first
        manifest = self.load_manifest(plugin_id)
        
        # Check if already loaded
        if plugin_id in self._loaded_plugins:
            logger.info(f"Plugin {plugin_id} already loaded")
            return self._loaded_plugins[plugin_id]
        
        # Load plugin source code
        plugin_file = self.plugins_dir / plugin_id / f"{plugin_id}_plugin.py"
        if not plugin_file.exists():
            raise PluginLoadError(f"Plugin {plugin_id} missing {plugin_id}_plugin.py")
            
        try:
            with open(plugin_file, 'r') as f:
                source_code = f.read()
        except Exception as e:
            raise PluginLoadError(f"Failed to read plugin {plugin_id} source: {e}")
        
        # Create plugin API
        plugin_api = self.create_plugin_api(plugin_id)
        
        # Create sandbox and execute plugin
        sandbox = PluginSandbox(plugin_id, plugin_api)
        self._sandbox_cache[plugin_id] = sandbox
        
        try:
            # Execute plugin registration
            register_func = sandbox.execute_code(source_code)
            if not register_func:
                raise PluginLoadError(f"Plugin {plugin_id} did not define register_plugin function")
            
            # Call registration function
            plugin = register_func(plugin_api)
            if not isinstance(plugin, PluginInterface):
                raise PluginLoadError(f"Plugin {plugin_id} register_plugin must return PluginInterface")
            
            # Initialize plugin
            plugin.initialize(plugin_api)
            
            # Store plugin
            self._loaded_plugins[plugin_id] = plugin
            self._plugin_manifests[plugin_id] = manifest
            
            logger.info(f"Successfully loaded plugin {plugin_id}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            raise PluginLoadError(f"Plugin {plugin_id} loading failed: {e}")
    
    def unload_plugin(self, plugin_id: str) -> None:
        """Unload a plugin"""
        if plugin_id not in self._loaded_plugins:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return
            
        plugin = self._loaded_plugins[plugin_id]
        
        # Call shutdown if available
        try:
            plugin.shutdown()
        except Exception as e:
            logger.warning(f"Plugin {plugin_id} shutdown failed: {e}")
        
        # Remove capabilities
        manifest = self._plugin_manifests[plugin_id]
        for capability in manifest.capabilities:
            if capability.id in self._capabilities:
                del self._capabilities[capability.id]
            if capability.id in self._capability_handlers:
                del self._capability_handlers[capability.id]
        
        # Remove from caches
        del self._loaded_plugins[plugin_id]
        del self._plugin_manifests[plugin_id]
        if plugin_id in self._sandbox_cache:
            del self._sandbox_cache[plugin_id]
            
        logger.info(f"Unloaded plugin {plugin_id}")
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a capability"""
        if capability_id not in self._capability_handlers:
            raise ValueError(f"Capability {capability_id} not found")
        
        capability = self._capabilities[capability_id]
        handler = self._capability_handlers[capability_id]
        
        logger.info(f"Executing capability {capability_id}")
        
        try:
            result = handler(capability_id, params)
            logger.info(f"Capability {capability_id} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Capability {capability_id} execution failed: {e}")
            raise
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin IDs"""
        return list(self._loaded_plugins.keys())
    
    def get_plugin_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin manifest"""
        return self._plugin_manifests.get(plugin_id)
    
    def get_capabilities(self) -> List[PluginCapability]:
        """Get all registered capabilities"""
        return list(self._capabilities.values())
    
    def get_plugin_capabilities(self, plugin_id: str) -> List[PluginCapability]:
        """Get capabilities for a specific plugin"""
        manifest = self._plugin_manifests.get(plugin_id)
        return manifest.capabilities if manifest else []