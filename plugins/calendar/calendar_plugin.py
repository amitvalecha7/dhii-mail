"""
Calendar Plugin for dhii Mail
Handles calendar operations as a plugin in the new kernel architecture
"""

import os
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator
from dataclasses import dataclass

from a2ui_integration.core.types import DomainModule, Capability, PluginType, PluginConfig

# Import the sync service
from .services.sync_service import CalendarSyncService, get_calendar_sync_service

logger = logging.getLogger(__name__)


class CalendarEvent(BaseModel):
    """Calendar event model"""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = []
    organizer: str
    status: str = "confirmed"  # confirmed, tentative, cancelled
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v


class TimeSlot(BaseModel):
    """Available time slot model"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CalendarPlugin(DomainModule):
    """Calendar plugin that provides calendar capabilities"""
    
    def __init__(self, db_path: str = "calendar_plugin.db"):
        self.db_path = db_path
        self._events: Dict[str, CalendarEvent] = {}
        self.sync_service: Optional[CalendarSyncService] = None
        
        # Initialize database
        self._init_database()
    
    @property
    def domain(self) -> str:
        """Return the domain name this module handles"""
        return "calendar"
    
    @property
    def capabilities(self) -> List[Capability]:
        """Return list of capabilities this module provides"""
        return [
            Capability(
                id="calendar.create_event",
                domain="calendar",
                name="Create Event",
                description="Create a new calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "start_time": {"type": "string", "format": "date-time"},
                        "end_time": {"type": "string", "format": "date-time"},
                        "location": {"type": "string"},
                        "attendees": {"type": "array", "items": {"type": "string"}},
                        "organizer": {"type": "string"}
                    },
                    "required": ["title", "start_time", "end_time", "organizer"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "success": {"type": "boolean"},
                        "error": {"type": "string"}
                    }
                },
                side_effects=["event_created"],
                requires_auth=False
            ),
            Capability(
                id="calendar.get_events",
                domain="calendar",
                name="Get Events",
                description="Get calendar events for a date range",
                input_schema={
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "format": "date"},
                        "end_date": {"type": "string", "format": "date"},
                        "organizer": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "events": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                },
                side_effects=[],
                requires_auth=False
            ),
            Capability(
                id="calendar.find_availability",
                domain="calendar",
                name="Find Availability",
                description="Find available time slots",
                input_schema={
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "format": "date"},
                        "duration_minutes": {"type": "integer", "minimum": 15},
                        "attendees": {"type": "array", "items": {"type": "string"}},
                        "working_hours_start": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"},
                        "working_hours_end": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}
                    },
                    "required": ["date", "duration_minutes"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "available_slots": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                },
                side_effects=[],
                requires_auth=False
            ),
            Capability(
                id="calendar.delete_event",
                domain="calendar",
                name="Delete Event",
                description="Delete a calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"}
                    },
                    "required": ["event_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "error": {"type": "string"}
                    }
                },
                side_effects=["event_deleted"],
                requires_auth=False
            ),
            Capability(
                id="calendar.update_event",
                domain="calendar",
                name="Update Event",
                description="Update an existing calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "start_time": {"type": "string", "format": "date-time"},
                        "end_time": {"type": "string", "format": "date-time"},
                        "location": {"type": "string"},
                        "attendees": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["event_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "success": {"type": "boolean"},
                        "error": {"type": "string"}
                    }
                },
                side_effects=["event_updated"],
                requires_auth=False
            ),
            Capability(
                id="calendar.trigger_sync",
                domain="calendar",
                name="Trigger Sync",
                description="Manually trigger calendar synchronization",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "error": {"type": "string"}
                    }
                },
                side_effects=["calendar_sync_triggered"],
                requires_auth=False
            )
        ]
    
    def _init_database(self):
        """Initialize the calendar plugin database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calendar events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                location TEXT,
                attendees TEXT,
                organizer TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Calendar availability table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_availability (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                working_hours_start TEXT,
                working_hours_end TEXT,
                busy_slots TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def initialize(self) -> bool:
        """Initialize the calendar plugin"""
        try:
            logger.info("Initializing calendar plugin")
            
            # Initialize calendar sync service
            self.sync_service = await get_calendar_sync_service(self.db_path)
            logger.info("Calendar sync service started")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize calendar plugin: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the calendar plugin"""
        try:
            # Stop the calendar sync service if it's running
            if self.sync_service:
                await self.sync_service.stop()
                logger.info("Calendar sync service stopped")
            
            logger.info("Calendar plugin shutdown complete")
            return True
        except Exception as e:
            logger.error(f"Error shutting down calendar plugin: {e}")
            return False
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific capability"""
        if capability_id == "calendar.create_event":
            return await self._create_event(params)
        elif capability_id == "calendar.get_events":
            return await self._get_events(params)
        elif capability_id == "calendar.find_availability":
            return await self._find_availability(params)
        elif capability_id == "calendar.delete_event":
            return await self._delete_event(params)
        elif capability_id == "calendar.update_event":
            return await self._update_event(params)
        elif capability_id == "calendar.trigger_sync":
            return await self._trigger_sync(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            import sqlite3
            import uuid
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            event_id = str(uuid.uuid4())
            start_time = datetime.fromisoformat(params['start_time'])
            end_time = datetime.fromisoformat(params['end_time'])
            
            cursor.execute('''
                INSERT INTO calendar_events 
                (id, title, description, start_time, end_time, location, attendees, organizer, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id,
                params['title'],
                params.get('description', ''),
                start_time,
                end_time,
                params.get('location', ''),
                json.dumps(params.get('attendees', [])),
                params['organizer'],
                'confirmed'
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "event_id": event_id,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return {
                "event_id": None,
                "success": False,
                "error": str(e)
            }
    
    async def _get_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get calendar events for a date range"""
        try:
            from datetime import datetime
            
            # Parse date parameters
            start_date = None
            end_date = None
            
            if 'start_date' in params:
                start_date = datetime.fromisoformat(params['start_date'])
            else:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if 'end_date' in params:
                end_date = datetime.fromisoformat(params['end_date'])
            else:
                end_date = start_date + timedelta(days=7)  # Default to 7 days
            
            # Get user_id from organizer or use default
            user_id = 1  # Default user_id, should be determined from auth context
            if 'organizer' in params:
                # Extract user_id from organizer email or use mapping
                organizer = params['organizer']
                if '@' in organizer:
                    user_id = 1  # Placeholder - should map organizer to user_id
            
            # Use sync service to get events if available, otherwise use local database
            if self.sync_service:
                events = self.sync_service.get_local_events(user_id, start_date, end_date)
            else:
                # Fallback to local database query
                events = await self._get_events_from_local_db(params)
            
            return {
                "events": events,
                "count": len(events)
            }
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return {
                "events": [],
                "count": 0
            }
    
    async def _get_events_from_local_db(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get events from local database (fallback method)"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            organizer = params.get('organizer')
            
            # Build query conditions
            conditions = []
            values = []
            
            if start_date:
                conditions.append("start_time >= ?")
                values.append(start_date)
            
            if end_date:
                conditions.append("end_time <= ?")
                values.append(end_date)
            
            if organizer:
                conditions.append("organizer = ?")
                values.append(organizer)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f'''
                SELECT * FROM calendar_events 
                WHERE {where_clause}
                ORDER BY start_time ASC
            ''', values)
            
            events_data = cursor.fetchall()
            conn.close()
            
            # Convert to proper format
            events = []
            for event_data in events_data:
                events.append({
                    "id": event_data[0],
                    "title": event_data[1],
                    "description": event_data[2],
                    "start_time": event_data[3],
                    "end_time": event_data[4],
                    "location": event_data[5],
                    "attendees": json.loads(event_data[6]),
                    "organizer": event_data[7],
                    "status": event_data[8]
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events from local DB: {e}")
            return []
    
    async def _find_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find available time slots"""
        try:
            import sqlite3
            from datetime import datetime, timedelta
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            date = datetime.fromisoformat(params['date'])
            duration_minutes = params['duration_minutes']
            attendees = params.get('attendees', [])
            working_hours_start = params.get('working_hours_start', '09:00')
            working_hours_end = params.get('working_hours_end', '17:00')
            
            # Parse working hours
            start_hour, start_minute = map(int, working_hours_start.split(':'))
            end_hour, end_minute = map(int, working_hours_end.split(':'))
            
            working_start = date.replace(hour=start_hour, minute=start_minute)
            working_end = date.replace(hour=end_hour, minute=end_minute)
            
            # Get existing events for the day
            cursor.execute('''
                SELECT * FROM calendar_events 
                WHERE DATE(start_time) = ? 
                AND status = 'confirmed'
                ORDER BY start_time ASC
            ''', (date.date().isoformat(),))
            
            existing_events = cursor.fetchall()
            conn.close()
            
            # Find available slots
            available_slots = []
            current_time = working_start
            
            while current_time + timedelta(minutes=duration_minutes) <= working_end:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with existing events
                is_available = True
                for event in existing_events:
                    event_start = datetime.fromisoformat(event[3])
                    event_end = datetime.fromisoformat(event[4])
                    
                    if (current_time < event_end and slot_end > event_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        "start_time": current_time.isoformat(),
                        "end_time": slot_end.isoformat(),
                        "duration_minutes": duration_minutes
                    })
                
                current_time += timedelta(minutes=30)  # 30-minute increments
            
            return {
                "available_slots": available_slots,
                "count": len(available_slots)
            }
            
        except Exception as e:
            logger.error(f"Failed to find availability: {e}")
            return {
                "available_slots": [],
                "count": 0
            }
    
    async def _delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM calendar_events WHERE id = ?', (params['event_id'],))
            
            success = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return {
                "success": success,
                "error": None if success else "Event not found"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query
            update_fields = []
            values = []
            
            if 'title' in params:
                update_fields.append("title = ?")
                values.append(params['title'])
            
            if 'description' in params:
                update_fields.append("description = ?")
                values.append(params['description'])
            
            if 'start_time' in params:
                update_fields.append("start_time = ?")
                values.append(datetime.fromisoformat(params['start_time']))
            
            if 'end_time' in params:
                update_fields.append("end_time = ?")
                values.append(datetime.fromisoformat(params['end_time']))
            
            if 'location' in params:
                update_fields.append("location = ?")
                values.append(params['location'])
            
            if 'attendees' in params:
                update_fields.append("attendees = ?")
                values.append(json.dumps(params['attendees']))
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            values.append(datetime.now())
            
            # Add event_id to values
            values.append(params['event_id'])
            
            if update_fields:
                set_clause = ", ".join(update_fields)
                cursor.execute(f'''
                    UPDATE calendar_events 
                    SET {set_clause}
                    WHERE id = ?
                ''', values)
                
                success = cursor.rowcount > 0
            else:
                success = False
            
            conn.commit()
            conn.close()
            
            return {
                "event_id": params['event_id'] if success else None,
                "success": success,
                "error": None if success else "Event not found or no fields to update"
            }
            
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return {
                "event_id": None,
                "success": False,
                "error": str(e)
            }

    async def _trigger_sync(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manually trigger calendar synchronization"""
        try:
            if not self.sync_service:
                return {
                    "success": False,
                    "error": "Calendar sync service not initialized"
                }
            
            success = await self.sync_service.trigger_sync()
            return {
                "success": success,
                "error": None if success else "Sync failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger calendar sync: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Plugin configuration
CALENDAR_PLUGIN_CONFIG = PluginConfig(
    id="calendar_plugin",
    name="Calendar Plugin",
    version="1.0.0",
    description="Comprehensive calendar management capabilities with automatic sync",
    type=PluginType.CALENDAR,
    author="dhii-mail-team",
    enabled=True,
    config={
        "default_working_hours_start": "09:00",
        "default_working_hours_end": "17:00",
        "sync_enabled": True,
        "sync_interval_minutes": 5,
        "caldav_support": True,
        "google_calendar_support": True,
        "slot_duration_minutes": 30
    },
    capabilities=[],  # Will be populated by the plugin instance
    dependencies=[]
)