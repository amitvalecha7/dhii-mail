import logging
import builtins

logger = logging.getLogger(__name__)

class SecurityViolation(Exception):
    """Raised when a plugin attempts a restricted operation."""
    pass

def create_safe_import(plugin_id: str):
    """
    Creates a safe import function for a specific plugin.
    """
    def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        """
        Replacement for __import__ that only allows whitelisted modules and internal plugin modules.
        """
        ALLOWED_MODULES = {
            'json', 'datetime', 're', 'math', 'random', 'logging', 'uuid',
            'imaplib', 'email', 'ssl', 'socket', 'binascii', 'base64', 'quopri',
            'time', 'os', 'smtplib', 'typing', 'dataclasses', 'enum', 'pydantic',
            'a2ui_integration.core.types', 'a2ui_integration.core', 'a2ui_integration',
            'sqlite3', 'asyncio', 'pathlib', 'urllib', 'http', 'ftplib', 'gzip',
            'zipfile', 'tarfile', 'csv', 'xml', 'html', 'json', 'pickle',
            'configparser', 'secrets', 'hashlib', 'hmac'
        }
        
        # Allow standard library modules
        if name in ALLOWED_MODULES or name.split('.')[0] in ALLOWED_MODULES:
            return builtins.__import__(name, globals, locals, fromlist, level)
        
        # Handle relative imports (level > 0) - resolve them to absolute imports
        if level > 0:
            # Resolve relative import to absolute import
            # For example: "from .services.sync_service import CalendarSyncService" 
            # becomes "from calendar.services.sync_service import CalendarSyncService"
            if name:  # If name is provided, it's a relative import like "from .module import something"
                resolved_name = f"{plugin_id}.{name}"
                # Check if this resolved import is allowed
                if resolved_name.startswith(f'{plugin_id}.'):
                    try:
                        return builtins.__import__(resolved_name, globals, locals, fromlist, level)
                    except ModuleNotFoundError:
                        # If the resolved import fails, try the original relative import
                        # This handles cases where the kernel has already pre-processed the imports
                        return builtins.__import__(name, globals, locals, fromlist, level)
            else:  # If name is empty, it's a relative import like "from . import something"
                # This is a relative import to the plugin's __init__.py
                return builtins.__import__(plugin_id, globals, locals, fromlist, level)
        
        # Allow internal plugin module imports (e.g., email.email_plugin, calendar.calendar_plugin)
        # These are plugin-specific internal modules that should be allowed
        if name.startswith(f'{plugin_id}.'):
            # This is an internal plugin module import like "email.email_plugin"
            return builtins.__import__(name, globals, locals, fromlist, level)
        
        # Allow direct plugin module imports for backward compatibility
        plugin_internal_modules = ['email_plugin', 'calendar_plugin', 'meeting_plugin', 'deal_flow_crm']
        if name in plugin_internal_modules or name.startswith('services.'):
            return builtins.__import__(name, globals, locals, fromlist, level)
        
        # Allow a2ui_integration imports for plugin framework
        if name.startswith('a2ui_integration'):
            return builtins.__import__(name, globals, locals, fromlist, level)
        
        # Allow imports of internal modules if passed in context (handled by loader)
        # But generally block everything else
        logger.warning(f"Plugin attempted to import restricted module: {name}")
        raise SecurityViolation(f"Import of '{name}' is strictly forbidden by Glass Wall.")
    
    return safe_import

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
        # Create safe import function for this plugin
        safe_import_func = create_safe_import(self.plugin_id)
        
        # Start with a clean slate
        import builtins as _builtins
        
        # Use a more complete builtins dictionary, but replace dangerous functions
        safe_builtins = dict(_builtins.__dict__)
        
        # Remove dangerous builtins
        dangerous_builtins = [
            '__import__', 'exec', 'eval', 'compile', 'open', 'input',
            '__loader__', '__spec__', 'breakpoint', 'copyright', 'credits', 'license'
        ]
        
        for dangerous in dangerous_builtins:
            if dangerous in safe_builtins:
                del safe_builtins[dangerous]
        
        # Replace the dangerous __import__ with our safe version
        safe_builtins['__import__'] = safe_import_func
        
        safe_globals = {
            "__name__": self.plugin_id,  # Add __name__ for proper module execution
            "__file__": f"plugins/{self.plugin_id}/__init__.py",  # Add __file__ for module context
            "__package__": self.plugin_id,  # Add __package__ for relative imports
            "__builtins__": safe_builtins,
            # Inject the Kernel API
            "kernel": self.api_context
        }
        return safe_globals

    def execute_code(self, source_code: str):
        """
        Executes the source code within the restricted scope.
        """
        restricted_globals = self.create_restricted_globals()
        
        # Debug: Log what kernel API is being provided
        logger.info(f"Sandbox: Providing kernel API to plugin {self.plugin_id}: {list(restricted_globals.get('kernel', {}).keys())}")
        
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
