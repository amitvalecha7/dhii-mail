# 🔌 dhii-mail: Plug-and-Play Extension Architecture

## Core Concept
Transform `dhii-mail` from a monolithic app into a **Kernel + Plugins** ecosystem.
**Email**, **Calendar**, and **Meetings** are no longer "core" code—they are just the *first three plugins*.

---

## 🏗️ The "Dhii Kernel"
The Kernel provides the shared infrastructure that all plugins use:
1.  **Identity & Auth**: "Log in once, authorize everywhere." The Kernel handles OAuth tokens for Jira, Slack, Gmail.
2.  **The Agent Bus**: Routes user intents ("Schedule a call") to the correct plugin (Calendar).
3.  **A2UI Renderer**: Displays the UI components sent by plugins.
4.  **Vector Memory**: Shared long-term memory (e.g., "User prefers morning meetings") accessible to authorized plugins.

---

## 🧩 The Plugin Structure
Every extension (e.g., `dhii-jira`, `dhii-slack`) is a standalone folder with this structure:

```text
/plugins/jira/
├── manifest.json       # Capabilities, Permissions, Triggers
├── tools.py            # Python functions exposed to the AI (get_tickets, update_status)
├── ui.py               # A2UI component generators (TicketCard, SprintBoard)
└── handlers.py         # Event listeners (e.g., on_email_received)
```

### 1. The Manifest (`manifest.json`)
Defines what the plugin *is* to the AI.
```json
{
  "id": "com.dhii.jira",
  "name": "Jira Integration",
  "description": "Manage backlog and sprint tickets",
  "intents": ["create_ticket", "check_status", "assign_issue"],
  "permissions": ["read_user_email", "write_tasks"],
  "auth_provider": "atlassian_oauth"
}
```

### 2. "Floating" Integrations (UI Features)
Plugins don't just add backend logic; they add **Contextual UI**.

*   **The "Sidecar" Panel**: When viewing an email about a bug, the *Jira Plugin* lights up and creates a "Related Tickets" card in the side panel automatically (via `on_email_view` trigger).
*   **Action Injection**: The *Zoom Plugin* injects a "Start Meeting" button into the *Calendar Plugin's* event details card.

---

## 🚀 Feature Wishlist for Extensibility

### 1. The "Skill Store" (Settings)
A UI where users toggle capabilities.
*   [x] **Core Mail** (Enabled)
*   [x] **Calendar** (Enabled)
*   [ ] **Jira** (Connect Account)
*   [ ] **WhatsApp** (Connect Account)
*   *Enabling "WhatsApp" instantly teaches the Agent how to "Send a message to John".*

### 2. "Cross-Plugin" Workflows
The Kernel allows plugins to talk to each other via the AI.
*   **User**: "If I get an urgent email from Boss, message me on WhatsApp."
*   **Flow**: `Email Plugin (Trigger)` -> `Kernel (Router)` -> `WhatsApp Plugin (Action)`.

### 3. "Universal Search" Bar
One search bar queries *all* enabled plugins.
*   Searching "Project Alpha" returns:
    *   3 Emails (Mail Plugin)
    *   2 Meetings (Calendar Plugin)
    *   5 Jira Tickets (Jira Plugin)
    *   1 Google Doc (Drive Plugin)

### 4. Zero-Code "Zapier-lite"
Users can define simple rules between plugins using natural language.
*   "When a Jira ticket is marked 'Done', email the reporter." -> The AI compiles this into a logic hook.

---

## 🎨 UI Implications
*   **Unified "Activity Feed"**: Instead of just an Inbox, you have a "Work Feed" merging emails, slack pings, and ticket updates.
*   **Plugin Icons**: Every card clearly shows *source* icon (small Gmail logo, Jira logo) so users know where data comes from.
*   **Consent Modals**: "Jira Plugin wants to access your Calendar. Allow?" (Android-style permissions).

---

## 🛠️ Implementation Strategy (Refining Issue #4)
To achieve this, the **Tool Registry** (Issue #4) must be upgraded to a **Plugin Manager**:
1.  **Scanner**: Scans processes `/plugins` directory on startup.
2.  **Loader**: Dynamically imports `tool.py` and registers functions with the LLM.
3.  **Router**: Maps incoming intents (`@jira`) to the specific plugin module.
