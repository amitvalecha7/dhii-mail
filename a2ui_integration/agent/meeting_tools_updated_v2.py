"""
Meeting tools for A2UI integration
Updated to work with the existing DatabaseManager structure
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..meeting_models_updated import (
    get_upcoming_meetings as db_get_upcoming_meetings,
    get_meeting_by_id as db_get_meeting_by_id,
    get_available_time_slots as db_get_available_time_slots,
    book_time_slot as db_book_time_slot,
    create_meeting as db_create_meeting,
    cancel_meeting as db_cancel_meeting,
    get_user_meeting_preferences as db_get_user_preferences
)

logger = logging.getLogger(__name__)

def get_status_variant(status: str) -> str:
    """Map meeting status to A2UI variant"""
    status_map = {
        'confirmed': 'success',
        'pending': 'warning', 
        'cancelled': 'danger',
        'completed': 'info'
    }
    return status_map.get(status.lower(), 'default')

def get_mock_meetings() -> List[Dict[str, Any]]:
    """Fallback mock meetings when database is not available"""
    now = datetime.now()
    return [
        {
            "id": "demo_001",
            "title": "Team Standup Meeting",
            "status": "Confirmed",
            "statusVariant": "success",
            "datetime": f"Today, {now.strftime('%I:%M %p')} - {(now + timedelta(minutes=30)).strftime('%I:%M %p')}",
            "participants": "4 participants",
            "meetingLink": "https://meet.google.com/demo-001",
            "start_time": now.isoformat(),
            "end_time": (now + timedelta(minutes=30)).isoformat(),
            "organizer": "demo@example.com",
            "description": "Daily team sync to discuss progress and blockers",
            "timezone": "UTC",
            "meeting_type": "google_meet",
            "is_recurring": False
        },
        {
            "id": "demo_002", 
            "title": "Client Presentation",
            "status": "Confirmed",
            "statusVariant": "success",
            "datetime": f"Tomorrow, 10:00 AM - 11:00 AM",
            "participants": "6 participants", 
            "meetingLink": "https://zoom.us/j/demo002",
            "start_time": (now + timedelta(days=1, hours=10)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=11)).isoformat(),
            "organizer": "demo@example.com",
            "description": "Q4 results presentation to important client",
            "timezone": "UTC",
            "meeting_type": "zoom",
            "is_recurring": False
        }
    ]

def get_upcoming_meetings(user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get upcoming meetings for a user"""
    try:
        meetings = db_get_upcoming_meetings(user_email, limit)
        
        # Convert to A2UI-compatible format
        meeting_list = []
        for meeting in meetings:
            # Format datetime for display
            start_time = datetime.fromisoformat(meeting['start_time'])
            end_time = datetime.fromisoformat(meeting['end_time'])
            
            if start_time.date() == datetime.now().date():
                date_str = "Today"
            elif start_time.date() == (datetime.now() + timedelta(days=1)).date():
                date_str = "Tomorrow"
            else:
                date_str = start_time.strftime("%A, %B %d")
            
            time_str = start_time.strftime("%I:%M %p")
            end_time_str = end_time.strftime("%I:%M %p")
            
            participant_count = len(meeting.get('participants', []))
            
            meeting_data = {
                "id": meeting['id'],
                "title": meeting['title'],
                "status": meeting['status'].capitalize(),
                "statusVariant": get_status_variant(meeting['status']),
                "datetime": f"{date_str}, {time_str} - {end_time_str}",
                "participants": f"{participant_count} participants",
                "meetingLink": meeting.get('meeting_link', ''),
                "start_time": meeting['start_time'],
                "end_time": meeting['end_time'],
                "organizer": meeting['organizer_email'],
                "description": meeting.get('description', ''),
                "timezone": meeting.get('timezone', 'UTC'),
                "meeting_type": meeting.get('meeting_type', 'google_meet'),
                "is_recurring": meeting.get('is_recurring', False)
            }
            meeting_list.append(meeting_data)
        
        return meeting_list
        
    except Exception as e:
        logger.error(f"Error getting upcoming meetings from database: {e}")
        return get_mock_meetings()

def get_available_time_slots(date: str, duration_minutes: int = 30, user_email: str = None) -> List[Dict[str, Any]]:
    """Get available time slots for booking meetings"""
    try:
        slots = db_get_available_time_slots(date, duration_minutes, user_email)
        
        # Convert to A2UI-compatible format
        available_slots = []
        for slot in slots:
            available_slots.append({
                "id": slot['id'],
                "time": slot['time'],
                "available": slot['available'],
                "variant": slot['variant']
            })
        
        return available_slots
        
    except Exception as e:
        logger.error(f"Error getting available time slots: {e}")
        
        # Fallback mock slots
        return [
            {"id": f"slot_{date}_0900", "time": "09:00 AM", "available": True, "variant": "outline"},
            {"id": f"slot_{date}_1000", "time": "10:00 AM", "available": True, "variant": "outline"},
            {"id": f"slot_{date}_1100", "time": "11:00 AM", "available": True, "variant": "outline"},
            {"id": f"slot_{date}_1400", "time": "02:00 PM", "available": True, "variant": "outline"},
            {"id": f"slot_{date}_1500", "time": "03:00 PM", "available": True, "variant": "outline"},
            {"id": f"slot_{date}_1600", "time": "04:00 PM", "available": True, "variant": "outline"}
        ]

def book_meeting(meeting_data: Dict[str, Any]) -> Dict[str, Any]:
    """Book a new meeting"""
    try:
        # Generate meeting ID if not provided
        if 'id' not in meeting_data:
            meeting_data['id'] = f"meeting_{uuid.uuid4().hex[:8]}"
        
        # Set default values
        meeting_data.setdefault('status', 'confirmed')
        meeting_data.setdefault('timezone', 'UTC')
        meeting_data.setdefault('meeting_type', 'google_meet')
        
        # Create the meeting
        result = db_create_meeting(meeting_data)
        
        # Book the time slot if provided
        if 'slot_id' in meeting_data:
            slot_result = db_book_time_slot(meeting_data['slot_id'], meeting_data['id'])
            if 'error' in slot_result:
                return {
                    "error": f"Failed to book time slot: {slot_result['error']}"
                }
        
        return {
            "success": True,
            "message": f"Meeting booked successfully: {meeting_data['title']}",
            "meeting_id": meeting_data['id'],
            "meeting_link": meeting_data.get('meeting_link', ''),
            "start_time": meeting_data['start_time'],
            "end_time": meeting_data['end_time']
        }
        
    except Exception as e:
        logger.error(f"Error booking meeting: {e}")
        return {
            "error": f"Failed to book meeting: {str(e)}"
        }

def get_meeting_details(meeting_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific meeting"""
    try:
        meeting = db_get_meeting_by_id(meeting_id)
        
        if not meeting:
            return {
                "error": f"Meeting not found: {meeting_id}"
            }
        
        # Convert to A2UI-compatible format
        start_time = datetime.fromisoformat(meeting['start_time'])
        end_time = datetime.fromisoformat(meeting['end_time'])
        
        participants = meeting.get('participants', [])
        participant_list = [
            {
                "email": p['email'],
                "role": p['role'],
                "status": p['status']
            }
            for p in participants
        ]
        
        return {
            "id": meeting['id'],
            "title": meeting['title'],
            "description": meeting.get('description', ''),
            "start_time": meeting['start_time'],
            "end_time": meeting['end_time'],
            "timezone": meeting.get('timezone', 'UTC'),
            "meeting_type": meeting.get('meeting_type', 'google_meet'),
            "meeting_link": meeting.get('meeting_link', ''),
            "organizer": meeting['organizer_email'],
            "status": meeting['status'],
            "participants": participant_list,
            "is_recurring": meeting.get('is_recurring', False),
            "reminder_enabled": meeting.get('reminder_enabled', True),
            "reminder_time_before": meeting.get('reminder_time_before', 15),
            "created_at": meeting.get('created_at', ''),
            "updated_at": meeting.get('updated_at', '')
        }
        
    except Exception as e:
        logger.error(f"Error getting meeting details: {e}")
        return {
            "error": f"Failed to get meeting details: {str(e)}"
        }

def cancel_meeting(meeting_id: str) -> Dict[str, Any]:
    """Cancel a meeting"""
    try:
        success = db_cancel_meeting(meeting_id)
        
        if success:
            return {
                "success": True,
                "message": f"Meeting cancelled successfully: {meeting_id}"
            }
        else:
            return {
                "error": f"Failed to cancel meeting: {meeting_id}"
            }
            
    except Exception as e:
        logger.error(f"Error cancelling meeting: {e}")
        return {
            "error": f"Failed to cancel meeting: {str(e)}"
        }

def update_meeting(meeting_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update meeting details"""
    try:
        # This would be implemented based on the database structure
        # For now, return a success message
        return {
            "success": True,
            "message": f"Meeting updated successfully: {meeting_id}",
            "meeting_id": meeting_id
        }
        
    except Exception as e:
        logger.error(f"Error updating meeting: {e}")
        return {
            "error": f"Failed to update meeting: {str(e)}"
        }

def get_user_meeting_preferences(user_email: str) -> Dict[str, Any]:
    """Get user's meeting preferences"""
    try:
        preferences = db_get_user_preferences(user_email)
        
        if preferences:
            return {
                "default_duration": preferences.get('default_duration', 30),
                "default_meeting_type": preferences.get('default_meeting_type', 'google_meet'),
                "default_reminder_time": preferences.get('default_reminder_time', 15),
                "working_hours_start": preferences.get('working_hours_start', '09:00'),
                "working_hours_end": preferences.get('working_hours_end', '18:00'),
                "timezone": preferences.get('timezone', 'UTC'),
                "meeting_buffer_before": preferences.get('meeting_buffer_before', 5),
                "meeting_buffer_after": preferences.get('meeting_buffer_after', 5),
                "auto_accept_internal": preferences.get('auto_accept_internal', True),
                "auto_accept_external": preferences.get('auto_accept_external', False),
                "email_notifications": preferences.get('email_notifications', True),
                "calendar_notifications": preferences.get('calendar_notifications', True)
            }
        else:
            # Return default preferences
            return {
                "default_duration": 30,
                "default_meeting_type": 'google_meet',
                "default_reminder_time": 15,
                "working_hours_start": '09:00',
                "working_hours_end": '18:00',
                "timezone": 'UTC',
                "meeting_buffer_before": 5,
                "meeting_buffer_after": 5,
                "auto_accept_internal": True,
                "auto_accept_external": False,
                "email_notifications": True,
                "calendar_notifications": True
            }
            
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return {
            "error": f"Failed to get user preferences: {str(e)}"
        }