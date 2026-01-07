"""
Framework 2.0: Core Types and Pydantic Models
Standardized types for plugin validation and serialization
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

# Import V2 framework enums
from .contract import PluginType, CapabilityType

class HealthStatus(str, Enum):
    """Plugin health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class PluginType(str, Enum):
    """Standardized plugin types"""
    INTEGRATION = "integration"
    TRANSPORT = "transport" 
    INTELLIGENCE = "intelligence"
    UI = "ui"
    PERSISTENCE = "persistence"
    UTILITY = "utility"

class CapabilityType(str, Enum):
    """Standardized capability types"""
    ACTION = "action"
    QUERY = "query"
    STREAM = "stream"
    TRANSFORM = "transform"
    VALIDATE = "validate"

class PluginCapability(BaseModel):
    """Standardized capability definition with Pydantic validation"""
    id: str = Field(..., description="Unique capability ID: plugin_id.capability_name")
    name: str = Field(..., description="Human readable name")
    description: str = Field(..., description="Capability description")
    capability_type: CapabilityType = Field(..., description="Type of capability")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for input validation")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for output validation")
    requires_auth: bool = Field(default=False, description="Whether capability requires authentication")
    rate_limit: Optional[int] = Field(default=None, description="Requests per minute limit")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Timeout in seconds (1-300)")
    
    @validator('capability_type', pre=True)
    def parse_capability_type(cls, v):
        """Parse capability type from string to enum"""
        if isinstance(v, str):
            try:
                return CapabilityType(v)
            except ValueError:
                raise ValueError(f"Invalid capability type: {v}")
        return v
    
    @validator('id')
    def validate_capability_id(cls, v):
        """Validate capability ID format"""
        # Basic validation - capability ID should be non-empty and reasonable format
        if not v or len(v.strip()) == 0:
            raise ValueError("Capability ID cannot be empty")
        return v

class PluginManifest(BaseModel):
    """Plugin manifest with Pydantic validation"""
    id: str = Field(..., description="Plugin ID (must match directory name)")
    name: str = Field(..., description="Human readable name")
    version: str = Field(..., description="Semantic version")
    plugin_type: PluginType = Field(..., description="Type of plugin")
    author: str = Field(..., description="Plugin author")
    description: str = Field(..., description="Plugin description")
    capabilities: List[PluginCapability] = Field(..., description="Plugin capabilities")
    dependencies: List[str] = Field(default_factory=list, description="Other plugin IDs this depends on")
    sandbox_config: Dict[str, Any] = Field(default_factory=dict, description="Sandbox configuration")
    
    @validator('plugin_type', pre=True)
    def parse_plugin_type(cls, v):
        """Parse plugin type from string to enum"""
        if isinstance(v, str):
            try:
                return PluginType(v)
            except ValueError:
                raise ValueError(f"Invalid plugin type: {v}")
        return v
    
    @validator('id')
    def validate_plugin_id(cls, v):
        """Validate plugin ID format"""
        if not v or not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Plugin ID must be alphanumeric with underscores/dashes only")
        return v
    
    @validator('capabilities', pre=True)
    def validate_capabilities(cls, v):
        """Validate capabilities list and convert dicts to PluginCapability objects"""
        if not v:
            raise ValueError("Plugin must define at least one capability")
        
        # Convert dicts to PluginCapability objects if needed
        converted_capabilities = []
        for cap_data in v:
            if isinstance(cap_data, dict):
                # Convert dict to PluginCapability
                converted_capabilities.append(PluginCapability(**cap_data))
            elif isinstance(cap_data, PluginCapability):
                # Already a PluginCapability object
                converted_capabilities.append(cap_data)
            else:
                raise ValueError(f"Invalid capability type: {type(cap_data)}")
        
        # Check for duplicate capability IDs
        capability_ids = [cap.id for cap in converted_capabilities]
        if len(capability_ids) != len(set(capability_ids)):
            raise ValueError("Capability IDs must be unique")
        
        return converted_capabilities

class ExecutionContext(BaseModel):
    """Execution context for plugin capabilities"""
    plugin_id: str = Field(..., description="Plugin ID")
    capability_id: str = Field(..., description="Capability ID")
    request_id: str = Field(..., description="Unique request ID")
    user_id: Optional[str] = Field(default=None, description="User ID if authenticated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    start_time: Optional[datetime] = Field(default=None, description="Execution start time")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Timeout in seconds")

class PluginHealth(BaseModel):
    """Plugin health status"""
    plugin_id: str = Field(..., description="Plugin ID")
    status: HealthStatus = Field(..., description="Health status")
    last_check: datetime = Field(default_factory=datetime.now, description="Last health check time")
    message: Optional[str] = Field(default=None, description="Health status message")
    capabilities: Dict[str, HealthStatus] = Field(default_factory=dict, description="Capability health status")

class PluginLoadResult(BaseModel):
    """Result of plugin loading operation"""
    plugin_id: str = Field(..., description="Plugin ID")
    success: bool = Field(..., description="Whether loading was successful")
    manifest: Optional[PluginManifest] = Field(default=None, description="Loaded manifest")
    error: Optional[str] = Field(default=None, description="Error message if loading failed")
    load_time: float = Field(..., description="Time taken to load in seconds")

class CapabilityExecutionResult(BaseModel):
    """Result of capability execution"""
    plugin_id: str = Field(..., description="Plugin ID")
    capability_id: str = Field(..., description="Capability ID")
    request_id: str = Field(..., description="Request ID")
    success: bool = Field(..., description="Whether execution was successful")
    result: Optional[Any] = Field(default=None, description="Execution result")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    start_time: datetime = Field(..., description="Execution start time")
    end_time: datetime = Field(..., description="Execution end time")