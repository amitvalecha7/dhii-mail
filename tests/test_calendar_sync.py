import pytest
import sqlite3
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from plugins.calendar.services.sync_service import CalendarSyncService

@pytest.fixture
def mock_db(tmp_path):
    """Create a test database with calendar tables"""
    db_path = tmp_path / "test_calendar.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Calendar accounts table
    cursor.execute('''
        CREATE TABLE calendar_accounts (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            credentials_encrypted TEXT,
            calendar_url TEXT,
            last_synced TIMESTAMP,
            sync_interval INTEGER DEFAULT 300,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Calendar events table (matches existing schema)
    cursor.execute('''
        CREATE TABLE calendar_events (
            id TEXT PRIMARY KEY,
            account_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            location TEXT,
            attendees TEXT,
            organizer TEXT,
            status TEXT DEFAULT 'confirmed',
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed test calendar accounts
    test_credentials = json.dumps({
        'username': 'testuser',
        'password': 'testpass'
    })
    
    google_credentials = json.dumps({
        'access_token': 'test_access_token'
    })
    
    cursor.execute('''
        INSERT INTO calendar_accounts 
        (id, provider, credentials_encrypted, calendar_url, last_synced, is_active)
        VALUES 
        ('caldav_acc1', 'caldav', ?, 'https://caldav.example.com/calendar', NULL, 1),
        ('google_acc1', 'google', ?, NULL, NULL, 1)
    ''', (test_credentials, google_credentials))
    
    conn.commit()
    conn.close()
    return str(db_path)

@pytest.fixture
def calendar_sync_service(mock_db):
    """Create a CalendarSyncService instance with test database"""
    return CalendarSyncService(mock_db)

@pytest.mark.asyncio
async def test_calendar_sync_service_initialization(calendar_sync_service):
    """Test that CalendarSyncService initializes correctly"""
    assert calendar_sync_service is not None
    assert calendar_sync_service.db_path is not None
    assert calendar_sync_service._running == False

@pytest.mark.asyncio
async def test_start_stop_service(calendar_sync_service):
    """Test starting and stopping the calendar sync service"""
    # Mock the session to avoid actual HTTP requests
    with patch('aiohttp.ClientSession') as mock_session:
        mock_session.return_value = AsyncMock()
        
        await calendar_sync_service.start()
        assert calendar_sync_service._running == True
        
        await calendar_sync_service.stop()
        assert calendar_sync_service._running == False

@pytest.mark.asyncio
async def test_sync_all_calendars(calendar_sync_service, mock_db):
    """Test syncing all calendar accounts"""
    # Mock the individual sync methods
    with patch.object(calendar_sync_service, '_sync_calendar_account') as mock_sync:
        mock_sync.return_value = None
        
        await calendar_sync_service._sync_all_calendars()
        
        # Should be called twice (once for each test account)
        assert mock_sync.call_count == 2

@pytest.mark.asyncio
async def test_sync_caldav_account(calendar_sync_service):
    """Test syncing a CalDAV account"""
    # Mock CalDAV fetching and processing
    with patch.object(calendar_sync_service, '_sync_caldav_account') as mock_caldav_sync:
        mock_caldav_sync.return_value = None
        
        await calendar_sync_service._sync_calendar_account(
            'caldav_acc1', 'caldav', 
            json.dumps({'username': 'test', 'password': 'test'}),
            'https://caldav.example.com/calendar', None
        )
        
        mock_caldav_sync.assert_called_once()

@pytest.mark.asyncio
async def test_sync_google_account(calendar_sync_service):
    """Test syncing a Google Calendar account"""
    # Mock Google Calendar fetching and processing
    with patch.object(calendar_sync_service, '_sync_google_account') as mock_google_sync:
        mock_google_sync.return_value = None
        
        await calendar_sync_service._sync_calendar_account(
            'google_acc1', 'google', 
            json.dumps({'access_token': 'test_token'}),
            None, None
        )
        
        mock_google_sync.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_google_events_success(calendar_sync_service):
    """Test successful Google Calendar API request"""
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'items': [
            {
                'id': 'event1',
                'summary': 'Test Event',
                'description': 'Test Description',
                'start': {'dateTime': '2024-01-01T10:00:00Z'},
                'end': {'dateTime': '2024-01-01T11:00:00Z'},
                'location': 'Test Location',
                'attendees': [{'email': 'test@example.com'}],
                'organizer': {'email': 'organizer@example.com'},
                'status': 'confirmed'
            }
        ]
    })
    
    calendar_sync_service.session = AsyncMock()
    calendar_sync_service.session.get = AsyncMock(return_value=mock_response)
    
    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 1, 2)
    
    events = await calendar_sync_service._fetch_google_events('test_token', start_time, end_time)
    
    assert len(events) == 1
    assert events[0]['id'] == 'event1'
    assert events[0]['summary'] == 'Test Event'

@pytest.mark.asyncio
async def test_fetch_google_events_failure(calendar_sync_service):
    """Test Google Calendar API failure"""
    # Mock failed API response
    mock_response = MagicMock()
    mock_response.status = 401  # Unauthorized
    
    calendar_sync_service.session = AsyncMock()
    calendar_sync_service.session.get = AsyncMock(return_value=mock_response)
    
    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 1, 2)
    
    events = await calendar_sync_service._fetch_google_events('invalid_token', start_time, end_time)
    
    assert events == []  # Should return empty list on failure

@pytest.mark.asyncio
async def test_process_calendar_events(calendar_sync_service, mock_db):
    """Test processing and saving calendar events"""
    google_events = [
        {
            'id': 'google_event_1',
            'summary': 'Google Meeting',
            'description': 'Important meeting',
            'start': {'dateTime': '2024-01-01T10:00:00Z'},
            'end': {'dateTime': '2024-01-01T11:00:00Z'},
            'location': 'Google Office',
            'attendees': [{'email': 'attendee@example.com'}],
            'organizer': {'email': 'organizer@example.com'},
            'status': 'confirmed'
        }
    ]
    
    await calendar_sync_service._process_calendar_events('google_acc1', google_events, 'google')
    
    # Verify event was saved to database
    conn = sqlite3.connect(mock_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM calendar_events WHERE source = 'google'")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1

@pytest.mark.asyncio
async def test_parse_google_event_valid(calendar_sync_service):
    """Test parsing valid Google Calendar event"""
    google_event = {
        'id': 'test_event',
        'summary': 'Test Event',
        'description': 'Test Description',
        'start': {'dateTime': '2024-01-01T10:00:00Z'},
        'end': {'dateTime': '2024-01-01T11:00:00Z'},
        'location': 'Test Location',
        'attendees': [{'email': 'test@example.com'}],
        'organizer': {'email': 'organizer@example.com'},
        'status': 'confirmed'
    }
    
    parsed = calendar_sync_service._parse_google_event(google_event)
    
    assert parsed is not None
    assert parsed['id'] == 'test_event'
    assert parsed['title'] == 'Test Event'
    assert parsed['description'] == 'Test Description'
    assert len(parsed['attendees']) == 1

@pytest.mark.asyncio
async def test_parse_google_event_invalid(calendar_sync_service):
    """Test parsing invalid Google Calendar event"""
    # Event missing required fields
    invalid_event = {
        'summary': 'Test Event'
        # Missing id, start, end
    }
    
    parsed = calendar_sync_service._parse_google_event(invalid_event)
    
    assert parsed is None  # Should return None for invalid events

def test_parse_google_datetime(calendar_sync_service):
    """Test parsing Google Calendar datetime formats"""
    # DateTime format
    datetime_data = {'dateTime': '2024-01-01T10:00:00Z'}
    result = calendar_sync_service._parse_google_datetime(datetime_data)
    # Compare without timezone (strip timezone info for comparison)
    assert result.replace(tzinfo=None) == datetime(2024, 1, 1, 10, 0, 0)
    
    # Date format (all-day event)
    date_data = {'date': '2024-01-01'}
    result = calendar_sync_service._parse_google_datetime(date_data)
    assert result == datetime(2024, 1, 1)
    
    # Invalid format
    invalid_data = {}
    result = calendar_sync_service._parse_google_datetime(invalid_data)
    assert result is None

def test_basic_auth_header(calendar_sync_service):
    """Test Basic Auth header generation"""
    header = calendar_sync_service._basic_auth_header('testuser', 'testpass')
    assert header.startswith('Basic ')
    assert 'dGVzdHVzZXI6dGVzdHBhc3M=' in header  # base64 of 'testuser:testpass'

@pytest.mark.asyncio
async def test_update_last_synced(calendar_sync_service, mock_db):
    """Test updating last sync timestamp"""
    await calendar_sync_service._update_last_synced('caldav_acc1')
    
    # Verify timestamp was updated
    conn = sqlite3.connect(mock_db)
    cursor = conn.cursor()
    cursor.execute("SELECT last_synced FROM calendar_accounts WHERE id = 'caldav_acc1'")
    last_synced = cursor.fetchone()[0]
    conn.close()
    
    assert last_synced is not None
    # Should be recent timestamp (within last minute)
    sync_time = datetime.fromisoformat(last_synced)
    assert (datetime.now() - sync_time).total_seconds() < 60

if __name__ == "__main__":
    pytest.main([__file__, "-v"])