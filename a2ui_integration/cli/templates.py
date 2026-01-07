"""
Framework 2.0: Plugin Templates
Templates for generating different types of plugins
"""

from a2ui_integration.framework.contract import PluginType

# Template constants - defined before the function that uses them
UI_PLUGIN_TEMPLATE = '''"""
{plugin_class} - UI plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any

class {plugin_class}(PluginInterface):
    """UI plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.UI,
            author="Plugin Author",
            description="A UI plugin for user interface components",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Render UI Component",
                    description="Render a UI component",
                    capability_type=CapabilityType.ACTION
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        # TODO: Implement UI component rendering logic
        component_type = params.get("component_type", "default")
        
        self.kernel_api["log"](f"Rendering UI component: {component_type}", "info")
        
        return {{
            "success": True,
            "component_id": f"ui_{component_type}_123",
            "html": f"<div>UI Component: {component_type}</div>",
            "message": "UI component rendered successfully"
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''

PERSISTENCE_PLUGIN_TEMPLATE = '''"""
{plugin_class} - Persistence plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any

class {plugin_class}(PluginInterface):
    """Persistence plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.PERSISTENCE,
            author="Plugin Author",
            description="A persistence plugin for data storage",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Store Data",
                    description="Store data persistently",
                    capability_type=CapabilityType.ACTION
                ),
                PluginCapability(
                    id="{plugin_name}.retrieve",
                    name="Retrieve Data",
                    description="Retrieve stored data",
                    capability_type=CapabilityType.QUERY
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        self.storage = {{}}
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        if capability_id == "{capability_id}":
            return self._store_data(params)
        elif capability_id == "{plugin_name}.retrieve":
            return self._retrieve_data(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _store_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Store data persistently"""
        # TODO: Implement data storage logic
        key = params.get("key", "default")
        value = params.get("value", "")
        
        self.kernel_api["log"](f"Storing data with key: {key}", "info")
        
        self.storage[key] = value
        
        return {{
            "success": True,
            "key": key,
            "size": len(str(value)),
            "message": "Data stored successfully"
        }}
    
    def _retrieve_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve stored data"""
        # TODO: Implement data retrieval logic
        key = params.get("key", "default")
        
        self.kernel_api["log"](f"Retrieving data with key: {key}", "info")
        
        value = self.storage.get(key)
        
        if value is None:
            return {{
                "success": False,
                "error": f"No data found for key: {key}",
                "message": "Data not found"
            }}
        
        return {{
            "success": True,
            "key": key,
            "value": value,
            "size": len(str(value)),
            "message": "Data retrieved successfully"
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''

UTILITY_PLUGIN_TEMPLATE = '''"""
{plugin_class} - Utility plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any

class {plugin_class}(PluginInterface):
    """Utility plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.UTILITY,
            author="Plugin Author",
            description="A utility plugin for helper functions",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Process Data",
                    description="Process data with utility functions",
                    capability_type=CapabilityType.TRANSFORM
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        if capability_id == "{capability_id}":
            return self._process_data(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _process_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with utility functions"""
        # TODO: Implement data processing logic
        data = params.get("data", "")
        operation = params.get("operation", "uppercase")
        
        self.kernel_api["log"](f"Processing data with operation: {operation}", "info")
        
        if operation == "uppercase":
            result = str(data).upper()
        elif operation == "lowercase":
            result = str(data).lower()
        elif operation == "reverse":
            result = str(data)[::-1]
        else:
            result = str(data)
        
        return {{
            "success": True,
            "input": data,
            "output": result,
            "operation": operation,
            "message": "Data processed successfully"
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''

def get_plugin_template(plugin_type: PluginType) -> str:
    """Get the appropriate plugin template based on type"""
    templates = {
        PluginType.INTEGRATION: INTEGRATION_PLUGIN_TEMPLATE,
        PluginType.TRANSPORT: TRANSPORT_PLUGIN_TEMPLATE,
        PluginType.INTELLIGENCE: INTELLIGENCE_PLUGIN_TEMPLATE,
        PluginType.UI: UI_PLUGIN_TEMPLATE,
        PluginType.PERSISTENCE: PERSISTENCE_PLUGIN_TEMPLATE,
        PluginType.UTILITY: UTILITY_PLUGIN_TEMPLATE,
    }
    return templates.get(plugin_type, DEFAULT_PLUGIN_TEMPLATE)

DEFAULT_PLUGIN_TEMPLATE = '''"""
{plugin_class} - Plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any

class {plugin_class}(PluginInterface):
    """Plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.{plugin_type.upper()},
            author="Plugin Author",
            description="A {plugin_type} plugin",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Example Capability",
                    description="An example capability",
                    capability_type=CapabilityType.ACTION
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        # TODO: Implement your capability logic here
        return {{"result": f"Executed {capability_id} with params: {{params}}"}}

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''

INTEGRATION_PLUGIN_TEMPLATE = '''"""
{plugin_class} - Integration plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any
import asyncio

class {plugin_class}(PluginInterface):
    """Integration plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.INTEGRATION,
            author="Plugin Author",
            description="An integration plugin for external services",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Connect to Service",
                    description="Connect to external service",
                    capability_type=CapabilityType.ACTION,
                    requires_auth=True
                ),
                PluginCapability(
                    id="{plugin_name}.test_connection",
                    name="Test Connection",
                    description="Test connection to external service",
                    capability_type=CapabilityType.QUERY
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        self.connection = None
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        if capability_id == "{capability_id}":
            return self._connect_to_service(params)
        elif capability_id == "{plugin_name}.test_connection":
            return self._test_connection(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _connect_to_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to external service"""
        # TODO: Implement service connection logic
        self.kernel_api["log"]("Connecting to external service...", "info")
        
        # Simulate connection
        connection_params = params.get("connection", {{}})
        
        return {{
            "success": True,
            "message": "Connected to external service",
            "connection_id": "conn_12345"
        }}
    
    def _test_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to external service"""
        # TODO: Implement connection test logic
        return {{
            "status": "connected",
            "response_time": 150,
            "healthy": True
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''

TRANSPORT_PLUGIN_TEMPLATE = '''"""
{plugin_class} - Transport plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any, AsyncGenerator
import asyncio

class {plugin_class}(PluginInterface):
    """Transport plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.TRANSPORT,
            author="Plugin Author",
            description="A transport plugin for data streaming",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Send Data",
                    description="Send data through transport",
                    capability_type=CapabilityType.ACTION
                ),
                PluginCapability(
                    id="{plugin_name}.receive_stream",
                    name="Receive Stream",
                    description="Receive data stream",
                    capability_type=CapabilityType.STREAM
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        self.transport = None
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        if capability_id == "{capability_id}":
            return self._send_data(params)
        elif capability_id == "{plugin_name}.receive_stream":
            return self._receive_stream(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _send_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send data through transport"""
        # TODO: Implement data sending logic
        data = params.get("data", "")
        destination = params.get("destination", "")
        
        self.kernel_api["log"](f"Sending data to {destination}", "info")
        
        return {{
            "success": True,
            "message": "Data sent successfully",
            "bytes_sent": len(data.encode() if isinstance(data, str) else data)
        }}
    
    async def _receive_stream(self, params: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Receive data stream"""
        # TODO: Implement stream receiving logic
        source = params.get("source", "")
        
        self.kernel_api["log"](f"Receiving stream from {source}", "info")
        
        # Simulate streaming data
        for i in range(5):
            yield {{
                "chunk_id": i,
                "data": f"Chunk {{i}} from {source}",
                "timestamp": asyncio.get_event_loop().time()
            }}
            await asyncio.sleep(0.1)

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''

INTELLIGENCE_PLUGIN_TEMPLATE = '''"""
{plugin_class} - Intelligence plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any

class {plugin_class}(PluginInterface):
    """Intelligence plugin implementation"""
    
    def __init__(self):
        self._manifest = PluginManifest(
            id="{plugin_name}",
            name="{plugin_class}",
            version="1.0.0",
            plugin_type=PluginType.INTELLIGENCE,
            author="Plugin Author",
            description="An intelligence plugin for AI/ML operations",
            capabilities=[
                PluginCapability(
                    id="{capability_id}",
                    name="Process Intelligence",
                    description="Process data with intelligence algorithms",
                    capability_type=CapabilityType.TRANSFORM
                ),
                PluginCapability(
                    id="{plugin_name}.analyze",
                    name="Analyze Data",
                    description="Analyze data and provide insights",
                    capability_type=CapabilityType.QUERY
                )
            ]
        )
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self.kernel_api = kernel_api
        self.plugin_id = kernel_api.get("plugin_id", "{plugin_name}")
        self.models = {{}}
        
        # Register capabilities
        for capability in self._manifest.capabilities:
            kernel_api["register_capability"](
                capability.id,
                capability,
                self._execute_capability
            )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        return self._execute_capability(capability_id, params)
    
    def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Capability execution logic"""
        if capability_id == "{capability_id}":
            return self._process_intelligence(params)
        elif capability_id == "{plugin_name}.analyze":
            return self._analyze_data(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _process_intelligence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with intelligence algorithms"""
        # TODO: Implement intelligence processing logic
        input_data = params.get("data", "")
        algorithm = params.get("algorithm", "default")
        
        self.kernel_api["log"](f"Processing intelligence with algorithm: {{algorithm}}", "info")
        
        # Simulate intelligence processing
        processed_data = {{
            "input_length": len(str(input_data)),
            "algorithm_used": algorithm,
            "confidence_score": 0.85,
            "processed_at": "2024-01-01T00:00:00Z"
        }}
        
        return {{
            "success": True,
            "data": processed_data,
            "message": "Intelligence processing completed"
        }}
    
    def _analyze_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and provide insights"""
        # TODO: Implement data analysis logic
        data = params.get("data", [])
        analysis_type = params.get("type", "summary")
        
        self.kernel_api["log"](f"Analyzing data with type: {{analysis_type}}", "info")
        
        # Simulate data analysis
        insights = {{
            "total_items": len(data),
            "analysis_type": analysis_type,
            "key_findings": [
                "Finding 1",
                "Finding 2",
                "Finding 3"
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2"
            ]
        }}
        
        return {{
            "success": True,
            "insights": insights,
            "message": "Data analysis completed"
        }}

def register_plugin(kernel_api: Dict[str, Any]) -> {plugin_class}:
    """Plugin registration function"""
    plugin = {plugin_class}()
    plugin.initialize(kernel_api)
    return plugin
'''