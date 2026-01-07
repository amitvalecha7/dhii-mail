"""
Framework 2.0: CLI Commands Implementation
Core command implementations for plugin development tools
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# Import V2 framework components
try:
    from ..framework.contract import PluginType, CapabilityType
    from ..framework.types import PluginManifest, PluginCapability
    from ..framework.exceptions import PluginValidationError
    from ..core.manager_v2 import PluginManagerV2
    from .templates import get_plugin_template
except ImportError:
    # Fallback for when running as module
    from framework.contract import PluginType, CapabilityType
    from framework.types import PluginManifest, PluginCapability
    from framework.exceptions import PluginValidationError
    from core.manager_v2 import PluginManagerV2
    from templates import get_plugin_template

def create_plugin_command(args) -> int:
    """Create a new plugin with V2 structure"""
    plugin_name = args.name
    plugin_type = PluginType(args.type)
    plugins_dir = Path(args.path)
    plugin_dir = plugins_dir / plugin_name
    
    print(f"Creating {plugin_type.value} plugin: {plugin_name}")
    
    # Create plugin directory
    if plugin_dir.exists():
        print(f"Error: Plugin directory '{plugin_dir}' already exists")
        return 1
    
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Generate manifest.json
        manifest = PluginManifest(
            id=plugin_name,
            name=plugin_name.replace('_', ' ').title(),
            version="1.0.0",
            plugin_type=plugin_type,
            author=args.author,
            description=args.description or f"A {plugin_type.value} plugin",
            capabilities=[
                PluginCapability(
                    id=f"{plugin_name}.example",
                    name="Example Capability",
                    description="An example capability",
                    capability_type=CapabilityType.ACTION,
                    input_schema={"type": "object", "properties": {}},
                    output_schema={"type": "object", "properties": {"result": {"type": "string"}}}
                )
            ]
        )
        
        # Write manifest.json
        manifest_file = plugin_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest.dict(), f, indent=2, default=str)
        
        # Generate plugin.py
        plugin_template = get_plugin_template(plugin_type)
        plugin_file = plugin_dir / "plugin.py"
        with open(plugin_file, 'w') as f:
            f.write(plugin_template.format(
                plugin_name=plugin_name,
                plugin_class=f"{plugin_name.title().replace('_', '')}Plugin",
                capability_id=f"{plugin_name}.example"
            ))
        
        # Generate models.py
        models_template = get_models_template(plugin_type)
        models_file = plugin_dir / "models.py"
        with open(models_file, 'w') as f:
            f.write(models_template)
        
        print(f"✅ Plugin '{plugin_name}' created successfully at {plugin_dir}")
        print(f"   - manifest.json: Plugin metadata and capabilities")
        print(f"   - plugin.py: Main plugin implementation")
        print(f"   - models.py: Pydantic models for input/output")
        print(f"\nNext steps:")
        print(f"  1. Edit the generated files to implement your plugin logic")
        print(f"  2. Run 'python -m a2ui_integration.cli validate --path {plugin_dir}' to validate")
        print(f"  3. Test your plugin with 'python -m a2ui_integration.cli test --plugin {plugin_name}'")
        
        return 0
        
    except Exception as e:
        print(f"Error creating plugin: {e}")
        # Cleanup on failure
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)
        return 1

def validate_plugin_command(args) -> int:
    """Validate plugin structure and manifest"""
    plugin_path = Path(args.path)
    
    print(f"Validating plugin: {plugin_path}")
    
    try:
        # Check required files
        manifest_file = plugin_path / "manifest.json"
        plugin_file = plugin_path / "plugin.py"
        models_file = plugin_path / "models.py"
        
        errors = []
        
        if not manifest_file.exists():
            errors.append("Missing manifest.json")
        if not plugin_file.exists():
            errors.append("Missing plugin.py")
        if not models_file.exists():
            errors.append("Missing models.py")
        
        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"   - {error}")
            return 1
        
        # Validate manifest.json
        try:
            with open(manifest_file, 'r') as f:
                manifest_data = json.load(f)
            
            # Use Pydantic validation
            manifest = PluginManifest(**manifest_data)
            
            print(f"✅ Manifest validated successfully")
            print(f"   Plugin: {manifest.name} ({manifest.version})")
            print(f"   Type: {manifest.plugin_type.value}")
            print(f"   Capabilities: {len(manifest.capabilities)}")
            
            for cap in manifest.capabilities:
                print(f"   - {cap.id}: {cap.name} ({cap.capability_type.value})")
            
            # Additional strict validation
            if args.strict:
                strict_errors = []
                
                # Check plugin.py syntax
                try:
                    with open(plugin_file, 'r') as f:
                        compile(f.read(), str(plugin_file), 'exec')
                except SyntaxError as e:
                    strict_errors.append(f"Syntax error in plugin.py: {e}")
                
                # Check models.py syntax
                try:
                    with open(models_file, 'r') as f:
                        compile(f.read(), str(models_file), 'exec')
                except SyntaxError as e:
                    strict_errors.append(f"Syntax error in models.py: {e}")
                
                if strict_errors:
                    print("\n⚠️  Strict validation warnings:")
                    for error in strict_errors:
                        print(f"   - {error}")
            
            return 0
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in manifest.json: {e}")
            return 1
        except Exception as e:
            print(f"❌ Manifest validation failed: {e}")
            return 1
            
    except Exception as e:
        print(f"Error validating plugin: {e}")
        return 1

def list_plugins_command(args) -> int:
    """List plugins"""
    plugins_dir = Path(args.plugins_dir)
    
    try:
        manager = PluginManagerV2(plugins_dir=str(plugins_dir))
        
        if args.all:
            # List all discovered plugins
            discovered = manager.discover_plugins()
            print(f"Discovered plugins ({len(discovered)}):")
            
            for plugin_id in discovered:
                try:
                    manifest = manager.load_manifest(plugin_id)
                    status = "✅" if plugin_id in manager.loaded_plugins else "⏸️"
                    print(f"  {status} {plugin_id}: {manifest.name} ({manifest.plugin_type.value})")
                except Exception as e:
                    print(f"  ❌ {plugin_id}: Error loading manifest - {e}")
        
        elif args.loaded:
            # List only loaded plugins
            loaded = manager.list_loaded_plugins()
            print(f"Loaded plugins ({len(loaded)}):")
            
            for plugin_id in loaded:
                info = manager.get_plugin_info(plugin_id)
                if info:
                    health = manager.get_plugin_health(plugin_id)
                    health_symbol = {
                        "healthy": "✅",
                        "degraded": "⚠️",
                        "unhealthy": "❌",
                        "unknown": "❓"
                    }.get(health.value, "❓")
                    
                    print(f"  {health_symbol} {plugin_id}: {info['name']} ({info['type']})")
                    print(f"     Capabilities: {len(info['capabilities'])}")
        
        else:
            # Default: show summary
            discovered = manager.discover_plugins()
            loaded = manager.list_loaded_plugins()
            
            print(f"Plugin Summary:")
            print(f"  Discovered: {len(discovered)}")
            print(f"  Loaded: {len(loaded)}")
            print(f"  Available capabilities: {len(manager.get_all_capabilities())}")
            
            if loaded:
                print(f"\nLoaded plugins:")
                for plugin_id in loaded:
                    info = manager.get_plugin_info(plugin_id)
                    if info:
                        print(f"  - {plugin_id}: {info['name']}")
        
        return 0
        
    except Exception as e:
        print(f"Error listing plugins: {e}")
        return 1

def migrate_plugin_command(args) -> int:
    """Migrate plugin to V2 format"""
    plugin_id = args.plugin
    target_version = args.target_version
    dry_run = args.dry_run
    
    print(f"Migrating plugin '{plugin_id}' to version {target_version}")
    
    if dry_run:
        print("🔍 DRY RUN MODE - no changes will be made")
    
    # This would implement migration logic from V1 to V2
    # For now, just show what would be changed
    
    changes = [
        "Create manifest.json with V2 schema",
        "Update plugin.py to implement PluginInterface",
        "Create models.py with Pydantic models",
        "Update imports to use a2ui_integration.framework",
        "Add capability registration using register_capability()",
        "Implement initialize() and execute_capability() methods"
    ]
    
    print(f"Migration changes needed:")
    for i, change in enumerate(changes, 1):
        print(f"  {i}. {change}")
    
    if not dry_run:
        print("\n⚠️  Migration not yet implemented - use dry-run mode to see required changes")
        return 1
    
    return 0

def bundle_plugin_command(args) -> int:
    """Bundle plugin for distribution"""
    plugin_id = args.plugin
    output_dir = Path(args.output)
    compress = args.compress
    
    print(f"Bundling plugin '{plugin_id}'")
    
    # This would implement bundling logic
    # For now, just show what would be bundled
    
    bundle_contents = [
        "manifest.json",
        "plugin.py", 
        "models.py",
        "README.md (if exists)",
        "requirements.txt (if exists)"
    ]
    
    print(f"Bundle contents:")
    for item in bundle_contents:
        print(f"  - {item}")
    
    print(f"Output directory: {output_dir}")
    if compress:
        print("Compression: enabled")
    
    print("\n⚠️  Bundling not yet implemented")
    return 1

def test_plugin_command(args) -> int:
    """Test plugin capabilities"""
    plugin_id = args.plugin
    capability_id = args.capability
    params_str = args.params
    
    try:
        params = json.loads(params_str) if params_str else {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON parameters: {e}")
        return 1
    
    print(f"Testing plugin '{plugin_id}'")
    if capability_id:
        print(f"Capability: {capability_id}")
    print(f"Parameters: {params}")
    
    try:
        manager = PluginManagerV2()
        
        # Load the plugin
        print("Loading plugin...")
        plugin = manager.load_plugin(plugin_id)
        print(f"✅ Plugin loaded successfully")
        
        if capability_id:
            # Test specific capability
            print(f"Testing capability '{capability_id}'...")
            result = manager.execute_capability(plugin_id, capability_id, params)
            print(f"✅ Capability executed successfully")
            print(f"Result: {result}")
        else:
            # Test all capabilities
            manifest = manager.plugin_manifests[plugin_id]
            print(f"Testing all {len(manifest.capabilities)} capabilities...")
            
            for cap in manifest.capabilities:
                try:
                    print(f"  Testing {cap.id}...")
                    result = manager.execute_capability(plugin_id, cap.id, {})
                    print(f"  ✅ {cap.id}: Success")
                except Exception as e:
                    print(f"  ❌ {cap.id}: Failed - {e}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Plugin test failed: {e}")
        return 1

def get_models_template(plugin_type: PluginType) -> str:
    """Get models.py template for plugin type"""
    return '''"""
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
'''

# Import templates from templates module
try:
    from .templates import get_plugin_template
except ImportError:
    # Fallback template
    def get_plugin_template(plugin_type: PluginType) -> str:
        return '''"""
{plugin_class} - {plugin_type} plugin implementation
"""

from a2ui_integration.framework import PluginInterface, PluginManifest, PluginCapability
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any

class {plugin_class}(PluginInterface):
    """{plugin_type} plugin implementation"""
    
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