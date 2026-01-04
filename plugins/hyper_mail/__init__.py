import imaplib
import email
from email.policy import default
import json
import datetime

def register(kernel):
    kernel["log"]("Hyper-Mail plugin loading...")

    async def fetch_inbox(params):
        kernel["log"]("Hyper-Mail: Fetching inbox...")
        
        server = params.get("server", "imap.gmail.com")
        username = params.get("username")
        password = params.get("password")
        
        if not username or not password:
            return {
                "type": "card",
                "title": "Error",
                "children": [{"type": "text", "content": "Missing credentials. Please provide username and password."}]
            }

        try:
            # Connect to IMAP
            # Note: This runs inside the sandbox, but imaplib is whitelisted
            mail = imaplib.IMAP4_SSL(server)
            mail.login(username, password)
            mail.select("inbox")
            
            # Search for latest 10 emails
            # We use 'ALL' for simplicity in this MVP
            typ, data = mail.search(None, "ALL")
            mail_ids = data[0].split()
            latest_ids = mail_ids[-10:] # Get last 10
            
            items = []
            
            # Iterate in reverse order (newest first)
            for msg_id in reversed(latest_ids):
                typ, msg_data = mail.fetch(msg_id, "(RFC822)")
                if not msg_data or not msg_data[0]:
                    continue
                    
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email, policy=default)
                
                subject = msg["subject"] or "(No Subject)"
                sender = msg["from"] or "Unknown"
                date = msg["date"] or ""
                
                items.append({
                    "id": str(msg_id.decode()),
                    "title": subject,
                    "subtitle": f"{sender} | {date}",
                    "action": {
                        "type": "run_capability",
                        "capability_id": "read_email",
                        "params": {
                            "email_id": str(msg_id.decode()),
                            "username": username,
                            "password": password
                        }
                    }
                })
            
            mail.close()
            mail.logout()
            
            return {
                "type": "card",
                "id": "inbox-card",
                "title": "Inbox",
                "children": [
                    {
                        "type": "list",
                        "items": items
                    }
                ]
            }
            
        except Exception as e:
            kernel["error"](f"Hyper-Mail Error: {e}")
            return {
                "type": "card",
                "title": "Connection Error",
                "children": [{"type": "text", "content": str(e)}]
            }

    async def read_email(params):
        kernel["log"]("Hyper-Mail: Reading email...")
        
        server = params.get("server", "imap.gmail.com")
        username = params.get("username")
        password = params.get("password")
        email_id = params.get("email_id")
        
        if not username or not password or not email_id:
            return {"type": "card", "title": "Error", "children": [{"type": "text", "content": "Missing parameters."}]}

        try:
            mail = imaplib.IMAP4_SSL(server)
            mail.login(username, password)
            mail.select("inbox")
            
            typ, msg_data = mail.fetch(email_id, "(RFC822)")
            if not msg_data or not msg_data[0]:
                return {"type": "card", "title": "Error", "children": [{"type": "text", "content": "Email not found."}]}
                
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email, policy=default)
            
            subject = msg["subject"] or "(No Subject)"
            sender = msg["from"] or "Unknown"
            date = msg["date"] or ""
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if "attachment" not in content_disposition:
                        if content_type == "text/plain":
                            body += part.get_payload(decode=True).decode()
                        elif content_type == "text/html":
                            # For MVP, just append HTML, though A2UI might want it sanitized or distinct
                            # Prefer plain text if available for simple cards
                            pass 
            else:
                body = msg.get_payload(decode=True).decode()
                
            mail.close()
            mail.logout()
            
            return {
                "type": "card",
                "title": subject,
                "children": [
                    {"type": "text", "content": f"From: {sender}"},
                    {"type": "text", "content": f"Date: {date}"},
                    {"type": "divider"},
                    {"type": "text", "content": body}
                ]
            }
            
        except Exception as e:
            kernel["error"](f"Hyper-Mail Error: {e}")
            return {
                "type": "card",
                "title": "Read Error",
                "children": [{"type": "text", "content": str(e)}]
            }

    kernel["register_capability"]("fetch_inbox", fetch_inbox)
    kernel["register_capability"]("read_email", read_email)
    kernel["log"]("Hyper-Mail: Capabilities registered.")
