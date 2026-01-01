# Meeting Tools for A2UI Integration
# Interfaces with existing FastAPI backend and database

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx
import asyncio
from sqlalchemy.orm import Session

# Import database models and functions
from meeting_models import (
    Meeting, TimeSlot, MeetingPreferences, MeetingRoom,
    create_meeting, get_meeting_by_id, get_upcoming_meetings,
    get_available_time_slots, book_time_slot, cancel_meeting,
    get_user_meeting_preferences
)
from main import get_db

logger = logging.getLogger(__name__)

# Configuration - will be set from environment or config
BACKEND_URL = "http://localhost:8005"  # Our existing FastAPI backend

def get_upcoming_meetings(user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get upcoming meetings for the user from database"""
    try:
        db = next(get_db())
        
        # Get meetings from database
        meetings = get_upcoming_meetings(db, user_email, limit)
        
        # Convert to A2UI-compatible format
        meeting_list = []
        for meeting in meetings:
            # Get participant count
            participant_count = len(meeting.participants)
            
            # Format datetime for display
            start_time = meeting.start_time
            if start_time.date() == datetime.now().date():
                date_str = "Today"
            elif start_time.date() == (datetime.now() + timedelta(days=1)).date():
                date_str = "Tomorrow"
            else:
                date_str = start_time.strftime("%A, %B %d")
            
            time_str = start_time.strftime("%I:%M %p")
            end_time_str = meeting.end_time.strftime("%I:%M %p")
            
            meeting_data = {
                "id": meeting.id,
                "title": meeting.title,
                "status": meeting.status.capitalize(),
                "statusVariant": get_status_variant(meeting.status),
                "datetime": f"{date_str}, {time_str} - {end_time_str}",
                "participants": f"{participant_count} participants",
                "meetingLink": meeting.meeting_link or "",
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat(),
                "organizer": meeting.organizer_email,
                "description": meeting.description or "",
                "timezone": meeting.timezone,
                "meeting_type": meeting.meeting_type,
                "is_recurring": meeting.is_recurring
            }
            
            meeting_list.append(meeting_data)
        
        db.close()
        return meeting_list
        
    except Exception as e:
        logger.error(f"Error getting upcoming meetings from database: {e}")
        # Fallback to mock data
        return get_mock_meetings()

def get_available_time_slots(date: str, duration_minutes: int = 30, user_email: str = None) -> List[Dict[str, Any]]:
    """Get available time slots for a specific date"""
    try:
        db = next(get_db())
        
        # Get user preferences for working hours
        preferences = get_user_meeting_preferences(db, user_email) if user_email else None
        
        # Get available slots from database
        available_slots = get_available_time_slots(db, date, duration_minutes, user_email)
        
        # Convert to A2UI-compatible format
        slots = []
        for slot in available_slots:
            slots.append({
                "id": slot.id,
                "time": slot.start_time,
                "available": slot.is_available,
                "variant": "outline" if slot.is_available else "disabled"
            })
        
        db.close()
        return slots
        
    except Exception as e:
        logger.error(f"Error getting available time slots from database: {e}")
        # Fallback to mock data
        return get_mock_time_slots()

def book_meeting(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 30,
    participants: List[str] = None,
    description: str = "",
    meeting_type: str = "google_meet",
    user_email: str = None
) -> Dict[str, Any]:
    """Book a new meeting"""
    try:
        db = next(get_db())
        
        # Parse date and time
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        time_obj = datetime.strptime(time, "%I:%M %p").time()
        
        start_time = datetime.combine(date_obj, time_obj)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Generate meeting ID
        meeting_id = f"meet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate meeting link based on type
        if meeting_type == "google_meet":
            meeting_link = f"https://meet.google.com/{meeting_id[-10:]}"
        elif meeting_type == "zoom":
            meeting_link = f"https://zoom.us/j/{hash(meeting_id) % 1000000000}"
        else:
            meeting_link = f"https://example.com/meeting/{meeting_id}"
        
        # Create meeting data
        meeting_data = {
            "id": meeting_id,
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "meeting_type": meeting_type,
            "meeting_link": meeting_link,
            "organizer_email": user_email or "user@example.com",
            "status": "confirmed",
            "created_at": datetime.now()
        }
        
        # Create the meeting
        meeting = create_meeting(db, meeting_data)
        
        # Add participants
        if participants:
            for participant_email in participants:
                participant = db.query(User).filter(User.email == participant_email).first()
                if participant:
                    meeting.participants.append(participant)
        
        db.commit()
        db.refresh(meeting)
        
        # Book time slot if available
        # This would need to be implemented based on your time slot logic
        
        logger.info(f"Meeting booked successfully: {meeting_id}")
        
        # Return meeting data in A2UI format
        return {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat(),
            "meeting_link": meeting.meeting_link,
            "meeting_type": meeting.meeting_type,
            "organizer": meeting.organizer_email,
            "participants": [p.email for p in meeting.participants],
            "status": meeting.status
        }
        
    except Exception as e:
        logger.error(f"Error booking meeting: {e}")
        raise
    finally:
        db.close()

def get_meeting_details(meeting_id: str, user_email: str = None) -> Dict[str, Any]:
    """Get detailed information about a specific meeting"""
    try:
        db = next(get_db())
        
        meeting = get_meeting_by_id(db, meeting_id)
        
        if not meeting:
            return {
                "id": meeting_id,
                "title": "Meeting Not Found",
                "error": "Meeting not found or you don't have access to it"
            }
        
        # Get participant details
        participants = []
        for participant in meeting.participants:
            participants.append({
                "email": participant.email,
                "name": participant.name or participant.email,
                "status": "accepted"  # This would come from the association table
            })
        
        # Format datetime
        start_time = meeting.start_time
        date_str = start_time.strftime("%A, %B %d, %Y")
        time_str = start_time.strftime("%I:%M %p")
        end_time_str = meeting.end_time.strftime("%I:%M %p")
        
        # Create agenda items (mock for now)
        agenda = [
            {"time": start_time.strftime("%I:%M %p"), "topic": "Welcome & Introductions"},
            {"time": (start_time + timedelta(minutes=5)).strftime("%I:%M %p"), "topic": "Main Discussion"},
            {"time": (start_time + timedelta(minutes=20)).strftime("%I:%M %p"), "topic": "Action Items & Next Steps"}
        ]
        
        # Documents (mock for now)
        documents = [
            {"name": "Meeting Agenda.pdf", "url": "#"},
            {"name": "Previous Notes.pdf", "url": "#"}
        ]
        
        detailed_meeting = {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "datetime": f"{date_str} at {time_str} - {end_time_str}",
            "date": start_time.strftime("%Y-%m-%d"),
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat(),
            "duration": (meeting.end_time - meeting.start_time).total_seconds() / 60,
            "timezone": meeting.timezone,
            "organizer": meeting.organizer_email,
            "meeting_link": meeting.meeting_link,
            "meeting_type": meeting.meeting_type,
            "status": meeting.status,
            "participants": participants,
            "participant_count": len(participants),
            "agenda": agenda,
            "documents": documents,
            "reminder": {
                "enabled": meeting.reminder_enabled,
                "time_before": f"{meeting.reminder_time_before} minutes"
            },
            "is_recurring": meeting.is_recurring,
            "created_at": meeting.created_at.isoformat()
        }
        
        db.close()
        return detailed_meeting
        
    except Exception as e:
        logger.error(f"Error getting meeting details: {e}")
        return {"error": str(e)}

def cancel_meeting(meeting_id: str, user_email: str = None) -> Dict[str, Any]:
    """Cancel a meeting"""
    try:
        db = next(get_db())
        
        # Check if user has permission to cancel
        meeting = get_meeting_by_id(db, meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}
        
        if meeting.organizer_email != user_email:
            return {"error": "You don't have permission to cancel this meeting"}
        
        # Cancel the meeting
        success = cancel_meeting(db, meeting_id)
        
        if success:
            logger.info(f"Meeting cancelled: {meeting_id}")
            return {
                "success": True,
                "message": f"Meeting {meeting_id} has been cancelled successfully.",
                "cancelled_at": datetime.now().isoformat()
            }
        else:
            return {"error": "Failed to cancel meeting"}
            
    except Exception as e:
        logger.error(f"Error canceling meeting: {e}")
        return {"error": str(e)}
    finally:
        db.close()

def update_meeting(meeting_id: str, updates: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
    """Update an existing meeting"""
    try:
        db = next(get_db())
        
        meeting = get_meeting_by_id(db, meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}
        
        # Check permission
        if meeting.organizer_email != user_email:
            return {"error": "You don't have permission to update this meeting"}
        
        # Update fields
        for key, value in updates.items():
            if hasattr(meeting, key):
                setattr(meeting, key, value)
        
        meeting.updated_at = datetime.now()
        db.commit()
        db.refresh(meeting)
        
        logger.info(f"Meeting updated: {meeting_id}")
        
        return {
            "success": True,
            "message": f"Meeting {meeting_id} has been updated successfully.",
            "updated_at": datetime.now().isoformat(),
            "changes": updates
        }
        
    except Exception as e:
        logger.error(f"Error updating meeting: {e}")
        return {"error": str(e)}
    finally:
        db.close()

# Helper functions
def get_status_variant(status: str) -> str:
    """Get A2UI status variant from meeting status"""
    status_map = {
        'confirmed': 'success',
        'cancelled': 'error',
        'tentative': 'warning',
        'draft': 'secondary'
    }
    return status_map.get(status, 'secondary')

def get_mock_meetings() -> List[Dict[str, Any]]:
    """Fallback mock meetings data"""
    return [
        {
            "id": "meet_001",
            "title": "Team Standup",
            "status": "Confirmed",
            "statusVariant": "success",
            "datetime": "Today, 2:00 PM - 2:30 PM",
            "participants": "5 participants",
            "meetingLink": "https://meet.google.com/abc-defg-hij",
            "start_time": "2024-01-15T14:00:00Z",
            "end_time": "2024-01-15T14:30:00Z",
            "organizer": "john@example.com",
            "description": "Weekly team standup meeting"
        },
        {
            "id": "meet_002",
            "title": "Client Presentation",
            "status": "Confirmed",
            "statusVariant": "success",
            "datetime": "Tomorrow, 10:00 AM - 11:00 AM",
            "participants": "8 participants",
            "meetingLink": "https://zoom.us/j/123456789",
            "start_time": "2024-01-16T10:00:00Z",
            "end_time": "2024-01-16T11:00:00Z",
            "organizer": "jane@example.com",
            "description": "Q4 results presentation to client"
        }
    ]

def get_mock_time_slots() -> List[Dict[str, Any]]:
    """Fallback mock time slots data"""
    return [
        {"time": "9:00 AM", "available": True, "variant": "outline"},
        {"time": "9:30 AM", "available": True, "variant": "outline"},
        {"time": "10:00 AM", "available": True, "variant": "outline"},
        {"time": "10:30 AM", "available": True, "variant": "outline"},
        {"time": "11:00 AM", "available": True, "variant": "outline"},
        {"time": "2:00 PM", "available": True, "variant": "outline"},
        {"time": "2:30 PM", "available": True, "variant": "outline"},
        {"time": "3:00 PM", "available": True, "variant": "outline"},
        {"time": "3:30 PM", "available": True, "variant": "outline"},
        {"time": "4:00 PM", "available": True, "variant": "outline"},
        {"time": "4:30 PM", "available": True, "variant": "outline"}
    ]

# Export all functions
__all__ = [
    'get_upcoming_meetings',
    'get_available_time_slots',
    'book_meeting',
    'get_meeting_details',
    'cancel_meeting',
    'update_meeting'
]