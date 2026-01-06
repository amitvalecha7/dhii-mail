#!/usr/bin/env python3
"""
Test script for Calendar Sync Engine
Tests the calendar sync daemon and plugin integration
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calendar_sync_daemon import CalendarSyncDaemon
from plugins.calendar.services.sync_service import CalendarSyncService
from plugins.calendar.calendar_plugin import CalendarPlugin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_calendar_sync_daemon():
    """Test the calendar sync daemon"""
    logger.info("Testing Calendar Sync Daemon...")
    
    try:
        # Create daemon instance
        daemon = CalendarSyncDaemon("test_calendar.db")
        
        # Test daemon initialization
        logger.info("Initializing daemon...")
        await daemon.start()
        
        # Let it run for a few seconds
        logger.info("Daemon running, waiting 5 seconds...")
        await asyncio.sleep(5)
        
        # Check status
        status = daemon.get_sync_status() if hasattr(daemon, 'get_sync_status') else "No status method"
        logger.info(f"Daemon status: {status}")
        
        # Stop daemon
        logger.info("Stopping daemon...")
        await daemon.stop()
        
        logger.info("✅ Calendar Sync Daemon test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Calendar Sync Daemon test failed: {e}")
        return False


async def test_calendar_sync_service():
    """Test the calendar sync service"""
    logger.info("Testing Calendar Sync Service...")
    
    try:
        # Create service instance
        service = CalendarSyncService("test_calendar.db")
        
        # Test service initialization
        logger.info("Initializing service...")
        await service.start()
        
        # Test getting sync status
        status = service.get_sync_status()
        logger.info(f"Sync service status: {status}")
        
        # Test getting account sync states
        account_states = service.get_account_sync_states()
        logger.info(f"Account sync states: {account_states}")
        
        # Test creating a local event
        logger.info("Creating test event...")
        event_data = {
            "title": "Test Meeting",
            "description": "Test calendar sync engine",
            "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "location": "Test Room",
            "attendees": ["test@example.com"],
            "organizer": "organizer@example.com",
            "status": "confirmed"
        }
        
        event_id = service.create_local_event(1, event_data)
        logger.info(f"Created event with ID: {event_id}")
        
        # Test getting local events
        logger.info("Getting local events...")
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        events = service.get_local_events(1, start_date, end_date)
        logger.info(f"Found {len(events)} events")
        
        # Test availability
        logger.info("Getting availability...")
        availability = service.get_availability(1, datetime.now().date())
        logger.info(f"Available slots: {len(availability)}")
        
        # Stop service
        logger.info("Stopping service...")
        await service.stop()
        
        logger.info("✅ Calendar Sync Service test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Calendar Sync Service test failed: {e}")
        return False


async def test_calendar_plugin():
    """Test the calendar plugin integration"""
    logger.info("Testing Calendar Plugin...")
    
    try:
        # Create plugin instance
        plugin = CalendarPlugin("test_calendar_plugin.db")
        
        # Test plugin initialization
        logger.info("Initializing plugin...")
        success = await plugin.initialize()
        logger.info(f"Plugin initialization: {'✅' if success else '❌'}")
        
        if not success:
            return False
        
        # Test capabilities
        capabilities = plugin.capabilities
        logger.info(f"Plugin capabilities: {len(capabilities)} capabilities")
        
        # Test get_events capability
        logger.info("Testing get_events capability...")
        params = {
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        result = await plugin.execute_capability("calendar.get_events", params)
        logger.info(f"get_events result: {result}")
        
        # Test create_event capability
        logger.info("Testing create_event capability...")
        create_params = {
            "title": "Plugin Test Meeting",
            "start_time": (datetime.now() + timedelta(hours=3)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=4)).isoformat(),
            "organizer": "plugin@test.com"
        }
        
        create_result = await plugin.execute_capability("calendar.create_event", create_params)
        logger.info(f"create_event result: {create_result}")
        
        # Test find_availability capability
        logger.info("Testing find_availability capability...")
        availability_params = {
            "date": datetime.now().date().isoformat(),
            "duration_minutes": 30
        }
        
        availability_result = await plugin.execute_capability("calendar.find_availability", availability_params)
        logger.info(f"find_availability result: {availability_result}")
        
        # Test plugin shutdown
        logger.info("Shutting down plugin...")
        shutdown_success = await plugin.shutdown()
        logger.info(f"Plugin shutdown: {'✅' if shutdown_success else '❌'}")
        
        logger.info("✅ Calendar Plugin test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Calendar Plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    logger.info("Starting Calendar Sync Engine Tests...")
    
    # Clean up test databases
    test_dbs = ["test_calendar.db", "test_calendar_plugin.db"]
    for db in test_dbs:
        if os.path.exists(db):
            os.remove(db)
            logger.info(f"Removed existing test database: {db}")
    
    # Run tests
    tests = [
        ("Calendar Sync Daemon", test_calendar_sync_daemon),
        ("Calendar Sync Service", test_calendar_sync_service),
        ("Calendar Plugin", test_calendar_plugin)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("Test Summary")
    logger.info(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    # Clean up test databases
    for db in test_dbs:
        if os.path.exists(db):
            os.remove(db)
            logger.info(f"Cleaned up test database: {db}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)