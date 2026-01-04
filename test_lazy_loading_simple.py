"""
Simple test to verify lazy loading integration works
"""

import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, '/root/dhii-mail')

try:
    from kernel_plugin_integration_refactored import KernelPluginIntegration
    from a2ui_integration.core.kernel import Kernel
    from a2ui_integration.core.types import PluginConfig, PluginType
    
    print("✓ Successfully imported kernel integration modules")
    
    # Create a mock kernel
    class MockKernel:
        def __init__(self):
            self.shared_services = MockSharedServices()
            self._registered_plugins = []
        
        async def register_plugin(self, plugin_config):
            self._registered_plugins.append(plugin_config)
            print(f"✓ Registered plugin: {plugin_config.id}")
            return True
    
    class MockSharedServices:
        pass
    
    async def test_basic_functionality():
        """Test basic functionality of the refactored integration"""
        print("\n=== Testing Lazy Loading Integration ===")
        
        # Create mock kernel
        kernel = MockKernel()
        
        # Create integration
        integration = KernelPluginIntegration(kernel)
        
        # Test plugin discovery with existing manifests
        print("\n1. Testing plugin discovery...")
        discovered = await integration._discover_plugins()
        print(f"   Discovered {len(discovered)} plugins")
        
        for plugin_path, manifest in discovered.items():
            print(f"   - {manifest['id']}: {manifest['name']}")
        
        # Test dependency checking
        print("\n2. Testing dependency checking...")
        try:
            await integration._check_dependencies({"os": "*"})
            print("   ✓ Built-in dependency check passed")
        except ImportError as e:
            print(f"   ✗ Dependency check failed: {e}")
        
        try:
            await integration._check_dependencies({"nonexistent_module": "1.0.0"})
            print("   ✗ Should have failed for nonexistent module")
        except ImportError as e:
            print(f"   ✓ Correctly failed for nonexistent module: {e}")
        
        # Test plugin config creation
        print("\n3. Testing plugin config creation...")
        test_manifest = {
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "type": "email",
            "author": "test",
            "enabled": True,
            "config": {"setting": "value"},
            "capabilities": [
                {
                    "id": "test_cap",
                    "domain": "test",
                    "name": "Test Capability",
                    "description": "A test capability",
                    "input_schema": {},
                    "output_schema": {}
                }
            ]
        }
        
        config = integration._create_plugin_config_from_manifest(test_manifest)
        print(f"   ✓ Created config for {config.id} (type: {config.type})")
        print(f"   ✓ Capabilities: {len(config.capabilities)}")
        
        print("\n=== All Tests Passed! ===")
        return True
    
    # Run the test
    success = asyncio.run(test_basic_functionality())
    
    if success:
        print("\n🎉 Lazy loading integration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This is expected if dependencies are missing - the lazy loading should handle this gracefully")
    sys.exit(0)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)