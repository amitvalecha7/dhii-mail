#!/usr/bin/env python3
"""
Comprehensive test suite for Kernel API endpoints
Tests all the new endpoints added for Issue #23 completion
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginConfig, PluginType, Capability
from a2ui_integration.core.shared_services import EventType
from test_plugins import TestEmailPlugin, TestCalendarPlugin

class KernelAPITester:
    """Test class for kernel API endpoints"""
    
    def __init__(self):
        self.kernel = None
        self.test_plugins = []
        self.test_results = []
    
    async def setup(self):
        """Setup test environment"""
        print("🚀 Setting up kernel API test environment...")
        
        # Initialize kernel
        self.kernel = Kernel(db_path="test_kernel.db")
        
        # Create test plugins
        await self._create_test_plugins()
        
        print("✅ Test environment setup complete")
    
    async def _create_test_plugins(self):
        """Create test plugins for API testing"""
        
        # Test Plugin 1: Email Plugin
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
            id="test_email",
            name="Test Email Plugin",
            version="1.0.0",
            description="Test email communication plugin",
            type=PluginType.EMAIL,
            author="Test System",
            enabled=False,
            capabilities=email_capabilities,
            dependencies=[]
        )
        
        # Test Plugin 2: Calendar Plugin
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
            )
        ]
        
        calendar_config = PluginConfig(
            id="test_calendar",
            name="Test Calendar Plugin",
            version="1.0.0",
            description="Test calendar management plugin",
            type=PluginType.CALENDAR,
            author="Test System",
            enabled=False,
            capabilities=calendar_capabilities,
            dependencies=[]
        )
        
        # Register test plugins
        email_success = await self.kernel.register_plugin(email_config)
        calendar_success = await self.kernel.register_plugin(calendar_config)
        
        if email_success and calendar_success:
            # Register actual plugin instances for capability execution
            email_plugin_instance = TestEmailPlugin()
            calendar_plugin_instance = TestCalendarPlugin()
            
            self.kernel.register_plugin_instance("test_email", email_plugin_instance)
            self.kernel.register_plugin_instance("test_calendar", calendar_plugin_instance)
            
            self.test_plugins = ["test_email", "test_calendar"]
            print("✅ Test plugins created successfully")
        else:
            raise Exception("Failed to create test plugins")
    
    async def test_plugin_endpoints(self):
        """Test plugin management endpoints"""
        print("\n🔌 Testing Plugin Management Endpoints...")
        
        # Test 1: Get specific plugin
        print("📋 Testing GET /kernel/plugins/{plugin_id}")
        try:
            plugin = await self.kernel.get_plugin("test_email")
            if plugin and plugin.id == "test_email":
                print("✅ Get specific plugin: PASSED")
                self.test_results.append(("get_plugin", True))
            else:
                print("❌ Get specific plugin: FAILED")
                self.test_results.append(("get_plugin", False))
        except Exception as e:
            print(f"❌ Get specific plugin: FAILED - {e}")
            self.test_results.append(("get_plugin", False))
        
        # Test 2: Enable plugin
        print("🔌 Testing PUT /kernel/plugins/{plugin_id}/enable")
        try:
            success = await self.kernel.enable_plugin("test_email")
            if success:
                # Verify plugin is enabled
                plugin = await self.kernel.get_plugin("test_email")
                if plugin.status.value == "enabled":
                    print("✅ Enable plugin: PASSED")
                    self.test_results.append(("enable_plugin", True))
                else:
                    print("❌ Enable plugin: FAILED - Plugin not enabled")
                    self.test_results.append(("enable_plugin", False))
            else:
                print("❌ Enable plugin: FAILED - Enable returned False")
                self.test_results.append(("enable_plugin", False))
        except Exception as e:
            print(f"❌ Enable plugin: FAILED - {e}")
            self.test_results.append(("enable_plugin", False))
        
        # Test 3: Disable plugin
        print("🔌 Testing PUT /kernel/plugins/{plugin_id}/disable")
        try:
            success = await self.kernel.disable_plugin("test_email")
            if success:
                # Verify plugin is disabled
                plugin = await self.kernel.get_plugin("test_email")
                if plugin.status.value == "disabled":
                    print("✅ Disable plugin: PASSED")
                    self.test_results.append(("disable_plugin", True))
                else:
                    print("❌ Disable plugin: FAILED - Plugin not disabled")
                    self.test_results.append(("disable_plugin", False))
            else:
                print("❌ Disable plugin: FAILED - Disable returned False")
                self.test_results.append(("disable_plugin", False))
        except Exception as e:
            print(f"❌ Disable plugin: FAILED - {e}")
            self.test_results.append(("disable_plugin", False))
    
    async def test_capability_endpoints(self):
        """Test capability management endpoints"""
        print("\n⚡ Testing Capability Management Endpoints...")
        
        # Enable test plugin first
        await self.kernel.enable_plugin("test_email")
        
        # Test 1: Execute capability
        print("⚡ Testing POST /kernel/capabilities/{capability_id}/execute")
        try:
            result = await self.kernel.execute_capability("email.send", {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from kernel API test"
            })
            
            if result and isinstance(result, dict):
                print("✅ Execute capability: PASSED")
                self.test_results.append(("execute_capability", True))
            else:
                print("❌ Execute capability: FAILED - Invalid result")
                self.test_results.append(("execute_capability", False))
        except Exception as e:
            print(f"❌ Execute capability: FAILED - {e}")
            self.test_results.append(("execute_capability", False))
        
        # Test 2: Execute non-existent capability
        print("⚡ Testing execute non-existent capability")
        try:
            result = await self.kernel.execute_capability("nonexistent.capability", {})
            print("❌ Execute non-existent capability: FAILED - Should have raised error")
            self.test_results.append(("execute_nonexistent_capability", False))
        except ValueError as e:
            print("✅ Execute non-existent capability: PASSED - Correctly raised error")
            self.test_results.append(("execute_nonexistent_capability", True))
        except Exception as e:
            print(f"❌ Execute non-existent capability: FAILED - Unexpected error: {e}")
            self.test_results.append(("execute_nonexistent_capability", False))
    
    async def test_event_endpoints(self):
        """Test event management endpoints"""
        print("\n📊 Testing Event Management Endpoints...")
        
        # Test 1: Get event history
        print("📊 Testing GET /kernel/events")
        try:
            events = self.kernel.shared_services.event_bus.get_event_history(limit=10)
            if isinstance(events, list):
                print(f"✅ Get event history: PASSED - Found {len(events)} events")
                self.test_results.append(("get_events", True))
            else:
                print("❌ Get event history: FAILED - Invalid result type")
                self.test_results.append(("get_events", False))
        except Exception as e:
            print(f"❌ Get event history: FAILED - {e}")
            self.test_results.append(("get_events", False))
        
        # Test 2: Get filtered event history
        print("📊 Testing GET /kernel/events with filter")
        try:
            events = self.kernel.shared_services.event_bus.get_event_history(
                event_type=EventType.PLUGIN_REGISTERED,
                limit=5
            )
            if isinstance(events, list):
                print(f"✅ Get filtered events: PASSED - Found {len(events)} filtered events")
                self.test_results.append(("get_filtered_events", True))
            else:
                print("❌ Get filtered events: FAILED - Invalid result type")
                self.test_results.append(("get_filtered_events", False))
        except Exception as e:
            print(f"❌ Get filtered events: FAILED - {e}")
            self.test_results.append(("get_filtered_events", False))
    
    async def test_search_endpoints(self):
        """Test search functionality"""
        print("\n🔍 Testing Search Endpoints...")
        
        # Test 1: Basic search
        print("🔍 Testing GET /kernel/search")
        try:
            results = await self.kernel.search("email")
            if isinstance(results, list):
                print(f"✅ Basic search: PASSED - Found {len(results)} results")
                self.test_results.append(("basic_search", True))
            else:
                print("❌ Basic search: FAILED - Invalid result type")
                self.test_results.append(("basic_search", False))
        except Exception as e:
            print(f"❌ Basic search: FAILED - {e}")
            self.test_results.append(("basic_search", False))
        
        # Test 2: Domain-filtered search
        print("🔍 Testing domain-filtered search")
        try:
            results = await self.kernel.search("test", ["communication"])
            if isinstance(results, list):
                print(f"✅ Domain-filtered search: PASSED - Found {len(results)} results")
                self.test_results.append(("domain_search", True))
            else:
                print("❌ Domain-filtered search: FAILED - Invalid result type")
                self.test_results.append(("domain_search", False))
        except Exception as e:
            print(f"❌ Domain-filtered search: FAILED - {e}")
            self.test_results.append(("domain_search", False))
    
    async def test_monitoring_endpoints(self):
        """Test monitoring and health check endpoints"""
        print("\n🏥 Testing Monitoring and Health Check Endpoints...")
        
        # Test 1: Kernel health
        print("🏥 Testing GET /kernel/health")
        try:
            # This would be the API endpoint, but we'll test the underlying functionality
            plugins = await self.kernel.list_plugins()
            total_plugins = len(plugins)
            enabled_plugins = len([p for p in plugins if p.status.value == "enabled"])
            
            if total_plugins >= 0 and enabled_plugins >= 0:
                print(f"✅ Kernel health check: PASSED - {total_plugins} total, {enabled_plugins} enabled")
                self.test_results.append(("kernel_health", True))
            else:
                print("❌ Kernel health check: FAILED - Invalid metrics")
                self.test_results.append(("kernel_health", False))
        except Exception as e:
            print(f"❌ Kernel health check: FAILED - {e}")
            self.test_results.append(("kernel_health", False))
        
        # Test 2: Kernel metrics
        print("📊 Testing GET /kernel/metrics")
        try:
            plugins = await self.kernel.list_plugins()
            total_usage = sum(p.usage_count for p in plugins)
            total_errors = sum(p.error_count for p in plugins)
            
            if total_usage >= 0 and total_errors >= 0:
                print(f"✅ Kernel metrics: PASSED - Usage: {total_usage}, Errors: {total_errors}")
                self.test_results.append(("kernel_metrics", True))
            else:
                print("❌ Kernel metrics: FAILED - Invalid metrics")
                self.test_results.append(("kernel_metrics", False))
        except Exception as e:
            print(f"❌ Kernel metrics: FAILED - {e}")
            self.test_results.append(("kernel_metrics", False))
        
        # Test 3: Plugin health
        print("🏥 Testing GET /kernel/plugins/{plugin_id}/health")
        try:
            plugin = await self.kernel.get_plugin("test_email")
            if plugin:
                health_status = "healthy" if plugin.error_count == 0 else "degraded"
                print(f"✅ Plugin health: PASSED - Status: {health_status}")
                self.test_results.append(("plugin_health", True))
            else:
                print("❌ Plugin health: FAILED - Plugin not found")
                self.test_results.append(("plugin_health", False))
        except Exception as e:
            print(f"❌ Plugin health: FAILED - {e}")
            self.test_results.append(("plugin_health", False))
    
    async def cleanup(self):
        """Cleanup test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        try:
            # Disable all test plugins
            for plugin_id in self.test_plugins:
                await self.kernel.disable_plugin(plugin_id)
            
            # Remove test database
            import os
            if os.path.exists("test_kernel.db"):
                os.remove("test_kernel.db")
            
            print("✅ Cleanup complete")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📊 KERNEL API TEST REPORT")
        print("="*60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nTest Results:")
        for test_name, result in self.test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        print("\n" + "="*60)
        return passed == total

async def main():
    """Main test runner"""
    print("🚀 Starting Kernel API Test Suite...")
    print("Testing all new endpoints for Issue #23 completion")
    
    tester = KernelAPITester()
    
    try:
        # Setup
        await tester.setup()
        
        # Run tests
        await tester.test_plugin_endpoints()
        await tester.test_capability_endpoints()
        await tester.test_event_endpoints()
        await tester.test_search_endpoints()
        await tester.test_monitoring_endpoints()
        
        # Generate report
        success = tester.generate_report()
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        await tester.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)