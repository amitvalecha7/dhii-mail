"""
Core Kernel and A2UI System for dhii Mail
Provides the foundational architecture for plugin-based functionality
"""

from .types import (
    PluginType, PluginStatus, Capability, AdjacencyOperation, 
    A2UIComponent, PluginConfig, PluginInfo, DomainModule, KernelInterface, A2UIRenderer
)
from .kernel import Kernel
from .renderer import A2UIAdjacencyRenderer

__all__ = [
    # Types
    'PluginType',
    'PluginStatus', 
    'Capability',
    'AdjacencyOperation',
    'A2UIComponent',
    'PluginConfig',
    'PluginInfo',
    'DomainModule',
    'KernelInterface',
    'A2UIRenderer',
    
    # Core implementations
    'Kernel',
    'A2UIAdjacencyRenderer'
]