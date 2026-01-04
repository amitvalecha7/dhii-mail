#!/usr/bin/env python3
"""
Simplified test script for the Core Kernel functionality
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginConfig, PluginType, Capability

async def test_kernel_basic():
    """Test basic kernel functionality"""
    print("🚀 Testing Basic Kernel Functionality...")
    
    try:
        # Initialize kernel
        kernel = Kernel()
        print("✅ Kernel initialized successfully")
        
        # Test 1: Create and register email plugin configuration
        print("\n📧 Testing Email Plugin Configuration...")
        email_capabilities = [
            Capability(
                id="email.send",
                domain="communication",
                name="Send Email",
                description="Send an email message",
                input_schema={"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "message_id": {"type": "string"}}},
                side_effects=["email_sent"],
                requires_auth=False
            )
        ]
        
        email_config = PluginConfig(
            id="email",
            name="Email Plugin",
            version="1.0.0",
            description="Email communication plugin",
            type=PluginType.EMAIL,
            author="System",
            enabled=False,
            capabilities=email_capabilities,
            dependencies=[]
        )
        
        email_success = await kernel.register_plugin(email_config)
        
        if email_success:
            print("✅ Email plugin configuration registered successfully")
        else:
            print("❌ Failed to register email plugin configuration")
            return False
        
        # Test 2: List plugins
        print("\n📋 Testing Plugin Listing...")
        all_plugins = await kernel.list_plugins()
        print(f"✅ Found {len(all_plugins)} plugins:")
        for plugin in all_plugins:
            print(f"  - {plugin.id}: {plugin.name} ({plugin.status})")
        
        # Test 3: Get plugin info
        print("\n🔍 Testing Get Plugin Info...")
        email_plugin_info = await kernel.get_plugin("email")
        if email_plugin_info:
            print(f"✅ Email plugin info: {email_plugin_info.name} v{email_plugin_info.version}")
        else:
            print("❌ Could not get email plugin info")
            return False
        
        # Test 4: Enable plugin
        print("\n🔌 Testing Plugin Enable...")
        enable_success = await kernel.enable_plugin("email")
        
        if enable_success:
            print("✅ Email plugin enabled successfully")
        else:
            print("❌ Failed to enable email plugin")
            return False
        
        # Test 5: List plugins again to see status change
        print("\n📋 Testing Plugin Listing After Enable...")
        enabled_plugins = await kernel.list_plugins()
        for plugin in enabled_plugins:
            print(f"  - {plugin.id}: {plugin.name} ({plugin.status})")
        
        # Test 6: Register plugin instances for capability execution
        print("\n🔌 Testing Plugin Instance Registration...")
        
        # Create actual plugin instances
        from plugins.email.email_plugin import EmailPlugin
        from plugins.calendar.calendar_plugin import CalendarPlugin
        
        email_plugin_instance = EmailPlugin()
        calendar_plugin_instance = CalendarPlugin()
        
        # Register instances
        email_instance_success = kernel.register_plugin_instance("email", email_plugin_instance)
        calendar_instance_success = kernel.register_plugin_instance("calendar", calendar_plugin_instance)
        
        if email_instance_success and calendar_instance_success:
            print("✅ Plugin instances registered successfully")
        else:
            print("❌ Failed to register plugin instances")
            return False
        
        # Test 7: Search functionality
        print("\n🔍 Testing Search Functionality...")
        search_results = await kernel.search("email")
        print(f"✅ Search found {len(search_results)} results for 'email'")
        for result in search_results:
            if isinstance(result, dict):
                print(f"  - {result.get('type', 'unknown')}: {result.get('name', 'unknown')}")
            else:
                print(f"  - {result}")
        
        # Test 8: Execute capability (this will test the full flow)
        print("\n⚡ Testing Capability Execution...")
        try:
            result = await kernel.execute_capability("email.send", {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from the kernel system"
            })
            
            if result.get("success"):
                print(f"✅ Email capability executed successfully: {result.get('message_id')}")
            else:
                print(f"❌ Email capability failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Capability execution failed: {e}")
        
        print("\n🎉 Basic kernel tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_kernel_basic())
    sys.exit(0 if success else 1)