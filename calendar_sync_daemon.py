"""
Calendar Sync Engine Daemon
Background synchronization service for calendar accounts

This daemon handles:
1. Periodic calendar event fetching from CalDAV/Google Calendar servers
2. Background event synchronization
3. Connection health monitoring
4. Smart sync scheduling based on user activity
"""

import asyncio
import logging
import signal
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3
import json
import httpx
from icalendar import Calendar, Event
import caldav

from calendar_manager import CalendarManager, CalendarEvent

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Calendar sync status"""
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    PAUSED = "paused"
    BACKOFF = "backoff"  # Exponential backoff due to errors


@dataclass
class SyncConfig:
    """Synchronization configuration"""
    sync_interval: int = 300  # 5 minutes between syncs
    max_sync_duration: int = 60  # 1 minute max sync time
    retry_interval: int = 60  # 1 minute between retries
    max_retries: int = 3
    exponential_backoff: bool = True
    backoff_factor: float = 2.0
    max_backoff: int = 3600  # 1 hour max backoff
    sync_on_startup: bool = True
    sync_on_user_activity: bool = True
    sync_window_days: int = 30  # Sync events 30 days in past/future


@dataclass
class CalendarAccount:
    """Calendar account details"""
    id: int
    user_id: int
    account_type: str  # 'caldav', 'google', 'outlook'
    server_url: str
    username: str
    password: str
    calendar_name: str = "personal"
    is_active: bool = True
    last_sync: Optional[datetime] = None


@dataclass
class AccountSyncState:
    """Per-account sync state"""
    account_id: int
    calendar_name: str
    status: SyncStatus = SyncStatus.IDLE
    last_sync: Optional[datetime] = None
    last_success: Optional[datetime] = None
    error_count: int = 0
    retry_count: int = 0
    next_retry: Optional[datetime] = None
    current_backoff: int = 0
    sync_duration: float = 0.0
    events_synced: int = 0
    sync_token: Optional[str] = None  # For incremental sync


class CalendarSyncDaemon:
    """Background calendar synchronization daemon"""
    
    def __init__(self, db_path: str = "dhii_mail.db", config: Optional[SyncConfig] = None):
        self.db_path = db_path
        self.config = config or SyncConfig()
        self.calendar_manager = CalendarManager(db_path)
        self.sync_states: Dict[int, AccountSyncState] = {}
        self.running = False
        self.sync_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'total_events_synced': 0,
            'active_accounts': 0,
            'last_sync_time': None,
            'uptime': 0.0
        }
        
        self.start_time = time.time()
    
    async def start(self):
        """Start the sync daemon"""
        if self.running:
            logger.warning("Calendar sync daemon already running")
            return
        
        logger.info("Starting Calendar Sync Daemon")
        self.running = True
        
        # Load initial account states
        await self._load_account_states()
        
        # Start background tasks
        self.sync_task = asyncio.create_task(self._sync_loop())
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Register signal handlers for graceful shutdown
        for sig in [signal.SIGINT, signal.SIGTERM]:
            asyncio.get_event_loop().add_signal_handler(
                sig, lambda: asyncio.create_task(self.stop())
            )
        
        logger.info(f"Calendar Sync Daemon started with {len(self.sync_states)} accounts")
    
    async def stop(self):
        """Stop the sync daemon gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping Calendar Sync Daemon")
        self.running = False
        
        # Cancel background tasks
        if self.sync_task:
            self.sync_task.cancel()
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # Wait for tasks to complete
        try:
            if self.sync_task:
                await self.sync_task
            if self.health_check_task:
                await self.health_check_task
        except asyncio.CancelledError:
            pass
        
        self.stats['uptime'] = time.time() - self.start_time
        logger.info(f"Calendar Sync Daemon stopped. Uptime: {self.stats['uptime']:.2f}s")
    
    async def _load_account_states(self):
        """Load active calendar accounts from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create calendar_accounts table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    account_type TEXT NOT NULL,
                    server_url TEXT,
                    username TEXT,
                    password TEXT,
                    calendar_name TEXT DEFAULT 'personal',
                    is_active BOOLEAN DEFAULT TRUE,
                    last_sync TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Load active accounts
            cursor.execute("""
                SELECT id, user_id, account_type, server_url, username, password, 
                       calendar_name, is_active, last_sync 
                FROM calendar_accounts 
                WHERE is_active = 1
            """)
            
            for row in cursor.fetchall():
                account_id, user_id, account_type, server_url, username, password, calendar_name, is_active, last_sync = row
                sync_state = AccountSyncState(
                    account_id=account_id,
                    calendar_name=calendar_name,
                    last_sync=datetime.fromisoformat(last_sync) if last_sync else None
                )
                self.sync_states[account_id] = sync_state
            
            conn.commit()
            conn.close()
            self.stats['active_accounts'] = len(self.sync_states)
            
        except Exception as e:
            logger.error(f"Failed to load account states: {e}")
    
    async def _sync_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                # Sync all active accounts
                for account_id, sync_state in list(self.sync_states.items()):
                    if self._should_sync_account(sync_state):
                        await self._sync_account(account_id, sync_state)
                
                # Wait for next sync interval
                await asyncio.sleep(self.config.sync_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(self.config.retry_interval)
    
    async def _health_check_loop(self):
        """Health check and statistics loop"""
        while self.running:
            try:
                # Update statistics
                self.stats['uptime'] = time.time() - self.start_time
                self.stats['active_accounts'] = len(self.sync_states)
                
                # Log statistics every 5 minutes
                if int(time.time()) % 300 == 0:
                    logger.info(f"Calendar Sync Daemon Stats: {json.dumps(self.stats, indent=2, default=str)}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    def _should_sync_account(self, sync_state: AccountSyncState) -> bool:
        """Determine if an account should be synced"""
        if sync_state.status == SyncStatus.PAUSED:
            return False
        
        if sync_state.status == SyncStatus.BACKOFF:
            if sync_state.next_retry and datetime.now(timezone.utc) < sync_state.next_retry:
                return False
            # Backoff period over, reset to IDLE
            sync_state.status = SyncStatus.IDLE
            sync_state.next_retry = None
        
        # If never synced, sync immediately
        if sync_state.last_sync is None:
            return True
        
        # Check if sync interval has passed
        time_since_last_sync = (datetime.now(timezone.utc) - sync_state.last_sync).total_seconds()
        return time_since_last_sync >= self.config.sync_interval
    
    async def _sync_account(self, account_id: int, sync_state: AccountSyncState):
        """Synchronize a single calendar account"""
        sync_state.status = SyncStatus.SYNCING
        sync_start_time = time.time()
        
        try:
            logger.info(f"Starting calendar sync for account: {account_id}")
            
            # Fetch account details
            account = await self._get_account_details(account_id)
            if not account:
                logger.error(f"Calendar account not found: {account_id}")
                sync_state.status = SyncStatus.ERROR
                return
            
            # Sync calendar events based on account type
            if account.account_type == 'caldav':
                events_synced = await self._sync_caldav_calendar(account, sync_state)
            elif account.account_type == 'google':
                events_synced = await self._sync_google_calendar(account, sync_state)
            else:
                logger.error(f"Unsupported calendar type: {account.account_type}")
                sync_state.status = SyncStatus.ERROR
                return
            
            # Update sync state
            sync_state.last_sync = datetime.now(timezone.utc)
            sync_state.last_success = datetime.now(timezone.utc)
            sync_state.status = SyncStatus.IDLE
            sync_state.error_count = 0
            sync_state.retry_count = 0
            sync_state.current_backoff = 0
            sync_state.events_synced += events_synced
            sync_state.sync_duration = time.time() - sync_start_time
            
            # Update statistics
            self.stats['total_syncs'] += 1
            self.stats['successful_syncs'] += 1
            self.stats['total_events_synced'] += events_synced
            self.stats['last_sync_time'] = datetime.now(timezone.utc)
            
            logger.info(f"Calendar sync completed for account {account_id}: {events_synced} events in {sync_state.sync_duration:.2f}s")
            
        except Exception as e:
            # Handle sync error
            sync_state.status = SyncStatus.ERROR
            sync_state.error_count += 1
            sync_state.retry_count += 1
            
            # Calculate backoff
            if self.config.exponential_backoff:
                sync_state.current_backoff = min(
                    self.config.max_backoff,
                    int(self.config.retry_interval * (self.config.backoff_factor ** sync_state.retry_count))
                )
            else:
                sync_state.current_backoff = self.config.retry_interval
            
            sync_state.next_retry = datetime.now(timezone.utc) + timedelta(seconds=sync_state.current_backoff)
            sync_state.status = SyncStatus.BACKOFF
            
            # Update statistics
            self.stats['total_syncs'] += 1
            self.stats['failed_syncs'] += 1
            
            logger.error(f"Calendar sync failed for account {account_id}: {e}")
            logger.info(f"Next retry in {sync_state.current_backoff}s")
    
    async def _get_account_details(self, account_id: int) -> Optional[CalendarAccount]:
        """Get calendar account details from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, account_type, server_url, username, password, 
                       calendar_name, is_active, last_sync 
                FROM calendar_accounts 
                WHERE id = ? AND is_active = 1
            """, (account_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            account = CalendarAccount(
                id=row[0],
                user_id=row[1],
                account_type=row[2],
                server_url=row[3],
                username=row[4],
                password=row[5],
                calendar_name=row[6],
                is_active=row[7],
                last_sync=datetime.fromisoformat(row[8]) if row[8] else None
            )
            
            conn.close()
            return account
            
        except Exception as e:
            logger.error(f"Failed to get account details for {account_id}: {e}")
            return None
    
    async def _sync_caldav_calendar(self, account: CalendarAccount, sync_state: AccountSyncState) -> int:
        """Sync CalDAV calendar"""
        try:
            # Connect to CalDAV server
            client = caldav.DAVClient(
                url=account.server_url,
                username=account.username,
                password=account.password
            )
            
            # Get principal and calendar
            principal = client.principal()
            calendars = principal.calendars()
            
            if not calendars:
                logger.warning(f"No calendars found for account {account.id}")
                return 0
            
            # Find the specified calendar or use the first one
            calendar = None
            for cal in calendars:
                if cal.name == account.calendar_name:
                    calendar = cal
                    break
            
            if not calendar:
                calendar = calendars[0]  # Use first calendar if specified not found
                logger.info(f"Using calendar '{calendar.name}' instead of '{account.calendar_name}'")
            
            # Calculate sync window
            now = datetime.now(timezone.utc)
            start_date = now - timedelta(days=self.config.sync_window_days)
            end_date = now + timedelta(days=self.config.sync_window_days)
            
            # Fetch events
            events = calendar.date_search(start=start_date, end=end_date)
            
            events_synced = 0
            for event in events:
                try:
                    # Parse event data
                    ical_data = event.data
                    cal = Calendar.from_ical(ical_data)
                    
                    for component in cal.walk():
                        if component.name == "VEVENT":
                            calendar_event = self._parse_ical_event(component, account.user_id)
                            if calendar_event:
                                # Store event in local database
                                self.calendar_manager.create_event(calendar_event, account.user_id)
                                events_synced += 1
                                
                except Exception as e:
                    logger.warning(f"Failed to parse calendar event: {e}")
                    continue
            
            client.close()
            return events_synced
            
        except Exception as e:
            logger.error(f"CalDAV sync failed for account {account.id}: {e}")
            raise
    
    async def _sync_google_calendar(self, account: CalendarAccount, sync_state: AccountSyncState) -> int:
        """Sync Google Calendar (placeholder implementation)"""
        logger.info(f"Google Calendar sync not yet implemented for account {account.id}")
        return 0
    
    def _parse_ical_event(self, component, user_id: int) -> Optional[CalendarEvent]:
        """Parse iCal event component to CalendarEvent"""
        try:
            # Extract basic event data
            title = str(component.get('summary', 'Untitled Event'))
            description = str(component.get('description', ''))
            location = str(component.get('location', ''))
            
            # Parse start and end times
            dtstart = component.get('dtstart')
            dtend = component.get('dtend')
            
            if not dtstart or not dtend:
                return None
            
            start_time = dtstart.dt
            end_time = dtend.dt
            
            # Convert to timezone-aware datetime if needed
            if not start_time.tzinfo:
                start_time = start_time.replace(tzinfo=timezone.utc)
            if not end_time.tzinfo:
                end_time = end_time.replace(tzinfo=timezone.utc)
            
            # Extract attendees
            attendees = []
            for attendee in component.get('attendee', []):
                email = str(attendee).replace('mailto:', '')
                if email and email not in attendees:
                    attendees.append(email)
            
            # Extract organizer
            organizer = str(component.get('organizer', ''))
            if organizer.startswith('mailto:'):
                organizer = organizer.replace('mailto:', '')
            else:
                organizer = f"user_{user_id}@dhii.local"  # Default organizer
            
            # Create CalendarEvent
            event = CalendarEvent(
                title=title,
                description=description if description else None,
                start_time=start_time,
                end_time=end_time,
                location=location if location else None,
                attendees=attendees,
                organizer=organizer,
                status="confirmed"
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to parse iCal event: {e}")
            return None


# Global daemon instance
daemon: Optional[CalendarSyncDaemon] = None


async def start_daemon(db_path: str = "dhii_mail.db"):
    """Start the calendar sync daemon"""
    global daemon
    if daemon is None:
        daemon = CalendarSyncDaemon(db_path)
        await daemon.start()
    return daemon


async def stop_daemon():
    """Stop the calendar sync daemon"""
    global daemon
    if daemon:
        await daemon.stop()
        daemon = None


def get_daemon() -> Optional[CalendarSyncDaemon]:
    """Get the current daemon instance"""
    return daemon