# 🔮 dhii-mail: Unified Product Vision & Specification

> **"The Interface is the Agent"**
> A Plug-and-Play ecosystem where the Agent builds the UI dynamically based on context, powered by a modular Kernel + Plugin architecture.

---

## 🏗️ 1. Architecture: "The Kernel & The Plugins"

### The Concept
dhii-mail is not a monolithic email app. It is a **Conversation Kernel** capable of hosting any "Skill" (Plugin).
*   **Kernel Responsibilities**: Identity, **A2UI Rendering (Official @a2ui/lit)**, Intent Routing, Vector Memory.
*   **Plugins**: Standalone modules (Email, Calendar, Jira, Slack) defined by a `manifest.json`.

### The Plugin Structure
Each extension lives in its own folder and provides:
1.  **Manifest**: Identity, Permissions (`read_email`), Intents (`create_ticket`).
2.  **Tools**: Python functions for the Agent.
3.  **UI Components**: **A2UI Standard Components** (Adjacency List model) via generators.
4.  **Hooks**: Event listeners (e.g., `on_email_view` triggers "Sidecar" search).

---

## 🎨 2. UI/UX: "Liquid Glass"

### Aesthetic
*   **Aesthetic**: **Glassmorphism 2.0**. Frosty, translucent panels floating over a slow-moving "Aurora" background.
*   **Dynamic Light**: Cursor acts as a subtle light source, illuminating borders of nearby cards.
*   **Depth Stacking**:
    *   *Layer 1 (Top)*: Active Task (Opaque, Crisp).
    *   *Layer 2 (Mid)*: Context/Reference (Blurry).
    *   *Layer 3 (Bot)*: Background Stream.

### Core Layout: "Stream vs. Canvas"
1.  **The Stream (Left)**: Continuous chat history with the Agent.
2.  **The Canvas (Right)**: A large persistent surface where the Agent "builds" complex UIs (Calendar Grid, Analytics Board) based on the conversation.
3.  **The Omni-Bar (Bottom)**: Floating input field. "One bar to rule them all."

---

## 🚀 3. Key Feature Sets

### A. Context Cards (Generative UI)
*   **Morning Brief**: A temporary card appearing at 8 AM with today's timeline & top priorities.
*   **Prep Mode**: 5 mins before a meeting, a card floats up with attendee bios and last 3 relevant emails.
*   **Conflict Resolver**: One-click UI to "Time Shift" conflicting meetings.

### B. Smart Actions
*   **Micro-Forms**: Embed forms *inside* emails to collect structured data from recipients.
*   **Live Slices**: Send interactive Calendar snippets instead of text times.

### C. Universal Plugin Integration
*   **Skill Store**: Enable/Disable plugins like "Jira" or "WhatsApp" instantly.
*   **Cross-Plugin Actions**: "If I get a P0 Jira ticket, WhatsApp me."
*   **Unified Search**: Query Email, Calendar, and Jira from one bar.

---

## 👤 4. User Stories by View

### 🏠 View: The Dashboard (Home)
*   **US-1.1**: As a user, I want to see a **"Morning Brief" card** at the start of my day so I know my top 3 priorities without digging through lists.
*   **US-1.2**: As a user, I want the dashboard to **change dynamically** (e.g., show "End of Day Summary" at 5 PM), so the UI matches my mental state.
*   **US-1.3**: As a user, I want to see **mixed content** (1 email, 2 tasks, 1 meeting) in a single "Up Next" feed, so I don't have to switch tabs.

### 📧 View: Email Experience
*   **US-2.1**: As a user, when I open an email about a "Bug", I want the **Jira Plugin** to automatically show related tickets in a **Sidecar Panel**, so I have context.
*   **US-2.2**: As a user, I want to use **"Draft Chips"** (Auto-generated reply options) that appear when I hover over the reply button, so I can respond in 1 second.
*   **US-2.3**: As a user, I want to **"Delegate to Agent"** (e.g., "Reply to John and book a time"), so the Agent handles the negotiation loop for me.

### 📅 View: Calendar & Meetings
*   **US-3.1**: As a user, I want to build an agenda by **talking to the Canvas** ("Add 15 mins for Q&A"), so I don't have to fill out complex forms.
*   **US-3.2**: As a user, during a video call, I want a **"Ghost Scribe"** to transcribe action items and float them as "Save as Task?" buttons.
*   **US-3.3**: As a user, I want to resolve conflicts by dragging a meeting to a **"Suggest New Time" drop zone**, which auto-emails participants.

### 🧩 View: Settings & Skill Store
*   **US-4.1**: As a user, I want to **enable/disable plugins** (e.g., toggle "Jira") and see the UI adapt instantly (e.g., Jira icon appears in Nav), so I control complexity.
*   **US-4.2**: As a user, I want to configure **Cross-Plugin Rules** ("When Slack status is 'Busy', block my Calendar"), so my tools work together.
*   **US-4.3**: As a user, I want to see a **Permission Audit** ("Jira accessed your Calendar 5 times"), so I trust the agent.
