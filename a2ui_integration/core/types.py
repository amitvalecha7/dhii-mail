"""
Core Kernel Types and Interfaces for dhii Mail A2UI System
Defines the foundational types and contracts for the plugin architecture
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
from pydantic import BaseModel


class PluginType(Enum):
    """Types of plugins supported by the system"""
    EMAIL = "email"
    CALENDAR = "calendar"
    TASKS = "tasks"
    CRM = "crm"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class PluginStatus(Enum):
    """Plugin lifecycle states"""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class Capability:
    """Represents a capability that a plugin provides"""
    id: str
    domain: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    side_effects: List[str]
    requires_auth: bool = False


@dataclass
class AdjacencyOperation:
    """Represents an operation in the adjacency list model"""
    operation: str  # "insert", "update", "delete"
    node_id: str
    node_type: str
    parent_id: Optional[str] = None
    properties: Dict[str, Any] = None
    position: Optional[int] = None


class A2UIComponent(BaseModel):
    """Base model for A2UI components"""
    id: str
    type: str
    properties: Dict[str, Any] = {}
    children: List['A2UIComponent'] = []
    parent_id: Optional[str] = None


class PluginConfig(BaseModel):
    """Configuration for a plugin"""
    id: str
    name: str
    version: str
    description: str
    type: PluginType
    author: str
    enabled: bool = False
    config: Dict[str, Any] = {}
    capabilities: List[Capability] = []
    dependencies: List[str] = []


class PluginInfo(BaseModel):
    """Information about an installed plugin"""
    id: str
    name: str
    version: str
    description: str
    type: PluginType
    status: PluginStatus
    installed_at: datetime
    last_updated: Optional[datetime] = None
    usage_count: int = 0
    error_count: int = 0
    config: Dict[str, Any] = {}


class DomainModule(ABC):
    """Abstract base class for domain modules (plugins)"""
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Return the domain name this module handles"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[Capability]:
        """Return list of capabilities this module provides"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the domain module"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the domain module"""
        pass
    
    @abstractmethod
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific capability"""
        pass


class KernelInterface(ABC):
    """Interface for the core kernel"""
    
    @abstractmethod
    async def register_plugin(self, plugin_config: PluginConfig) -> bool:
        """Register a new plugin"""
        pass
    
    @abstractmethod
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        pass
    
    @abstractmethod
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        pass
    
    @abstractmethod
    async def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        pass
    
    @abstractmethod
    async def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins or filter by type"""
        pass
    
    @abstractmethod
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability from any plugin"""
        pass
    
    @abstractmethod
    async def search(self, query: str, domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Universal search across enabled plugins"""
        pass


class A2UIRenderer(ABC):
    """Interface for A2UI rendering"""
    
    @abstractmethod
    def create_component(self, component_type: str, properties: Dict[str, Any]) -> A2UIComponent:
        """Create a new A2UI component"""
        pass
    
    @abstractmethod
    def build_adjacency_list(self, components: List[A2UIComponent]) -> List[AdjacencyOperation]:
        """Build adjacency list operations from components"""
        pass
    
    @abstractmethod
    def render_dashboard(self, context: Dict[str, Any]) -> List[AdjacencyOperation]:
        """Render dashboard using adjacency list operations"""
        pass