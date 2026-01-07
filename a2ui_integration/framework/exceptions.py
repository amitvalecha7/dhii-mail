"""
Framework 2.0: Plugin Error Hierarchy
Standardized exception classes for plugin operations
"""

from typing import Optional, Dict, Any

class PluginError(Exception):
    """Base exception for all plugin-related errors"""
    
    def __init__(self, message: str, plugin_id: Optional[str] = None, 
                 capability_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.plugin_id = plugin_id
        self.capability_id = capability_id
        self.details = details or {}
        self.message = message
    
    def __str__(self):
        parts = [self.message]
        if self.plugin_id:
            parts.append(f"Plugin: {self.plugin_id}")
        if self.capability_id:
            parts.append(f"Capability: {self.capability_id}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)

class PluginValidationError(PluginError):
    """Raised when plugin validation fails"""
    
    def __init__(self, message: str, plugin_id: str, validation_errors: list):
        super().__init__(message, plugin_id=plugin_id)
        self.validation_errors = validation_errors
    
    def __str__(self):
        errors_str = "; ".join(self.validation_errors)
        return f"{self.message} | Validation errors: {errors_str}"

class PluginLoadError(PluginError):
    """Raised when plugin loading fails"""
    
    def __init__(self, message: str, plugin_id: str, load_error: Optional[str] = None):
        super().__init__(message, plugin_id=plugin_id)
        self.load_error = load_error

class PluginExecutionError(PluginError):
    """Raised when plugin capability execution fails"""
    
    def __init__(self, message: str, plugin_id: str, capability_id: str, 
                 execution_error: Optional[str] = None):
        super().__init__(message, plugin_id=plugin_id, capability_id=capability_id)
        self.execution_error = execution_error

class PluginNotFoundError(PluginError):
    """Raised when requested plugin is not found"""
    
    def __init__(self, plugin_id: str):
        super().__init__(f"Plugin '{plugin_id}' not found", plugin_id=plugin_id)

class CapabilityNotFoundError(PluginError):
    """Raised when requested capability is not found"""
    
    def __init__(self, plugin_id: str, capability_id: str):
        super().__init__(f"Capability '{capability_id}' not found in plugin '{plugin_id}'", 
                         plugin_id=plugin_id, capability_id=capability_id)

class PluginDependencyError(PluginError):
    """Raised when plugin dependencies are not satisfied"""
    
    def __init__(self, plugin_id: str, missing_dependencies: list):
        message = f"Missing dependencies for plugin '{plugin_id}': {', '.join(missing_dependencies)}"
        super().__init__(message, plugin_id=plugin_id)
        self.missing_dependencies = missing_dependencies

class PluginSandboxError(PluginError):
    """Raised when plugin sandbox operations fail"""
    
    def __init__(self, message: str, plugin_id: str, sandbox_error: Optional[str] = None):
        super().__init__(message, plugin_id=plugin_id)
        self.sandbox_error = sandbox_error

class PluginHealthError(PluginError):
    """Raised when plugin health check fails"""
    
    def __init__(self, message: str, plugin_id: str, health_status: Optional[str] = None):
        super().__init__(message, plugin_id=plugin_id)
        self.health_status = health_status