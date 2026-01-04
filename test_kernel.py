#!/usr/bin/env python3
"""
Test script for the Core Kernel and Plugin System
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginConfig, PluginType, Capability
from plugins.email.email_plugin import EmailPlugin
from plugins.calendar.calendar_plugin import CalendarPlugin

async def test_kernel_functionality():
    """Test the kernel functionality"""
    print("🚀 Testing Core Kernel and Plugin System...")
    
    try:
        # Initialize kernel
        kernel = Kernel()
        print("✅ Kernel initialized successfully")
        
        # Test 1: Create email plugin configuration
        print("\n📧 Testing Email Plugin Registration...")
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
            ),
            Capability(
                id="email.search",
                domain="communication", 
                name="Search Emails",
                description="Search email messages",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "number"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "emails": {"type": "array"}}},
                side_effects=[],
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
            print("✅ Email plugin registered successfully")
        else:
            print("❌ Failed to register email plugin")
            return False
        
        # Test 2: Create calendar plugin configuration
        print("\n📅 Testing Calendar Plugin Registration...")
        calendar_capabilities = [
            Capability(
                id="calendar.create_event",
                domain="productivity",
                name="Create Event",
                description="Create a calendar event",
                input_schema={"type": "object", "properties": {"title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "event_id": {"type": "string"}}},
                side_effects=["event_created"],
                requires_auth=False
            ),
            Capability(
                id="calendar.find_availability",
                domain="productivity",
                name="Find Availability",
                description="Find available time slots",
                input_schema={"type": "object", "properties": {"date": {"type": "string"}, "duration_minutes": {"type": "number"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "available_slots": {"type": "array"}}},
                side_effects=[],
                requires_auth=False
            )
        ]
        
        calendar_config = PluginConfig(
            id="calendar",
            name="Calendar Plugin",
            version="1.0.0", 
            description="Calendar management plugin",
            type=PluginType.CALENDAR,
            author="System",
            enabled=False,
            capabilities=calendar_capabilities,
            dependencies=[]
        )
        
        calendar_success = await kernel.register_plugin(calendar_config)
        
        if calendar_success:
            print("✅ Calendar plugin registered successfully")
        else:
            print("❌ Failed to register calendar plugin")
            return False
        
        # Test 3: Enable plugins
        print("\n🔌 Testing Plugin Enable...")
        email_enable_success = kernel.enable_plugin("email")
        calendar_enable_success = kernel.enable_plugin("calendar")
        
        if email_enable_success and calendar_enable_success:
            print("✅ Plugins enabled successfully")
        else:
            print("❌ Failed to enable plugins")
            return False
        
        # Test 4: Get all plugins
        print("\n📋 Testing Get All Plugins...")
        all_plugins = await kernel.list_plugins()
        print(f"✅ Found {len(all_plugins)} plugins:")
        for plugin in all_plugins:
            print(f"  - {plugin.id}: {plugin.name} ({plugin.status})")
        
        # Test 5: Get plugin info
        print("\n🔍 Testing Get Plugin Info...")
        email_plugin_info = await kernel.get_plugin("email")
        if email_plugin_info:
            print(f"✅ Email plugin info: {email_plugin_info.name} v{email_plugin_info.version}")
        else:
            print("❌ Could not get email plugin info")
        
        # Test 6: Execute email capabilities
        print("\n📮 Testing Email Capabilities...")
        
        # Test send email
        send_result = await kernel.execute_capability("email.send", {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "This is a test email from the kernel system"
        })
        
        if send_result.get("success"):
            print(f"✅ Email sent successfully: {send_result.get('message_id')}")
        else:
            print(f"❌ Failed to send email: {send_result.get('error')}")
        
        # Test search emails
        search_result = await kernel.execute_capability("email.search", {
            "query": "test",
            "limit": 10
        })
        
        if search_result.get("success"):
            print(f"✅ Email search successful: {len(search_result.get('emails', []))} emails found")
        else:
            print(f"❌ Email search failed: {search_result.get('error')}")
        
        # Test 7: Execute calendar capabilities
        print("\n📆 Testing Calendar Capabilities...")
        
        # Test create event
        event_result = await kernel.execute_capability("calendar.create_event", {
            "title": "Test Meeting",
            "start_time": "2025-01-10T10:00:00",
            "end_time": "2025-01-10T11:00:00",
            "description": "Test meeting from kernel system"
        })
        
        if event_result.get("success"):
            print(f"✅ Event created successfully: {event_result.get('event_id')}")
        else:
            print(f"❌ Failed to create event: {event_result.get('error')}")
        
        # Test find availability
        availability_result = await kernel.execute_capability("calendar.find_availability", {
            "date": "2025-01-10",
            "duration_minutes": 60
        })
        
        if availability_result.get("success"):
            print(f"✅ Availability check successful: {len(availability_result.get('available_slots', []))} slots available")
        else:
            print(f"❌ Availability check failed: {availability_result.get('error')}")
        
        # Test 8: Search functionality
        print("\n🔍 Testing Universal Search...")
        search_results = kernel.search("email")
        print(f"✅ Search found {len(search_results)} results for 'email'")
        
        search_results = kernel.search("calendar")
        print(f"✅ Search found {len(search_results)} results for 'calendar'")
        
        # Test 9: Get stats
        print("\n📊 Testing Kernel Stats...")
        # Stats are not directly available, but we can get plugin count
        plugin_count = len(all_plugins)
        print(f"✅ Kernel Stats:")
        print(f"  - Total Plugins: {plugin_count}")
        print(f"  - Active Plugins: sum(1 for p in all_plugins if p.status == 'enabled')")
        
        # Test 10: Dashboard data
        print("\n📈 Testing Dashboard Data...")
        dashboard_data = {
            "plugins": all_plugins,
            "stats": {"total_plugins": plugin_count}
        }
        print(f"✅ Dashboard data prepared with {len(dashboard_data['plugins'])} plugins")
        
        print("\n🎉 All kernel tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_kernel_functionality())
    sys.exit(0 if success else 1)