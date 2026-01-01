"""
Video Conference Manager for dhii Mail
Handles video meeting creation, management, and integration with external services
"""

import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from fastapi import HTTPException
import httpx
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class VideoMeeting(BaseModel):
    """Video meeting model"""
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    organizer_email: str
    participants: List[str] = []
    meeting_url: Optional[str] = None
    meeting_id: Optional[str] = None
    password: Optional[str] = None
    status: str = "scheduled"  # scheduled, active, completed, cancelled
    created_at: datetime = datetime.now(timezone.utc)
    recording_url: Optional[str] = None
    transcription: Optional[str] = None

class VideoMeetingCreate(BaseModel):
    """Video meeting creation request"""
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[str] = []
    auto_recording: bool = True

class VideoMeetingUpdate(BaseModel):
    """Video meeting update request"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: Optional[List[str]] = None
    status: Optional[str] = None

class VideoManager:
    """Video Conference Manager"""
    
    def __init__(self):
        self.meetings = {}  # In-memory storage for now, can be moved to database
        self.supported_providers = ["jitsi", "zoom", "google_meet", "teams"]
        self.default_provider = "jitsi"  # Default to open-source Jitsi
        
    def create_meeting(self, meeting_data: VideoMeetingCreate, organizer_email: str) -> VideoMeeting:
        """Create a new video meeting"""
        try:
            meeting_id = str(uuid.uuid4())
            
            # Generate meeting URL based on provider
            meeting_url, meeting_password = self._generate_meeting_url(
                meeting_data.title, meeting_id, self.default_provider
            )
            
            meeting = VideoMeeting(
                id=meeting_id,
                title=meeting_data.title,
                description=meeting_data.description,
                start_time=meeting_data.start_time,
                end_time=meeting_data.end_time,
                organizer_email=organizer_email,
                participants=meeting_data.participants,
                meeting_url=meeting_url,
                meeting_id=meeting_id,
                password=meeting_password,
                status="scheduled"
            )
            
            # Store meeting
            self.meetings[meeting_id] = meeting
            
            logger.info(f"Created video meeting: {meeting_id} for {organizer_email}")
            return meeting
            
        except Exception as e:
            logger.error(f"Error creating video meeting: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create meeting: {str(e)}")
    
    def get_meeting(self, meeting_id: str) -> VideoMeeting:
        """Get meeting details"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return self.meetings[meeting_id]
    
    def update_meeting(self, meeting_id: str, update_data: VideoMeetingUpdate) -> VideoMeeting:
        """Update meeting details"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting = self.meetings[meeting_id]
        
        # Update fields if provided
        if update_data.title is not None:
            meeting.title = update_data.title
        if update_data.description is not None:
            meeting.description = update_data.description
        if update_data.start_time is not None:
            meeting.start_time = update_data.start_time
        if update_data.end_time is not None:
            meeting.end_time = update_data.end_time
        if update_data.participants is not None:
            meeting.participants = update_data.participants
        if update_data.status is not None:
            meeting.status = update_data.status
        
        logger.info(f"Updated video meeting: {meeting_id}")
        return meeting
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        del self.meetings[meeting_id]
        logger.info(f"Deleted video meeting: {meeting_id}")
        return True
    
    def list_user_meetings(self, user_email: str) -> List[VideoMeeting]:
        """List all meetings for a user"""
        user_meetings = []
        for meeting in self.meetings.values():
            if (meeting.organizer_email == user_email or 
                user_email in meeting.participants):
                user_meetings.append(meeting)
        return user_meetings
    
    def start_meeting(self, meeting_id: str) -> VideoMeeting:
        """Start a meeting"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting = self.meetings[meeting_id]
        meeting.status = "active"
        
        logger.info(f"Started video meeting: {meeting_id}")
        return meeting
    
    def end_meeting(self, meeting_id: str, recording_url: Optional[str] = None) -> VideoMeeting:
        """End a meeting"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting = self.meetings[meeting_id]
        meeting.status = "completed"
        if recording_url:
            meeting.recording_url = recording_url
        
        logger.info(f"Ended video meeting: {meeting_id}")
        return meeting
    
    def add_transcription(self, meeting_id: str, transcription: str) -> VideoMeeting:
        """Add meeting transcription"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting = self.meetings[meeting_id]
        meeting.transcription = transcription
        
        logger.info(f"Added transcription to meeting: {meeting_id}")
        return meeting
    
    def _generate_meeting_url(self, title: str, meeting_id: str, provider: str) -> tuple:
        """Generate meeting URL and password based on provider"""
        if provider == "jitsi":
            # Jitsi Meet integration (self-hosted or public)
            base_url = "https://meet.jit.si"  # Can be changed to self-hosted instance
            room_name = f"dhii-{meeting_id[:8]}"  # Use first 8 chars of UUID
            meeting_url = f"{base_url}/{room_name}"
            password = self._generate_password()
            return meeting_url, password
        
        elif provider == "zoom":
            # Placeholder for Zoom integration (would need API keys)
            # In a real implementation, you'd call Zoom API here
            meeting_url = f"https://zoom.us/j/{meeting_id[:10]}"
            password = self._generate_password()
            return meeting_url, password
        
        elif provider == "google_meet":
            # Placeholder for Google Meet integration
            meeting_url = f"https://meet.google.com/dhii-{meeting_id[:8]}"
            password = None  # Google Meet typically doesn't use passwords
            return meeting_url, password
        
        else:
            # Default to Jitsi
            return self._generate_meeting_url(title, meeting_id, "jitsi")
    
    def _generate_password(self) -> str:
        """Generate a secure meeting password"""
        import secrets
        import string
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Get meeting analytics and statistics"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting = self.meetings[meeting_id]
        
        analytics = {
            "meeting_id": meeting_id,
            "title": meeting.title,
            "organizer": meeting.organizer_email,
            "participant_count": len(meeting.participants),
            "status": meeting.status,
            "created_at": meeting.created_at.isoformat(),
            "has_recording": bool(meeting.recording_url),
            "has_transcription": bool(meeting.transcription),
            "duration_minutes": None
        }
        
        # Calculate duration if meeting has ended
        if meeting.end_time and meeting.start_time:
            duration = meeting.end_time - meeting.start_time
            analytics["duration_minutes"] = duration.total_seconds() / 60
        
        return analytics
    
    def export_meeting_data(self, meeting_id: str) -> Dict[str, Any]:
        """Export meeting data for backup or migration"""
        if meeting_id not in self.meetings:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting = self.meetings[meeting_id]
        return asdict(meeting)

# Global video manager instance
video_manager = VideoManager()