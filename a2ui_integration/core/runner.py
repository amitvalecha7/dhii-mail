import logging
import traceback
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
