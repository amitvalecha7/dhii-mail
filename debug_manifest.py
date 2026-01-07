#!/usr/bin/env python3
"""Debug manifest loading"""

import sys
sys.path.insert(0, '/root/dhii-mail')

from a2ui_integration.core.manager_v2 import PluginManagerV2

def debug_manifest():
    """Debug manifest loading"""
    print("🔍 Debugging manifest loading...")
    
    manager = PluginManagerV2(plugins_dir="plugins")
    
    # Load manifest for test_plugin
    try:
        manifest = manager.load_manifest('test_plugin')
        print(f"✅ Loaded manifest for test_plugin")
        print(f"   Plugin ID: {manifest.id}")
        print(f"   Plugin name: {manifest.name}")
        print(f"   Capabilities: {len(manifest.capabilities)}")
        
        for i, cap in enumerate(manifest.capabilities):
            print(f"   Capability {i}: {cap} (type: {type(cap)})")
            print(f"     ID: {cap.id}")
            print(f"     Name: {cap.name}")
            
        # Store in manager
        manager.plugin_manifests['test_plugin'] = manifest
        
        # Retrieve from manager
        retrieved = manager.plugin_manifests['test_plugin']
        print(f"\n✅ Retrieved manifest from manager")
        print(f"   Capabilities: {len(retrieved.capabilities)}")
        
        for cap in retrieved.capabilities:
            print(f"   Capability: {cap} (type: {type(cap)})")
            print(f"     ID: {cap.id}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_manifest()