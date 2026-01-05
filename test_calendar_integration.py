#!/usr/bin/env python3
"""
Test script to verify Calendar Plugin integration with Sync Service
"""

import asyncio
import logging
import os
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_calendar_integration():
    """Test the calendar plugin integration with sync service"""
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Import and initialize the calendar plugin
        from plugins.calendar.calendar_plugin import CalendarPlugin
        
        print("Creating CalendarPlugin instance...")
        plugin = CalendarPlugin(db_path=db_path)
        
        print("Initializing CalendarPlugin...")
        success = await plugin.initialize()
        
        if not success:
            print("❌ Failed to initialize calendar plugin")
            return False
        
        print("✅ Calendar plugin initialized successfully")
        
        # Test that sync service was created
        if not hasattr(plugin, 'sync_service') or plugin.sync_service is None:
            print("❌ Sync service not initialized")
            return False
        
        print("✅ Calendar sync service initialized")
        
        # Test manual sync trigger capability
        print("Testing manual sync trigger...")
        result = await plugin.execute_capability("calendar.trigger_sync", {})
        
        if result.get("success"):
            print("✅ Manual sync triggered successfully")
        else:
            print(f"⚠️  Manual sync failed (expected for empty DB): {result.get('error')}")
        
        # Test creating a calendar event
        print("Testing event creation...")
        event_params = {
            "title": "Test Meeting",
            "description": "Test integration meeting",
            "start_time": "2024-01-01T10:00:00",
            "end_time": "2024-01-01T11:00:00", 
            "organizer": "test@example.com"
        }
        
        create_result = await plugin.execute_capability("calendar.create_event", event_params)
        
        if create_result.get("success"):
            print("✅ Event created successfully")
            print(f"   Event ID: {create_result.get('event_id')}")
        else:
            print(f"❌ Failed to create event: {create_result.get('error')}")
            return False
        
        # Test getting events
        print("Testing event retrieval...")
        get_result = await plugin.execute_capability("calendar.get_events", {
            "start_date": "2024-01-01",
            "end_date": "2024-01-02"
        })
        
        if get_result.get("count", 0) > 0:
            print("✅ Events retrieved successfully")
            print(f"   Found {get_result.get('count')} events")
        else:
            print("❌ No events found")
            return False
        
        # Test shutdown
        print("Testing plugin shutdown...")
        shutdown_success = await plugin.shutdown()
        
        if shutdown_success:
            print("✅ Calendar plugin shutdown successfully")
        else:
            print("❌ Calendar plugin shutdown failed")
            return False
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    result = asyncio.run(test_calendar_integration())
    exit(0 if result else 1)