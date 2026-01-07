"""
Framework 2.0: Plugin Template Generator
Standardized plugin templates for consistent development
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Standard plugin templates by type
PLUGIN_TEMPLATES = {
    "integration": '''"""
{plugin_name} Integration Plugin
Framework 2.0 Standard Plugin
"""

from a2ui_integration.core.plugin_contract import (
    PluginInterface, PluginManifest, PluginCapability, 
    PluginType, CapabilityType, register_plugin
)
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class {class_name}Plugin(PluginInterface):
    """{plugin_name} Integration Plugin"""
    
    def __init__(self):
        self._manifest = None
        self._kernel_api = None
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self._kernel_api = kernel_api
        self._manifest = self._create_manifest()
        logger.info(f"{class_name} plugin initialized")
    
    def _create_manifest(self) -> PluginManifest:
        """Create plugin manifest"""
        return PluginManifest(
            id="{plugin_id}",
            name="{plugin_name}",
            version="1.0.0",
            plugin_type=PluginType.INTEGRATION,
            author="dhii-team",
            description="{description}",
            capabilities=[
                PluginCapability(
                    id="{plugin_id}.connect",
                    name="Connect",
                    description="Connect to {plugin_name} service",
                    capability_type=CapabilityType.ACTION,
                    input_schema={{
                        "type": "object",
                        "properties": {{
                            "credentials": {{"type": "object"}}
                        }},
                        "required": ["credentials"]
                    }},
                    output_schema={{
                        "type": "object",
                        "properties": {{
                            "status": {{"type": "string"}},
                            "connection_id": {{"type": "string"}}
                        }}
                    }}
                )
            ]
        )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a capability"""
        if capability_id == "{plugin_id}.connect":
            return self._handle_connect(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _handle_connect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle connect capability"""
        self._kernel_api["log"](f"Connecting to {plugin_name}...")
        
        # TODO: Implement actual connection logic
        return {{
            "status": "connected",
            "connection_id": "test_connection_123"
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Standard registration function"""
    plugin = {class_name}Plugin()
    plugin.initialize(kernel_api)
    
    # Register capabilities
    for capability in plugin.manifest.capabilities:
        kernel_api["register_capability"](
            capability.id,
            capability,
            plugin.execute_capability
        )
    
    return plugin
''',

    "transport": '''"""
{plugin_name} Transport Plugin
Framework 2.0 Standard Plugin
"""

from a2ui_integration.core.plugin_contract import (
    PluginInterface, PluginManifest, PluginCapability,
    PluginType, CapabilityType, register_plugin
)
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class {class_name}Plugin(PluginInterface):
    """{plugin_name} Transport Plugin"""
    
    def __init__(self):
        self._manifest = None
        self._kernel_api = None
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self._kernel_api = kernel_api
        self._manifest = self._create_manifest()
        logger.info(f"{class_name} plugin initialized")
    
    def _create_manifest(self) -> PluginManifest:
        """Create plugin manifest"""
        return PluginManifest(
            id="{plugin_id}",
            name="{plugin_name}",
            version="1.0.0",
            plugin_type=PluginType.TRANSPORT,
            author="dhii-team",
            description="{description}",
            capabilities=[
                PluginCapability(
                    id="{plugin_id}.send",
                    name="Send",
                    description="Send data via {plugin_name}",
                    capability_type=CapabilityType.ACTION,
                    input_schema={{
                        "type": "object",
                        "properties": {{
                            "data": {{"type": "string"}},
                            "destination": {{"type": "string"}}
                        }},
                        "required": ["data", "destination"]
                    }},
                    output_schema={{
                        "type": "object",
                        "properties": {{
                            "status": {{"type": "string"}},
                            "message_id": {{"type": "string"}}
                        }}
                    }}
                )
            ]
        )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a capability"""
        if capability_id == "{plugin_id}.send":
            return self._handle_send(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _handle_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send capability"""
        self._kernel_api["log"](f"Sending via {plugin_name}...")
        
        # TODO: Implement actual send logic
        return {{
            "status": "sent",
            "message_id": "msg_123"
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Standard registration function"""
    plugin = {class_name}Plugin()
    plugin.initialize(kernel_api)
    
    # Register capabilities
    for capability in plugin.manifest.capabilities:
        kernel_api["register_capability"](
            capability.id,
            capability,
            plugin.execute_capability
        )
    
    return plugin
''',

    "intelligence": '''"""
{plugin_name} Intelligence Plugin
Framework 2.0 Standard Plugin
"""

from a2ui_integration.core.plugin_contract import (
    PluginInterface, PluginManifest, PluginCapability,
    PluginType, CapabilityType, register_plugin
)
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class {class_name}Plugin(PluginInterface):
    """{plugin_name} Intelligence Plugin"""
    
    def __init__(self):
        self._manifest = None
        self._kernel_api = None
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self._kernel_api = kernel_api
        self._manifest = self._create_manifest()
        logger.info(f"{class_name} plugin initialized")
    
    def _create_manifest(self) -> PluginManifest:
        """Create plugin manifest"""
        return PluginManifest(
            id="{plugin_id}",
            name="{plugin_name}",
            version="1.0.0",
            plugin_type=PluginType.INTELLIGENCE,
            author="dhii-team",
            description="{description}",
            capabilities=[
                PluginCapability(
                    id="{plugin_id}.analyze",
                    name="Analyze",
                    description="Analyze data with {plugin_name}",
                    capability_type=CapabilityType.QUERY,
                    input_schema={{
                        "type": "object",
                        "properties": {{
                            "data": {{"type": "string"}},
                            "analysis_type": {{"type": "string"}}
                        }},
                        "required": ["data"]
                    }},
                    output_schema={{
                        "type": "object",
                        "properties": {{
                            "analysis": {{"type": "object"}},
                            "confidence": {{"type": "number"}}
                        }}
                    }}
                )
            ]
        )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a capability"""
        if capability_id == "{plugin_id}.analyze":
            return self._handle_analyze(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _handle_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analyze capability"""
        self._kernel_api["log"](f"Analyzing with {plugin_name}...")
        
        # TODO: Implement actual analysis logic
        return {{
            "analysis": {{"result": "sample_analysis"}},
            "confidence": 0.85
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Standard registration function"""
    plugin = {class_name}Plugin()
    plugin.initialize(kernel_api)
    
    # Register capabilities
    for capability in plugin.manifest.capabilities:
        kernel_api["register_capability"](
            capability.id,
            capability,
            plugin.execute_capability
        )
    
    return plugin
'''
}

class PluginTemplateGenerator:
    """Generate standardized plugin templates"""
    
    @staticmethod
    def generate_plugin(plugin_id: str, plugin_type: str, name: str, 
                       description: str, author: str = "dhii-team") -> Dict[str, str]:
        """Generate complete plugin template"""
        
        if plugin_type not in PLUGIN_TEMPLATES:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        
        # Generate class name from plugin_id
        class_name = "".join(word.capitalize() for word in plugin_id.split("_"))
        
        # Generate plugin code
        plugin_code = PLUGIN_TEMPLATES[plugin_type].format(
            plugin_id=plugin_id,
            plugin_name=name,
            class_name=class_name,
            description=description
        )
        
        # Generate manifest
        manifest = {
            "id": plugin_id,
            "name": name,
            "version": "1.0.0",
            "plugin_type": plugin_type,
            "author": author,
            "description": description,
            "capabilities": [],  # Will be populated from plugin code
            "dependencies": [],
            "sandbox_config": {
                "allowed_modules": ["logging", "typing"],
                "max_memory_mb": 100,
                "timeout_seconds": 30
            }
        }
        
        return {
            "plugin_code": plugin_code,
            "manifest": manifest,
            "files": {
                f"{plugin_id}_plugin.py": plugin_code,
                "manifest.json": json.dumps(manifest, indent=2)
            }
        }
    
    @staticmethod
    def create_plugin_directory(plugin_id: str, template_data: Dict[str, str], 
                              base_path: Optional[Path] = None) -> Path:
        """Create plugin directory with all files"""
        
        if base_path is None:
            base_path = Path("plugins")
        
        plugin_dir = base_path / plugin_id
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in template_data["files"].items():
            file_path = plugin_dir / filename
            file_path.write_text(content)
            logger.info(f"Created {file_path}")
        
        return plugin_dir
    
    @staticmethod
    def validate_plugin_structure(plugin_path: Path) -> list[str]:
        """Validate plugin directory structure"""
        errors = []
        
        if not plugin_path.exists():
            errors.append(f"Plugin directory {plugin_path} does not exist")
            return errors
        
        # Check manifest.json
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            errors.append("Missing manifest.json")
        else:
            try:
                import json
                with open(manifest_path) as f:
                    manifest = json.load(f)
                
                plugin_id = manifest.get("id")
                if not plugin_id:
                    errors.append("Manifest missing 'id' field")
                else:
                    # Check plugin file
                    plugin_file = plugin_path / f"{plugin_id}_plugin.py"
                    if not plugin_file.exists():
                        errors.append(f"Missing {plugin_id}_plugin.py")
                    
                    # Check if plugin file has register_plugin function
                    if plugin_file.exists():
                        content = plugin_file.read_text()
                        if "def register_plugin(" not in content:
                            errors.append("Missing register_plugin function")
            
            except (json.JSONDecodeError, KeyError) as e:
                errors.append(f"Invalid manifest.json: {e}")
        
        return errors