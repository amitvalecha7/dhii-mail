# dhii Mail A2UI Workspace Specsheet

## 1. Workspace Overview

**Name (working):** dhii Mail Workspace (A2UI‑Native)

**Core idea:**  
A single **A2UI‑driven workspace** where:

- The **center canvas** is a conversational + dynamic A2UI surface.
- **Left/right panes, ribbon, and bottom bar** provide context, navigation, and plugin controls.
- All domain features (Mail, Meetings, Tasks, Integrations) are expressed as **A2UI components/schemas** the orchestrator emits.
- External systems (CRM, ERP, WhatsApp, etc.) are **plugins** that provide data + actions to the orchestrator, which then decides how/when to surface them via A2UI.

---

## 2. Multi‑Pane Layout Spec

### 2.1 Regions

We define 5 persistent UI regions:

1. **Top Ribbon (R1 – Ribbon)**
2. **Left Pane (R2 – Context & Navigation)**
3. **Center Canvas (R3 – Conversation & A2UI Canvas)**
4. **Right Pane (R4 – Context Stack & Insights)**
5. **Bottom Bar (R5 – Plugins & Autonomy Controls)**

#### R1 – Ribbon

**Purpose:**

- Global module selection (Mail, Meetings, Tasks, Integrations).
- High‑level actions (New Email, New Meeting, New Task, Global Search, Settings).
- Mode toggles (Assist / Recommend / Act) surfaced as autonomy hints.
- Surface **module‑specific ribbon groups** (like Office).

**Key design points:**

- Always visible on desktop; condensed on mobile.
- A2UI can control:
  - Which ribbon groups are visible.
  - What contextual actions are available for the current selection/state.

#### R2 – Left Pane (Context & Navigation)

**Purpose:**

- Stable anchors and navigation for the current module:
  - Mail: folders, smart views, saved searches, pinned threads.
  - Meetings: upcoming list, templates, favorite rooms.
  - Tasks: projects, labels, views.
- Plugin‑provided anchors:
  - CRM accounts, deals, channels (Slack, WhatsApp), Jira projects, etc.

**Behavior:**

- Mostly **list/tree and filter components**.
- Items selected here feed into **GLOBAL CONTEXT** for orchestrator (used at `CONTEXT_RESOLVED` state).
- A2UI can:
  - Add context chips / quick filters.
  - Insert plugin‑scoped sections (e.g. “CRM: Important Accounts”).

#### R3 – Center Canvas (Conversation & A2UI Blocks)

**Purpose:**

- **Primary interaction space**.
- Chat thread + A2UI blocks:
  - Chat messages (user + AI).
  - Rich cards (email threads, meeting proposals, tasks, dashboards).
  - Editors (reply editor, task editor, meeting form).
  - Multi‑step flows (wizards, confirmation sheets).

**Behavior:**

- Everything in this region is **A2UI‑generated** (no arbitrary custom UI).
- Each round trip:
  - User acts (chat or UI action).
  - Orchestrator produces a **stack of A2UI components** for the canvas.
- Canvas can collapse older blocks to keep focus.

#### R4 – Right Pane (Context Stack & Insights)

**Purpose:**

- A **live “context stack”** that shows:
  - What objects are currently in context (emails, meetings, tasks, CRM records).
  - Related insights (summaries, recommendations).
  - Plugin‑specific contextual tools and metrics.

**Behavior:**

- Updated at `CONTEXT_RESOLVED` and `STATE_UPDATED` states.
- Typically shows:
  - Context chips list.
  - Detailed view of the currently focused object.
  - Suggested actions (e.g., “Create follow‑up task”, “Add to CRM”).

#### R5 – Bottom Bar (Plugins & Autonomy)

**Purpose:**

- Central **Chat Composer**.
- Plugin controls:
  - Quickly attach plugin contexts (e.g. “+ CRM Contact”, “+ Jira Issue”).
  - Toggle plugin activation for this session.
- Autonomy settings per session:
  - Assist / Recommend / Act slider.
  - “Ask before every send / schedule / commit” checkboxes.

**Behavior:**

- Chat composer always visible in center; bottom bar extends left/right below panes.
- A2UI can:
  - Add context chips next to composer.
  - Show inline warnings (e.g. “This will send 25 emails”).

### 2.2 Layout Variants & Responsiveness

- **Desktop (≥ 1200px):**
  - All 5 regions visible.
  - Left pane ~260–320px.
  - Right pane ~320–360px.
  - Center canvas fills remaining width.

- **Tablet (768–1199px):**
  - Ribbon condensed; left or right pane collapsible into tabs.
  - Center canvas remains primary.
  - Bottom bar still shows chat + minimal plugin strip.

- **Mobile (< 768px):**
  - Focus on **Center Canvas + Bottom Composer**.
  - Left and right panes become overlays/sheets accessible from icons.
  - Ribbon becomes a top dropdown / segmented control.

---

## 3. A2UI Component Taxonomy (High‑Level)

We group components into:

1. **Foundational / Global Components**
2. **AI & Control Components**
3. **Mail Domain Components**
4. **Meetings Domain Components**
5. **Tasks Domain Components**
6. **Plugin / Integration Components**

Each component is an **A2UI schema type** (e.g. `component: 'mail.thread-list'`) with `props` + `actions`.

---

## 3.1 Foundational / Global Components

These are generic, reusable A2UI building blocks.

### 3.1.1 `layout.workspace`

Top‑level layout for the desktop shell.

**Role:** Orchestrator can produce a single `layout.workspace` that includes sub‑regions.

```json
{
  "component": "layout.workspace",
  "props": {
    "module": "mail",               // mail | meetings | tasks | integrations
    "ribbon": [/* ribbon groups */],
    "leftPane": [/* components for R2 */],
    "centerCanvas": [/* components for R3 */],
    "rightPane": [/* components for R4 */],
    "bottomBar": [/* components for R5 */]
  }
}
```

The renderer is responsible for placing these components in each zone.

### 3.1.2 `surface.card`, `surface.panel`, `surface.section`

- Encapsulate visual containers with glassmorphism styling.
- Used across panes and center canvas.

Key props (shared):

- `title`, `subtitle`, `icon`
- `variant`: `"glass" | "solid" | "borderless"`
- `emphasis`: `"default" | "primary" | "danger" | "info"`

### 3.1.3 `list.basic`, `list.grouped`, `list.grid`

Generic lists / grids for the left and right panes.

Props:

- `items`: array of `{ id, title, subtitle?, icon?, badge?, meta? }`
- `selectionMode`: `"single" | "multi" | "none"`
- `groupBy?`: field name
- `onSelectActionId`: string (intent/action key)

---

## 3.2 AI & Control Components

### 3.2.1 `chat.thread`

Represents the conversation history in the center canvas.

Props:

- `messages`: array of:
  - `{ id, role: "user" | "assistant" | "system", text, timestamp, attachments?, a2uiBlocks? }`
- `threadId`
- `showAvatars`, `compact`

### 3.2.2 `chat.composer`

Lives in the bottom bar (or top of center on mobile).

Props:

- `placeholder`: string
- `sessionId`
- `defaultMode`: `"ask" | "act" | "design"`
- `suggestions`: array of quick prompts.
- `attachedContexts`: array of `contextChip` objects.

Actions:

- `onSubmit` → `execute_intent` (intent = `free_form_request`).
- `onAddContext`, `onRemoveContext`.

### 3.2.3 `control.autonomy-toggle`

Controls autonomy levels.

Props:

- `level`: `"assist" | "recommend" | "act"`
- `showWarnings`: boolean
- `requiresConfirmationFor`: array of `"send_email" | "schedule_meeting" | ...`

Actions:

- `onChange` → `set_autonomy_level`.

### 3.2.4 `context.chips`

Shows the **current context stack** (right pane, sometimes bottom bar).

Props:

- `items`: array of chips:
  - `{ id, type, label, source, pinned, removable }`
- `type` examples: `email_thread`, `meeting`, `task`, `crm_contact`, `slack_channel`.

Actions:

- `onPin`, `onUnpin`, `onRemove`, `onFocus`.

---

## 3.3 Mail Domain Components

### 3.3.1 `mail.folder-list` (Left Pane)

Navigation for mail.

Props:

- `folders`: array:
  - `{ id, name, type: "system" | "user", unreadCount, icon }`
- `smartViews`: array (e.g. “Important”, “Needs Reply”).
- `selectedId`.

Actions:

- `onSelectFolder` → `navigate_mail_folder`.

### 3.3.2 `mail.thread-list` (Left Pane / Center Canvas)

List of email threads.

Props:

- `threads`: array:
  - `{ id, subject, participants, lastMessagePreview, timestamp, unread, tags, importance }`
- `selectedThreadId`
- `viewMode`: `"compact" | "comfortable"`

Actions:

- `onSelectThread` → `open_mail_thread`.
- `onBulkAction` → `bulk_apply_label`, `bulk_archive`, etc.

### 3.3.3 `mail.thread-view` (Center Canvas)

Full view of a selected thread.

Props:

- `threadId`
- `messages`: array of `mail.message-card` props.
- `summary`: optional AI summary string.
- `smartActions`: e.g. “Draft reply”, “Summarize thread”, “Create task”.

Actions:

- `onSmartAction` → `execute_intent` (e.g. `draft_reply`, `summarize_thread`).

### 3.3.4 `mail.message-card`

One message within a thread.

Props:

- `messageId`
- `from`, `to`, `cc`, `bcc`
- `subject`
- `sentAt`
- `bodyHtml` or `bodyText`
- `attachments`: array
- `flags`: `isImportant`, `isRead`, `labels`

Actions:

- `onToggleImportant`, `onMarkRead`, `onOpenAttachment`.

### 3.3.5 `mail.composer`

Email editor (e.g. inside center canvas or as modal block).

Props:

- `draftId`
- `to`, `cc`, `bcc`, `subject`, `body`, `signature`
- `mode`: `"new" | "reply" | "forward"`
- `suggestedContent` (AI drafted body).
- `warnings`: e.g., “This goes to 50 recipients”.

Actions:

- `onSend` → `send_email`.
- `onRequestRewrite` (to AI).
- `onSaveDraft`, `onDiscard`.

### 3.3.6 `mail.smart-filter-bar`

Filters above a thread list or thread view.

Props:

- `searchQuery`
- `filters`: date, from, to, labels, importance.
- `quickFilters`: “Unread”, “Needs reply”, “AI flagged”.

Actions:

- `onChangeFilter` → `update_mail_view`.
- `onSearch` → `search_email`.

---

## 3.4 Meetings Domain Components

### 3.4.1 `meetings.list` (Left Pane)

Props:

- `meetings`: `{ id, title, startTime, endTime, organizer, status, location?, isOnline, provider? }`
- `selectedMeetingId`

Actions:

- `onSelectMeeting` → `open_meeting_detail`.

### 3.4.2 `meetings.detail` (Center Canvas / Right Pane)

Details & actions for a selected meeting.

Props:

- `meetingId`
- `title`, `description`
- `participants`: list with RSVP status.
- `agenda`, `notes`, `recordingLink?`
- `status`: `scheduled`, `in_progress`, `completed`, `canceled`.

Actions:

- `onReschedule`, `onCancel`, `onSendUpdate`.
- `onGenerateSummary`, `onCreateFollowUpTasks`.

### 3.4.3 `meetings.scheduler`

Interactive scheduler block.

Props:

- `proposedTimes`: list of time slots.
- `availabilityGrid`: per participant.
- `durationOptions`
- `constraints`: time zone, working hours.

Actions:

- `onConfirmSlot` → `book_meeting`.
- `onAskAIForBestSlot` → `suggest_best_time`.

### 3.4.4 `meetings.timeline`

Day/week timeline view.

Props:

- `dateRange`
- `events` (meetings) mapped to time slots.
- `highlightedSlot`

Actions:

- `onSelectSlot` → create new meeting at that time.

---

## 3.5 Tasks Domain Components

### 3.5.1 `tasks.project-list` (Left Pane)

Props:

- `projects`: `{ id, name, status, openTasksCount }`
- `selectedProjectId`.

Actions:

- `onSelectProject` → `open_task_board`.

### 3.5.2 `tasks.board` (Center Canvas)

Kanban‑style board.

Props:

- `columns`: `Backlog`, `In Progress`, `Done`, etc.
- `tasks`: each with:
  - `{ id, title, assignee, dueDate, priority, labels, linkedEmails?, linkedMeetings? }`.

Actions:

- `onMoveTask` → `update_task_status`.
- `onOpenTaskDetail`.

### 3.5.3 `tasks.detail`

Task detail panel (center or right).

Props:

- `taskId`
- `title`, `description`, `assignee`, `dueDate`, `status`, `priority`
- `linkedContext`: emails, meetings, CRM entities.

Actions:

- `onUpdateField` → `update_task`.
- `onLinkEmail`, `onLinkMeeting`.

### 3.5.4 `tasks.quick-add`

Inline add component.

Props:

- `placeholder`, `defaultProjectId`.

Action:

- `onCreateTask` → `create_task`.

---

## 3.6 Plugin / Integration Components

Plugins never render arbitrary UI themselves; they provide data/actions the orchestrator maps into these A2UI components.

### 3.6.1 `plugin.context-chips`

Shows plugin‑sourced contexts (e.g. CRM deals, Jira issues, WhatsApp chats).

Props:

- `items`: `{ id, pluginId, type, label, icon, metadata }`.

Actions:

- `onFocus`, `onRemove`.
- `onOpenPluginPanel`.

### 3.6.2 `plugin.panel`

A generic, right/left pane or center block that visualizes plugin data.

Props:

- `pluginId`
- `title`, `icon`
- `sections`: array of:
  - `{ title, items, type: "list" | "metrics" | "timeline" | "activity-log" }`.

Actions:

- Plugin‑specific actions like `log_activity`, `create_contact`, `create_ticket`.

### 3.6.3 Domain‑specific plugin cards

Examples:

- `crm.contact-card`
  - `contactId`, `name`, `company`, `email`, `phone`, `lifecycleStage`.
  - Actions: `log_call`, `add_note`, `create_deal`.

- `pm.ticket-card` (Jira, Linear, etc.)
  - `ticketId`, `title`, `status`, `assignee`, `priority`.
  - Actions: `change_status`, `assign_to_me`.

- `chat.channel-card` (Slack, WhatsApp, Telegram)
  - `channelId`, `name`, `platform`, `lastMessagePreview`.
  - Actions: `open_channel`, `send_message`.

---

## 4. How Orchestrator Uses These Components

### 4.1 State Machine → Layout Mapping

Global states:

- `IDLE`
- `INTENT_CAPTURED`
- `CONTEXT_RESOLVED`
- `AI_PROCESSING`
- `A2UI_RENDERED`
- `USER_DECISION`
- `ACTION_EXECUTED`
- `STATE_UPDATED`

**Example flow: “Summarize my inbox and suggest tasks”**

1. **IDLE**
   - Layout:
     - Left: `mail.folder-list`, `mail.thread-list`.
     - Center: `chat.thread`, last A2UI blocks.
     - Right: `context.chips`.
     - Bottom: `chat.composer`, `control.autonomy-toggle`.

2. **INTENT_CAPTURED**
   - `chat.composer` submitted with user text.
   - Orchestrator logs intent: `summarize_inbox_and_tasks`.

3. **CONTEXT_RESOLVED**
   - Left pane selections (folder = Inbox).
   - Plugin contexts (CRM contact open).
   - Right pane context stack updated with focused email threads & contact.

4. **AI_PROCESSING**
   - Orchestrator queries:
     - Email manager for top N threads.
     - Task manager for open tasks.
     - CRM for related opportunities.
     - LLM for summarization and recommendations.

5. **A2UI_RENDERED**
   - Orchestrator emits a `layout.workspace` with mail module, updated panes, and center canvas cards for summary + suggested tasks.

6. **USER_DECISION**
   - User clicks a suggested action (e.g. `Create follow-up tasks`).
   - Orchestrator transitions to `ACTION_EXECUTED` only after explicit click.

7. **ACTION_EXECUTED**
   - Backend creates tasks, logs plugin activity.

8. **STATE_UPDATED**
   - Right pane context updated with new tasks.
   - Center canvas may show `tasks.board` preview or confirmation card.

---

## 5. Extensibility & Versioning

- **Versioning:**
  - Each A2UI schema component has a `version` field (e.g. `"v1"`).
  - Orchestrator and renderer should tolerate unknown components with graceful fallback (ignore or show minimal text).

  ```json
  {
    "component": "mail.thread-list",
    "version": "v1",
    "props": { /* ... */ }
  }
  ```

- **Plugin extension:**
  - Plugins can declare supported **A2UI component types** in their manifest:
    - e.g. `"a2uiSchemas": ["crm.contact-card", "crm.deal-card"]`.
  - Orchestrator decides **when** to use them; plugin never directly pushes UI.

- **Module growth:**
  - New modules (e.g. “Documents”, “Analytics”) can be added by:
    - Defining new A2UI component families (e.g. `docs.document-card`, `analytics.chart`).
    - Adding corresponding tabs/groups in the Ribbon.
