"""
Test script for calendar management functionality
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta, timezone
from calendar_manager import CalendarManager, CalendarEvent

def test_calendar_manager():
    """Test the calendar manager directly"""
    print("=== Testing Calendar Manager ===")
    
    # Create calendar manager
    calendar = CalendarManager()
    
    # Test event creation
    print("\n1. Testing event creation...")
    event = CalendarEvent(
        title="Team Meeting",
        description="Weekly team sync meeting",
        start_time=datetime.now(timezone.utc) + timedelta(hours=2),
        end_time=datetime.now(timezone.utc) + timedelta(hours=3),
        location="Conference Room A",
        attendees=["john@example.com", "jane@example.com"],
        organizer="admin@dhii-mail.local"
    )
    
    # For testing, we'll use a mock user_id
    user_id = 1
    event_id = calendar.create_event(event, user_id)
    
    if event_id:
        print(f"✓ Event created successfully: {event_id}")
    else:
        print("✗ Event creation failed")
    
    # Test getting events
    print("\n2. Testing event retrieval...")
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=7)
    
    events = calendar.get_events(user_id, start_date, end_date)
    print(f"✓ Retrieved {len(events)} events")
    
    for evt in events:
        print(f"  - {evt.title}: {evt.start_time.strftime('%Y-%m-%d %H:%M')} to {evt.end_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Test availability checking
    print("\n3. Testing availability checking...")
    target_date = datetime.now(timezone.utc) + timedelta(days=1)
    available_slots = calendar.get_availability(user_id, target_date, 30)
    
    print(f"✓ Found {len(available_slots)} available slots for {target_date.strftime('%Y-%m-%d')}")
    
    for slot in available_slots[:5]:  # Show first 5 slots
        print(f"  - {slot.start_time.strftime('%H:%M')} to {slot.end_time.strftime('%H:%M')} ({slot.duration_minutes} min)")

def test_calendar_api():
    """Test calendar API endpoints"""
    print("\n=== Testing Calendar API ===")
    
    base_url = "http://localhost:8004"
    
    # First, we need to authenticate to get a token
    print("\n1. Testing authentication...")
    
    # For testing, we'll try to create a simple event (this might fail without auth)
    event_data = {
        "title": "API Test Meeting",
        "description": "Testing calendar API",
        "start_time": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat(),
        "location": "Virtual",
        "attendees": ["test@example.com"],
        "organizer": "test@dhii-mail.local"
    }
    
    try:
        # Test creating event (will likely fail without auth)
        print("\n2. Testing event creation via API...")
        response = requests.post(
            f"{base_url}/calendar/events",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test getting availability
        print("\n3. Testing availability API...")
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        
        response = requests.get(
            f"{base_url}/calendar/availability",
            params={
                "date": tomorrow.isoformat(),
                "duration_minutes": 30
            }
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server. Make sure it's running on port 8004.")
    except Exception as e:
        print(f"✗ API test failed: {e}")

def test_ai_calendar_integration():
    """Test AI engine with calendar integration"""
    print("\n=== Testing AI Calendar Integration ===")
    
    from ai_engine import ai_engine
    
    # Test calendar-related intents
    test_messages = [
        "What's on my calendar today?",
        "Schedule a meeting for tomorrow at 2 PM",
        "Check my availability for next week",
        "Book a 30-minute meeting with John on Friday"
    ]
    
    print("\nTesting AI responses to calendar queries...")
    
    for message in test_messages:
        print(f"\nMessage: '{message}'")
        
        # Create mock context with user_id
        context = {
            'user_id': 1,  # Mock user ID
            'session_id': 'test_session_001'
        }
        
        try:
            response = asyncio.run(ai_engine.process_message(message, context))
            print(f"Response: {response.message}")
            print(f"Intent: {response.intent.intent} (confidence: {response.intent.confidence})")
            
            if response.ui_components:
                print(f"UI Components: {response.ui_components.get('type', 'none')}")
            
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    print("dhii Mail Calendar Management Test Suite")
    print("=" * 50)
    
    # Run tests
    try:
        test_calendar_manager()
        test_calendar_api()
        test_ai_calendar_integration()
        
        print("\n" + "=" * 50)
        print("Calendar management tests completed!")
        
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        import traceback
        traceback.print_exc()