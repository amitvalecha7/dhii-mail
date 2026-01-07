# Framework 2.0 Migration Guide

## Overview

This guide provides comprehensive instructions for migrating plugins from **Framework 1.0** (using `DomainModule`) to **Framework 2.0** (using `PluginInterface`).

## Key Changes

### 1. Contract Changes

**Framework 1.0:**
```python
from a2ui_integration.core.types import DomainModule, Capability

class MyPlugin(DomainModule):
    @property
    def domain(self) -> str:
        return "my_domain"
    
    @property
    def capabilities(self) -> List[Capability]:
        return [Capability(...)]
```

**Framework 2.0:**
```python
from a2ui_integration.framework.contract import PluginInterface, PluginManifest, PluginCapability

class MyPluginV2(PluginInterface):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            id="my_plugin",
            name="My Plugin",
            version="2.0.0",
            plugin_type=PluginType.INTEGRATION,
            capabilities=[PluginCapability(...)]
        )
```

### 2. Method Signature Changes

| Framework 1.0 | Framework 2.0 |
|---------------|---------------|
| `async def initialize(self) -> bool:` | `def initialize(self, kernel_api: Dict[str, Any]) -> None:` |
| `async def shutdown(self) -> bool:` | `def shutdown(self) -> None:` |
| `async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:` | `def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:` |

### 3. Capability Changes

**Framework 1.0:**
```python
Capability(
    id="my_plugin.action",
    domain="my_plugin",
    name="My Action",
    description="Does something",
    input_schema={...},
    output_schema={...},
    side_effects=["something_happened"],
    requires_auth=True
)
```

**Framework 2.0:**
```python
PluginCapability(
    id="my_plugin.action",
    name="My Action",
    description="Does something",
    capability_type=CapabilityType.ACTION,
    input_schema={...},
    output_schema={...},
    requires_auth=True,
    timeout_seconds=30
)
```

### 4. New Features in Framework 2.0

- **Health Status**: Plugins can report their health status
- **Execution Context**: Standardized execution tracking
- **Sandbox Configuration**: Enhanced security controls
- **Pydantic Validation**: Strong typing and validation
- **Async-First Design**: Better performance and scalability

## Migration Steps

### Step 1: Update Imports

Replace Framework 1.0 imports:
```python
from a2ui_integration.core.types import DomainModule, Capability, PluginType, PluginConfig
```

With Framework 2.0 imports:
```python
from a2ui_integration.framework.contract import (
    PluginInterface, PluginManifest, PluginCapability, 
    PluginType, CapabilityType, ExecutionContext
)
from a2ui_integration.framework.types import (
    PluginHealth, HealthStatus, CapabilityExecutionResult
)
```

### Step 2: Update Class Inheritance

Change from:
```python
class MyPlugin(DomainModule):
```

To:
```python
class MyPluginV2(PluginInterface):
```

### Step 3: Replace Domain Property with Manifest

Framework 1.0:
```python
@property
def domain(self) -> str:
    return "my_plugin"
```

Framework 2.0:
```python
@property
def manifest(self) -> PluginManifest:
    return PluginManifest(
        id="my_plugin",
        name="My Plugin",
        version="2.0.0",
        plugin_type=PluginType.INTEGRATION,
        author="Your Name",
        description="Plugin description",
        capabilities=[...],
        dependencies=[],
        sandbox_config={}
    )
```

### Step 4: Convert Capabilities

Framework 1.0:
```python
@property
def capabilities(self) -> List[Capability]:
    return [
        Capability(
            id="my_plugin.action",
            domain="my_plugin",
            name="My Action",
            description="Does something",
            input_schema={...},
            output_schema={...},
            side_effects=["action_completed"],
            requires_auth=True
        )
    ]
```

Framework 2.0:
```python
@property
def manifest(self) -> PluginManifest:
    return PluginManifest(
        id="my_plugin",
        name="My Plugin",
        version="2.0.0",
        plugin_type=PluginType.INTEGRATION,
        capabilities=[
            PluginCapability(
                id="my_plugin.action",
                name="My Action",
                description="Does something",
                capability_type=CapabilityType.ACTION,
                input_schema={...},
                output_schema={...},
                requires_auth=True,
                timeout_seconds=30
            )
        ]
    )
```

### Step 5: Update Method Signatures

#### Initialize Method
Framework 1.0:
```python
async def initialize(self) -> bool:
    # Initialize plugin
    return True
```

Framework 2.0:
```python
def initialize(self, kernel_api: Dict[str, Any]) -> None:
    self._kernel_api = kernel_api
    # Initialize plugin with kernel API access
```

#### Execute Capability Method
Framework 1.0:
```python
async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    # Execute capability
    return {"result": "success"}
```

Framework 2.0:
```python
def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
    start_time = datetime.now()
    
    try:
        if capability_id == "my_plugin.action":
            result = self._execute_action(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
        
        return CapabilityExecutionResult(
            plugin_id="my_plugin",
            capability_id=capability_id,
            request_id=params.get("request_id", "unknown"),
            success=True,
            result=result,
            execution_time=(datetime.now() - start_time).total_seconds(),
            start_time=start_time,
            end_time=datetime.now()
        )
        
    except Exception as e:
        return CapabilityExecutionResult(
            plugin_id="my_plugin",
            capability_id=capability_id,
            request_id=params.get("request_id", "unknown"),
            success=False,
            error=str(e),
            execution_time=(datetime.now() - start_time).total_seconds(),
            start_time=start_time,
            end_time=datetime.now()
        )
```

### Step 6: Add Health Status

Framework 2.0 plugins should implement health status reporting:

```python
def get_health_status(self) -> PluginHealth:
    return PluginHealth(
        plugin_id="my_plugin",
        status=HealthStatus.HEALTHY,
        message="Plugin is operational",
        capabilities={
            "my_plugin.action": HealthStatus.HEALTHY,
            "my_plugin.query": HealthStatus.HEALTHY
        }
    )
```

### Step 7: Add Registration Function

Framework 2.0 plugins need a registration function:

```python
def register(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Register the plugin with Framework 2.0"""
    plugin = MyPluginV2()
    plugin.initialize(kernel_api)
    return plugin
```

## Migration Checklist

- [ ] Update imports to Framework 2.0
- [ ] Change class inheritance to PluginInterface
- [ ] Replace domain property with manifest property
- [ ] Convert capabilities to PluginCapability format
- [ ] Update initialize method signature
- [ ] Update execute_capability method signature
- [ ] Add health status reporting
- [ ] Add registration function
- [ ] Test with Framework 2.0 PluginManager
- [ ] Update plugin manifest.json if needed

## Testing Framework 2.0 Plugins

Use the Framework 2.0 PluginManager to test migrated plugins:

```python
from a2ui_integration.core.manager_v2 import PluginManagerV2
from a2ui_integration.framework.contract import PluginInterface

# Create plugin manager
manager = PluginManagerV2()

# Load Framework 2.0 plugin
plugin = manager.load_plugin("my_plugin")

# Execute capability
result = plugin.execute_capability("my_plugin.action", {"param": "value"})

# Check health status
health = plugin.get_health_status()
```

## Common Issues and Solutions

### Issue 1: Import Errors
**Problem**: Missing Framework 2.0 imports
**Solution**: Ensure all required imports are included

### Issue 2: Method Signature Mismatches
**Problem**: Framework 1.0 async methods vs Framework 2.0 sync methods
**Solution**: Remove async/await keywords and update return types

### Issue 3: Capability Type Mapping
**Problem**: Old domain-based capabilities don't map directly to new types
**Solution**: Use the migration tool's capability type mapping logic

### Issue 4: Health Status Not Implemented
**Problem**: Missing health status implementation
**Solution**: Add get_health_status method to plugin class

## Benefits of Framework 2.0

1. **Better Type Safety**: Pydantic models provide runtime validation
2. **Improved Performance**: Async-first design with better resource management
3. **Enhanced Security**: Sandboxing and capability-based access control
4. **Standardized Contracts**: Consistent plugin interface across all plugins
5. **Health Monitoring**: Built-in health status reporting
6. **Better Error Handling**: Structured error reporting with execution context

## Next Steps

1. Use the automated migration tool for initial conversion
2. Review and test migrated plugins manually
3. Update plugin manifests to Framework 2.0 format
4. Register migrated plugins with the Framework 2.0 PluginManager
5. Update documentation and examples

For additional support, refer to the Framework 2.0 specification documents in `/specs/v1/PLUGIN_FRAMEWORK_2_0_SPEC.md`.