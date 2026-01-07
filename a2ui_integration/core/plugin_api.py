"""
Plugin API Builder - Decouples plugin API construction from kernel internals
"""
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PluginAPI:
    """Complete API provided to plugins for kernel interaction"""
    log: Callable
    error: Callable
    register_capability: Callable
    plugin_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for sandbox injection"""
        return {
            "log": self.log,
            "error": self.error,
            "register_capability": self.register_capability,
            "plugin_id": self.plugin_id
        }

class PluginAPIBuilder:
    """Builds plugin API incrementally without touching kernel core"""
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self._api = {
            "log": logger.info,
            "error": logger.error,
            "plugin_id": plugin_id
        }
    
    def with_register_capability(self, register_func: Callable) -> 'PluginAPIBuilder':
        """Add register_capability function to the API"""
        self._api["register_capability"] = register_func
        return self
    
    def with_function(self, name: str, func: Callable) -> 'PluginAPIBuilder':
        """Add any custom function to the API"""
        self._api[name] = func
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the complete API dictionary"""
        return self._api.copy()
    
    def build_complete(self) -> PluginAPI:
        """Build as a complete PluginAPI object"""
        return PluginAPI(
            log=self._api["log"],
            error=self._api["error"],
            register_capability=self._api.get("register_capability", lambda *args: None),
            plugin_id=self.plugin_id
        )