"""
Integration tests for Intelligence Layer
"""

import pytest
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta

from a2ui_integration.core.shared_services import EventBus, EventType, Event
from intelligence_layer import IntelligenceLayer, get_intelligence_layer


@pytest.fixture
def test_db_path():
    """Create a test database"""
    return ":memory:"


@pytest.fixture
def event_bus():
    """Create a test event bus"""
    return EventBus()


@pytest.fixture
async def intelligence_layer(event_bus, test_db_path):
    """Create and initialize intelligence layer"""
    layer = IntelligenceLayer(event_bus, test_db_path)
    await layer.start()
    yield layer
    await layer.stop()


@pytest.mark.asyncio
async def test_intelligence_layer_initialization(intelligence_layer):
    """Test that intelligence layer initializes properly"""
    assert intelligence_layer is not None
    assert intelligence_layer.running == True
    assert len(intelligence_layer.subscriptions) > 0
    assert len(intelligence_layer.analysis_workers) == 3


@pytest.mark.asyncio
async def test_database_tables_created(intelligence_layer, test_db_path):
    """Test that intelligence database tables are created"""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Check that all intelligence tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name IN ('ai_email_insights', 'user_behavior_patterns', 'meeting_intelligence')
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    assert len(tables) == 3
    assert 'ai_email_insights' in tables
    assert 'user_behavior_patterns' in tables
    assert 'meeting_intelligence' in tables
    
    conn.close()


@pytest.mark.asyncio
async def test_email_received_analysis(event_bus, intelligence_layer, test_db_path):
    """Test email received event analysis"""
    # Create test email event
    email_event = Event(
        id="test-email-001",
        type=EventType.EMAIL_RECEIVED,
        source="email_plugin",
        timestamp=datetime.now(),
        data={
            "email": {
                "id": "email-001",
                "body": "This is a great email! I really appreciate your help with this project.",
                "subject": "Thank you for your help",
                "from": "sender@example.com",
                "to": ["recipient@example.com"]
            }
        }
    )
    
    # Publish the event
    await event_bus.publish(email_event)
    
    # Wait a bit for async processing
    await asyncio.sleep(0.1)
    
    # Check that analysis was stored
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM ai_email_insights WHERE email_id = ?", ("email-001",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == "email-001"  # email_id
    assert result[1] > 0.7  # sentiment_score should be positive
    assert result[2] == "low"  # urgency_level
    
    conn.close()


@pytest.mark.asyncio
async def test_email_sent_analysis(event_bus, intelligence_layer, test_db_path):
    """Test email sent event analysis"""
    # Create test email sent event
    email_event = Event(
        id="test-email-sent-001",
        type=EventType.EMAIL_SENT,
        source="email_plugin",
        timestamp=datetime.now(),
        data={
            "email": {
                "id": "email-sent-001",
                "body": "URGENT: Please review this document immediately. We need your feedback ASAP.",
                "subject": "Urgent Review Required",
                "from": "sender@example.com",
                "to": ["recipient@example.com"]
            }
        }
    )
    
    # Publish the event
    await event_bus.publish(email_event)
    
    # Wait for async processing
    await asyncio.sleep(0.1)
    
    # Check that analysis was stored
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM ai_email_insights WHERE email_id = ?", ("email-sent-001",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == "email-sent-001"
    assert result[2] == "high"  # urgency_level should be high
    
    conn.close()


@pytest.mark.asyncio
async def test_meeting_created_analysis(event_bus, intelligence_layer, test_db_path):
    """Test meeting created event analysis"""
    # Create test meeting event
    meeting_event = Event(
        id="test-meeting-001",
        type=EventType.MEETING_CREATED,
        source="calendar_plugin",
        timestamp=datetime.now(),
        data={
            "meeting": {
                "id": "meeting-001",
                "summary": "Project Kickoff",
                "description": "Initial project kickoff meeting",
                "start": {
                    "dateTime": "2024-01-15T10:00:00Z",
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": "2024-01-15T11:00:00Z", 
                    "timeZone": "UTC"
                },
                "duration": 60,
                "attendees": [
                    {"email": "user1@example.com", "external": False},
                    {"email": "user2@example.com", "external": False}
                ]
            }
        }
    )
    
    # Publish the event
    await event_bus.publish(meeting_event)
    
    # Wait for async processing
    await asyncio.sleep(0.1)
    
    # Check that analysis was stored
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM meeting_intelligence WHERE meeting_id = ?", ("meeting-001",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == "meeting-001"
    assert result[1] > 0.8  # optimality_score should be high
    assert result[3] == "optimal_morning"  # time_slot_quality
    
    # Check participant analysis
    participant_data = json.loads(result[2])
    assert participant_data["count"] == 2
    assert participant_data["external_count"] == 0
    assert participant_data["internal_count"] == 2
    
    conn.close()


@pytest.mark.asyncio
async def test_user_behavior_analysis(event_bus, intelligence_layer, test_db_path):
    """Test user behavior event analysis"""
    # Create test capability executed event
    behavior_event = Event(
        id="test-behavior-001",
        type=EventType.CAPABILITY_EXECUTED,
        source="ui_plugin",
        timestamp=datetime.now(),
        data={
            "user_id": "user-001",
            "capability": {
                "id": "email.send",
                "input": {
                    "to": "recipient@example.com",
                    "subject": "Test Email",
                    "body": "This is a test email"
                },
                "output": {"success": True}
            }
        }
    )
    
    # Publish the event
    await event_bus.publish(behavior_event)
    
    # Wait for async processing
    await asyncio.sleep(0.1)
    
    # Check that behavior was tracked
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_behavior_patterns WHERE user_id = ?", ("user-001",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[1] == "user-001"  # user_id
    assert result[2] == "email.send"  # action_type
    
    conn.close()


@pytest.mark.asyncio
async def test_negative_sentiment_analysis(event_bus, intelligence_layer, test_db_path):
    """Test negative sentiment analysis"""
    # Create test email with negative content
    email_event = Event(
        id="test-negative-email",
        type=EventType.EMAIL_RECEIVED,
        source="email_plugin",
        timestamp=datetime.now(),
        data={
            "email": {
                "id": "negative-email-001",
                "body": "I'm very disappointed with the service. There are serious problems that need immediate attention.",
                "subject": "Complaint about service",
                "from": "customer@example.com",
                "to": ["support@example.com"]
            }
        }
    )
    
    # Publish the event
    await event_bus.publish(email_event)
    
    # Wait for async processing
    await asyncio.sleep(0.1)
    
    # Check that negative sentiment was detected
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT sentiment_score FROM ai_email_insights WHERE email_id = ?", ("negative-email-001",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] < 0.3  # sentiment_score should be negative
    
    conn.close()


@pytest.mark.asyncio
async def test_off_hours_meeting_analysis(event_bus, intelligence_layer, test_db_path):
    """Test off-hours meeting analysis"""
    # Create test meeting event during off-hours
    meeting_event = Event(
        id="test-off-hours-meeting",
        type=EventType.MEETING_CREATED,
        source="calendar_plugin",
        timestamp=datetime.now(),
        data={
            "meeting": {
                "id": "off-hours-meeting",
                "summary": "Late Night Meeting",
                "start": {
                    "dateTime": "2024-01-15T20:00:00Z",  # 8 PM UTC
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": "2024-01-15T21:00:00Z",
                    "timeZone": "UTC"
                },
                "duration": 60,
                "attendees": [
                    {"email": "user1@example.com", "external": False}
                ]
            }
        }
    )
    
    # Publish the event
    await event_bus.publish(meeting_event)
    
    # Wait for async processing
    await asyncio.sleep(0.1)
    
    # Check that off-hours was detected
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT time_slot_quality FROM meeting_intelligence WHERE meeting_id = ?", ("off-hours-meeting",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == "off_hours"  # time_slot_quality
    
    conn.close()


@pytest.mark.asyncio
async def test_intelligence_layer_stop(event_bus, test_db_path):
    """Test that intelligence layer stops properly"""
    layer = IntelligenceLayer(event_bus, test_db_path)
    await layer.start()
    assert layer.running == True
    
    await layer.stop()
    assert layer.running == False
    assert len(layer.subscriptions) == 0


@pytest.mark.asyncio
async def test_global_instance():
    """Test global intelligence layer instance"""
    layer = get_intelligence_layer()
    assert layer is not None
    assert isinstance(layer, IntelligenceLayer)