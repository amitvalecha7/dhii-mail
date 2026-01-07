#!/usr/bin/env python3
"""
Test script for Kernel with PluginManagerV2 integration
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from a2ui_integration.core.kernel import Kernel

async def test_kernel():
    """Test the kernel with PluginManagerV2"""
    print("🧪 Testing Kernel with PluginManagerV2...")
    
    # Initialize kernel
    kernel = Kernel()
    
    try:
        # Initialize kernel
        await kernel.initialize()
        print("✅ Kernel initialized successfully")
        
        # Test plugin discovery
        print("\n📋 Discovering plugins...")
        plugins = kernel.plugin_manager.discover_plugins()
        print(f"Found {len(plugins)} plugins: {plugins}")
        
        # Test loading a plugin
        if 'test_plugin' in plugins:
            print("\n🔌 Loading test_plugin...")
            plugin = kernel.plugin_manager.load_plugin('test_plugin')
            print(f"✅ Loaded plugin: {plugin.manifest.name} v{plugin.manifest.version}")
            
            # Test capability execution
            print("\n⚡ Testing capability execution...")
            result = kernel.plugin_manager.execute_capability(
                'test_plugin', 
                'test_plugin.example', 
                {}
            )
            print(f"✅ Capability executed: {result}")
        
        # Test email plugin
        if 'email' in plugins:
            print("\n📧 Loading email plugin...")
            plugin = kernel.plugin_manager.load_plugin('email')
            print(f"✅ Loaded plugin: {plugin.manifest.name} v{plugin.manifest.version}")
            
            # Test email connection
            print("\n🔗 Testing email connection...")
            result = kernel.plugin_manager.execute_capability(
                'email',
                'email.test_connection',
                {}
            )
            print(f"✅ Connection test: {result}")
        
        print("\n✅ Kernel test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing kernel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kernel())