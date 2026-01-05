"""
Email Plugin for dhii Mail
Handles email operations as a plugin in the new kernel architecture
"""

import os
import imaplib
import smtplib
import email
import logging
import json
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

from a2ui_integration.core.types import DomainModule, Capability, PluginType, PluginStatus, PluginConfig

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


class EmailMessage(BaseModel):
    """Email message model"""
    id: Optional[str] = None
    subject: str
    sender: str
    recipients: List[str]
    body: str
    html_body: Optional[str] = None
    attachments: List[Dict[str, str]] = []
    timestamp: datetime
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: List[str] = []
    priority: str = "normal"
    flags: List[str] = []


class EmailPlugin(DomainModule):
    """Email plugin that provides email capabilities"""
    
    def __init__(self, db_path: str = "email_plugin.db"):
        self.db_path = db_path
        self._connections: Dict[str, ConnectionInfo] = {}
        self._imap_connections: Dict[str, imaplib.IMAP4] = {}
        self._smtp_connections: Dict[str, smtplib.SMTP] = {}
        
        # Initialize database
        self._init_database()
    
    @property
    def domain(self) -> str:
        """Return the domain name this module handles"""
        return "email"
    
    @property
    def capabilities(self) -> List[Capability]:
        """Return list of capabilities this module provides"""
        return [
            Capability(
                id="email.send",
                domain="email",
                name="Send Email",
                description="Send an email message",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "array", "items": {"type": "string"}},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "html_body": {"type": "string"},
                        "attachments": {"type": "array"}
                    },
                    "required": ["to", "subject", "body"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "message_id": {"type": "string"},
                        "error": {"type": "string"}
                    }
                },
                side_effects=["email_sent"],
                requires_auth=True
            ),
            Capability(
                id="email.receive",
                domain="email",
                name="Receive Emails",
                description="Fetch emails from mailbox",
                input_schema={
                    "type": "object",
                    "properties": {
                        "folder": {"type": "string", "default": "INBOX"},
                        "limit": {"type": "integer", "default": 10},
                        "unread_only": {"type": "boolean", "default": False}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "emails": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                },
                side_effects=["email_fetched"],
                requires_auth=True
            ),
            Capability(
                id="email.search",
                domain="email",
                name="Search Emails",
                description="Search emails by criteria",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "from": {"type": "string"},
                        "subject": {"type": "string"},
                        "date_from": {"type": "string", "format": "date"},
                        "date_to": {"type": "string", "format": "date"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                },
                side_effects=[],
                requires_auth=True
            )
        ]
    
    def _init_database(self):
        """Initialize the email plugin database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Email accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                imap_server TEXT NOT NULL,
                imap_port INTEGER NOT NULL,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER NOT NULL,
                username TEXT NOT NULL,
                password_encrypted TEXT NOT NULL,
                use_ssl BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_connected TIMESTAMP,
                last_synced_uid INTEGER DEFAULT 0
            )
        ''')
        
        # Migration for existing tables
        try:
            cursor.execute('ALTER TABLE email_accounts ADD COLUMN last_synced_uid INTEGER DEFAULT 0')
        except:
            pass # Column likely exists
        
        # Sent emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_emails (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                message_id TEXT,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipients TEXT NOT NULL,
                body TEXT,
                html_body TEXT,
                attachments TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                error_message TEXT,
                FOREIGN KEY (account_id) REFERENCES email_accounts (id)
            )
        ''')
        
        # Received emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS received_emails (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                message_id TEXT,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipients TEXT NOT NULL,
                body TEXT,
                html_body TEXT,
                attachments TEXT,
                timestamp TIMESTAMP,
                folder TEXT DEFAULT 'INBOX',
                flags TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (account_id) REFERENCES email_accounts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def initialize(self) -> bool:
        """Initialize the email plugin"""
        try:
            logger.info("Initializing email plugin")
            from .services.sync_service import EmailSyncService
            self.sync_service = EmailSyncService(self.db_path)
            await self.sync_service.start()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize email plugin: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the email plugin"""
        try:
            # Stop sync service
            if hasattr(self, 'sync_service'):
                await self.sync_service.stop()

            # Close all connections
            for conn in self._imap_connections.values():
                try:
                    conn.close()
                    conn.logout()
                except:
                    pass
            
            for conn in self._smtp_connections.values():
                try:
                    conn.quit()
                except:
                    pass
            
            logger.info("Email plugin shutdown complete")
            return True
        except Exception as e:
            logger.error(f"Error shutting down email plugin: {e}")
            return False
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific capability"""
        if capability_id == "email.send":
            return await self._send_email(params)
        elif capability_id == "email.receive":
            return await self._receive_emails(params)
        elif capability_id == "email.search":
            return await self._search_emails(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email"""
        try:
            # Get account configuration
            account_id = params.get("account_id", "default")
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = params['subject']
            msg['From'] = params.get('from', 'noreply@dhii-mail.com')
            msg['To'] = ', '.join(params['to'])
            
            # Add body
            if 'body' in params:
                text_part = MIMEText(params['body'], 'plain')
                msg.attach(text_part)
            
            if 'html_body' in params:
                html_part = MIMEText(params['html_body'], 'html')
                msg.attach(html_part)
            
            # Add attachments
            if 'attachments' in params:
                for attachment in params['attachments']:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{attachment["filename"]}"')
                    msg.attach(part)
            
            # Store in database
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            message_id = f"msg_{datetime.now().timestamp()}"
            cursor.execute('''
                INSERT INTO sent_emails 
                (id, account_id, message_id, subject, sender, recipients, body, html_body, attachments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                account_id,
                msg['Message-ID'],
                params['subject'],
                msg['From'],
                json.dumps(params['to']),
                params.get('body', ''),
                params.get('html_body', ''),
                json.dumps(params.get('attachments', []))
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message_id": message_id,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    async def _receive_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Receive emails from mailbox"""
        try:
            # This is a simplified implementation
            # In a real implementation, you would connect to IMAP server
            
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent emails from database
            limit = params.get('limit', 10)
            folder = params.get('folder', 'INBOX')
            
            cursor.execute('''
                SELECT * FROM received_emails 
                WHERE folder = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (folder, limit))
            
            emails = cursor.fetchall()
            conn.close()
            
            # Convert to proper format
            email_list = []
            for email_data in emails:
                email_list.append({
                    "id": email_data[0],
                    "subject": email_data[3],
                    "sender": email_data[4],
                    "recipients": json.loads(email_data[5]),
                    "body": email_data[6],
                    "html_body": email_data[7],
                    "timestamp": email_data[9],
                    "folder": email_data[10],
                    "is_read": email_data[12]
                })
            
            return {
                "emails": email_list,
                "count": len(email_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to receive emails: {e}")
            return {
                "emails": [],
                "count": 0
            }
    
    async def _search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails by criteria"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = params.get('query', '')
            
            # Build search query
            conditions = []
            values = []
            
            if query:
                conditions.append("(subject LIKE ? OR body LIKE ?)")
                values.extend([f"%{query}%", f"%{query}%"])
            
            if 'from' in params:
                conditions.append("sender LIKE ?")
                values.append(f"%{params['from']}%")
            
            if 'subject' in params:
                conditions.append("subject LIKE ?")
                values.append(f"%{params['subject']}%")
            
            if 'date_from' in params:
                conditions.append("timestamp >= ?")
                values.append(params['date_from'])
            
            if 'date_to' in params:
                conditions.append("timestamp <= ?")
                values.append(params['date_to'])
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f'''
                SELECT * FROM received_emails 
                WHERE {where_clause}
                ORDER BY timestamp DESC
            ''', values)
            
            results = cursor.fetchall()
            conn.close()
            
            # Convert to proper format
            search_results = []
            for result in results:
                search_results.append({
                    "id": result[0],
                    "subject": result[3],
                    "sender": result[4],
                    "recipients": json.loads(result[5]),
                    "body": result[6],
                    "html_body": result[7],
                    "timestamp": result[9]
                })
            
            return {
                "results": search_results,
                "count": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to search emails: {e}")
            return {
                "results": [],
                "count": 0
            }


# Plugin configuration
EMAIL_PLUGIN_CONFIG = PluginConfig(
    id="email_plugin",
    name="Email Plugin",
    version="1.0.0",
    description="Comprehensive email management capabilities",
    type=PluginType.EMAIL,
    author="dhii-mail-team",
    enabled=False,
    config={
        "max_connections": 10,
        "connection_timeout": 30,
        "retry_attempts": 3
    },
    capabilities=[],  # Will be populated by the plugin instance
    dependencies=[]
)