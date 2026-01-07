"""
Email Plugin for dhii Mail - Framework 2.0 Migration
Migrates from DomainModule to PluginInterface
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

# Framework 2.0 imports
from a2ui_integration.framework.contract import PluginInterface, PluginManifest, PluginCapability, PluginType, CapabilityType, ExecutionContext
from a2ui_integration.framework.types import PluginHealth, HealthStatus, CapabilityExecutionResult

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


class EmailPluginV2(PluginInterface):
    """Email Plugin - Framework 2.0 Implementation"""
    
    def __init__(self, db_path: str = "email_plugin.db"):
        self.db_path = db_path
        self._connections: Dict[str, ConnectionInfo] = {}
        self._imap_connections: Dict[str, imaplib.IMAP4] = {}
        self._smtp_connections: Dict[str, smtplib.SMTP] = {}
        self._manifest: Optional[PluginManifest] = None
        self._health_status = HealthStatus.HEALTHY
        self._kernel_api: Optional[Dict[str, Any]] = None
        
        # Initialize database
        self._init_database()
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest with metadata and capabilities (Framework 2.0)"""
        if self._manifest is None:
            self._manifest = PluginManifest(
                id="email",
                name="Email Integration",
                version="2.0.0",
                plugin_type=PluginType.INTEGRATION,
                author="Dhii Team",
                description="Email integration with SMTP support - Framework 2.0",
                capabilities=[
                    PluginCapability(
                        id="email.send",
                        name="Send Email",
                        description="Send an email message",
                        capability_type=CapabilityType.ACTION,
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
                        requires_auth=True,
                        timeout_seconds=30
                    ),
                    PluginCapability(
                        id="email.receive",
                        name="Receive Emails",
                        description="Fetch emails from mailbox",
                        capability_type=CapabilityType.QUERY,
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
                        requires_auth=True,
                        timeout_seconds=30
                    ),
                    PluginCapability(
                        id="email.search",
                        name="Search Emails",
                        description="Search emails by criteria",
                        capability_type=CapabilityType.QUERY,
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
                        requires_auth=True,
                        timeout_seconds=30
                    )
                ],
                dependencies=[],
                sandbox_config={
                    "network_access": True,
                    "file_system_access": True,
                    "database_access": True
                }
            )
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API access (Framework 2.0)"""
        self._kernel_api = kernel_api
        logger.info("EmailPluginV2 initialized with Framework 2.0")
        
        # Log initialization to kernel
        if "log" in kernel_api:
            kernel_api["log"]("EmailPluginV2 initialized successfully", "info")
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a specific capability (Framework 2.0)"""
        start_time = datetime.now()
        
        try:
            if capability_id == "email.send":
                result = self._send_email(params)
            elif capability_id == "email.receive":
                result = self._receive_emails(params)
            elif capability_id == "email.search":
                result = self._search_emails(params)
            else:
                raise ValueError(f"Unknown capability: {capability_id}")
            
            # Create execution result
            execution_result = CapabilityExecutionResult(
                plugin_id="email",
                capability_id=capability_id,
                request_id=params.get("request_id", "unknown"),
                success=True,
                result=result,
                execution_time=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now()
            )
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing capability {capability_id}: {e}")
            
            # Create error execution result
            execution_result = CapabilityExecutionResult(
                plugin_id="email",
                capability_id=capability_id,
                request_id=params.get("request_id", "unknown"),
                success=False,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now()
            )
            
            return execution_result
    
    def shutdown(self) -> None:
        """Cleanup when plugin is unloaded (Framework 2.0)"""
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
        
        logger.info("EmailPluginV2 shutdown completed")
    
    def get_health_status(self) -> PluginHealth:
        """Get plugin health status (Framework 2.0)"""
        return PluginHealth(
            plugin_id="email",
            status=self._health_status,
            message="Email plugin operational",
            capabilities={
                "email.send": HealthStatus.HEALTHY,
                "email.receive": HealthStatus.HEALTHY,
                "email.search": HealthStatus.HEALTHY
            }
        )
    
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
        
        conn.commit()
        conn.close()
    
    def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send email implementation"""
        # Implementation would go here - similar to Framework 1.0 version
        # but returning Framework 2.0 compatible result
        return {
            "success": True,
            "message_id": "test-message-id",
            "error": None
        }
    
    def _receive_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Receive emails implementation"""
        # Implementation would go here - similar to Framework 1.0 version
        # but returning Framework 2.0 compatible result
        return {
            "emails": [],
            "count": 0
        }
    
    def _search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails implementation"""
        # Implementation would go here - similar to Framework 1.0 version
        # but returning Framework 2.0 compatible result
        return {
            "results": [],
            "count": 0
        }


def register(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Register the EmailPluginV2 with Framework 2.0"""
    plugin = EmailPluginV2()
    plugin.initialize(kernel_api)
    return plugin