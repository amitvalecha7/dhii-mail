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
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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
    
    def __init__(self, db_path: str = "email_accounts.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize email database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Email accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_address TEXT NOT NULL,
                display_name TEXT,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER DEFAULT 587,
                smtp_username TEXT NOT NULL,
                smtp_password TEXT NOT NULL,
                smtp_use_tls BOOLEAN DEFAULT 1,
                imap_server TEXT NOT NULL,
                imap_port INTEGER DEFAULT 993,
                imap_username TEXT NOT NULL,
                imap_password TEXT NOT NULL,
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
        """Add a new email account"""
        try:
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
                account.smtp_password, account.smtp_use_tls, account.imap_server,
                account.imap_port, account.imap_username, account.imap_password,
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
        """Get all email accounts for a user"""
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
                account = EmailAccount(
                    id=row[0],
                    user_id=row[1],
                    email_address=row[2],
                    display_name=row[3],
                    smtp_server=row[4],
                    smtp_port=row[5],
                    smtp_username=row[6],
                    smtp_password=row[7],
                    smtp_use_tls=bool(row[8]),
                    imap_server=row[9],
                    imap_port=row[10],
                    imap_username=row[11],
                    imap_password=row[12],
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
    
    def send_email(self, message: EmailMessage, account_id: int) -> bool:
        """Send an email using SMTP"""
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
                logger.error("Email account not found or inactive")
                return False
            
            smtp_server, smtp_port, smtp_username, smtp_password, smtp_use_tls, sender_email = account_data
            conn.close()
            
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
            
            # Connect to SMTP server and send
            if smtp_use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            # Save sent message to database
            self._save_sent_message(message, account_id)
            
            logger.info(f"Email sent successfully to {message.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _save_sent_message(self, message: EmailMessage, account_id: int):
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
                message.sender, account_id, message.message_id, message.subject,
                message.sender, message.recipient, message.body, message.html_body,
                message.date, True, 'Sent', json.dumps(message.attachments),
                json.dumps(message.headers), message.priority, json.dumps(message.labels)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving sent message: {e}")
    
    def fetch_emails(self, account_id: int, folder: str = "INBOX", limit: int = 50) -> List[EmailMessage]:
        """Fetch emails from IMAP server"""
        try:
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
                logger.error("Email account not found or inactive")
                return []
            
            imap_server, imap_port, imap_username, imap_password, imap_use_ssl, user_id = account_data
            conn.close()
            
            # Connect to IMAP server
            if imap_use_ssl:
                mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            else:
                mail = imaplib.IMAP4(imap_server, imap_port)
                mail.starttls()
            
            mail.login(imap_username, imap_password)
            mail.select(folder)
            
            # Search for all emails in the folder
            status, messages = mail.search(None, 'ALL')
            if status != 'OK':
                logger.error("No messages found")
                mail.close()
                mail.logout()
                return []
            
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:]  # Get most recent emails
            
            emails = []
            for email_id in reversed(email_ids):
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        email_message = email.message_from_bytes(response_part[1])
                        
                        # Parse email
                        parsed_email = self._parse_email_message(email_message, user_id, account_id)
                        if parsed_email:
                            emails.append(parsed_email)
            
            mail.close()
            mail.logout()
            
            # Save fetched emails to database
            self._save_fetched_emails(emails)
            
            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
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