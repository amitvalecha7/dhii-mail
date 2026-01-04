"""
Email Manager for dhii Mail
Handles SMTP sending, IMAP receiving, and email processing
"""

import os
import imaplib
import smtplib
import email
import logging
import sqlite3
import json
import time
import ssl
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel
from smtplib import SMTPException, SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected
from security_manager import security_manager

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Email connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class ConnectionInfo:
    """Connection information for email accounts"""
    server: str
    port: int
    username: str
    password: str
    use_ssl: bool
    last_successful_connection: Optional[datetime] = None
    connection_attempts: int = 0
    connection_errors: List[str] = None
    state: ConnectionState = ConnectionState.DISCONNECTED
    
    def __post_init__(self):
        if self.connection_errors is None:
            self.connection_errors = []


@dataclass
class FetchResult:
    """Result of email fetch operation"""
    success: bool
    emails_fetched: int = 0
    errors: List[str] = None
    connection_time: float = 0.0
    fetch_time: float = 0.0
    total_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class IMAPConnectionPool:
    """Connection pool for IMAP connections"""
    
    def __init__(self, max_connections: int = 5, connection_timeout: int = 30):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.connections: Dict[str, Tuple[imaplib.IMAP4, datetime]] = {}
        self.connection_locks: Dict[str, asyncio.Lock] = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_connection(self, connection_info: ConnectionInfo) -> Optional[imaplib.IMAP4]:
        """Get or create IMAP connection"""
        connection_key = f"{connection_info.username}@{connection_info.server}"
        
        if connection_key not in self.connection_locks:
            self.connection_locks[connection_key] = asyncio.Lock()
        
        async with self.connection_locks[connection_key]:
            # Check if we have an existing connection
            if connection_key in self.connections:
                imap_conn, last_used = self.connections[connection_key]
                
                # Check if connection is still valid
                try:
                    # Test connection with NOOP
                    status, _ = imap_conn.noop()
                    if status == 'OK':
                        self.connections[connection_key] = (imap_conn, datetime.now(timezone.utc))
                        self.logger.info(f"Reused existing IMAP connection for {connection_key}")
                        return imap_conn
                except Exception as e:
                    self.logger.warning(f"Existing connection failed for {connection_key}: {e}")
                    # Remove invalid connection
                    del self.connections[connection_key]
            
            # Create new connection
            try:
                imap_conn = await self._create_imap_connection(connection_info)
                if imap_conn:
                    self.connections[connection_key] = (imap_conn, datetime.now(timezone.utc))
                    self.logger.info(f"Created new IMAP connection for {connection_key}")
                    return imap_conn
            except Exception as e:
                self.logger.error(f"Failed to create IMAP connection for {connection_key}: {e}")
                return None
    
    async def _create_imap_connection(self, connection_info: ConnectionInfo) -> Optional[imaplib.IMAP4]:
        """Create new IMAP connection"""
        try:
            connection_info.state = ConnectionState.CONNECTING
            
            if connection_info.use_ssl:
                imap_conn = imaplib.IMAP4_SSL(connection_info.server, connection_info.port)
            else:
                imap_conn = imaplib.IMAP4(connection_info.server, connection_info.port)
                imap_conn.starttls()
            
            connection_info.state = ConnectionState.AUTHENTICATING
            imap_conn.login(connection_info.username, connection_info.password)
            
            connection_info.state = ConnectionState.AUTHENTICATED
            connection_info.last_successful_connection = datetime.now(timezone.utc)
            connection_info.connection_attempts = 0
            connection_info.connection_errors.clear()
            
            self.logger.info(f"IMAP connection established for {connection_info.username}")
            return imap_conn
            
        except Exception as e:
            connection_info.state = ConnectionState.ERROR
            connection_info.connection_attempts += 1
            connection_info.connection_errors.append(str(e))
            self.logger.error(f"IMAP connection failed for {connection_info.username}: {e}")
            raise
    
    async def release_connection(self, connection_info: ConnectionInfo, imap_conn: imaplib.IMAP4):
        """Release connection back to pool"""
        connection_key = f"{connection_info.username}@{connection_info.server}"
        
        if connection_key in self.connections:
            self.connections[connection_key] = (imap_conn, datetime.now(timezone.utc))
            self.logger.debug(f"Released IMAP connection for {connection_key}")
    
    async def close_connection(self, connection_info: ConnectionInfo):
        """Close specific connection"""
        connection_key = f"{connection_info.username}@{connection_info.server}"
        
        if connection_key in self.connections:
            try:
                imap_conn, _ = self.connections[connection_key]
                imap_conn.close()
                imap_conn.logout()
                del self.connections[connection_key]
                self.logger.info(f"Closed IMAP connection for {connection_key}")
            except Exception as e:
                self.logger.error(f"Error closing IMAP connection for {connection_key}: {e}")
    
    async def cleanup_expired_connections(self):
        """Clean up expired connections"""
        current_time = datetime.now(timezone.utc)
        expired_keys = []
        
        for connection_key, (imap_conn, last_used) in self.connections.items():
            # Check if connection has been idle for more than 5 minutes
            if (current_time - last_used).total_seconds() > 300:
                try:
                    # Test connection
                    status, _ = imap_conn.noop()
                    if status != 'OK':
                        expired_keys.append(connection_key)
                except Exception:
                    expired_keys.append(connection_key)
        
        # Remove expired connections
        for key in expired_keys:
            try:
                imap_conn, _ = self.connections[key]
                imap_conn.close()
                imap_conn.logout()
                del self.connections[key]
                self.logger.info(f"Cleaned up expired IMAP connection for {key}")
            except Exception as e:
                self.logger.error(f"Error cleaning up expired connection for {key}: {e}")
    
    async def close_all_connections(self):
        """Close all connections in pool"""
        for connection_key, (imap_conn, _) in list(self.connections.items()):
            try:
                imap_conn.close()
                imap_conn.logout()
                del self.connections[connection_key]
                self.logger.info(f"Closed IMAP connection for {connection_key}")
            except Exception as e:
                self.logger.error(f"Error closing IMAP connection for {connection_key}: {e}")

class EmailRetryConfig:
    """Configuration for email retry logic"""
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 30.0,
                 exponential_backoff: float = 2.0,
                 retry_on_auth_error: bool = True,
                 retry_on_connection_error: bool = True,
                 retry_on_server_busy: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.retry_on_auth_error = retry_on_auth_error
        self.retry_on_connection_error = retry_on_connection_error
        self.retry_on_server_busy = retry_on_server_busy

class EmailSendResult:
    """Result of email sending operation"""
    def __init__(self, success: bool, message: str, attempts: int = 1, 
                 last_error: Optional[str] = None, retry_count: int = 0):
        self.success = success
        self.message = message
        self.attempts = attempts
        self.last_error = last_error
        self.retry_count = retry_count
    
    def __str__(self):
        if self.success:
            return f"Email sent successfully after {self.attempts} attempt(s)"
        else:
            return f"Failed to send email after {self.attempts} attempt(s): {self.message}"

class EmailMessage(BaseModel):
    """Email message model"""
    id: Optional[str] = None
    message_id: Optional[str] = None
    subject: str
    sender: str
    recipient: str
    body: str
    html_body: Optional[str] = None
    date: datetime
    is_read: bool = False
    is_sent: bool = False
    folder: str = "INBOX"
    attachments: List[Dict[str, Any]] = []
    headers: Dict[str, str] = {}
    priority: str = "normal"
    labels: List[str] = []

class EmailAccount(BaseModel):
    """Email account configuration"""
    id: Optional[int] = None
    user_id: int
    email_address: str
    display_name: str
    smtp_server: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    imap_server: str
    imap_port: int = 993
    imap_username: str
    imap_password: str
    imap_use_ssl: bool = True
    is_active: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    last_sync: Optional[datetime] = None

class EmailManager:
    """Manages email operations for multiple users"""
    
    def __init__(self, db_path: str = "email_accounts.db", retry_config: Optional[EmailRetryConfig] = None):
        self.db_path = db_path
        self.retry_config = retry_config or EmailRetryConfig()
        self.imap_pool = IMAPConnectionPool(max_connections=5, connection_timeout=30)
        self.connection_cache: Dict[int, ConnectionInfo] = {}
        self.fetch_stats: Dict[str, Any] = {
            'total_fetches': 0,
            'successful_fetches': 0,
            'failed_fetches': 0,
            'emails_fetched': 0,
            'average_fetch_time': 0.0
        }
        self._init_database()
    
    def _init_database(self):
        """Initialize email database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Email accounts table
        # SECURITY: All password fields store encrypted data using security_manager.encrypt_sensitive_data()
        # Passwords are encrypted before storage and decrypted after retrieval
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_address TEXT NOT NULL,
                display_name TEXT,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER DEFAULT 587,
                smtp_username TEXT NOT NULL,
                smtp_password TEXT NOT NULL,  -- ENCRYPTED: Stores encrypted password data
                smtp_use_tls BOOLEAN DEFAULT 1,
                imap_server TEXT NOT NULL,
                imap_port INTEGER DEFAULT 993,
                imap_username TEXT NOT NULL,
                imap_password TEXT NOT NULL,  -- ENCRYPTED: Stores encrypted password data
                imap_use_ssl BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Email messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                message_id TEXT,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                body TEXT NOT NULL,
                html_body TEXT,
                date TIMESTAMP NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                is_sent BOOLEAN DEFAULT 0,
                folder TEXT DEFAULT 'INBOX',
                attachments TEXT,
                headers TEXT,
                priority TEXT DEFAULT 'normal',
                labels TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (account_id) REFERENCES email_accounts(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_accounts_user_id ON email_accounts(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_messages_user_id ON email_messages(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_messages_account_id ON email_messages(account_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_messages_date ON email_messages(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_messages_folder ON email_messages(folder)")
        
        conn.commit()
        conn.close()
        logger.info("Email database initialized")
    
    def add_email_account(self, account: EmailAccount) -> Optional[int]:
        """Add a new email account with encrypted passwords"""
        try:
            # SECURITY: Encrypt passwords before storing to prevent plaintext exposure
            # This ensures database only contains encrypted password data
            encrypted_smtp_password = security_manager.encrypt_sensitive_data(account.smtp_password)
            encrypted_imap_password = security_manager.encrypt_sensitive_data(account.imap_password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO email_accounts (
                    user_id, email_address, display_name, smtp_server, smtp_port,
                    smtp_username, smtp_password, smtp_use_tls, imap_server, imap_port,
                    imap_username, imap_password, imap_use_ssl, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.user_id, account.email_address, account.display_name,
                account.smtp_server, account.smtp_port, account.smtp_username,
                encrypted_smtp_password, account.smtp_use_tls, account.imap_server,
                account.imap_port, account.imap_username, encrypted_imap_password,
                account.imap_use_ssl, account.is_active
            ))
            
            account_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Email account added for {account.email_address}")
            return account_id
            
        except Exception as e:
            logger.error(f"Error adding email account: {e}")
            return None
    
    def get_email_accounts(self, user_id: int) -> List[EmailAccount]:
        """Get all email accounts for a user with decrypted passwords"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, email_address, display_name, smtp_server, smtp_port,
                       smtp_username, smtp_password, smtp_use_tls, imap_server, imap_port,
                       imap_username, imap_password, imap_use_ssl, is_active, created_at, last_sync
                FROM email_accounts
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (user_id,))
            
            accounts = []
            for row in cursor.fetchall():
                try:
                    # Decrypt passwords
                    decrypted_smtp_password = security_manager.decrypt_sensitive_data(row[7])
                    decrypted_imap_password = security_manager.decrypt_sensitive_data(row[12])
                except Exception as decrypt_error:
                    logger.error(f"Error decrypting passwords for account {row[2]}: {decrypt_error}")
                    continue
                
                account = EmailAccount(
                    id=row[0],
                    user_id=row[1],
                    email_address=row[2],
                    display_name=row[3],
                    smtp_server=row[4],
                    smtp_port=row[5],
                    smtp_username=row[6],
                    smtp_password=decrypted_smtp_password,
                    smtp_use_tls=bool(row[8]),
                    imap_server=row[9],
                    imap_port=row[10],
                    imap_username=row[11],
                    imap_password=decrypted_imap_password,
                    imap_use_ssl=bool(row[13]),
                    is_active=bool(row[14]),
                    created_at=datetime.fromisoformat(row[15]) if row[15] else datetime.now(timezone.utc),
                    last_sync=datetime.fromisoformat(row[16]) if row[16] else None
                )
                accounts.append(account)
            
            conn.close()
            return accounts
            
        except Exception as e:
            logger.error(f"Error getting email accounts: {e}")
            return []
    
    def send_email(self, message: EmailMessage, account_id: int, sender: Optional[str] = None, user_id: Optional[int] = None) -> bool:
        """Send an email using SMTP (legacy method) - use send_email_with_retry for better reliability"""
        result = self.send_email_with_retry(message, account_id, sender, user_id=user_id)
        return result.success
    
    def send_email_with_retry(self, message: EmailMessage, account_id: int, 
                              sender: Optional[str] = None,
                              retry_config: Optional[EmailRetryConfig] = None,
                              user_id: Optional[int] = None) -> EmailSendResult:
        """Send an email with retry logic and comprehensive error handling"""
        if retry_config is None:
            retry_config = self.retry_config
        
        last_error = None
        attempts = 0
        
        for attempt in range(retry_config.max_retries + 1):
            attempts += 1
            try:
                # Get account details
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT smtp_server, smtp_port, smtp_username, smtp_password, smtp_use_tls, email_address
                    FROM email_accounts
                    WHERE id = ? AND is_active = 1
                """, (account_id,))
                
                account_data = cursor.fetchone()
                if not account_data:
                    error_msg = "Email account not found or inactive"
                    logger.error(error_msg)
                    return EmailSendResult(False, error_msg, attempts, error_msg, attempt)
                
                smtp_server, smtp_port, smtp_username, smtp_password, smtp_use_tls, account_email = account_data
                conn.close()
                
                # Decrypt the SMTP password for use
                try:
                    smtp_password = security_manager.decrypt_sensitive_data(smtp_password)
                except Exception as decrypt_error:
                    error_msg = f"Failed to decrypt SMTP password: {decrypt_error}"
                    logger.error(error_msg)
                    return EmailSendResult(False, error_msg, attempts, error_msg, attempt)
                
                # Use provided sender email or fall back to account email
                sender_email = sender if sender else account_email
                
                # Create email message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = message.subject
                msg['From'] = f"{message.sender} <{sender_email}>"
                msg['To'] = message.recipient
                
                # Add text body
                if message.body:
                    text_part = MIMEText(message.body, 'plain')
                    msg.attach(text_part)
                
                # Add HTML body if available
                if message.html_body:
                    html_part = MIMEText(message.html_body, 'html')
                    msg.attach(html_part)
                
                # Add attachments if any
                for attachment in message.attachments:
                    if 'filename' in attachment and 'content' in attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment['content'])
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{attachment["filename"]}"')
                        msg.attach(part)
                
                # Connect to SMTP server and send with timeout
                server = None
                try:
                    if smtp_use_tls:
                        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                        server.starttls()
                    else:
                        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
                    
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
                    
                    # Save sent message to database
                    self._save_sent_message(message, account_id, user_id)
                    
                    logger.info(f"Email sent successfully to {message.recipient} on attempt {attempts}")
                    return EmailSendResult(True, f"Email sent successfully to {message.recipient}", 
                                         attempts, retry_count=attempt)
                    
                finally:
                    if server:
                        try:
                            server.quit()
                        except Exception as quit_error:
                            logger.warning(f"Error closing SMTP connection: {quit_error}")
                
            except SMTPAuthenticationError as e:
                last_error = f"SMTP authentication failed: {str(e)}"
                logger.error(last_error)
                
                # Don't retry authentication errors unless configured to do so
                if not retry_config.retry_on_auth_error or attempt == retry_config.max_retries:
                    return EmailSendResult(False, "SMTP authentication failed", attempts, last_error, attempt)
                
            except (SMTPConnectError, SMTPServerDisconnected, ConnectionError) as e:
                last_error = f"SMTP connection error: {str(e)}"
                logger.warning(f"{last_error} on attempt {attempts}")
                
                # Don't retry connection errors unless configured to do so
                if not retry_config.retry_on_connection_error or attempt == retry_config.max_retries:
                    return EmailSendResult(False, "SMTP connection failed", attempts, last_error, attempt)
                
            except SMTPException as e:
                error_code = getattr(e, 'smtp_code', None)
                error_message = str(e)
                
                # Check for server busy (421) or temporary errors
                if error_code == 421 and retry_config.retry_on_server_busy and attempt < retry_config.max_retries:
                    last_error = f"SMTP server busy (421): {error_message}"
                    logger.warning(f"{last_error} on attempt {attempts}")
                else:
                    last_error = f"SMTP error: {error_message}"
                    logger.error(f"{last_error} on attempt {attempts}")
                    return EmailSendResult(False, "SMTP error", attempts, last_error, attempt)
                
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"{last_error} on attempt {attempts}")
                
                # For unexpected errors, don't retry unless it's a network-related issue
                if attempt == retry_config.max_retries:
                    return EmailSendResult(False, "Unexpected error", attempts, last_error, attempt)
            
            # Calculate delay for next attempt (exponential backoff)
            if attempt < retry_config.max_retries:
                delay = min(
                    retry_config.base_delay * (retry_config.exponential_backoff ** attempt),
                    retry_config.max_delay
                )
                logger.info(f"Retrying email send in {delay:.1f} seconds... (attempt {attempts + 1}/{retry_config.max_retries + 1})")
                time.sleep(delay)
        
        # If we get here, all retries failed
        return EmailSendResult(False, "All retry attempts failed", attempts, last_error, retry_config.max_retries)
    
    def send_email_aggressive_retry(self, message: EmailMessage, account_id: int, sender: Optional[str] = None, user_id: Optional[int] = None) -> EmailSendResult:
        """Send email with aggressive retry policy for critical emails"""
        aggressive_config = EmailRetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=60.0,
            exponential_backoff=1.5,
            retry_on_auth_error=False,  # Don't retry auth errors
            retry_on_connection_error=True,
            retry_on_server_busy=True
        )
        return self.send_email_with_retry(message, account_id, sender, aggressive_config, user_id)
    
    def send_email_quick_retry(self, message: EmailMessage, account_id: int, sender: Optional[str] = None, user_id: Optional[int] = None) -> EmailSendResult:
        """Send email with quick retry policy for non-critical emails"""
        quick_config = EmailRetryConfig(
            max_retries=2,
            base_delay=0.5,
            max_delay=5.0,
            exponential_backoff=2.0,
            retry_on_auth_error=False,
            retry_on_connection_error=True,
            retry_on_server_busy=False
        )
        return self.send_email_with_retry(message, account_id, sender, quick_config, user_id)
    
    def get_email_sending_stats(self, account_id: int, days: int = 30) -> Dict[str, Any]:
        """Get email sending statistics for an account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total sent emails
            cursor.execute("""
                SELECT COUNT(*) FROM email_messages 
                WHERE account_id = ? AND is_sent = 1 
                AND date >= datetime('now', '-' || ? || ' days')
            """, (account_id, days))
            total_sent = cursor.fetchone()[0]
            
            # Get emails by folder
            cursor.execute("""
                SELECT folder, COUNT(*) as count 
                FROM email_messages 
                WHERE account_id = ? 
                AND date >= datetime('now', '-' || ? || ' days')
                GROUP BY folder
                ORDER BY count DESC
            """, (account_id, days))
            folder_stats = dict(cursor.fetchall())
            
            # Get recent activity
            cursor.execute("""
                SELECT date, subject, recipient 
                FROM email_messages 
                WHERE account_id = ? AND is_sent = 1 
                AND date >= datetime('now', '-' || ? || ' days')
                ORDER BY date DESC 
                LIMIT 10
            """, (account_id, days))
            recent_activity = []
            for row in cursor.fetchall():
                recent_activity.append({
                    'date': row[0],
                    'subject': row[1],
                    'recipient': row[2]
                })
            
            conn.close()
            
            return {
                'total_sent': total_sent,
                'folder_stats': folder_stats,
                'recent_activity': recent_activity,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting email sending stats: {e}")
            return {'total_sent': 0, 'folder_stats': {}, 'recent_activity': [], 'period_days': days}
    
    def _save_sent_message(self, message: EmailMessage, account_id: int, user_id: Optional[int] = None):
        """Save sent message to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO email_messages (
                    user_id, account_id, message_id, subject, sender, recipient, body,
                    html_body, date, is_sent, folder, attachments, headers, priority, labels
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id or message.sender, account_id, message.message_id, message.subject,
                message.sender, message.recipient, message.body, message.html_body,
                message.date, True, 'Sent', json.dumps(message.attachments),
                json.dumps(message.headers), message.priority, json.dumps(message.labels)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving sent message: {e}")
    
    async def fetch_emails_async(self, account_id: int, folder: str = "INBOX", limit: int = 50, 
                                use_connection_pool: bool = True, enable_retry: bool = True) -> FetchResult:
        """Enhanced fetch emails with retry logic and connection pooling (async version)"""
        start_time = time.time()
        fetch_result = FetchResult(success=False)
        
        try:
            # Update fetch statistics
            self.fetch_stats['total_fetches'] += 1
            
            # Get account details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT imap_server, imap_port, imap_username, imap_password, imap_use_ssl, user_id
                FROM email_accounts
                WHERE id = ? AND is_active = 1
            """, (account_id,))
            
            account_data = cursor.fetchone()
            if not account_data:
                error_msg = "Email account not found or inactive"
                logger.error(error_msg)
                fetch_result.errors.append(error_msg)
                self.fetch_stats['failed_fetches'] += 1
                return fetch_result
            
            imap_server, imap_port, imap_username, imap_password, imap_use_ssl, user_id = account_data
            conn.close()
            
            # Decrypt the IMAP password for use
            try:
                imap_password = security_manager.decrypt_sensitive_data(imap_password)
            except Exception as decrypt_error:
                error_msg = f"Failed to decrypt IMAP password: {decrypt_error}"
                logger.error(error_msg)
                fetch_result.errors.append(error_msg)
                self.fetch_stats['failed_fetches'] += 1
                return fetch_result
            
            # Create connection info
            connection_info = ConnectionInfo(
                server=imap_server,
                port=imap_port,
                username=imap_username,
                password=imap_password,
                use_ssl=bool(imap_use_ssl)
            )
            
            # Store in cache for future use
            self.connection_cache[account_id] = connection_info
            
            # Use connection pool if enabled
            if use_connection_pool:
                imap_conn = await self.imap_pool.get_connection(connection_info)
                if not imap_conn:
                    error_msg = "Failed to get IMAP connection from pool"
                    logger.error(error_msg)
                    fetch_result.errors.append(error_msg)
                    self.fetch_stats['failed_fetches'] += 1
                    return fetch_result
            else:
                # Create direct connection
                imap_conn = await self._create_imap_connection_direct(connection_info)
                if not imap_conn:
                    error_msg = "Failed to create direct IMAP connection"
                    logger.error(error_msg)
                    fetch_result.errors.append(error_msg)
                    self.fetch_stats['failed_fetches'] += 1
                    return fetch_result
            
            connection_time = time.time() - start_time
            fetch_result.connection_time = connection_time
            
            try:
                # Select folder
                status, _ = imap_conn.select(folder)
                if status != 'OK':
                    error_msg = f"Failed to select folder {folder}"
                    logger.error(error_msg)
                    fetch_result.errors.append(error_msg)
                    self.fetch_stats['failed_fetches'] += 1
                    return fetch_result
                
                # Search for emails with retry logic if enabled
                if enable_retry:
                    emails, search_errors = await self._search_emails_with_retry(
                        imap_conn, folder, limit, user_id, account_id
                    )
                else:
                    emails, search_errors = await self._search_emails_simple(
                        imap_conn, folder, limit, user_id, account_id
                    )
                
                if search_errors:
                    fetch_result.errors.extend(search_errors)
                
                fetch_result.emails_fetched = len(emails)
                fetch_result.success = True
                
                # Save fetched emails to database
                if emails:
                    self._save_fetched_emails(emails)
                
                logger.info(f"Successfully fetched {len(emails)} emails from {folder} for account {account_id}")
                
            finally:
                # Release connection back to pool or close direct connection
                if use_connection_pool:
                    await self.imap_pool.release_connection(connection_info, imap_conn)
                else:
                    try:
                        imap_conn.close()
                        imap_conn.logout()
                    except Exception as e:
                        logger.warning(f"Error closing IMAP connection: {e}")
            
            # Update statistics
            fetch_time = time.time() - start_time - connection_time
            total_time = time.time() - start_time
            
            fetch_result.fetch_time = fetch_time
            fetch_result.total_time = total_time
            
            # Update global fetch statistics
            self.fetch_stats['successful_fetches'] += 1
            self.fetch_stats['emails_fetched'] += len(emails)
            
            # Update average fetch time (moving average)
            total_fetches = self.fetch_stats['successful_fetches']
            current_avg = self.fetch_stats['average_fetch_time']
            self.fetch_stats['average_fetch_time'] = (
                (current_avg * (total_fetches - 1) + total_time) / total_fetches
            )
            
            return fetch_result
            
        except Exception as e:
            error_msg = f"Unexpected error in fetch_emails_async: {e}"
            logger.error(error_msg)
            fetch_result.errors.append(error_msg)
            self.fetch_stats['failed_fetches'] += 1
            return fetch_result
    
    async def _create_imap_connection_direct(self, connection_info: ConnectionInfo) -> Optional[imaplib.IMAP4]:
        """Create direct IMAP connection (for non-pooled connections)"""
        try:
            connection_info.state = ConnectionState.CONNECTING
            
            if connection_info.use_ssl:
                imap_conn = imaplib.IMAP4_SSL(connection_info.server, connection_info.port)
            else:
                imap_conn = imaplib.IMAP4(connection_info.server, connection_info.port)
                imap_conn.starttls()
            
            connection_info.state = ConnectionState.AUTHENTICATING
            imap_conn.login(connection_info.username, connection_info.password)
            
            connection_info.state = ConnectionState.AUTHENTICATED
            connection_info.last_successful_connection = datetime.now(timezone.utc)
            connection_info.connection_attempts = 0
            connection_info.connection_errors.clear()
            
            logger.info(f"Direct IMAP connection established for {connection_info.username}")
            return imap_conn
            
        except Exception as e:
            connection_info.state = ConnectionState.ERROR
            connection_info.connection_attempts += 1
            connection_info.connection_errors.append(str(e))
            logger.error(f"Direct IMAP connection failed for {connection_info.username}: {e}")
            return None
    
    async def _search_emails_with_retry(self, imap_conn: imaplib.IMAP4, folder: str, limit: int, 
                                       user_id: int, account_id: int) -> Tuple[List[EmailMessage], List[str]]:
        """Search emails with retry logic"""
        errors = []
        
        for attempt in range(1, self.retry_config.max_retries + 1):
            try:
                return await self._search_emails_simple(imap_conn, folder, limit, user_id, account_id)
            except Exception as e:
                error_msg = f"Search attempt {attempt} failed: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
                
                if attempt < self.retry_config.max_retries:
                    # Calculate delay with exponential backoff
                    delay = min(
                        self.retry_config.base_delay * (self.retry_config.exponential_backoff ** (attempt - 1)),
                        self.retry_config.max_delay
                    )
                    logger.info(f"Retrying email search in {delay:.1f} seconds... (attempt {attempt + 1}/{self.retry_config.max_retries})")
                    await asyncio.sleep(delay)
        
        # All retries failed
        return [], errors
    
    async def _search_emails_simple(self, imap_conn: imaplib.IMAP4, folder: str, limit: int, 
                                   user_id: int, account_id: int) -> Tuple[List[EmailMessage], List[str]]:
        """Simple email search without retry logic"""
        errors = []
        emails = []
        
        try:
            # Search for all emails in the folder
            status, messages = imap_conn.search(None, 'ALL')
            if status != 'OK':
                error_msg = "No messages found or search failed"
                errors.append(error_msg)
                logger.error(error_msg)
                return emails, errors
            
            email_ids = messages[0].split()
            if not email_ids:
                logger.info(f"No emails found in folder {folder}")
                return emails, errors
            
            # Get most recent emails
            email_ids = email_ids[-limit:]  # Get last 'limit' emails
            
            # Fetch emails in batches for better performance
            batch_size = 10
            for i in range(0, len(email_ids), batch_size):
                batch_ids = email_ids[i:i + batch_size]
                batch_emails, batch_errors = await self._fetch_email_batch(
                    imap_conn, batch_ids, user_id, account_id
                )
                emails.extend(batch_emails)
                errors.extend(batch_errors)
            
            # Sort emails by date (newest first)
            emails.sort(key=lambda x: x.date, reverse=True)
            
            logger.info(f"Fetched {len(emails)} emails from folder {folder}")
            return emails, errors
            
        except Exception as e:
            error_msg = f"Error searching emails: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
            return emails, errors
    
    async def _fetch_email_batch(self, imap_conn: imaplib.IMAP4, email_ids: List[bytes], 
                                user_id: int, account_id: int) -> Tuple[List[EmailMessage], List[str]]:
        """Fetch a batch of emails"""
        emails = []
        errors = []
        
        for email_id in reversed(email_ids):  # Process newest first
            try:
                status, msg_data = imap_conn.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    error_msg = f"Failed to fetch email ID {email_id}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        email_message = email.message_from_bytes(response_part[1])
                        
                        # Parse email
                        parsed_email = self._parse_email_message(email_message, user_id, account_id)
                        if parsed_email:
                            emails.append(parsed_email)
                        else:
                            error_msg = f"Failed to parse email ID {email_id}"
                            errors.append(error_msg)
                            logger.warning(error_msg)
                            
            except Exception as e:
                error_msg = f"Error fetching email ID {email_id}: {e}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        return emails, errors
    
    def fetch_emails(self, account_id: int, folder: str = "INBOX", limit: int = 50) -> List[EmailMessage]:
        """Synchronous wrapper for fetch_emails_async (maintains backward compatibility)"""
        try:
            # Run async version synchronously
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.fetch_emails_async(account_id, folder, limit)
                )
                loop.close()
            else:
                result = loop.run_until_complete(
                    self.fetch_emails_async(account_id, folder, limit)
                )
            
            if result.success:
                return []  # Return empty list (for backward compatibility - emails are saved to DB)
            else:
                return []  # Return empty list if fetch failed (for backward compatibility)
                
        except Exception as e:
            logger.error(f"Error in synchronous fetch_emails wrapper: {e}")
            return []
    
    def _parse_email_message(self, email_message, user_id: int, account_id: int) -> Optional[EmailMessage]:
        """Parse email message from IMAP"""
        try:
            # Extract basic info
            subject = self._decode_email_header(email_message.get('Subject', ''))
            sender = self._decode_email_header(email_message.get('From', ''))
            recipient = self._decode_email_header(email_message.get('To', ''))
            message_id = email_message.get('Message-ID', '')
            date_str = email_message.get('Date', '')
            
            # Parse date
            try:
                email_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except:
                try:
                    email_date = datetime.strptime(date_str, '%d %b %Y %H:%M:%S %z')
                except:
                    email_date = datetime.now(timezone.utc)
            
            # Extract body
            body = ""
            html_body = ""
            attachments = []
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                'filename': filename,
                                'content_type': content_type,
                                'size': len(part.get_payload(decode=True))
                            })
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return EmailMessage(
                user_id=user_id,
                account_id=account_id,
                message_id=message_id,
                subject=subject,
                sender=sender,
                recipient=recipient,
                body=body,
                html_body=html_body,
                date=email_date,
                is_read=False,
                is_sent=False,
                folder="INBOX",
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Error parsing email message: {e}")
            return None
    
    def _decode_email_header(self, header_value: str) -> str:
        """Decode email header"""
        try:
            decoded_parts = decode_header(header_value)
            decoded_header = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_header += part.decode(encoding, errors='ignore')
                    else:
                        decoded_header += part.decode('utf-8', errors='ignore')
                else:
                    decoded_header += part
            
            return decoded_header.strip()
            
        except Exception as e:
            logger.error(f"Error decoding email header: {e}")
            return header_value
    
    def _save_fetched_emails(self, emails: List[EmailMessage]):
        """Save fetched emails to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for email_msg in emails:
                # Check if email already exists
                cursor.execute("SELECT id FROM email_messages WHERE message_id = ?", (email_msg.message_id,))
                if cursor.fetchone():
                    continue
                
                cursor.execute("""
                    INSERT INTO email_messages (
                        user_id, account_id, message_id, subject, sender, recipient, body,
                        html_body, date, is_read, is_sent, folder, attachments, priority, labels
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email_msg.user_id, email_msg.account_id, email_msg.message_id,
                    email_msg.subject, email_msg.sender, email_msg.recipient,
                    email_msg.body, email_msg.html_body, email_msg.date,
                    email_msg.is_read, email_msg.is_sent, email_msg.folder,
                    json.dumps(email_msg.attachments), email_msg.priority,
                    json.dumps(email_msg.labels)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(emails)} fetched emails to database")
            
        except Exception as e:
            logger.error(f"Error saving fetched emails: {e}")
    
    def get_emails(self, user_id: int, folder: str = "INBOX", limit: int = 50, offset: int = 0) -> List[EmailMessage]:
        """Get emails from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, account_id, message_id, subject, sender, recipient, body,
                       html_body, date, is_read, is_sent, folder, attachments, headers,
                       priority, labels, created_at
                FROM email_messages
                WHERE user_id = ? AND folder = ?
                ORDER BY date DESC
                LIMIT ? OFFSET ?
            """, (user_id, folder, limit, offset))
            
            emails = []
            for row in cursor.fetchall():
                email_msg = EmailMessage(
                    id=str(row[0]),
                    account_id=row[1],
                    message_id=row[2],
                    subject=row[3],
                    sender=row[4],
                    recipient=row[5],
                    body=row[6],
                    html_body=row[7],
                    date=datetime.fromisoformat(row[8]) if isinstance(row[8], str) else row[8],
                    is_read=bool(row[9]),
                    is_sent=bool(row[10]),
                    folder=row[11],
                    attachments=json.loads(row[12]) if row[12] else [],
                    headers=json.loads(row[13]) if row[13] else {},
                    priority=row[14],
                    labels=json.loads(row[15]) if row[15] else []
                )
                emails.append(email_msg)
            
            conn.close()
            return emails
            
        except Exception as e:
            logger.error(f"Error getting emails from database: {e}")
            return []
    
    def mark_as_read(self, email_id: str, user_id: int) -> bool:
        """Mark email as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE email_messages
                SET is_read = 1
                WHERE id = ? AND user_id = ?
            """, (email_id, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Email {email_id} marked as read")
            return True
            
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    def delete_email(self, email_id: str, user_id: int) -> bool:
        """Delete email (move to trash)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE email_messages
                SET folder = 'Trash'
                WHERE id = ? AND user_id = ?
            """, (email_id, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Email {email_id} moved to trash")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting email: {e}")
            return False

# Global email manager instance
email_manager = EmailManager()

# Export the manager and models
__all__ = ['EmailManager', 'EmailMessage', 'EmailAccount', 'email_manager']