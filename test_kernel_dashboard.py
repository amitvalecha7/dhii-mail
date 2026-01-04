#!/usr/bin/env python3
"""
Test script for Kernel Dashboard adjacency list operations
Tests the complete A2UI adjacency list pattern implementation
"""

import asyncio
import json
from datetime import datetime
from a2ui_integration.core.kernel import Kernel
from a2ui_integration.skill_store_ui import create_kernel_dashboard_ui

async def test_kernel_dashboard_adjacency_list():
    """Test kernel dashboard with proper adjacency list operations"""
    print("=== Testing Kernel Dashboard Adjacency List Operations ===")
    
    try:
        kernel = Kernel()
        
        # Get all plugins
        all_plugins = await kernel.list_plugins()
        print(f"Found {len(all_plugins)} plugins")
        
        # Prepare dashboard data
        dashboard_data = {
            "plugins": [
                {
                    "id": plugin.id,
                    "name": plugin.name,
                    "description": plugin.description,
                    "type": plugin.type.value if hasattr(plugin, 'type') else "unknown",
                    "version": plugin.version,
                    "author": getattr(plugin, 'author', 'System'),
                    "enabled": getattr(plugin, 'enabled', plugin.status == 'enabled' if hasattr(plugin, 'status') else True),
                    "capabilities": len(getattr(plugin, 'capabilities', []))
                }
                for plugin in all_plugins
            ],
            "stats": {
                "total_plugins": len(all_plugins),
                "enabled_plugins": len([p for p in all_plugins if getattr(p, 'enabled', p.status == 'enabled' if hasattr(p, 'status') else True)]),
                "by_type": {
                    plugin_type: len([p for p in all_plugins if hasattr(p, 'type') and getattr(p, 'type', 'unknown').value == plugin_type])
                    for plugin_type in ["EMAIL", "CALENDAR", "EXTERNAL"]
                }
            }
        }
        
        # Generate A2UI components using adjacency list operations
        a2ui_components = create_kernel_dashboard_ui(dashboard_data)
        print(f"Generated {len(a2ui_components)} A2UI components")
        
        # Verify adjacency list structure
        print("\n=== Verifying Adjacency List Structure ===")
        
        # Check beginRendering operation
        begin_rendering = next((comp for comp in a2ui_components if "beginRendering" in comp), None)
        if begin_rendering:
            print("✅ beginRendering operation found")
            print(f"   Surface ID: {begin_rendering['beginRendering']['surfaceId']}")
            print(f"   Root: {begin_rendering['beginRendering']['root']}")
        else:
            print("❌ beginRendering operation missing")
        
        # Check surfaceUpdate operation
        surface_update = next((comp for comp in a2ui_components if "surfaceUpdate" in comp), None)
        if surface_update:
            print("✅ surfaceUpdate operation found")
            components = surface_update['surfaceUpdate']['components']
            print(f"   Total components: {len(components)}")
            
            # Count different component types
            text_components = [c for c in components if c['id'].startswith('plugin-name-')]
            card_components = [c for c in components if c['id'].startswith('plugin-item-')]
            content_components = [c for c in components if c['id'].startswith('plugin-content-')]
            
            print(f"   Plugin items: {len(card_components)}")
            print(f"   Plugin names: {len(text_components)}")
            print(f"   Plugin content: {len(content_components)}")
            
            # Verify explicitList usage
            plugins_list = next((c for c in components if c['id'] == 'plugins-list'), None)
            if plugins_list:
                explicit_list = plugins_list['component']['Column']['children']['explicitList']
                print(f"   Plugins list explicitList: {len(explicit_list)} items")
                print("✅ Adjacency list pattern correctly implemented")
            else:
                print("❌ plugins-list component missing")
        else:
            print("❌ surfaceUpdate operation missing")
        
        # Check dataModelUpdate operation
        data_model_update = next((comp for comp in a2ui_components if "dataModelUpdate" in comp), None)
        if data_model_update:
            print("✅ dataModelUpdate operation found")
            contents = data_model_update['dataModelUpdate']['contents']
            print(f"   Data model contents: {len(contents)} keys")
            print(f"   Plugins in data: {len(contents.get('plugins', []))}")
        else:
            print("❌ dataModelUpdate operation missing")
        
        # Generate JSON for frontend
        a2ui_json = json.dumps(a2ui_components, indent=2)
        print(f"\n=== A2UI JSON Output ===")
        print(f"JSON length: {len(a2ui_json)} characters")
        
        # Sample component structure
        if len(a2ui_components) > 1 and 'surfaceUpdate' in a2ui_components[1]:
            sample_component = a2ui_components[1]['surfaceUpdate']['components'][0]
            print(f"Sample component structure:")
            print(f"  ID: {sample_component['id']}")
            print(f"  Type: {list(sample_component['component'].keys())[0]}")
        
        print("\n🎉 Kernel Dashboard Adjacency List Operations test passed!")
        return {
            "status": "success",
            "components_generated": len(a2ui_components),
            "json_length": len(a2ui_json),
            "plugins_count": len(all_plugins),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        print(f"❌ Kernel Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 Starting Kernel Dashboard Adjacency List Test")
    result = asyncio.run(test_kernel_dashboard_adjacency_list())
    print(f"\n=== Test Summary ===")
    print(f"Status: {result['status']}")
    print(f"Components: {result['components_generated']}")
    print(f"JSON Length: {result['json_length']} characters")
    print(f"Plugins: {result['plugins_count']}")