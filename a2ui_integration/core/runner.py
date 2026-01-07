import logging
import traceback
import asyncio
from typing import Dict, Any, Optional

from .sandbox import PluginSandbox, SecurityViolation

logger = logging.getLogger(__name__)

class PluginRunner:
    """
    Manages the execution of a single plugin.
    """
    
    def __init__(self, plugin_id: str, source_code: str, manifest: Dict[str, Any], kernel_api):
        self.plugin_id = plugin_id
        self.source_code = source_code
        self.manifest = manifest
        self.kernel_api = kernel_api
        self.sandbox = PluginSandbox(plugin_id, kernel_api)
        self.is_active = False
        self._capabilities = {} # Map capability_id -> function
    
    def update_kernel_api(self, new_kernel_api: Dict[str, Any]):
        """Update the kernel API and recreate the sandbox with the new API"""
        self.kernel_api = new_kernel_api
        self.sandbox = PluginSandbox(self.plugin_id, new_kernel_api)

    def register_capability(self, capability_id: str, capability, func):
        """
        Registers a python function as a capability handler.
        """
        logger.info(f"Runner: Registering capability {capability_id} for plugin {self.plugin_id}")
        self._capabilities[capability_id] = func

    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """
        Executes a registered capability.
        """
        if capability_id not in self._capabilities:
            raise ValueError(f"Capability {capability_id} not registered in plugin {self.plugin_id}")
            
        handler = self._capabilities[capability_id]
        
        try:
            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                return await handler(params)
            else:
                return handler(params)
        except Exception as e:
            logger.error(f"Runner: Error executing capability {capability_id}: {e}")
            raise

    def load_and_register(self) -> bool:
        """
        Loads the plugin code in the sandbox and calls its 'register' function.
        """
        logger.info(f"Runner: Loading plugin {self.plugin_id}...")
        
        try:
            # 1. Execute in Sandbox
            register_func = self.sandbox.execute_code(self.source_code)
            
            if not register_func:
                return False
                
            # 2. Call Register (Pass the restricted API)
            try:
                register_func(self.kernel_api)
                self.is_active = True
                logger.info(f"Runner: Plugin {self.plugin_id} successfully registered.")
                return True
            except Exception as e:
                logger.error(f"Runner: Plugin {self.plugin_id} threw error during registration: {e}")
                logger.debug(traceback.format_exc())
                return False

        except SecurityViolation:
            logger.critical(f"Runner: Plugin {self.plugin_id} BLOCKED by Security Policy.")
            return False
        except Exception as e:
            logger.error(f"Runner: Fatal error running plugin {self.plugin_id}: {e}")
            return False

    def unload(self):
        """
        Cleanup logic (if needed).
        """
        self.is_active = False
        logger.info(f"Runner: Plugin {self.plugin_id} unloaded.")
