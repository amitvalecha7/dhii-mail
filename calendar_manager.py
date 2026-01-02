"""
Calendar Manager for dhii Mail
Handles calendar operations, meeting scheduling, and availability checking
"""

import os
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator
import sqlite3

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

class CalendarManager:
    """Calendar management system"""
    
    def __init__(self, db_path: str = "dhii_mail.db"):
        self.db_path = db_path
        self.init_calendar_tables()
    
    def init_calendar_tables(self):
        """Initialize calendar tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create calendar_events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    location TEXT,
                    attendees TEXT, -- JSON array of email addresses
                    organizer TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create calendar_availability table for storing availability preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_availability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    day_of_week INTEGER NOT NULL, -- 0=Monday, 6=Sunday
                    start_time TEXT NOT NULL, -- HH:MM format
                    end_time TEXT NOT NULL,   -- HH:MM format
                    is_available BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Calendar tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing calendar tables: {e}")
            raise
    
    def create_event(self, event: CalendarEvent, user_id: int) -> Optional[str]:
        """Create a new calendar event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for conflicts
            if self._has_conflicts(cursor, event.start_time, event.end_time, user_id):
                logger.warning(f"Time slot conflict for user {user_id}")
                return None
            
            # Insert event
            cursor.execute("""
                INSERT INTO calendar_events 
                (title, description, start_time, end_time, location, attendees, organizer, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.title,
                event.description,
                event.start_time.isoformat(),
                event.end_time.isoformat(),
                event.location,
                json.dumps(event.attendees),
                event.organizer,
                event.status,
                user_id
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Event created successfully: {event.title} (ID: {event_id})")
            return str(event_id)
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def get_events(self, user_id: int, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events for a user within a date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, description, start_time, end_time, location, attendees, organizer, status, created_at, updated_at
                FROM calendar_events
                WHERE user_id = ? AND start_time >= ? AND end_time <= ?
                ORDER BY start_time
            """, (user_id, start_date.isoformat(), end_date.isoformat()))
            
            events = []
            for row in cursor.fetchall():
                event = CalendarEvent(
                    id=str(row[0]),
                    title=row[1],
                    description=row[2],
                    start_time=datetime.fromisoformat(row[3]),
                    end_time=datetime.fromisoformat(row[4]),
                    location=row[5],
                    attendees=json.loads(row[6]) if row[6] else [],
                    organizer=row[7],
                    status=row[8],
                    created_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    updated_at=datetime.fromisoformat(row[10]) if row[10] else None
                )
                events.append(event)
            
            conn.close()
            return events
            
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def get_availability(self, user_id: int, date: datetime, duration_minutes: int = 30) -> List[TimeSlot]:
        """Get available time slots for a user on a specific date"""
        try:
            # Get working hours for the day
            day_of_week = date.weekday()
            working_hours = self._get_working_hours(user_id, day_of_week)
            
            if not working_hours:
                return []
            
            # Get existing events for the day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT start_time, end_time
                FROM calendar_events
                WHERE user_id = ? AND start_time >= ? AND end_time <= ? AND status = 'confirmed'
                ORDER BY start_time
            """, (user_id, start_of_day.isoformat(), end_of_day.isoformat()))
            
            existing_events = []
            for row in cursor.fetchall():
                existing_events.append({
                    'start': datetime.fromisoformat(row[0]),
                    'end': datetime.fromisoformat(row[1])
                })
            
            conn.close()
            
            # Calculate available slots
            available_slots = self._calculate_available_slots(
                working_hours, existing_events, duration_minutes, date
            )
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting availability: {e}")
            return []
    
    def _get_working_hours(self, user_id: int, day_of_week: int) -> List[Dict[str, str]]:
        """Get working hours for a user on a specific day of week"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT start_time, end_time
                FROM calendar_availability
                WHERE user_id = ? AND day_of_week = ? AND is_available = TRUE
                ORDER BY start_time
            """, (user_id, day_of_week))
            
            working_hours = []
            for row in cursor.fetchall():
                working_hours.append({
                    'start': row[0],
                    'end': row[1]
                })
            
            conn.close()
            
            # If no custom availability, use default 9 AM - 5 PM
            if not working_hours:
                working_hours = [{'start': '09:00', 'end': '17:00'}]
            
            return working_hours
            
        except Exception as e:
            logger.error(f"Error getting working hours: {e}")
            return [{'start': '09:00', 'end': '17:00'}]
    
    def _calculate_available_slots(self, working_hours: List[Dict[str, str]], 
                                   existing_events: List[Dict], 
                                   duration_minutes: int, 
                                   date: datetime) -> List[TimeSlot]:
        """Calculate available time slots"""
        available_slots = []
        
        # Ensure date is timezone-aware
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        
        for work_period in working_hours:
            work_start = datetime.combine(date.date(), 
                                        datetime.strptime(work_period['start'], '%H:%M').time())
            work_end = datetime.combine(date.date(), 
                                      datetime.strptime(work_period['end'], '%H:%M').time())
            
            # Make work times timezone-aware
            work_start = work_start.replace(tzinfo=date.tzinfo)
            work_end = work_end.replace(tzinfo=date.tzinfo)
            
            # Convert existing events to datetime objects for the specific date
            events_for_period = []
            for event in existing_events:
                event_start = event['start'].replace(year=date.year, month=date.month, day=date.day)
                event_end = event['end'].replace(year=date.year, month=date.month, day=date.day)
                events_for_period.append({'start': event_start, 'end': event_end})
            
            # Sort events by start time
            events_for_period.sort(key=lambda x: x['start'])
            
            current_time = work_start
            
            for event in events_for_period:
                # Check if there's time before this event
                if event['start'] > current_time:
                    slot_duration = int((event['start'] - current_time).total_seconds() / 60)
                    if slot_duration >= duration_minutes:
                        # Add available slots in this gap
                        slots_in_gap = self._create_slots_in_gap(
                            current_time, event['start'], duration_minutes
                        )
                        available_slots.extend(slots_in_gap)
                
                current_time = max(current_time, event['end'])
            
            # Check for time after last event
            if work_end > current_time:
                slot_duration = int((work_end - current_time).total_seconds() / 60)
                if slot_duration >= duration_minutes:
                    slots_in_gap = self._create_slots_in_gap(
                        current_time, work_end, duration_minutes
                    )
                    available_slots.extend(slots_in_gap)
        
        return available_slots
    
    def _create_slots_in_gap(self, start_time: datetime, end_time: datetime, 
                            duration_minutes: int) -> List[TimeSlot]:
        """Create time slots within a gap"""
        slots = []
        current = start_time
        
        while current + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current + timedelta(minutes=duration_minutes)
            slots.append(TimeSlot(
                start_time=current,
                end_time=slot_end,
                duration_minutes=duration_minutes
            ))
            current += timedelta(minutes=30)  # 30-minute increments
        
        return slots
    
    def _has_conflicts(self, cursor, start_time: datetime, end_time: datetime, user_id: int) -> bool:
        """Check if there are conflicts with existing events"""
        cursor.execute("""
            SELECT COUNT(*)
            FROM calendar_events
            WHERE user_id = ? AND status = 'confirmed'
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
        """, (user_id, start_time.isoformat(), start_time.isoformat(), 
              end_time.isoformat(), end_time.isoformat()))
        
        return cursor.fetchone()[0] > 0
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing calendar event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Validate allowed fields to prevent SQL injection
            allowed_fields = {
                'title', 'description', 'start_time', 'end_time', 'location', 
                'status', 'priority', 'attendees', 'reminder_minutes', 'user_id'
            }
            
            # Build update query
            update_fields = []
            values = []
            
            for field, value in updates.items():
                if field not in allowed_fields:
                    continue  # Skip invalid fields
                    
                if field == 'attendees':
                    update_fields.append("attendees = ?")
                    values.append(json.dumps(value))
                elif field in ['start_time', 'end_time']:
                    update_fields.append(f"{field} = ?")
                    values.append(value.isoformat() if isinstance(value, datetime) else value)
                else:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            values.append(datetime.now(timezone.utc).isoformat())
            
            # Add event_id to values
            values.append(event_id)
            
            query = f"UPDATE calendar_events SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            updated = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if updated:
                logger.info(f"Event updated successfully: {event_id}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info(f"Event deleted successfully: {event_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False

# Global calendar manager instance
calendar_manager = CalendarManager()

# Export the manager and models
__all__ = ['CalendarManager', 'CalendarEvent', 'TimeSlot', 'calendar_manager']