import subprocess
import time
import json

# Define the issues to create
issues = [
    # --- Core OS ---
    {
        "title": "Plugin: Hyper-Mail (Unified Inbox)",
        "body": """
### 🚀 User Stories
- [ ] **US-1.1**: Unified feed (Email + WhatsApp + Slack) in time-order.
- [ ] **US-1.2**: High-priority items appear physically larger (Smart Triage).
- [ ] **US-1.3**: Snooze items to specific geolocation.
- [ ] **US-1.4**: Bulk-select by "Topic" (e.g., Archive all receipts).
- [ ] **US-1.5**: "TL;DR" summary on card instead of snippet.

### 🖼️ Technical Spec (A2UI)
- **Component**: `feed_container` (Virtual Scroll)
- **Component**: `communication_card` (Props: priority_score, sentiment_color)
""",
        "labels": ["area/plugin", "priority/p0", "layer/core"]
    },
    {
        "title": "Plugin: Chrono-Calendar",
        "body": """
### 🚀 User Stories
- [ ] **US-1.6**: Natural Language Scheduling ("Book 30 mins with Amit").
- [ ] **US-1.7**: "Time Rail" UI at top of AppShell.
- [ ] **US-1.8**: Drag-and-drop Email to Time Rail to book.

### 🖼️ Technical Spec (A2UI)
- **Component**: `time_rail_widget`
- **Integration**: Two-way sync with Google/Outlook.
""",
        "labels": ["area/plugin", "priority/p1", "layer/core"]
    },
    {
        "title": "Plugin: Holo-Meet",
        "body": """
### 🚀 User Stories
- [ ] **US-1.9**: Native Jitsi Server integration (Self-hosted).
- [ ] **US-1.10**: Adapter for Zoom/Teams links.
- [ ] **US-1.11**: Picture-in-Picture "Bubble" mode.

### 🖼️ Technical Spec (A2UI)
- **Component**: `video_bubble_overlay`
""",
        "labels": ["area/plugin", "priority/p1", "layer/core"]
    },

    # --- Communication Bridges ---
    {
        "title": "Plugin: WhatsApp/Telegram Bridge",
        "body": """
### 🚀 User Stories
- [ ] **US-2.1**: QR Code Auth Flow for WhatsApp Web.
- [ ] **US-2.2**: Reply to chats using full keyboard + AI tools.
- [ ] **US-2.3**: Green/Blue accent colors for threads in Unified Inbox.

### 🖼️ Technical Spec (A2UI)
- **Component**: `qr_auth_modal`
- **Library**: `whatsapp-web.js`
""",
        "labels": ["area/plugin", "priority/p1", "layer/bridge"]
    },
    {
        "title": "Plugin: Enterprise-Chat (Teams/Slack)",
        "body": """
### 🚀 User Stories
- [ ] **US-2.4**: Sync Status (Busy in Calendar = Busy in Teams).
- [ ] **US-2.5**: Slash Command Handler (`/deskai`).

### 🖼️ Technical Spec (A2UI)
- **Integration**: Webhook / Bot API integration.
""",
        "labels": ["area/plugin", "priority/p2", "layer/bridge"]
    },

    # --- Business Suite ---
    {
        "title": "Plugin: Deal-Flow (CRM)",
        "body": """
### 🚀 User Stories
- [ ] **US-4.1**: Auto-inject "Lead Card" for new prospect emails.
- [ ] **US-4.2**: Drag-and-Drop Kanban for Deal Stages.
- [ ] **US-4.3**: "Relationship Health Score" visualization.

### 🖼️ Technical Spec (A2UI)
- **Component**: `crm_sidebar_widget`
- **Component**: `pipeline_kanban`
""",
        "labels": ["area/plugin", "priority/p1", "layer/business"]
    },
    {
        "title": "Plugin: Finance-Flow",
        "body": """
### 🚀 User Stories
- [ ] **US-4.6**: Generate PDF Invoice from "Won" Deal.
- [ ] **US-4.7**: Live Preview Split-Pane for Invoices.
- [ ] **US-4.8**: Auto-chase overdue payments.

### 🖼️ Technical Spec (A2UI)
- **Component**: `invoice_builder`
- **Component**: `live_pdf_preview` (IFrame)
""",
        "labels": ["area/plugin", "priority/p2", "layer/business"]
    },
    {
        "title": "Plugin: Project-Nexus",
        "body": """
### 🚀 User Stories
- [ ] **US-4.10**: Assign Tasks to "Dhii-Connect" network.
- [ ] **US-4.11**: Link Task to source Email.
- [ ] **US-4.12**: Visual Boards (Kanban/Timeline).

### 🖼️ Technical Spec (A2UI)
- **Component**: `project_board_view`
""",
        "labels": ["area/plugin", "priority/p2", "layer/business"]
    },
    {
        "title": "Plugin: Legal-Stack",
        "body": """
### 🚀 User Stories
- [ ] **US-4.13**: Detect PDFs needing signature.
- [ ] **US-4.14**: Docu-Flow Overlay for e-signing.
- [ ] **US-4.15**: AI Smart-Reader for contract risks.

### 🖼️ Technical Spec (A2UI)
- **Component**: `docu_sign_overlay`
- **Component**: `contract_analysis_panel`
""",
        "labels": ["area/plugin", "priority/p2", "layer/business"]
    },

    # --- Social OS ---
    {
        "title": "Plugin: Dhii-Connect (Internal Network)",
        "body": """
### 🚀 User Stories
- [ ] **US-3.1**: Connection Request System.
- [ ] **US-3.2**: "Inner Circle" Trust Graph.
- [ ] **US-3.3**: User Profile Cards on hover.

### 🖼️ Technical Spec (A2UI)
- **Component**: `connection_request_card`
- **Component**: `user_profile_popover`
""",
        "labels": ["area/plugin", "priority/p2", "layer/social"]
    },
    {
        "title": "Plugin: Sync-Chat (Internal)",
        "body": """
### 🚀 User Stories
- [ ] **US-3.4**: Encrypted Internal Instant Messaging.
- [ ] **US-3.5**: Drag Email/Task to Chat to share context.
- [ ] **US-3.6**: Create temporary "War Rooms".

### 🖼️ Technical Spec (A2UI)
- **Component**: `chat_thread_view`
- **Feature**: Context Embedding
""",
        "labels": ["area/plugin", "priority/p2", "layer/social"]
    },

    # --- Creative Studio ---
    {
        "title": "Plugin: Writer's Room",
        "body": """
### 🚀 User Stories
- [ ] **US-5.1**: AI Smart-Compose (Tab-to-Complete).
- [ ] **US-5.2**: Tone Slider (Casual <-> Formal).
- [ ] **US-5.3**: Newsletter-Bot (Auto-Compile).

### 🖼️ Technical Spec (A2UI)
- **Component**: `ghost_overlay`
- **Component**: `tone_control_panel`
""",
        "labels": ["area/plugin", "priority/p2", "layer/creative"]
    },
    {
        "title": "Plugin: Pixel-Studio",
        "body": """
### 🚀 User Stories
- [ ] **US-5.5**: Text-to-Image Generation Pane.
- [ ] **US-5.6**: Drag generated image into Email.

### 🖼️ Technical Spec (A2UI)
- **Component**: `flux_image_generator`
""",
        "labels": ["area/plugin", "priority/p3", "layer/creative"]
    },
    {
        "title": "Plugin: Brand-Identity Manager",
        "body": """
### 🚀 User Stories
- [ ] **US-5.7**: Enforce Brand Voice/Fonts.
- [ ] **US-5.8**: Asset Sync across documents.

### 🖼️ Technical Spec (A2UI)
- **Component**: `brand_guard_settings`
""",
        "labels": ["area/plugin", "priority/p3", "layer/creative"]
    },
    
    # --- Dev ---
    {
        "title": "Plugin: Dev-Hub",
        "body": """
### 🚀 User Stories
- [ ] **US-6.1**: GitHub PR Stream.
- [ ] **US-6.2**: In-Flow Code Review.

### 🖼️ Technical Spec (A2UI)
- **Component**: `code_diff_viewer`
""",
        "labels": ["area/plugin", "priority/p2", "layer/dev"]
    }
]

def create_issue(issue):
    cmd = [
        "gh", "issue", "create",
        "--title", issue["title"],
        "--body", issue["body"]
    ]
    
    for label in issue["labels"]:
        cmd.extend(["--label", label])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Created: {issue['title']}")
        print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {issue['title']}")
        print(e.stderr)
        return False

print(f"🚀 Starting creation of {len(issues)} Plugin Issues...")

success_count = 0
for issue in issues:
    if create_issue(issue):
        success_count += 1
    # Small sleep to be nice to the API
    time.sleep(2)

print(f"\n✨ Done! Created {success_count}/{len(issues)} issues.")
