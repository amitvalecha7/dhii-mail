import asyncio
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class CalendarSyncService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._running = False
        self._tasks = []
        self.session = None

    async def start(self):
        """Start the background calendar sync loop"""
        self._running = True
        self.session = aiohttp.ClientSession()
        logger.info("Calendar Sync Service Started")
        self._tasks.append(asyncio.create_task(self._sync_loop()))

    async def stop(self):
        """Stop the background sync loop"""
        self._running = False
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        if self.session:
            await self.session.close()
        logger.info("Calendar Sync Service Stopped")

    async def trigger_sync(self):
        """Manually trigger a calendar sync operation"""
        if not self._running:
            logger.warning("Calendar sync service not running, cannot trigger sync")
            return False
        
        try:
            logger.info("Manual calendar sync triggered")
            await self._sync_all_calendars()
            return True
        except Exception as e:
            logger.error(f"Manual sync failed: {e}")
            return False

    async def _sync_loop(self):
        """Main loop that polls calendar accounts periodically"""
        while self._running:
            try:
                logger.debug("Starting calendar polling cycle...")
                await self._sync_all_calendars()
                # Sync every 5 minutes for calendars (more frequent than email)
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Global calendar sync error: {e}")
                await asyncio.sleep(60)

    async def _sync_all_calendars(self):
        """Fetch calendar accounts from DB and sync them"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, provider, credentials_encrypted, calendar_url, 
                       last_synced, sync_interval, is_active 
                FROM calendar_accounts 
                WHERE is_active = 1
            """)
            accounts = cursor.fetchall()
            conn.close()

            for acc in accounts:
                if not self._running:
                    break
                
                # Unpack account data
                acc_id, provider, credentials, calendar_url, last_synced, sync_interval, is_active = acc
                
                # Sync single calendar account
                await self._sync_calendar_account(acc_id, provider, credentials, calendar_url, last_synced)
                
        except Exception as e:
            logger.error(f"Failed to fetch calendar accounts: {e}")

    async def _sync_calendar_account(self, acc_id: str, provider: str, 
                                   credentials: str, calendar_url: str, last_synced: str):
        """Sync a specific calendar account"""
        try:
            # Decrypt credentials (placeholder - use security_manager in production)
            # credentials_decrypted = security_manager.decrypt_sensitive_data(credentials)
            
            if provider.lower() == "caldav":
                await self._sync_caldav_account(acc_id, calendar_url, credentials, last_synced)
            elif provider.lower() == "google":
                await self._sync_google_account(acc_id, credentials, last_synced)
            else:
                logger.warning(f"Unknown calendar provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error syncing calendar account {acc_id}: {e}")

    async def _sync_caldav_account(self, acc_id: str, calendar_url: str, 
                                 credentials: str, last_synced: str):
        """Sync with CalDAV server"""
        try:
            # Parse credentials
            creds = json.loads(credentials)
            username = creds.get('username')
            password = creds.get('password')
            
            # Calculate sync window (last 7 days to next 30 days)
            sync_start = datetime.now() - timedelta(days=7)
            sync_end = datetime.now() + timedelta(days=30)
            
            # Fetch events from CalDAV server
            events = await self._fetch_caldav_events(calendar_url, username, password, sync_start, sync_end)
            
            # Process and save events
            await self._process_calendar_events(acc_id, events, 'caldav')
            
            # Update last sync time
            await self._update_last_synced(acc_id)
            
        except Exception as e:
            logger.error(f"CalDAV sync error for account {acc_id}: {e}")

    async def _sync_google_account(self, acc_id: str, credentials: str, last_synced: str):
        """Sync with Google Calendar"""
        try:
            # Parse OAuth2 credentials
            creds = json.loads(credentials)
            access_token = creds.get('access_token')
            
            if not access_token:
                logger.warning(f"No access token for Google account {acc_id}")
                return
            
            # Calculate sync window
            sync_start = datetime.now() - timedelta(days=7)
            sync_end = datetime.now() + timedelta(days=30)
            
            # Fetch events from Google Calendar API
            events = await self._fetch_google_events(access_token, sync_start, sync_end)
            
            # Process and save events
            await self._process_calendar_events(acc_id, events, 'google')
            
            # Update last sync time
            await self._update_last_synced(acc_id)
            
        except Exception as e:
            logger.error(f"Google Calendar sync error for account {acc_id}: {e}")

    async def _fetch_caldav_events(self, calendar_url: str, username: str, 
                                 password: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Fetch events from CalDAV server using WebDAV requests"""
        try:
            # Basic WebDAV calendar query implementation
            headers = {
                'Content-Type': 'application/xml',
                'Authorization': self._basic_auth_header(username, password)
            }
            
            # Build CALDAV calendar query
            calendar_query = f"""<?xml version="1.0" encoding="utf-8" ?>
<C:calendar-query xmlns:C="urn:ietf:params:xml:ns:caldav">
    <D:prop xmlns:D="DAV:">
        <D:getetag/>
        <C:calendar-data/>
    </D:prop>
    <C:filter>
        <C:comp-filter name="VCALENDAR">
            <C:comp-filter name="VEVENT">
                <C:time-range start="{start_time.strftime('%Y%m%dT%H%M%SZ')}"
                             end="{end_time.strftime('%Y%m%dT%H%M%SZ')}"/>
            </C:comp-filter>
        </C:comp-filter>
    </C:filter>
</C:calendar-query>"""
            
            async with self.session.request(
                'REPORT', calendar_url, 
                headers=headers, 
                data=calendar_query,
                ssl=False
            ) as response:
                if response.status == 207:  # Multi-Status
                    response_text = await response.text()
                    return self._parse_caldav_response(response_text)
                else:
                    logger.error(f"CalDAV request failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"CalDAV fetch error: {e}")
            return []
    
    def _basic_auth_header(self, username: str, password: str) -> str:
        """Generate Basic Auth header"""
        import base64
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _parse_caldav_response(self, response_text: str) -> List[Dict]:
        """Parse CalDAV multi-status response"""
        events = []
        
        # Simple parsing - in production use proper XML parsing
        # This is a simplified implementation for V1
        lines = response_text.split('\n')
        current_event = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('BEGIN:VEVENT'):
                current_event = {}
            elif line.startswith('END:VEVENT'):
                if current_event:
                    events.append(current_event)
                current_event = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.split(';')[0]  # Remove parameters
                current_event[key.lower()] = value.strip()
        
        return events

    async def _fetch_google_events(self, access_token: str, 
                                 start_time: datetime, end_time: datetime) -> List[Dict]:
        """Fetch events from Google Calendar API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Format dates for Google API
            time_min = start_time.isoformat() + 'Z'
            time_max = end_time.isoformat() + 'Z'
            
            url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
            params = {
                'timeMin': time_min,
                'timeMax': time_max,
                'singleEvents': 'true',
                'orderBy': 'startTime'
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                else:
                    logger.error(f"Google API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Google Calendar fetch error: {e}")
            return []

    async def _process_calendar_events(self, acc_id: str, events: List[Dict], source: str):
        """Process and save calendar events to database"""
        if not events:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            processed_count = 0
            
            for event in events:
                # Extract event data based on source
                if source == 'google':
                    event_data = self._parse_google_event(event)
                elif source == 'caldav':
                    event_data = self._parse_caldav_event(event)
                else:
                    continue
                
                if not event_data or not event_data.get('id'):
                    continue
                
                event_id = event_data['id']
                
                # Check if event already exists
                cursor.execute(
                    "SELECT updated_at FROM calendar_events WHERE id = ? AND account_id = ? AND source = ?", 
                    (event_id, acc_id, source)
                )
                existing = cursor.fetchone()
                
                # For V1, we'll always update events for simplicity
                # In production, compare timestamps to avoid unnecessary updates
                
                # Save to database
                cursor.execute('''
                    INSERT OR REPLACE INTO calendar_events 
                    (id, account_id, title, description, start_time, end_time, 
                     location, attendees, organizer, status, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_id, acc_id, 
                    event_data.get('title', 'No Title'),
                    event_data.get('description', ''),
                    event_data.get('start_time'),
                    event_data.get('end_time'),
                    event_data.get('location', ''), 
                    json.dumps(event_data.get('attendees', [])),
                    event_data.get('organizer', ''),
                    event_data.get('status', 'confirmed'),
                    source,
                    datetime.now(),
                    datetime.now()
                ))
                
                processed_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Processed {processed_count} events from {source}")
            
        except Exception as e:
            logger.error(f"Error processing calendar events: {e}")
    
    def _parse_google_event(self, event: Dict) -> Optional[Dict]:
        """Parse Google Calendar event format"""
        try:
            event_id = event.get('id')
            if not event_id:
                return None
            
            # Parse start/end times
            start_data = event.get('start', {})
            end_data = event.get('end', {})
            
            start_time = self._parse_google_datetime(start_data)
            end_time = self._parse_google_datetime(end_data)
            
            if not start_time or not end_time:
                return None
            
            return {
                'id': event_id,
                'title': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start_time': start_time,
                'end_time': end_time,
                'location': event.get('location', ''),
                'attendees': [attendee.get('email') for attendee in event.get('attendees', []) 
                             if attendee.get('email')],
                'organizer': event.get('organizer', {}).get('email', ''),
                'status': event.get('status', 'confirmed')
            }
            
        except Exception as e:
            logger.error(f"Error parsing Google event: {e}")
            return None
    
    def _parse_caldav_event(self, event: Dict) -> Optional[Dict]:
        """Parse CalDAV event format (iCalendar)"""
        try:
            # Extract UID from CalDAV event
            event_id = event.get('uid')
            if not event_id:
                return None
            
            # Parse iCalendar format fields
            # This is simplified - in production use proper iCalendar parsing
            
            return {
                'id': event_id,
                'title': event.get('summary', event.get('uid', 'No Title')),
                'description': event.get('description', ''),
                'start_time': self._parse_ical_datetime(event.get('dtstart')),
                'end_time': self._parse_ical_datetime(event.get('dtend')),
                'location': event.get('location', ''),
                'attendees': [],  # Simplified for V1
                'organizer': event.get('organizer', ''),
                'status': 'confirmed'  # Default for V1
            }
            
        except Exception as e:
            logger.error(f"Error parsing CalDAV event: {e}")
            return None
    
    def _parse_ical_datetime(self, ical_string: Optional[str]) -> Optional[datetime]:
        """Parse iCalendar datetime format"""
        if not ical_string:
            return None
            
        try:
            # Simple iCalendar datetime parsing for V1
            # In production, use proper iCalendar library
            if 'T' in ical_string:
                # DateTime format: 20231231T235959Z
                dt_str = ical_string.replace('Z', '+00:00')
                return datetime.fromisoformat(dt_str)
            else:
                # Date format: 20231231
                return datetime.strptime(ical_string, '%Y%m%d')
        except:
            return None

    def _parse_google_datetime(self, time_data: Dict) -> Optional[datetime]:
        """Parse Google Calendar datetime format"""
        if 'dateTime' in time_data:
            return datetime.fromisoformat(time_data['dateTime'].replace('Z', '+00:00'))
        elif 'date' in time_data:
            return datetime.fromisoformat(time_data['date'])
        return None

    async def _update_last_synced(self, acc_id: str):
        """Update last sync timestamp for account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE calendar_accounts SET last_synced = ? WHERE id = ?",
                (datetime.now().isoformat(), acc_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating last sync time: {e}")