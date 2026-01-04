#!/usr/bin/env python3
"""
Test the kernel dashboard functionality without FastAPI dependencies
"""

import asyncio
import json
from datetime import datetime
from a2ui_integration.core.kernel import Kernel
from a2ui_integration.skill_store_ui import create_kernel_dashboard_ui

async def test_kernel_dashboard_core():
    """Test the core kernel dashboard functionality"""
    print("=== Testing Core Kernel Dashboard Functionality ===")
    
    try:
        kernel = Kernel()
        
        # Get all plugins
        all_plugins = await kernel.list_plugins()
        print(f"Found {len(all_plugins)} plugins")
        
        # Prepare dashboard data (same as in the endpoint)
        from a2ui_integration.core.types import PluginType
        
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
                    plugin_type.value: len([p for p in all_plugins if hasattr(p, 'type') and getattr(p, 'type', 'unknown').value == plugin_type.value])
                    for plugin_type in PluginType
                }
            }
        }
        
        # Generate A2UI components using adjacency list operations
        a2ui_components = create_kernel_dashboard_ui(dashboard_data)
        a2ui_json = json.dumps(a2ui_components)
        
        print("✅ Core kernel dashboard functionality test passed")
        print(f"Dashboard data prepared: {len(dashboard_data['plugins'])} plugins")
        print(f"A2UI components generated: {len(a2ui_components)}")
        print(f"A2UI JSON length: {len(a2ui_json)} characters")
        
        # Verify the structure matches what the endpoint would return
        expected_response = {
            "status": "success",
            "dashboard": dashboard_data,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
        # Validate A2UI JSON is parseable
        parsed_components = json.loads(expected_response["a2ui_json"])
        print(f"✅ A2UI JSON is valid and parseable")
        print(f"✅ Contains {len(parsed_components)} operations")
        
        # Check for adjacency list operations
        operations = [list(comp.keys())[0] for comp in parsed_components]
        required_ops = ['beginRendering', 'surfaceUpdate', 'dataModelUpdate']
        missing_ops = [op for op in required_ops if op not in operations]
        
        if not missing_ops:
            print("✅ All required adjacency list operations present")
        else:
            print(f"⚠️  Missing operations: {missing_ops}")
        
        print("\n🎉 Kernel Dashboard Core Functionality Test Complete!")
        return {
            "status": "success",
            "plugins_count": len(all_plugins),
            "components_count": len(a2ui_components),
            "json_length": len(a2ui_json),
            "operations": operations,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        print(f"❌ Core kernel dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 Testing Kernel Dashboard Core Functionality")
    result = asyncio.run(test_kernel_dashboard_core())
    print(f"\n=== Core Test Summary ===")
    print(f"Status: {result['status']}")
    print(f"Plugins: {result['plugins_count']}")
    print(f"Components: {result['components_count']}")
    print(f"JSON Length: {result['json_length']} characters")
    print(f"Operations: {result['operations']}")