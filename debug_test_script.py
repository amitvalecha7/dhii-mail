import logging
import sqlite3
import asyncio
from unittest.mock import MagicMock, patch
from plugins.email.services.sync_service import EmailSyncService

# Setup Logging
logging.basicConfig(level=logging.DEBUG)

def setup_mock_db():
    db_path = "debug_db.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS email_accounts")
    cursor.execute("DROP TABLE IF EXISTS received_emails")
    
    cursor.execute('''
        CREATE TABLE email_accounts (
            id TEXT PRIMARY KEY,
            name TEXT,
            imap_server TEXT,
            imap_port INTEGER,
            smtp_server TEXT,
            smtp_port INTEGER,
            username TEXT,
            password_encrypted TEXT,
            use_ssl BOOLEAN,
            created_at TIMESTAMP,
            last_connected TIMESTAMP,
            last_synced_uid INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE received_emails (
            id TEXT PRIMARY KEY,
            account_id TEXT,
            subject TEXT,
            sender TEXT,
            recipients TEXT,
            body TEXT,
            timestamp TIMESTAMP,
            folder TEXT,
            is_read BOOLEAN
        )
    ''')
    cursor.execute("INSERT INTO email_accounts VALUES ('acc1', 'Test', 'imap.test', 993, 'smtp.test', 587, 'user', 'pwd', 1, null, null, 100)")
    conn.commit()
    conn.close()
    return db_path

async def run_debug():
    print("Setting up DB...")
    db_path = setup_mock_db()
    
    print("Instantiating Service...")
    try:
        service = EmailSyncService(db_path)
    except Exception as e:
        print(f"FAILED to instantiate: {e}")
        return

    print("Running Poll...")
    with patch('plugins.email.services.sync_service.imaplib.IMAP4_SSL') as mock_imap_cls:
        mock_imap = mock_imap_cls.return_value
        # Configure Mock
        mock_imap.uid.side_effect = [
            ('OK', [b'101 102']), 
            ('OK', [(b'1 (RFC822 {10}', b'Subject: Debug Email\r\nFrom: me@debug.com\r\n\r\nDebugBody')])
        ]
        
        try:
            await service._poll_all_accounts()
            print("Poll Completed Successfully.")
        except Exception as e:
            print(f"FAILED during poll: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_debug())
