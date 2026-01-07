"""
Pydantic models for plugin input/output validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ExampleInput(BaseModel):
    """Example input model"""
    message: str = Field(..., description="Example message")
    optional_field: Optional[str] = Field(None, description="Optional field")

class ExampleOutput(BaseModel):
    """Example output model"""
    result: str = Field(..., description="Result message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# Add more models as needed for your plugin capabilities
