"""
Plugin Framework 2.0: Core interfaces and contracts.

This module provides the fundamental abstractions that all plugins must implement
to ensure compatibility with the kernel runtime.
"""

from .contract import PluginInterface, ExecutionContext
from .types import PluginCapability, HealthStatus, PluginType, CapabilityType
from .exceptions import PluginError, PluginValidationError, PluginExecutionError

__all__ = [
    'PluginInterface',
    'ExecutionContext', 
    'PluginCapability',
    'HealthStatus',
    'PluginType',
    'CapabilityType',
    'PluginError',
    'PluginValidationError',
    'PluginExecutionError'
]