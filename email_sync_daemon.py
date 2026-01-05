"""
Email Sync Engine Daemon
Background synchronization service for email accounts

This daemon handles:
1. Periodic email fetching from IMAP servers
2. Background email sending retries
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

from email_manager import EmailManager, EmailAccount, EmailMessage, ConnectionInfo

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Email sync status"""
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


@dataclass
class AccountSyncState:
    """Per-account sync state"""
    account_id: int
    email_address: str
    status: SyncStatus = SyncStatus.IDLE
    last_sync: Optional[datetime] = None
    last_success: Optional[datetime] = None
    error_count: int = 0
    retry_count: int = 0
    next_retry: Optional[datetime] = None
    current_backoff: int = 0
    sync_duration: float = 0.0
    emails_synced: int = 0
    folders_synced: List[str] = None
    
    def __post_init__(self):
        self.folders_synced = []


class EmailSyncDaemon:
    """Background email synchronization daemon"""
    
    def __init__(self, db_path: str = "email_accounts.db", config: Optional[SyncConfig] = None):
        self.db_path = db_path
        self.config = config or SyncConfig()
        self.email_manager = EmailManager(db_path)
        self.sync_states: Dict[int, AccountSyncState] = {}
        self.running = False
        self.sync_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'total_emails_synced': 0,
            'active_accounts': 0,
            'last_sync_time': None,
            'uptime': 0.0
        }
        
        self.start_time = time.time()
    
    async def start(self):
        """Start the sync daemon"""
        if self.running:
            logger.warning("Sync daemon already running")
            return
        
        logger.info("Starting Email Sync Daemon")
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
        
        logger.info(f"Email Sync Daemon started with {len(self.sync_states)} accounts")
    
    async def stop(self):
        """Stop the sync daemon gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping Email Sync Daemon")
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
        
        # Close email manager connections
        await self.email_manager.imap_pool.close_all_connections()
        
        self.stats['uptime'] = time.time() - self.start_time
        logger.info(f"Email Sync Daemon stopped. Uptime: {self.stats['uptime']:.2f}s")
    
    async def _load_account_states(self):
        """Load active email accounts from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email_address, last_sync 
                FROM email_accounts 
                WHERE is_active = 1
            """)
            
            for row in cursor.fetchall():
                account_id, email_address, last_sync = row
                sync_state = AccountSyncState(
                    account_id=account_id,
                    email_address=email_address,
                    last_sync=datetime.fromisoformat(last_sync) if last_sync else None
                )
                self.sync_states[account_id] = sync_state
            
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
                    logger.info(f"Sync Daemon Stats: {json.dumps(self.stats, indent=2, default=str)}")
                
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
        """Synchronize a single email account"""
        sync_state.status = SyncStatus.SYNCING
        sync_start_time = time.time()
        
        try:
            logger.info(f"Starting sync for account: {sync_state.email_address}")
            
            # Fetch account details
            account = await self._get_account_details(account_id)
            if not account:
                logger.error(f"Account not found: {account_id}")
                sync_state.status = SyncStatus.ERROR
                return
            
            # Sync inbox folder
            emails_synced = await self._sync_folder(account, "INBOX")
            
            # Update sync state
            sync_state.last_sync = datetime.now(timezone.utc)
            sync_state.last_success = datetime.now(timezone.utc)
            sync_state.status = SyncStatus.IDLE
            sync_state.error_count = 0
            sync_state.retry_count = 0
            sync_state.current_backoff = 0
            sync_state.emails_synced += emails_synced
            sync_state.sync_duration = time.time() - sync_start_time
            sync_state.folders_synced.append("INBOX")
            
            # Update statistics
            self.stats['total_syncs'] += 1
            self.stats['successful_syncs'] += 1
            self.stats['total_emails_synced'] += emails_synced
            self.stats['last_sync_time'] = datetime.now(timezone.utc)
            
            logger.info(f"Sync completed for {sync_state.email_address}: {emails_synced} emails in {sync_state.sync_duration:.2f}s")
            
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
            
            logger.error(f"Sync failed for {sync_state.email_address}: {e}")
            logger.info(f"Next retry in {sync_state.current_backoff}s")
    
    async def _get_account_details(self, account_id: int) -> Optional[EmailAccount]:
        """Get email account details from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, email_address, display_name, smtp_server, smtp_port,
                       smtp_username, smtp_password, smtp_use_tls, imap_server, imap_port,
                       imap_username, imap_password, imap_use_ssl, is_active, last_sync
                FROM email_accounts 
                WHERE id = ? AND is_active = 1
            """, (account_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return EmailAccount(
                    id=row[0],
                    user_id=row[1],
                    email_address=row[2],
                    display_name=row[3],
                    smtp_server=row[4],
                    smtp_port=row[5],
                    smtp_username=row[6],
                    smtp_password=row[7],  # Note: This is encrypted, need decryption
                    smtp_use_tls=bool(row[8]),
                    imap_server=row[9],
                    imap_port=row[10],
                    imap_username=row[11],
                    imap_password=row[12],  # Note: This is encrypted, need decryption
                    imap_use_ssl=bool(row[13]),
                    is_active=bool(row[14]),
                    last_sync=datetime.fromisoformat(row[15]) if row[15] else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get account details: {e}")
            return None
    
    async def _sync_folder(self, account: EmailAccount, folder: str) -> int:
        """Synchronize a specific folder"""
        emails_synced = 0
        
        try:
            # Create ConnectionInfo from EmailAccount
            connection_info = ConnectionInfo(
                server=account.imap_server,
                port=account.imap_port,
                username=account.imap_username,
                password=account.imap_password,  # Note: This needs decryption
                use_ssl=account.imap_use_ssl
            )
            
            # Get IMAP connection
            imap_conn = await self.email_manager.imap_pool.get_connection(connection_info)
            if not imap_conn:
                raise Exception("Failed to get IMAP connection")
            
            # Select folder
            status, _ = imap_conn.select(folder)
            if status != 'OK':
                raise Exception(f"Failed to select folder: {folder}")
            
            # Search for recent messages (last 24 hours)
            since_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%d-%b-%Y')
            status, message_nums = imap_conn.search(None, f'(SINCE {since_date})')
            if status != 'OK':
                raise Exception("Failed to search for messages")
            
            # Fetch messages
            if message_nums[0]:
                message_ids = message_nums[0].split()
                
                for msg_id in message_ids:
                    try:
                        # Fetch message
                        status, msg_data = imap_conn.fetch(msg_id, '(RFC822)')
                        if status != 'OK':
                            continue
                        
                        # Parse and store message
                        email_message = self._parse_email_message(msg_data[0][1], account, folder)
                        await self._store_email_message(email_message)
                        
                        emails_synced += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to process message {msg_id}: {e}")
                        continue
            
            # Release connection
            await self.email_manager.imap_pool.release_connection(connection_info, imap_conn)
            
            return emails_synced
            
        except Exception as e:
            logger.error(f"Failed to sync folder {folder}: {e}")
            # Ensure connection is closed on error
            await self.email_manager.imap_pool.close_connection(connection_info)
            raise
    
    def _parse_email_message(self, raw_message: bytes, account: EmailAccount, folder: str) -> EmailMessage:
        """Parse raw email message into EmailMessage object"""
        # TODO: Implement proper email parsing
        # This is a simplified implementation
        
        return EmailMessage(
            subject="Parsed Subject",
            sender="sender@example.com",
            recipient=account.email_address,
            body="Parsed body content",
            date=datetime.now(timezone.utc),
            folder=folder
        )
    
    async def _store_email_message(self, email_message: EmailMessage):
        """Store email message in database"""
        # TODO: Implement database storage
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current daemon statistics"""
        return self.stats
    
    def get_account_status(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Get status for specific account"""
        sync_state = self.sync_states.get(account_id)
        if not sync_state:
            return None
        
        return {
            'account_id': sync_state.account_id,
            'email_address': sync_state.email_address,
            'status': sync_state.status.value,
            'last_sync': sync_state.last_sync,
            'last_success': sync_state.last_success,
            'error_count': sync_state.error_count,
            'retry_count': sync_state.retry_count,
            'next_retry': sync_state.next_retry,
            'emails_synced': sync_state.emails_synced,
            'sync_duration': sync_state.sync_duration
        }


# Singleton instance for easy access
_email_sync_daemon: Optional[EmailSyncDaemon] = None


def get_sync_daemon(db_path: str = "email_accounts.db") -> EmailSyncDaemon:
    """Get or create the email sync daemon singleton"""
    global _email_sync_daemon
    if _email_sync_daemon is None:
        _email_sync_daemon = EmailSyncDaemon(db_path)
    return _email_sync_daemon


async def start_sync_daemon():
    """Start the email sync daemon"""
    daemon = get_sync_daemon()
    await daemon.start()


async def stop_sync_daemon():
    """Stop the email sync daemon"""
    daemon = get_sync_daemon()
    await daemon.stop()


# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Email Sync Daemon")
    parser.add_argument("--db-path", default="email_accounts.db", help="Database path")
    parser.add_argument("--sync-interval", type=int, default=300, help="Sync interval in seconds")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run daemon
    daemon = EmailSyncDaemon(
        db_path=args.db_path,
        config=SyncConfig(sync_interval=args.sync_interval)
    )
    
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        asyncio.run(daemon.stop())