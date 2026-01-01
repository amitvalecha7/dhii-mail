# Meeting Tools for A2UI Integration
# Interfaces with existing FastAPI backend

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx
import asyncio

logger = logging.getLogger(__name__)

# Configuration - will be set from environment or config
BACKEND_URL = "http://localhost:8005"  # Our existing FastAPI backend

async def make_backend_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make request to FastAPI backend"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise

def get_upcoming_meetings() -> List[Dict[str, Any]]:
    """Get upcoming meetings for the user"""
    try:
        # This would normally call our existing backend
        # For now, return mock data
        mock_meetings = [
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
                "status": "Pending",
                "statusVariant": "warning",
                "datetime": "Tomorrow, 10:00 AM - 11:00 AM",
                "participants": "8 participants",
                "meetingLink": "https://zoom.us/j/123456789",
                "start_time": "2024-01-16T10:00:00Z",
                "end_time": "2024-01-16T11:00:00Z",
                "organizer": "jane@example.com",
                "description": "Q4 results presentation to client"
            },
            {
                "id": "meet_003",
                "title": "Sprint Planning",
                "status": "Confirmed",
                "statusVariant": "success",
                "datetime": "Friday, 9:00 AM - 10:30 AM",
                "participants": "6 participants",
                "meetingLink": "https://meet.google.com/xyz-abcd-efg",
                "start_time": "2024-01-19T09:00:00Z",
                "end_time": "2024-01-19T10:30:00Z",
                "organizer": "sarah@example.com",
                "description": "Sprint planning for next iteration"
            }
        ]
        
        return mock_meetings
        
    except Exception as e:
        logger.error(f"Error getting upcoming meetings: {e}")
        return []

def get_available_time_slots(date: str, duration_minutes: int = 30) -> List[Dict[str, Any]]:
    """Get available time slots for a specific date"""
    try:
        # Mock available time slots
        # In a real implementation, this would check calendar availability
        
        slots = [
            {"time": "9:00 AM", "available": True, "variant": "outline"},
            {"time": "9:30 AM", "available": True, "variant": "outline"},
            {"time": "10:00 AM", "available": True, "variant": "outline"},
            {"time": "10:30 AM", "available": True, "variant": "outline"},
            {"time": "11:00 AM", "available": True, "variant": "outline"},
            {"time": "11:30 AM", "available": False, "variant": "disabled"},
            {"time": "2:00 PM", "available": True, "variant": "outline"},
            {"time": "2:30 PM", "available": True, "variant": "outline"},
            {"time": "3:00 PM", "available": True, "variant": "outline"},
            {"time": "3:30 PM", "available": False, "variant": "disabled"},
            {"time": "4:00 PM", "available": True, "variant": "outline"},
            {"time": "4:30 PM", "available": True, "variant": "outline"},
        ]
        
        # Return only available slots
        return [slot for slot in slots if slot["available"]]
        
    except Exception as e:
        logger.error(f"Error getting available time slots: {e}")
        return []

def book_meeting(
    title: str,
    date: str,
    time: str,
    duration_minutes: int,
    participants: List[str],
    description: str = "",
    meeting_type: str = "google_meet"
) -> Dict[str, Any]:
    """Book a new meeting"""
    try:
        # Mock successful booking
        # In a real implementation, this would:
        # 1. Create calendar event
        # 2. Generate meeting link
        # 3. Send invitations
        # 4. Store in database
        
        meeting_id = f"meet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate meeting link based on type
        if meeting_type == "google_meet":
            meeting_link = f"https://meet.google.com/{meeting_id[-10:]}"
        elif meeting_type == "zoom":
            meeting_link = f"https://zoom.us/j/{hash(meeting_id) % 1000000000}"
        else:
            meeting_link = f"https://example.com/meeting/{meeting_id}"
        
        # Parse date and time
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        time_obj = datetime.strptime(time, "%I:%M %p").time()
        
        start_time = datetime.combine(date_obj, time_obj)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        meeting_data = {
            "id": meeting_id,
            "title": title,
            "description": description,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "participants": participants,
            "meeting_link": meeting_link,
            "meeting_type": meeting_type,
            "status": "confirmed",
            "organizer": "user@example.com",  # Would be actual user
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Meeting booked successfully: {meeting_id}")
        return meeting_data
        
    except Exception as e:
        logger.error(f"Error booking meeting: {e}")
        raise

def get_meeting_details(meeting_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific meeting"""
    try:
        # Mock meeting details
        # In a real implementation, this would fetch from database
        
        mock_meetings = get_upcoming_meetings()
        
        for meeting in mock_meetings:
            if meeting["id"] == meeting_id:
                # Add additional details
                detailed_meeting = meeting.copy()
                detailed_meeting.update({
                    "agenda": [
                        {"time": "2:00 PM", "topic": "Welcome & Introductions"},
                        {"time": "2:05 PM", "topic": "Team Updates"},
                        {"time": "2:15 PM", "topic": "Discussion Topics"},
                        {"time": "2:25 PM", "topic": "Action Items & Next Steps"}
                    ],
                    "documents": [
                        {"name": "Meeting Agenda.pdf", "url": "#"},
                        {"name": "Previous Notes.pdf", "url": "#"}
                    ],
                    "reminder": {
                        "enabled": True,
                        "time_before": "15 minutes"
                    }
                })
                return detailed_meeting
        
        # Return default if not found
        return {
            "id": meeting_id,
            "title": "Meeting Not Found",
            "error": "Meeting not found or you don't have access to it"
        }
        
    except Exception as e:
        logger.error(f"Error getting meeting details: {e}")
        return {"error": str(e)}

def cancel_meeting(meeting_id: str) -> Dict[str, Any]:
    """Cancel a meeting"""
    try:
        # Mock cancellation
        # In a real implementation, this would:
        # 1. Update calendar event status
        # 2. Send cancellation notifications
        # 3. Update database
        
        logger.info(f"Meeting cancelled: {meeting_id}")
        
        return {
            "success": True,
            "message": f"Meeting {meeting_id} has been cancelled successfully.",
            "cancelled_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error canceling meeting: {e}")
        return {"error": str(e)}

def update_meeting(meeting_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing meeting"""
    try:
        # Mock update
        # In a real implementation, this would update the meeting in the database
        
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

# Export all functions
__all__ = [
    'get_upcoming_meetings',
    'get_available_time_slots',
    'book_meeting',
    'get_meeting_details',
    'cancel_meeting',
    'update_meeting',
    'make_backend_request'
]