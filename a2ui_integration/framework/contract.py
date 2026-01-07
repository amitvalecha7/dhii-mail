"""
Framework 2.0: Core Plugin Contracts
Standardized contracts for plugin development - NEVER CHANGE
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

class PluginType(Enum):
    """Standardized plugin types"""
    INTEGRATION = "integration"
    TRANSPORT = "transport" 
    INTELLIGENCE = "intelligence"
    UI = "ui"
    PERSISTENCE = "persistence"
    UTILITY = "utility"

class CapabilityType(Enum):
    """Standardized capability types"""
    ACTION = "action"
    QUERY = "query"
    STREAM = "stream"
    TRANSFORM = "transform"
    VALIDATE = "validate"

@dataclass
class PluginCapability:
    """Standardized capability definition"""
    id: str  # Unique capability ID: "plugin_id.capability_name"
    name: str  # Human readable name
    description: str
    capability_type: CapabilityType
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    requires_auth: bool = False
    rate_limit: Optional[int] = None  # requests per minute
    timeout_seconds: int = 30

@dataclass 
class PluginManifest:
    """Plugin manifest - defines plugin metadata"""
    id: str  # Plugin ID (must match directory name)
    name: str  # Human readable name
    version: str  # Semantic version
    plugin_type: PluginType
    author: str
    description: str
    capabilities: List[PluginCapability]
    dependencies: List[str] = field(default_factory=list)  # Other plugin IDs
    sandbox_config: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate manifest - returns list of errors"""
        errors = []
        
        if not self.id or not self.id.replace('_', '').replace('-', '').isalnum():
            errors.append("Plugin ID must be alphanumeric with underscores/dashes only")
            
        if not self.capabilities:
            errors.append("Plugin must define at least one capability")
            
        capability_ids = [cap.id for cap in self.capabilities]
        if len(capability_ids) != len(set(capability_ids)):
            errors.append("Capability IDs must be unique")
            
        for cap in self.capabilities:
            if not cap.id.startswith(f"{self.id}."):
                errors.append(f"Capability {cap.id} must start with plugin ID {self.id}")
                
        return errors

@dataclass
class ExecutionContext:
    """Execution context for plugin capabilities"""
    plugin_id: str
    capability_id: str
    request_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[float] = None
    timeout_seconds: int = 30

class PluginInterface(ABC):
    """
    Standard contract ALL plugins must implement
    This interface is NEVER CHANGED - only extended
    """
    
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Plugin manifest with metadata and capabilities"""
        pass
    
    @abstractmethod
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API access"""
        pass
    
    @abstractmethod
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        pass
    
    def shutdown(self) -> None:
        """Optional cleanup when plugin is unloaded"""
        pass

class PluginAPIInterface(ABC):
    """Interface for plugin API - what plugins can access"""
    
    @abstractmethod
    def log(self, message: str, level: str = "info") -> None:
        """Log messages to kernel"""
        pass
    
    @abstractmethod
    def error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log errors to kernel"""
        pass
    
    @abstractmethod
    def register_capability(self, capability_id: str, capability: PluginCapability, 
                          handler: Callable) -> None:
        """Register a capability with the kernel"""
        pass
    
    @abstractmethod
    def get_plugin_id(self) -> str:
        """Get current plugin ID"""
        pass