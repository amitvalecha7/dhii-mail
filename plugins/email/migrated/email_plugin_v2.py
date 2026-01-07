from a2ui_integration.framework.contract import PluginInterface, PluginManifest, PluginCapability, PluginType, CapabilityType, ExecutionContext
from a2ui_integration.framework.types import PluginHealth, HealthStatus, CapabilityExecutionResult
"""

def register(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Register the EmailPluginV2 with Framework 2.0"""
    plugin = EmailPluginV2()
    plugin.initialize(kernel_api)
    return plugin
