# Database models for meeting assistant
# Extends existing models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

# Import existing base from main.py
from main import Base

# Association table for meeting participants
meeting_participants = Table(
    'meeting_participants',
    Base.metadata,
    Column('meeting_id', String, ForeignKey('meetings.id'), primary_key=True),
    Column('user_email', String, ForeignKey('users.email'), primary_key=True),
    Column('role', String(50), default='attendee'),  # organizer, attendee, optional
    Column('status', String(50), default='pending'),  # pending, accepted, declined, tentative
    Column('response_time', DateTime, nullable=True)
)

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), default='UTC')
    
    # Meeting type and platform
    meeting_type = Column(String(50), default='google_meet')  # google_meet, zoom, teams, custom
    meeting_link = Column(String(500), nullable=True)
    meeting_id_external = Column(String(100), nullable=True)  # External platform meeting ID
    
    # Organizer information
    organizer_email = Column(String, ForeignKey('users.email'), nullable=False)
    organizer = relationship("User", foreign_keys=[organizer_email], back_populates="organized_meetings")
    
    # Meeting status
    status = Column(String(50), default='confirmed')  # confirmed, cancelled, tentative, draft
    visibility = Column(String(50), default='private')  # private, public, organization
    
    # Recurrence information
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(200), nullable=True)  # RRULE format
    parent_meeting_id = Column(String, ForeignKey('meetings.id'), nullable=True)
    
    # Reminder settings
    reminder_enabled = Column(Boolean, default=True)
    reminder_time_before = Column(Integer, default=15)  # minutes before meeting
    
    # Creation and update timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    participants = relationship(
        "User", 
        secondary=meeting_participants,
        back_populates="meetings",
        overlaps="organized_meetings"
    )
    
    # Self-referential relationship for recurring meetings
    parent_meeting = relationship("Meeting", remote_side=[id])
    recurring_meetings = relationship("Meeting", remote_side=[parent_meeting_id])

class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    capacity = Column(Integer, default=10)
    location = Column(String(200), nullable=True)
    
    # Room features
    has_video_conference = Column(Boolean, default=True)
    has_whiteboard = Column(Boolean, default=True)
    has_projector = Column(Boolean, default=True)
    
    # Availability settings
    is_active = Column(Boolean, default=True)
    booking_enabled = Column(Boolean, default=True)
    
    # Time slots configuration
    working_hours_start = Column(String(5), default='09:00')  # HH:MM format
    working_hours_end = Column(String(5), default='18:00')
    timezone = Column(String(50), default='UTC')
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(String, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD format
    start_time = Column(String(5), nullable=False)  # HH:MM format
    end_time = Column(String(5), nullable=False)  # HH:MM format
    
    # Availability status
    is_available = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    # Meeting reference (if booked)
    meeting_id = Column(String, ForeignKey('meetings.id'), nullable=True)
    meeting = relationship("Meeting", backref="time_slot")
    
    # Room reference (if specific room)
    room_id = Column(String, ForeignKey('meeting_rooms.id'), nullable=True)
    room = relationship("MeetingRoom", backref="time_slots")
    
    # User who blocked this slot
    blocked_by_email = Column(String, ForeignKey('users.email'), nullable=True)
    blocked_by = relationship("User", foreign_keys=[blocked_by_email])
    blocked_reason = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MeetingPreferences(Base):
    __tablename__ = "meeting_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False, unique=True)
    user = relationship("User", back_populates="meeting_preferences")
    
    # Default meeting settings
    default_duration = Column(Integer, default=30)  # minutes
    default_meeting_type = Column(String(50), default='google_meet')
    default_reminder_time = Column(Integer, default=15)  # minutes
    
    # Working hours
    working_hours_start = Column(String(5), default='09:00')
    working_hours_end = Column(String(5), default='18:00')
    working_days = Column(String(20), default='1,2,3,4,5')  # 0=Sunday, 1=Monday, etc.
    timezone = Column(String(50), default='UTC')
    
    # Buffer times
    meeting_buffer_before = Column(Integer, default=5)  # minutes
    meeting_buffer_after = Column(Integer, default=5)  # minutes
    
    # Auto-accept settings
    auto_accept_internal = Column(Boolean, default=True)
    auto_accept_external = Column(Boolean, default=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    calendar_notifications = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# User relationships are handled through email references in sqlite3

# Database helper functions for meetings
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

def create_meeting(db: Session, meeting_data: Dict[str, Any]) -> Meeting:
    """Create a new meeting"""
    meeting = Meeting(**meeting_data)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

def get_meeting_by_id(db: Session, meeting_id: str) -> Optional[Meeting]:
    """Get meeting by ID"""
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()

def get_upcoming_meetings(db: Session, user_email: str, limit: int = 10) -> List[Meeting]:
    """Get upcoming meetings for a user"""
    now = datetime.now()
    return db.query(Meeting).join(meeting_participants).filter(
        meeting_participants.c.user_email == user_email,
        Meeting.start_time > now,
        Meeting.status == 'confirmed'
    ).order_by(Meeting.start_time).limit(limit).all()

def get_meetings_by_date_range(db: Session, user_email: str, start_date: datetime, end_date: datetime) -> List[Meeting]:
    """Get meetings for a user within a date range"""
    return db.query(Meeting).join(meeting_participants).filter(
        meeting_participants.c.user_email == user_email,
        Meeting.start_time >= start_date,
        Meeting.start_time <= end_date,
        Meeting.status == 'confirmed'
    ).order_by(Meeting.start_time).all()

def get_available_time_slots(db: Session, date: str, duration_minutes: int = 30, user_email: str = None) -> List[TimeSlot]:
    """Get available time slots for a specific date"""
    return db.query(TimeSlot).filter(
        TimeSlot.date == date,
        TimeSlot.is_available == True,
        TimeSlot.is_blocked == False,
        TimeSlot.meeting_id == None
    ).all()

def book_time_slot(db: Session, slot_id: str, meeting_id: str) -> TimeSlot:
    """Book a time slot"""
    slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if slot and slot.is_available and not slot.is_blocked:
        slot.is_available = False
        slot.meeting_id = meeting_id
        db.commit()
        db.refresh(slot)
    return slot

def cancel_meeting(db: Session, meeting_id: str) -> bool:
    """Cancel a meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting:
        meeting.status = 'cancelled'
        meeting.cancelled_at = datetime.now()
        
        # Free up time slots
        db.query(TimeSlot).filter(TimeSlot.meeting_id == meeting_id).update({
            'is_available': True,
            'meeting_id': None
        })
        
        db.commit()
        return True
    return False

def get_user_meeting_preferences(db: Session, user_email: str) -> Optional[MeetingPreferences]:
    """Get user's meeting preferences"""
    return db.query(MeetingPreferences).filter(MeetingPreferences.user_email == user_email).first()

def create_or_update_meeting_preferences(db: Session, user_email: str, preferences: Dict[str, Any]) -> MeetingPreferences:
    """Create or update user's meeting preferences"""
    existing = get_user_meeting_preferences(db, user_email)
    
    if existing:
        for key, value in preferences.items():
            setattr(existing, key, value)
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        preferences['user_email'] = user_email
        new_preferences = MeetingPreferences(**preferences)
        db.add(new_preferences)
        db.commit()
        db.refresh(new_preferences)
        return new_preferences