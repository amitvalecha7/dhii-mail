# 📧 Email Plugin Design Specification

## 📦 Overview
The **dhii-email** plugin is a self-contained module that provides full email functionality. It is designed to be "dropped in" to the `dhii-mail` Kernel and immediately provide:
1.  **Backend**: SMTP/IMAP handling, Storage, Sending/Receiving.
2.  **UI**: A complete A2UI-based interface (Inbox, Folders, Compose, Detail).
3.  **Agent Skills**: Tools for the AI to "Send email", "Summarize inbox".

---

## 📂 Directory Structure
```text
/plugins/email/
├── manifest.json          # Identity, Routes, Permissions
├── plugin.py              # Main Entry Point (Backend Logic)
├── server.py              # SMTP/IMAP Server Components
├── ui.py                  # A2UI View Generators (The "Frontend" logic)
├── models.py              # Database Models (SQLAlchemy)
└── assets/                # Icons, default templates
```

---

## 📄 1. The Manifest (`manifest.json`)
Defines the plugin's contract with the Kernel.

```json
{
  "id": "com.dhii.email",
  "name": "dhii Core Mail",
  "version": "1.0.0",
  "description": "Full-stack email client and server",
  "entry_point": "plugin:EmailPlugin",
  "permissions": ["network_access", "fs_read", "fs_write"],
  "ui_routes": [
    { "path": "/email/inbox", "view": "inbox_view", "label": "Inbox", "icon": "mail" },
    { "path": "/email/compose", "view": "compose_view", "label": "Compose", "icon": "plus" },
    { "path": "/email/sent", "view": "sent_view", "label": "Sent", "icon": "send" }
  ],
  "agent_tools": [
    "send_email_tool",
    "search_emails_tool",
    "get_unread_summary_tool"
  ]
}
```

---

## 🖥️ 2. UI Generation (`ui.py`)
This module is responsible for returning **A2UI Adjacency List Operations** that render a Gmail-like interface.

### A. The Inbox View (`inbox_view`)
Returns a **3-Pane Layout**:
1.  **Sidebar**: Folders list (Inbox, Sent, Drafts).
2.  **Main**: Recursive List of Email Cards.
3.  **Utility**: Search bar & Quick Filters.

**Generated A2UI Structure (Conceptual):**
```python
def render_inbox(context):
    return [
        Operation.Insert(node=Container(id="email_root", layout="row")),
        # Sidebar
        Operation.Insert(parent="email_root", node=Card(id="sidebar", width="20%")),
        Operation.Insert(parent="sidebar", node=List(items=["Inbox (5)", "Sent", "Drafts"])),
        
        # Main Feed
        Operation.Insert(parent="email_root", node=Container(id="feed", width="80%")),
        Operation.Insert(parent="feed", node=Input(placeholder="Search emails...")),
        # Dynamic Email Cards
        *[
            Operation.Insert(parent="feed", node=EmailRowComponent(
                id=f"msg_{email.id}",
                sender=email.sender,
                subject=email.subject,
                preview=email.preview,
                on_click=Action("navigate", path=f"/email/{email.id}")
            )) for email in get_emails()
        ]
    ]
```

### B. The Compose View (`compose_view`)
A "Floating Modal" or "Full Page" form depending on context.
*   **Smart Features**: Includes "AI Draft" button inside the editor toolbar.

---

## ⚙️ 3. Backend Logic (`plugin.py` & `server.py`)

### The `EmailPlugin` Class
Implements the abstract `PluginBase`.
```python
class EmailPlugin(PluginBase):
    async def on_load(self):
        # 1. Initialize DB tables (if not exist)
        # 2. Start internal SMTP server (aiosmtpd)
        self.server = await start_smtp_server()
        
    async def render(self, view_id, context):
        # Route verification to ui.py
        if view_id == "inbox_view":
            return ui.render_inbox(self.db.get_emails())
            
    async def execute_tool(self, tool_name, params):
        if tool_name == "send_email_tool":
            return self.send_email(**params)
```

### The Integrated Server (`server.py`)
This is what makes it "plug and play". The plugin *contains* the listener.
*   **Input**: Listens on Port 2525 (for internal) or specifically configured ports.
*   **Storage**: Saves incoming bytes directly to the Plugin's SQLite file (`plugins/email/data/mail.db`).
*   **Notification**: Triggers a `kernel.broadcast("email_received")` event so the Agent can say "You've got mail!".

---

## 🔌 4. The "Immediate Working" Magic
1.  **Drop Folder**: User places `email` folder in `plugins/`.
2.  **Kernel Scan**: Kernel sees `manifest.json`.
3.  **Auto-Mount**: 
    *   Kernel adds `/api/a2ui/email/*` routes.
    *   Kernel adds "Inbox" icon to the main `AppShell` sidebar.
4.  **Auto-Start**: `plugin.on_load()` fires, spinning up the SMTP listener.
5.  **Result**: User refreshes page -> "Mail" icon appears -> Clicks it -> Sees Inbox. Zero config required.
