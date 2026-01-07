"""
Framework 2.0: Plugin Manager V2
Advanced plugin lifecycle management with V2 contracts
"""

import os
import json
import logging
import asyncio
import importlib.util
import time
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

# Import V2 framework components
from ..framework.contract import PluginInterface
from ..framework.types import PluginManifest, PluginCapability, PluginLoadResult, CapabilityExecutionResult, ExecutionContext, HealthStatus
from ..framework.exceptions import (
    PluginError, PluginValidationError, PluginLoadError, PluginNotFoundError,
    CapabilityNotFoundError, PluginDependencyError
)
from ..framework.telemetry import get_telemetry

# Get telemetry instance
telemetry = get_telemetry()
from .sandbox import PluginSandbox
from .plugin_api import PluginAPIBuilder

logger = logging.getLogger(__name__)

class PluginManagerV2:
    """
    V2 Plugin Manager - Advanced plugin lifecycle management
    
    Responsibilities:
    - Plugin discovery and validation
    - Secure sandboxed loading
    - Capability execution management
    - Health monitoring
    - Dependency resolution
    """
    
    def __init__(self, plugins_dir: str = "plugins", sandbox_config: Optional[Dict] = None):
        self.plugins_dir = Path(plugins_dir)
        self.sandbox_config = sandbox_config or {}
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_manifests: Dict[str, PluginManifest] = {}
        self.plugin_capabilities: Dict[str, Dict[str, PluginCapability]] = {}
        self.plugin_health: Dict[str, HealthStatus] = {}
        self.telemetry = get_telemetry()
        
        logger.info(f"PluginManagerV2 initialized with plugins directory: {plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory"""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist")
            return []
        
        plugins = []
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                manifest_file = item / "manifest.json"
                plugin_file = item / "plugin.py"
                
                if manifest_file.exists() and plugin_file.exists():
                    plugins.append(item.name)
                    logger.debug(f"Discovered plugin: {item.name}")
                else:
                    logger.warning(f"Plugin directory {item.name} missing required files")
        
        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins
    
    def load_manifest(self, plugin_id: str) -> PluginManifest:
        """Load and validate plugin manifest"""
        manifest_file = self.plugins_dir / plugin_id / "manifest.json"
        
        if not manifest_file.exists():
            raise PluginLoadError(f"Manifest file not found for plugin {plugin_id}", plugin_id)
        
        try:
            with open(manifest_file, 'r') as f:
                manifest_data = json.load(f)
            
            # Create manifest with Pydantic validation
            manifest = PluginManifest(**manifest_data)
            
            # Additional validation
            if manifest.id != plugin_id:
                raise PluginValidationError(
                    f"Manifest ID '{manifest.id}' does not match plugin directory name '{plugin_id}'",
                    plugin_id, ["Manifest ID mismatch"]
                )
            
            logger.info(f"Loaded manifest for plugin {plugin_id}: {manifest.name} v{manifest.version}")
            return manifest
            
        except json.JSONDecodeError as e:
            raise PluginValidationError(f"Invalid JSON in manifest: {e}", plugin_id, [str(e)])
        except Exception as e:
            raise PluginLoadError(f"Failed to load manifest: {e}", plugin_id)
    
    def validate_dependencies(self, manifest: PluginManifest) -> None:
        """Validate that all plugin dependencies are satisfied"""
        missing_deps = []
        
        for dep_id in manifest.dependencies:
            if dep_id not in self.loaded_plugins:
                missing_deps.append(dep_id)
        
        if missing_deps:
            raise PluginDependencyError(manifest.id, missing_deps)
    
    def create_plugin_api(self, plugin_id: str) -> Dict[str, Any]:
        """Create the kernel API for a plugin"""
        # Create a new API builder for this plugin
        api_builder = PluginAPIBuilder(plugin_id)
        
        # Build the complete kernel API
        kernel_api = api_builder.build()
        
        # Add plugin-specific API functions
        kernel_api.update({
            'plugin_id': plugin_id,
            'log': lambda msg, level="info": logger.log(getattr(logging, level.upper(), logging.INFO), f"[{plugin_id}] {msg}"),
            'error': lambda msg, err=None: logger.error(f"[{plugin_id}] {msg}", exc_info=err),
            'register_capability': lambda cap_id, cap, handler: self._register_plugin_capability(plugin_id, cap_id, cap, handler),
            'get_plugin_id': lambda: plugin_id,
        })
        
        return kernel_api
    
    def _register_plugin_capability(self, plugin_id: str, capability_id: str, 
                                  capability: PluginCapability, handler: callable):
        """Register a capability for a plugin"""
        if plugin_id not in self.plugin_capabilities:
            self.plugin_capabilities[plugin_id] = {}
        
        self.plugin_capabilities[plugin_id][capability_id] = capability
        logger.info(f"Registered capability {capability_id} for plugin {plugin_id}")
    
    @telemetry.instrument_plugin_load()
    def load_plugin(self, plugin_id: str) -> PluginInterface:
        """Load a plugin with full validation and sandboxing"""
        logger.info(f"Loading plugin: {plugin_id}")
        
        # Check if already loaded
        if plugin_id in self.loaded_plugins:
            logger.info(f"Plugin {plugin_id} already loaded")
            return self.loaded_plugins[plugin_id]
        
        # Load and validate manifest
        manifest = self.load_manifest(plugin_id)
        
        # Validate dependencies
        self.validate_dependencies(manifest)
        
        # Create plugin API
        plugin_api = self.create_plugin_api(plugin_id)
        
        # Load plugin implementation
        plugin_file = self.plugins_dir / plugin_id / "plugin.py"
        if not plugin_file.exists():
            raise PluginLoadError(f"Plugin file not found: {plugin_file}", plugin_id)
        
        try:
            # Create sandbox and execute plugin registration
            sandbox = PluginSandbox(plugin_id, plugin_api)
            
            with open(plugin_file, 'r') as f:
                source_code = f.read()
            
            # Execute plugin registration
            register_func = sandbox.execute_code(source_code)
            
            if not callable(register_func):
                raise PluginLoadError("Plugin registration function not callable", plugin_id)
            
            # Create plugin instance
            plugin_instance = register_func(plugin_api)
            
            if not isinstance(plugin_instance, PluginInterface):
                raise PluginLoadError("Plugin instance does not implement PluginInterface", plugin_id)
            
            # Initialize plugin
            plugin_instance.initialize(plugin_api)
            
            # Store plugin information
            self.loaded_plugins[plugin_id] = plugin_instance
            self.plugin_manifests[plugin_id] = manifest
            self.plugin_health[plugin_id] = HealthStatus.HEALTHY
            
            logger.info(f"Successfully loaded plugin {plugin_id}")
            return plugin_instance
            
        except Exception as e:
            self.plugin_health[plugin_id] = HealthStatus.UNHEALTHY
            raise PluginLoadError(f"Failed to load plugin: {e}", plugin_id)
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin and cleanup resources"""
        logger.info(f"Unloading plugin: {plugin_id}")
        
        if plugin_id not in self.loaded_plugins:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return False
        
        try:
            # Call plugin shutdown if implemented
            plugin_instance = self.loaded_plugins[plugin_id]
            if hasattr(plugin_instance, 'shutdown'):
                plugin_instance.shutdown()
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_id]
            del self.plugin_manifests[plugin_id]
            del self.plugin_health[plugin_id]
            
            if plugin_id in self.plugin_capabilities:
                del self.plugin_capabilities[plugin_id]
            
            logger.info(f"Successfully unloaded plugin {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def execute_capability(self, plugin_id: str, capability_id: str, 
                          params: Dict[str, Any]) -> Any:
        """Execute a plugin capability"""
        
        # Create instrumented function
        @telemetry.instrument_capability_execution(plugin_id, capability_id)
        def _execute():
            logger.info(f"Executing capability {plugin_id}.{capability_id}")
            
            # Check if plugin is loaded
            if plugin_id not in self.loaded_plugins:
                raise PluginNotFoundError(plugin_id)
            
            plugin_instance = self.loaded_plugins[plugin_id]
            manifest = self.plugin_manifests[plugin_id]
            
            # Find capability in manifest
            capability = None
            for cap in manifest.capabilities:
                if cap.id == capability_id:
                    capability = cap
                    break
            
            if not capability:
                raise CapabilityNotFoundError(plugin_id, capability_id)
            
            # Create execution context
            execution_context = ExecutionContext(
                plugin_id=plugin_id,
                capability_id=capability_id,
                request_id=f"{plugin_id}_{capability_id}_{int(time.time() * 1000)}",
                timeout_seconds=capability.timeout_seconds
            )
            
            # Execute capability
            result = plugin_instance.execute_capability(capability_id, params)
            
            logger.info(f"Successfully executed capability {plugin_id}.{capability_id}")
            return result
        
        try:
            return _execute()
        except Exception as e:
            logger.error(f"Failed to execute capability {plugin_id}.{capability_id}: {e}")
            raise PluginError(f"Capability execution failed: {e}", plugin_id, capability_id)
    
    def get_plugin_health(self, plugin_id: str) -> HealthStatus:
        """Get plugin health status"""
        if plugin_id not in self.plugin_health:
            return HealthStatus.UNKNOWN
        return self.plugin_health[plugin_id]
    
    def list_loaded_plugins(self) -> List[str]:
        """List all loaded plugins"""
        return list(self.loaded_plugins.keys())
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed plugin information"""
        if plugin_id not in self.loaded_plugins:
            return None
        
        manifest = self.plugin_manifests[plugin_id]
        return {
            'id': manifest.id,
            'name': manifest.name,
            'version': manifest.version,
            'type': manifest.plugin_type.value,
            'author': manifest.author,
            'description': manifest.description,
            'health': self.get_plugin_health(plugin_id).value,
            'capabilities': [
                {
                    'id': cap.id,
                    'name': cap.name,
                    'type': cap.capability_type.value,
                    'description': cap.description
                }
                for cap in manifest.capabilities
            ],
            'dependencies': manifest.dependencies
        }
    
    def get_all_capabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available capabilities across all plugins"""
        all_capabilities = {}
        
        for plugin_id, manifest in self.plugin_manifests.items():
            all_capabilities[plugin_id] = [
                {
                    'id': cap.id,
                    'name': cap.name,
                    'type': cap.capability_type.value,
                    'description': cap.description,
                    'requires_auth': cap.requires_auth,
                    'timeout_seconds': cap.timeout_seconds
                }
                for cap in manifest.capabilities
            ]
        
        return all_capabilities