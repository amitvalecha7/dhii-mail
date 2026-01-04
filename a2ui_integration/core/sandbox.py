import logging
import builtins

logger = logging.getLogger(__name__)

class SecurityViolation(Exception):
    """Raised when a plugin attempts a restricted operation."""
    pass

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Replacement for __import__ that only allows whitelisted modules.
    """
    ALLOWED_MODULES = {
        'json', 'datetime', 're', 'math', 'random', 'logging', 'uuid'
    }
    
    if name in ALLOWED_MODULES:
        return builtins.__import__(name, globals, locals, fromlist, level)
    
    # Allow imports of internal modules if passed in context (handled by loader)
    # But generally block everything else
    logger.warning(f"Plugin attempted to import restricted module: {name}")
    raise SecurityViolation(f"Import of '{name}' is strictly forbidden by Glass Wall.")

class PluginSandbox:
    """
    The Glass Wall Execution Environment.
    """
    
    def __init__(self, plugin_id: str, api_context: dict):
        self.plugin_id = plugin_id
        self.api_context = api_context
        
    def create_restricted_globals(self):
        """
        Creates a dictionary of globals that effectively hides unsafe builtins.
        """
        # Start with a clean slate
        safe_globals = {
            "__builtins__": {
                # Whitelist safe builtins
                'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,
                'enumerate': enumerate, 'filter': filter, 'float': float, 'int': int,
                'len': len, 'list': list, 'map': map, 'max': max, 'min': min,
                'print': print, # Redirect to logger in future
                'range': range, 'set': set, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'zip': zip, 
                'Exception': Exception, 'ValueError': ValueError, 
                'TypeError': TypeError, 'KeyError': KeyError,
                # Crucially, we REPLACE __import__
                '__import__': safe_import
            },
            # Inject the Kernel API
            "kernel": self.api_context
        }
        return safe_globals

    def execute_code(self, source_code: str):
        """
        Executes the source code within the restricted scope.
        """
        restricted_globals = self.create_restricted_globals()
        
        try:
            # We use exec() but with our crippled globals
            exec(source_code, restricted_globals)
            
            # If the plugin defines a 'register' function, we return it
            if 'register' in restricted_globals:
                return restricted_globals['register']
            else:
                logger.warning(f"Plugin {self.plugin_id} did not define a 'register(kernel)' function.")
                return None
                
        except SecurityViolation as e:
            logger.critical(f"SECURITY ALERT: Plugin {self.plugin_id} violated Glass Wall: {e}")
            raise
        except Exception as e:
            logger.error(f"Plugin {self.plugin_id} crashed during load: {e}")
            raise
