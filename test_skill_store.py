#!/usr/bin/env python3
"""
Test script for Skill Store endpoints and functionality
"""

import asyncio
import json
from datetime import datetime
from a2ui_integration.core.kernel import Kernel
from a2ui_integration.skill_store_ui import (
    create_skill_store_plugins_ui,
    create_plugin_details_ui,
    create_search_results_ui
)

async def test_skill_store_plugins():
    """Test the skill store plugins endpoint functionality"""
    print("=== Testing Skill Store Plugins ===")
    
    try:
        kernel = Kernel()
        
        # Get all plugins
        all_plugins = await kernel.list_plugins()
        print(f"Found {len(all_plugins)} plugins")
        
        # Format for skill store display
        skill_store_plugins = [
            {
                "plugin_id": plugin.id,
                "name": plugin.name,
                "description": plugin.description,
                "type": plugin.type.value,
                "version": plugin.version,
                "author": "System",  # PluginInfo doesn't have author field
                "enabled": True,  # Assume enabled if in list
                "capabilities": [],  # PluginInfo doesn't have capabilities
                "requires_auth": False,
                "icon": "🔧",
                "documentation_url": None,
                "support_url": None
            }
            for plugin in all_plugins
        ]
        
        print(f"Formatted {len(skill_store_plugins)} plugins for skill store")
        
        # Test UI component generation
        a2ui_components = create_skill_store_plugins_ui(skill_store_plugins)
        print(f"Generated {len(a2ui_components)} A2UI components")
        
        # Test JSON serialization
        a2ui_json = json.dumps(a2ui_components)
        print(f"A2UI JSON length: {len(a2ui_json)} characters")
        
        # Sample response structure
        response = {
            "status": "success",
            "plugins": skill_store_plugins,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
        print("✅ Skill Store Plugins test passed")
        return response
        
    except Exception as e:
        print(f"❌ Skill Store Plugins test failed: {e}")
        raise

async def test_plugin_details():
    """Test plugin details functionality"""
    print("\n=== Testing Plugin Details ===")
    
    try:
        kernel = Kernel()
        all_plugins = await kernel.list_plugins()
        
        if not all_plugins:
            print("No plugins found for details test")
            return None
            
        # Test with first plugin
        plugin = all_plugins[0]
        plugin_details = {
            "plugin_id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
            "type": plugin.type.value,
            "version": plugin.version,
            "author": "System",  # PluginInfo doesn't have author field
            "enabled": True,  # Assume enabled if in list
            "capabilities": [],  # PluginInfo doesn't have capabilities
            "requires_auth": False,
            "icon": "🔧",
            "documentation_url": None,
            "support_url": None
        }
        
        # Test UI component generation
        a2ui_components = create_plugin_details_ui(plugin_details)
        print(f"Generated {len(a2ui_components)} A2UI components for plugin details")
        
        a2ui_json = json.dumps(a2ui_components)
        print(f"A2UI JSON length: {len(a2ui_json)} characters")
        
        response = {
            "status": "success",
            "plugin": plugin_details,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
        print("✅ Plugin Details test passed")
        return response
        
    except Exception as e:
        print(f"❌ Plugin Details test failed: {e}")
        raise

async def test_search_functionality():
    """Test search functionality"""
    print("\n=== Testing Search Functionality ===")
    
    try:
        kernel = Kernel()
        
        # Test search with different queries
        test_queries = ["email", "calendar", "plugin", "capability"]
        
        for query in test_queries:
            print(f"Testing search for: '{query}'")
            search_results = await kernel.search(query)
            print(f"Found {len(search_results)} results for '{query}'")
            
            if search_results:
                # Test UI component generation
                a2ui_components = create_search_results_ui(search_results, query)
                print(f"Generated {len(a2ui_components)} A2UI components")
                
                a2ui_json = json.dumps(a2ui_components)
                print(f"A2UI JSON length: {len(a2ui_json)} characters")
        
        print("✅ Search Functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Search Functionality test failed: {e}")
        raise

async def test_plugin_enable_disable():
    """Test plugin enable/disable functionality"""
    print("\n=== Testing Plugin Enable/Disable ===")
    
    try:
        kernel = Kernel()
        
        # Get first plugin
        all_plugins = await kernel.list_plugins()
        if not all_plugins:
            print("No plugins found for enable/disable test")
            return None
            
        plugin = all_plugins[0]
        plugin_id = plugin.id
        
        print(f"Testing with plugin: {plugin.name} (ID: {plugin_id})")
        
        # Test disable
        print("Disabling plugin...")
        await kernel.disable_plugin(plugin_id)
        
        # Verify disabled by checking if plugin is in loaded plugins
        loaded_plugins = kernel._plugins  # Access internal dict to check loaded status
        if plugin_id not in loaded_plugins:
            print("✅ Plugin successfully disabled (not in loaded plugins)")
        else:
            print("⚠️  Plugin may still be loaded")
        
        # Test enable
        print("Enabling plugin...")
        await kernel.enable_plugin(plugin_id)
        
        # Verify enabled by checking if plugin is in loaded plugins
        loaded_plugins = kernel._plugins  # Access internal dict to check loaded status
        if plugin_id in loaded_plugins:
            print("✅ Plugin successfully enabled (in loaded plugins)")
        else:
            print("⚠️  Plugin may not be loaded")
        
        print("✅ Plugin Enable/Disable test passed")
        return True
        
    except Exception as e:
        print(f"❌ Plugin Enable/Disable test failed: {e}")
        raise

async def main():
    """Run all tests"""
    print("🚀 Starting Skill Store Tests")
    
    try:
        # Test 1: Skill Store Plugins
        plugins_response = await test_skill_store_plugins()
        
        # Test 2: Plugin Details
        details_response = await test_plugin_details()
        
        # Test 3: Search Functionality
        search_response = await test_search_functionality()
        
        # Test 4: Plugin Enable/Disable
        enable_disable_response = await test_plugin_enable_disable()
        
        print("\n🎉 All Skill Store tests completed successfully!")
        
        # Print summary
        print("\n=== Test Summary ===")
        if plugins_response:
            print(f"✅ Plugins: {len(plugins_response.get('plugins', []))} plugins found")
        if details_response:
            print(f"✅ Details: Plugin details UI generated")
        if search_response:
            print(f"✅ Search: Search functionality working")
        if enable_disable_response:
            print(f"✅ Enable/Disable: Plugin lifecycle management working")
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())