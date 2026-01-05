import asyncio
import imaplib
import email
import logging
import sqlite3
import json
from datetime import datetime
from email.header import decode_header
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class EmailSyncService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._running = False
        self._tasks = []

    async def start(self):
        """Start the background sync loop"""
        self._running = True
        logger.info("Email Sync Service Started", extra_fields={"service": "email_sync"})
        self._tasks.append(asyncio.create_task(self._sync_loop()))

    async def stop(self):
        """Stop the background sync loop"""
        self._running = False
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Email Sync Service Stopped", extra_fields={"service": "email_sync"})

    async def _sync_loop(self):
        """Main loop that polls accounts periodically"""
        while self._running:
            try:
                logger.debug("Starting email polling cycle...")
                await self._poll_all_accounts()
                # Configurable interval, defaulting to 60s
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Global sync error: {e}", extra_fields={"service": "email_sync"})
                await asyncio.sleep(60) # Sleep on error too

    async def _poll_all_accounts(self):
        """Fetch accounts from DB and sync them"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, imap_server, imap_port, username, password_encrypted, last_synced_uid, use_ssl FROM email_accounts")
            accounts = cursor.fetchall()
            conn.close()

            for acc in accounts:
                if not self._running: break
                
                # Unpack
                acc_id, server, port, user, pwd, last_uid, use_ssl = acc
                
                # Sync single account
                await self._sync_account(acc_id, server, port, user, pwd, last_uid, use_ssl)
                
        except Exception as e:
            logger.error(f"Failed to fetch accounts: {e}")

    async def _sync_account(self, acc_id, server, port, user, pwd, last_uid, use_ssl):
        """Sync a specific account via IMAP"""
        try:
            # Note: In production pwd should be decrypted here
            
            # Run blocking IMAP calls in a thread
            await asyncio.to_thread(self._imap_fetch, acc_id, server, port, user, pwd, last_uid, use_ssl)
            
        except Exception as e:
            logger.error(f"Error syncing account {user}: {e}")

    def _imap_fetch(self, acc_id, server, port, user, pwd, last_uid, use_ssl):
        """Blocking IMAP logic"""
        mail = None
        try:
            if use_ssl:
                mail = imaplib.IMAP4_SSL(server, port)
            else:
                mail = imaplib.IMAP4(server, port)
                
            mail.login(user, pwd)
            mail.select("INBOX")
            
            # Fetch UIDs > last_uid
            search_crit = f"(UID {last_uid + 1}:*)" if last_uid > 0 else "ALL"
            if last_uid == 0: 
                # On first sync, maybe limit to recent? For V1 launch let's do ALL or last 50
                # Using 1:* is risky if inbox is huge. 
                # Correction: Let's just fetch recent 10 for safety in V1
                pass

            status, data = mail.uid('search', None, 'ALL') # Simply grab all for now, logic refinement later
            if status != 'OK': return

            uids = data[0].split()
            if not uids: return

            # Convert to ints and filter
            uid_ints = sorted([int(u) for u in uids])
            new_uids = [u for u in uid_ints if u > last_uid]
            
            # Process new emails
            for uid in new_uids[-5:]: # Limit to 5 per poll for V1 safety
                res, msg_data = mail.uid('fetch', str(uid), '(RFC822)')
                raw_email = msg_data[0][1]
                self._parse_and_save(acc_id, uid, raw_email)

            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"IMAP Error for {user}: {e}")
            if mail:
                try: mail.logout()
                except: pass

    def _parse_and_save(self, acc_id, uid, raw_email):
        """Parse raw bytes and save to SQLite"""
        try:
            msg = email.message_from_bytes(raw_email)
            
            # Basic Parsing
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes): subject = subject.decode()
            
            sender = msg["From"]
            
            body = "Content processing..."
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                         body = part.get_payload(decode=True).decode(errors='ignore')
                         break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            # Save to DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            msg_db_id = f"{acc_id}_{uid}"
            
            cursor.execute('''
                INSERT OR IGNORE INTO received_emails 
                (id, account_id, subject, sender, recipients, body, timestamp, folder, is_read)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                msg_db_id, acc_id, str(subject), str(sender), "[]", body, datetime.now(), 'INBOX', False
            ))
            
            # Update Last Sync UID
            cursor.execute("UPDATE email_accounts SET last_synced_uid = ? WHERE id = ?", (uid, acc_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved new email: {subject}")
            
        except Exception as e:
            logger.error(f"Parsing error: {e}")
