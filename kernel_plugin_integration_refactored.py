"""
Refactored Kernel Plugin Integration with Lazy Loading & Dynamic Discovery
Addresses Issue #34: Refactor Kernel Bridge - Lazy Loading & Dynamic Discovery
"""

import logging
import asyncio
import importlib
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.shared_services import EventType, Event
from a2ui_integration.core.types import PluginConfig, PluginType, Capability, PluginStatus

logger = logging.getLogger(__name__)


class KernelPluginIntegration:
    """Integrates plugins with lazy loading and dynamic discovery"""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.shared_services = kernel.shared_services
        self._plugin_instances: Dict[str, Any] = {}
        self._manifest_cache: Dict[str, Dict[str, Any]] = {}
        
    async def integrate_all_plugins(self):
        """Integrate all plugins with lazy loading and dynamic discovery"""
        logger.info("Starting plugin integration with lazy loading...")
        
        # Discover plugins dynamically
        discovered_plugins = await self._discover_plugins()
        
        # Register each discovered plugin with lazy loading
        for plugin_path, manifest in discovered_plugins.items():
            try:
                await self._register_plugin_with_manifest(plugin_path, manifest)
            except Exception as e:
                logger.error(f"Failed to register plugin {manifest.get('id', 'unknown')}: {e}")
                # Continue with other plugins instead of crashing
                continue
        
        logger.info(f"Plugin integration completed. Registered {len(self._plugin_instances)} plugins.")
    
    async def _discover_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Discover plugins by scanning for manifest.json files"""
        discovered = {}
        plugins_dir = Path("/root/dhii-mail/plugins")
        
        if not plugins_dir.exists():
            logger.warning(f"Plugins directory {plugins_dir} does not exist")
            return discovered
        
        # Scan for manifest.json files in plugin directories
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            discovered[str(plugin_dir)] = manifest
                            logger.info(f"Discovered plugin: {manifest.get('id', 'unknown')} in {plugin_dir}")
                    except (json.JSONDecodeError, IOError) as e:
                        logger.error(f"Failed to read manifest from {manifest_path}: {e}")
                        continue
        
        return discovered
    
    async def _register_plugin_with_manifest(self, plugin_path: str, manifest: Dict[str, Any]):
        """Register a plugin using its manifest configuration"""
        plugin_id = manifest.get('id')
        if not plugin_id:
            raise ValueError("Plugin manifest missing 'id' field")
        
        # Check if plugin is enabled
        if not manifest.get('enabled', True):
            logger.info(f"Plugin {plugin_id} is disabled, skipping registration")
            return
        
        # Lazy load plugin dependencies
        try:
            await self._check_dependencies(manifest.get('dependencies', {}))
        except ImportError as e:
            logger.error(f"Plugin {plugin_id} dependencies not satisfied: {e}")
            return
        
        # Create plugin config from manifest
        plugin_config = self._create_plugin_config_from_manifest(manifest)
        
        # Register with kernel
        await self.kernel.register_plugin(plugin_config)
        
        # Initialize plugin instance with lazy loading
        await self._initialize_plugin_instance(plugin_path, manifest)
        
        # Register UI routes if present
        await self._register_ui_routes(manifest)
        
        logger.info(f"Successfully registered plugin: {plugin_id}")
    
    async def _check_dependencies(self, dependencies: Dict[str, str]):
        """Check if plugin dependencies are available"""
        for package, version_spec in dependencies.items():
            try:
                importlib.import_module(package)
                logger.debug(f"Dependency {package} satisfied")
            except ImportError:
                raise ImportError(f"Required dependency '{package}' not found")
    
    def _create_plugin_config_from_manifest(self, manifest: Dict[str, Any]) -> PluginConfig:
        """Create PluginConfig from manifest data"""
        # Convert capabilities from manifest format
        capabilities = []
        for cap_data in manifest.get('capabilities', []):
            capability = Capability(
                id=cap_data['id'],
                domain=cap_data['domain'],
                name=cap_data['name'],
                description=cap_data['description'],
                input_schema=cap_data.get('input_schema', {}),
                output_schema=cap_data.get('output_schema', {}),
                side_effects=cap_data.get('side_effects', []),
                requires_auth=cap_data.get('requires_auth', False)
            )
            capabilities.append(capability)
        
        # Determine plugin type
        plugin_type = PluginType(manifest.get('type', 'general'))
        
        return PluginConfig(
            id=manifest['id'],
            name=manifest['name'],
            version=manifest['version'],
            description=manifest['description'],
            type=plugin_type,
            author=manifest.get('author', 'unknown'),
            enabled=manifest.get('enabled', True),
            config=manifest.get('config', {}),
            capabilities=capabilities,
            dependencies=manifest.get('dependencies', {}).keys()
        )
    
    async def _initialize_plugin_instance(self, plugin_path: str, manifest: Dict[str, Any]):
        """Initialize plugin instance with lazy loading"""
        plugin_id = manifest['id']
        
        try:
            # Dynamically import plugin module
            plugin_module_path = plugin_path.replace('/root/dhii-mail/', '').replace('/', '.')
            plugin_module = importlib.import_module(f"{plugin_module_path}.{manifest['id']}")
            
            # Get plugin class/instance
            if hasattr(plugin_module, 'Plugin'):
                plugin_class = getattr(plugin_module, 'Plugin')
                plugin_instance = plugin_class()
                self._plugin_instances[plugin_id] = plugin_instance
                logger.debug(f"Initialized plugin instance: {plugin_id}")
            else:
                logger.warning(f"Plugin {plugin_id} does not have a Plugin class")
                
        except Exception as e:
            logger.error(f"Failed to initialize plugin instance {plugin_id}: {e}")
            # Don't crash - just log the error and continue
    
    async def _register_ui_routes(self, manifest: Dict[str, Any]):
        """Register UI routes from manifest"""
        ui_routes = manifest.get('ui_routes', [])
        if not ui_routes:
            return
        
        # Register routes with AppShell if available
        if hasattr(self.kernel, 'app_shell'):
            for route in ui_routes:
                try:
                    await self.kernel.app_shell.register_route(
                        path=route['path'],
                        name=route['name'],
                        component=route['component'],
                        description=route.get('description', '')
                    )
                    logger.info(f"Registered UI route: {route['path']}")
                except Exception as e:
                    logger.error(f"Failed to register UI route {route['path']}: {e}")
                    continue
    
    def get_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        """Get a registered plugin instance"""
        return self._plugin_instances.get(plugin_id)
    
    def list_registered_plugins(self) -> List[str]:
        """List all registered plugin IDs"""
        return list(self._plugin_instances.keys())


# Legacy support for existing integration method
async def integrate_all_plugins(kernel: Kernel):
    """Legacy integration function for backward compatibility"""
    integration = KernelPluginIntegration(kernel)
    await integration.integrate_all_plugins()
    return integration