"""
Calendar Sync Service for dhii Mail Plugin
Handles calendar synchronization operations
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json

from calendar_sync_daemon import CalendarSyncDaemon, start_daemon, stop_daemon
from calendar_manager import CalendarManager, CalendarEvent

logger = logging.getLogger(__name__)


class CalendarSyncService:
    """Calendar synchronization service"""
    
    def __init__(self, db_path: str = "dhii_mail.db"):
        self.db_path = db_path
        self.calendar_manager = CalendarManager(db_path)
        self.sync_daemon: Optional[CalendarSyncDaemon] = None
        self.is_running = False
    
    async def start(self):
        """Start the calendar sync service"""
        if self.is_running:
            logger.warning("Calendar sync service already running")
            return
        
        logger.info("Starting Calendar Sync Service")
        self.sync_daemon = await start_daemon(self.db_path)
        self.is_running = True
        logger.info("Calendar Sync Service started successfully")
    
    async def stop(self):
        """Stop the calendar sync service"""
        if not self.is_running:
            return
        
        logger.info("Stopping Calendar Sync Service")
        await stop_daemon()
        self.sync_daemon = None
        self.is_running = False
        logger.info("Calendar Sync Service stopped")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        if not self.sync_daemon:
            return {
                "status": "not_running",
                "active_accounts": 0,
                "total_syncs": 0,
                "successful_syncs": 0,
                "failed_syncs": 0,
                "total_events_synced": 0,
                "uptime": 0
            }
        
        return {
            "status": "running",
            "active_accounts": self.sync_daemon.stats.get('active_accounts', 0),
            "total_syncs": self.sync_daemon.stats.get('total_syncs', 0),
            "successful_syncs": self.sync_daemon.stats.get('successful_syncs', 0),
            "failed_syncs": self.sync_daemon.stats.get('failed_syncs', 0),
            "total_events_synced": self.sync_daemon.stats.get('total_events_synced', 0),
            "uptime": self.sync_daemon.stats.get('uptime', 0),
            "last_sync_time": self.sync_daemon.stats.get('last_sync_time', None)
        }
    
    def get_account_sync_states(self) -> Dict[int, Dict[str, Any]]:
        """Get sync states for all accounts"""
        if not self.sync_daemon:
            return {}
        
        states = {}
        for account_id, sync_state in self.sync_daemon.sync_states.items():
            states[account_id] = {
                "status": sync_state.status.value,
                "last_sync": sync_state.last_sync.isoformat() if sync_state.last_sync else None,
                "last_success": sync_state.last_success.isoformat() if sync_state.last_success else None,
                "error_count": sync_state.error_count,
                "retry_count": sync_state.retry_count,
                "next_retry": sync_state.next_retry.isoformat() if sync_state.next_retry else None,
                "events_synced": sync_state.events_synced,
                "sync_duration": sync_state.sync_duration
            }
        
        return states
    
    async def sync_account_now(self, account_id: int) -> bool:
        """Force sync a specific account immediately"""
        if not self.sync_daemon:
            logger.error("Sync daemon not running")
            return False
        
        if account_id not in self.sync_daemon.sync_states:
            logger.error(f"Account {account_id} not found in sync states")
            return False
        
        sync_state = self.sync_daemon.sync_states[account_id]
        
        # Reset sync state to force immediate sync
        sync_state.status = self.sync_daemon.__class__.__dict__['SyncStatus'].IDLE
        sync_state.last_sync = None
        sync_state.next_retry = None
        
        logger.info(f"Forcing immediate sync for account {account_id}")
        return True
    
    def get_local_events(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events from local database"""
        events = self.calendar_manager.get_events(user_id, start_date, end_date)
        
        # Convert to JSON-serializable format
        return [
            {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "attendees": event.attendees,
                "organizer": event.organizer,
                "status": event.status
            }
            for event in events
        ]
    
    def create_local_event(self, user_id: int, event_data: Dict[str, Any]) -> Optional[str]:
        """Create a local calendar event"""
        try:
            # Parse datetime strings
            start_time = datetime.fromisoformat(event_data['start_time'])
            end_time = datetime.fromisoformat(event_data['end_time'])
            
            # Create CalendarEvent
            event = CalendarEvent(
                title=event_data['title'],
                description=event_data.get('description'),
                start_time=start_time,
                end_time=end_time,
                location=event_data.get('location'),
                attendees=event_data.get('attendees', []),
                organizer=event_data.get('organizer', f'user_{user_id}@dhii.local'),
                status=event_data.get('status', 'confirmed')
            )
            
            # Create event in local database
            event_id = self.calendar_manager.create_event(event, user_id)
            
            if event_id:
                logger.info(f"Local calendar event created: {event_id}")
            else:
                logger.error("Failed to create local calendar event")
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error creating local calendar event: {e}")
            return None
    
    def get_availability(self, user_id: int, date: datetime, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """Get available time slots for a user"""
        time_slots = self.calendar_manager.get_availability(user_id, date, duration_minutes)
        
        # Convert to JSON-serializable format
        return [
            {
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "duration_minutes": slot.duration_minutes
            }
            for slot in time_slots
        ]


# Global service instance
_service_instance: Optional[CalendarSyncService] = None


async def get_calendar_sync_service(db_path: str = "dhii_mail.db") -> CalendarSyncService:
    """Get or create the calendar sync service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CalendarSyncService(db_path)
        await _service_instance.start()
    return _service_instance


async def stop_calendar_sync_service():
    """Stop the calendar sync service"""
    global _service_instance
    if _service_instance:
        await _service_instance.stop()
        _service_instance = None