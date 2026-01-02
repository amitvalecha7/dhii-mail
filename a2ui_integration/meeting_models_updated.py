# Database models for meeting assistant
# Compatible with existing DatabaseManager structure

import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class MeetingDatabaseManager:
    """Meeting database manager that works with the existing DatabaseManager"""
    
    def __init__(self, db_path: str = "dhii_mail.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize meeting-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create meetings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                timezone TEXT DEFAULT 'UTC',
                meeting_type TEXT DEFAULT 'google_meet',
                meeting_link TEXT,
                meeting_id_external TEXT,
                organizer_email TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                visibility TEXT DEFAULT 'private',
                is_recurring BOOLEAN DEFAULT 0,
                recurrence_rule TEXT,
                parent_meeting_id TEXT,
                reminder_enabled BOOLEAN DEFAULT 1,
                reminder_time_before INTEGER DEFAULT 15,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                cancelled_at TEXT
            )
        ''')
        
        # Create meeting participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meeting_participants (
                meeting_id TEXT,
                user_email TEXT,
                role TEXT DEFAULT 'attendee',
                status TEXT DEFAULT 'pending',
                response_time TEXT,
                PRIMARY KEY (meeting_id, user_email),
                FOREIGN KEY (meeting_id) REFERENCES meetings (id),
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        # Create meeting rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meeting_rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                capacity INTEGER DEFAULT 10,
                location TEXT,
                has_video_conference BOOLEAN DEFAULT 1,
                has_whiteboard BOOLEAN DEFAULT 1,
                has_projector BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                booking_enabled BOOLEAN DEFAULT 1,
                working_hours_start TEXT DEFAULT '09:00',
                working_hours_end TEXT DEFAULT '18:00',
                timezone TEXT DEFAULT 'UTC',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create time slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_slots (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                is_blocked BOOLEAN DEFAULT 0,
                meeting_id TEXT,
                room_id TEXT,
                blocked_by_email TEXT,
                blocked_reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings (id),
                FOREIGN KEY (room_id) REFERENCES meeting_rooms (id),
                FOREIGN KEY (blocked_by_email) REFERENCES users (email)
            )
        ''')
        
        # Create meeting preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meeting_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT UNIQUE NOT NULL,
                default_duration INTEGER DEFAULT 30,
                default_meeting_type TEXT DEFAULT 'google_meet',
                default_reminder_time INTEGER DEFAULT 15,
                working_hours_start TEXT DEFAULT '09:00',
                working_hours_end TEXT DEFAULT '18:00',
                working_days TEXT DEFAULT '1,2,3,4,5',
                timezone TEXT DEFAULT 'UTC',
                meeting_buffer_before INTEGER DEFAULT 5,
                meeting_buffer_after INTEGER DEFAULT 5,
                auto_accept_internal BOOLEAN DEFAULT 1,
                auto_accept_external BOOLEAN DEFAULT 0,
                email_notifications BOOLEAN DEFAULT 1,
                calendar_notifications BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Meeting database tables initialized")
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new meeting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO meetings (
                    id, title, description, start_time, end_time, timezone,
                    meeting_type, meeting_link, organizer_email, status, 
                    reminder_enabled, reminder_time_before, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meeting_data['id'],
                meeting_data['title'],
                meeting_data.get('description', ''),
                meeting_data['start_time'].isoformat(),
                meeting_data['end_time'].isoformat(),
                meeting_data.get('timezone', 'UTC'),
                meeting_data.get('meeting_type', 'google_meet'),
                meeting_data.get('meeting_link', ''),
                meeting_data['organizer_email'],
                meeting_data.get('status', 'confirmed'),
                meeting_data.get('reminder_enabled', True),
                meeting_data.get('reminder_time_before', 15),
                datetime.now().isoformat()
            ))
            
            # Add participants
            participants = meeting_data.get('participants', [])
            for participant_email in participants:
                cursor.execute('''
                    INSERT INTO meeting_participants (meeting_id, user_email, role, status)
                    VALUES (?, ?, ?, ?)
                ''', (meeting_data['id'], participant_email, 'attendee', 'pending'))
            
            conn.commit()
            logger.info(f"Meeting created: {meeting_data['id']}")
            return meeting_data
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating meeting: {e}")
            raise
        finally:
            conn.close()
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM meetings WHERE id = ?
            ''', (meeting_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convert to dict
            columns = [description[0] for description in cursor.description]
            meeting = dict(zip(columns, row))
            
            # Get participants
            cursor.execute('''
                SELECT user_email, role, status FROM meeting_participants 
                WHERE meeting_id = ?
            ''', (meeting_id,))
            
            participants = []
            for row in cursor.fetchall():
                participants.append({
                    'email': row[0],
                    'role': row[1],
                    'status': row[2]
                })
            
            meeting['participants'] = participants
            return meeting
            
        finally:
            conn.close()
    
    def get_upcoming_meetings(self, user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming meetings for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            
            cursor.execute('''
                SELECT DISTINCT m.* FROM meetings m
                JOIN meeting_participants mp ON m.id = mp.meeting_id
                WHERE mp.user_email = ? AND m.start_time > ? AND m.status = 'confirmed'
                ORDER BY m.start_time
                LIMIT ?
            ''', (user_email, now, limit))
            
            meetings = []
            columns = [description[0] for description in cursor.description]
            
            for row in cursor.fetchall():
                meeting = dict(zip(columns, row))
                
                # Get participants for each meeting
                cursor.execute('''
                    SELECT user_email, role, status FROM meeting_participants 
                    WHERE meeting_id = ?
                ''', (meeting['id'],))
                
                participants = []
                for participant_row in cursor.fetchall():
                    participants.append({
                        'email': participant_row[0],
                        'role': participant_row[1],
                        'status': participant_row[2]
                    })
                
                meeting['participants'] = participants
                meetings.append(meeting)
            
            return meetings
            
        finally:
            conn.close()
    
    def get_available_time_slots(self, date: str, duration_minutes: int = 30, user_email: str = None) -> List[Dict[str, Any]]:
        """Get available time slots for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM time_slots 
                WHERE date = ? AND is_available = 1 AND is_blocked = 0 AND meeting_id IS NULL
                ORDER BY start_time
            ''', (date,))
            
            slots = []
            columns = [description[0] for description in cursor.description]
            
            for row in cursor.fetchall():
                slot = dict(zip(columns, row))
                slots.append({
                    'id': slot['id'],
                    'time': slot['start_time'],
                    'available': slot['is_available'],
                    'variant': 'outline' if slot['is_available'] else 'disabled'
                })
            
            return slots
            
        finally:
            conn.close()
    
    def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a meeting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE meetings 
                SET status = 'cancelled', cancelled_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), meeting_id))
            
            # Free up time slots
            cursor.execute('''
                UPDATE time_slots 
                SET is_available = 1, meeting_id = NULL
                WHERE meeting_id = ?
            ''', (meeting_id,))
            
            conn.commit()
            logger.info(f"Meeting cancelled: {meeting_id}")
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error cancelling meeting: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_meeting_preferences(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Get user's meeting preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM meeting_preferences WHERE user_email = ?
            ''', (user_email,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
            
        finally:
            conn.close()
    
    def create_or_update_meeting_preferences(self, user_email: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update user's meeting preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Validate allowed fields to prevent SQL injection
            allowed_fields = {
                'default_duration', 'default_reminder_time', 'meeting_buffer_before', 
                'meeting_buffer_after', 'auto_accept_internal', 'auto_accept_external', 
                'email_notifications', 'calendar_notifications', 'preferred_time_start', 
                'preferred_time_end', 'max_daily_meetings', 'working_days'
            }
            
            existing = self.get_user_meeting_preferences(user_email)
            
            if existing:
                # Update existing preferences
                update_fields = []
                values = []
                for key, value in preferences.items():
                    if key not in allowed_fields:
                        continue  # Skip invalid fields
                        
                    if key in ['default_duration', 'default_reminder_time', 'meeting_buffer_before', 'meeting_buffer_after']:
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                    elif key in ['auto_accept_internal', 'auto_accept_external', 'email_notifications', 'calendar_notifications']:
                        update_fields.append(f"{key} = ?")
                        values.append(bool(value))
                    else:
                        update_fields.append(f"{key} = ?")
                        values.append(str(value))
                
                update_fields.append("updated_at = ?")
                values.append(datetime.now().isoformat())
                values.append(user_email)
                
                query = f"UPDATE meeting_preferences SET {', '.join(update_fields)} WHERE user_email = ?"
                cursor.execute(query, values)
            else:
                # Create new preferences
                preferences['user_email'] = user_email
                preferences['created_at'] = datetime.now().isoformat()
                preferences['updated_at'] = datetime.now().isoformat()
                
                fields = []
                values = []
                for key, value in preferences.items():
                    if key not in allowed_fields and key not in ['user_email', 'created_at', 'updated_at']:
                        continue  # Skip invalid fields
                        
                    fields.append(key)
                    if key in ['default_duration', 'default_reminder_time', 'meeting_buffer_before', 'meeting_buffer_after']:
                        values.append(value)
                    elif key in ['auto_accept_internal', 'auto_accept_external', 'email_notifications', 'calendar_notifications']:
                        values.append(bool(value))
                    else:
                        values.append(str(value))
                
                query = f"INSERT INTO meeting_preferences ({', '.join(fields)}) VALUES ({', '.join(['?' for _ in fields])})"
                cursor.execute(query, values)
            
            conn.commit()
            return preferences
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating meeting preferences: {e}")
            raise
        finally:
            conn.close()

# Global instance
_meeting_db_manager = None

def get_meeting_db_manager() -> MeetingDatabaseManager:
    """Get the global meeting database manager instance"""
    global _meeting_db_manager
    if _meeting_db_manager is None:
        _meeting_db_manager = MeetingDatabaseManager()
    return _meeting_db_manager

# Database helper functions
def create_meeting(meeting_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new meeting"""
    return get_meeting_db_manager().create_meeting(meeting_data)

def get_meeting_by_id(meeting_id: str) -> Optional[Dict[str, Any]]:
    """Get meeting by ID"""
    return get_meeting_db_manager().get_meeting_by_id(meeting_id)

def get_upcoming_meetings(user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get upcoming meetings for a user"""
    return get_meeting_db_manager().get_upcoming_meetings(user_email, limit)

def get_meetings_by_date_range(user_email: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Get meetings for a user within a date range"""
    # This would be implemented based on the existing database structure
    # For now, return all upcoming meetings
    return get_upcoming_meetings(user_email, limit=100)

def get_available_time_slots(date: str, duration_minutes: int = 30, user_email: str = None) -> List[Dict[str, Any]]:
    """Get available time slots for a specific date"""
    return get_meeting_db_manager().get_available_time_slots(date, duration_minutes, user_email)

def book_time_slot(slot_id: str, meeting_id: str) -> Dict[str, Any]:
    """Book a time slot"""
    conn = sqlite3.connect(get_meeting_db_manager().db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE time_slots 
            SET is_available = 0, meeting_id = ?
            WHERE id = ? AND is_available = 1 AND is_blocked = 0
        ''', (meeting_id, slot_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"success": True, "message": "Time slot booked successfully"}
        else:
            return {"error": "Time slot not available or already booked"}
            
    finally:
        conn.close()

def cancel_meeting(meeting_id: str) -> bool:
    """Cancel a meeting"""
    return get_meeting_db_manager().cancel_meeting(meeting_id)

def get_user_meeting_preferences(user_email: str) -> Optional[Dict[str, Any]]:
    """Get user's meeting preferences"""
    return get_meeting_db_manager().get_user_meeting_preferences(user_email)

def create_or_update_meeting_preferences(user_email: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update user's meeting preferences"""
    return get_meeting_db_manager().create_or_update_meeting_preferences(user_email, preferences)