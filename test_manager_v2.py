#!/usr/bin/env python3
"""
Test PluginManagerV2 functionality
"""

import sys
import os
sys.path.insert(0, '/root/dhii-mail')

from a2ui_integration.core.manager_v2 import PluginManagerV2

def test_plugin_manager():
    """Test PluginManagerV2 functionality"""
    print("🧪 Testing PluginManagerV2...")
    
    # Initialize manager
    manager = PluginManagerV2(plugins_dir="plugins")
    
    # Test discovery
    print("\n📋 Discovering plugins...")
    discovered = manager.discover_plugins()
    print(f"Found {len(discovered)} plugins: {discovered}")
    
    # Test loading
    if 'test_plugin' in discovered:
        print("\n🔌 Loading test_plugin...")
        try:
            plugin = manager.load_plugin('test_plugin')
            print(f"✅ Successfully loaded test_plugin")
            
            # Test capability execution
            print("\n⚡ Testing capability execution...")
            result = manager.execute_capability('test_plugin', 'test_plugin.example', {})
            print(f"✅ Capability executed successfully: {result}")
            
            # Get plugin info
            print("\n📊 Plugin info:")
            info = manager.get_plugin_info('test_plugin')
            print(f"   Name: {info['name']}")
            print(f"   Version: {info['version']}")
            print(f"   Health: {info['health']}")
            print(f"   Capabilities: {len(info['capabilities'])}")
            
        except Exception as e:
            print(f"❌ Error loading test_plugin: {e}")
            import traceback
            traceback.print_exc()
    
    # Test email plugin
    if 'email' in discovered:
        print("\n📧 Loading email plugin...")
        try:
            plugin = manager.load_plugin('email')
            print(f"✅ Successfully loaded email plugin")
            
            # Test connection capability
            print("\n🔗 Testing email connection...")
            test_params = {
                "smtp_config": {
                    "host": "smtp.gmail.com",
                    "port": 587,
                    "use_tls": True
                }
            }
            result = manager.execute_capability('email', 'email.test_connection', test_params)
            print(f"✅ Connection test result: {result}")
            
        except Exception as e:
            print(f"❌ Error loading email plugin: {e}")
            import traceback
            traceback.print_exc()
    
    # List all capabilities
    print("\n📋 All available capabilities:")
    all_caps = manager.get_all_capabilities()
    for plugin_id, caps in all_caps.items():
        print(f"   {plugin_id}:")
        for cap in caps:
            print(f"     - {cap['id']}: {cap['name']} ({cap['type']})")
    
    print("\n✅ PluginManagerV2 test completed!")

if __name__ == "__main__":
    test_plugin_manager()