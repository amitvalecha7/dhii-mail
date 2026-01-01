# dhii Mail UI/UX Component & Icon Design

## 1. Visual & Interaction Principles

### 1.1 Visual language

- **Base canvas:**
  - Background: pure or near‑pure white (`#FFFFFF` or `#F9FAFB`).
  - Text: near‑black (`#0B0B0F` / `#111827`).
- **Surfaces (cards, panes):**
  - White with very light border (`#E5E7EB`), subtle shadow.
  - Elevation used sparingly: center canvas blocks stand out; side panes are flatter.
- **Color usage:**
  - Single primary accent color (e.g. deep blue/violet) for actions and focus rings.
  - Error/success colors: muted red/green, low saturation, used minimally.
  - Almost everything else is grayscale.
- **Typography:**
  - One sans‑serif font (e.g. Inter).
  - 3 main text scales: `Title`, `Body`, `Caption`.
  - Truncate aggressively; reveal details on hover/expand.
- **Icon style:**
  - Outline icons, 2px stroke, consistent sizes (16/20/24 px).
  - Line‑based, geometric; avoid busy or filled icons.

### 1.2 Interaction principles

- **Minimal chrome, maximum content.**
  - Ribbon and side panes stay visually light and thin.
  - Center canvas gets visual priority.
- **Always show "why" before "do".**
  - For destructive/large actions, show a short explanation in a confirmation block.
- **One primary action per surface.**
  - Each card/panel has only one visually dominant primary button.
- **Keyboard‑first where possible.**
  - Global `Ctrl+K` / `⌘K` command palette.
  - `↑/↓` to move through lists, `Enter` to open, `Esc` to close panels/dialogs.

---

## 2. Shell / Layout Components

These are the high‑level layout pieces into which A2UI components render.

### 2.1 `AppShell`

- Regions:
  - `Ribbon`
  - `LeftPane`
  - `CenterCanvas`
  - `RightPane`
  - `BottomBar`
- Behavior:
  - Manages pane sizing and responsiveness.
  - Desktop: all regions visible.
  - Tablet: one side pane may collapse into tabs.
  - Mobile: focus on `CenterCanvas` + `BottomBar`; panes become overlays.

### 2.2 `Ribbon`

- Contents:
  - Module switcher: `Mail | Meetings | Tasks | Plugins`.
  - Global search input (icon + minimal placeholder).
  - Right‑aligned cluster: notifications, help, user avatar.
- UX:
  - Minimal height (like a browser tab bar).
  - Module switch snaps panes and center canvas to module presets.

### 2.3 `LeftPane`

- Scrollable vertical column.
- Hosts:
  - Folder/project/navigation lists.
  - Saved views.
  - Plugin anchors.
- UX:
  - Resizable width.
  - Collapsible to icon‑only strip.

### 2.4 `RightPane`

- Scrollable vertical column.
- Hosts:
  - Context stack (chips list).
  - Detail views and insights for the focused object.
- UX:
  - Collapsible; can temporarily slide in when user focuses a context item.

### 2.5 `BottomBar`

- Contains:
  - Chat composer (dominant element).
  - Plugin chips row (left or right aligned).
  - Autonomy toggle (compact control).
- UX:
  - Fixed height at bottom.
  - On mobile, floats above keyboard.

### 2.6 `ResizablePaneHandle`

- Thin grip between panes.
- UX:
  - Hover: handle thickens slightly.
  - Drag to resize adjacent panes.

---

## 3. Primitive Components (Shadcn‑Style)

These are low‑level building blocks, implemented as web components and styled minimally.

### 3.1 `Button`

- Variants: `primary`, `secondary`, `ghost`, `icon`.
- Sizes: `sm`, `md`.
- States: `default`, `hover`, `active`, `disabled`, `loading`.

### 3.2 `Input`

- Single‑line text input.
- Optional left icon.
- Used for search, titles, simple forms.

### 3.3 `Textarea`

- Multiline text input.
- Used in composer and editors.

### 3.4 `Select` / `Combobox`

- Dropdown or searchable selector.
- Used for filters, folder selection, assignees, etc.

### 3.5 `Checkbox` / `Switch`

- For toggles and multi‑select.

### 3.6 `Badge` / `Pill`

- Small label chips.
- Used for labels, statuses, priorities, counts.

### 3.7 `Avatar`

- Circle or rounded square with initial or image.
- Used for users and participants.

### 3.8 `Tooltip`

- Minimal bubble for labels and shortcuts.

### 3.9 `Popover` / `DropdownMenu`

- For overflow actions, filter menus, etc.

### 3.10 `Dialog` / `Modal`

- For confirmations and focused flows.

### 3.11 `Toast` / `InlineBanner`

- For short feedback messages.

### 3.12 `Spinner` / `Skeleton`

- Loading indicators and placeholder skeletons.

---

## 4. Chat & Canvas Components

### 4.1 `ChatThread`

- Center canvas view of the conversation.
- Message structure:
  - Avatar, name, timestamp.
  - Bubble with message text.
  - Optional embedded A2UI blocks (cards, lists, summaries).
- UX:
  - User messages align right; AI messages align left.
  - Long content collapses with “Show more”.

### 4.2 `ChatComposer`

- Located in `BottomBar`.
- Elements:
  - Textarea (1–3 lines auto‑expand).
  - Left: `+` button to attach context (emails, tasks, plugin objects).
  - Right:
    - Mode pill: `Ask | Act | Design`.
    - Send button (icon + label).
- UX:
  - `Enter` to send; `Shift+Enter` for newline.
  - Shows attached context chips above text field.

### 4.3 `A2UICanvasBlock`

- Generic container for orchestrator‑generated UI clusters.
- Structure:
  - Header: icon + title + badges.
  - Body: lists, cards, or rich text.
  - Footer: primary action + optional secondary icon buttons.
- UX:
  - Collapsible.
  - Older blocks auto‑collapse to header‑only view.

### 4.4 `ContextChipsBar`

- Row of small context chips.
- Each chip:
  - Kind label (Email, Meeting, Task, Contact) + name/subject.
- UX:
  - Clicking focuses detail in `RightPane`.
  - `x` removes from context.

---

## 5. Mail Components

### 5.1 `MailFolderList` (LeftPane)

- Sections:
  - System folders: Inbox, Sent, Drafts, Archive, Trash, Spam.
  - Smart views: Important, Needs Reply, AI‑Flagged.
  - Custom folders.
- Row content:
  - Icon + label + optional unread count.
- UX:
  - Selected row: subtle filled background.
  - Hover: `⋯` menu for folder actions.

### 5.2 `MailThreadList` (LeftPane / Center)

- Row content:
  - Sender (bold), subject (truncate), snippet, time.
  - Unread indicator, labels (badges), importance icon.
- UX:
  - Keyboard navigation with `↑/↓` + `Enter`.
  - Hover: inline quick actions (Archive, Mark read, Pin).

### 5.3 `MailThreadView` (CenterCanvas)

- Layout:
  - Header: subject, participant list, main actions.
  - Timeline: stack of `MailMessageCard`.
  - Optional AI summary at top (collapsible).
- Main actions:
  - Reply, Reply All, Forward, More (`⋯`).

### 5.4 `MailMessageCard`

- Content:
  - Header: from, recipients, timestamp.
  - Body: rendered HTML/text in white card.
  - Attachments row as chips/icons.
- UX:
  - Collapsed quoted text with “Show quoted text”.
  - Hover actions: copy, inline reply, open full.

### 5.5 `MailComposer`

- Fields:
  - To, Cc, Bcc (chip inputs).
  - Subject.
  - Body (minimal rich text controls).
- AI integration:
  - Ghost suggestion text.
  - “Use AI suggestion” button.
- UX:
  - Small header pill: “Replying to: [Subject]”.

### 5.6 `MailSmartFilterBar`

- Position: top of thread list or view.
- Elements:
  - Search input with search icon.
  - Filter pills: `Unread`, `Starred`, `Has attachment`, date range, `From: X`.
- UX:
  - Filters appear as removable chips.
  - Changes update list immediately.

---

## 6. Meetings Components

### 6.1 `MeetingList` (LeftPane)

- Row content:
  - Title, time range.
  - Status dot (upcoming, in‑progress, completed).
  - Optional provider icon (Meet, Zoom, etc.).
- UX:
  - Grouped by date: Today, Tomorrow, This week.

### 6.2 `MeetingDetailCard` (Center/Right)

- Shows:
  - Title, organizer, time, link, location.
  - Participants (avatars) and RSVP statuses.
  - Agenda and notes.
- Main actions:
  - Join (if imminent/in progress).
  - Edit, Copy invite.

### 6.3 `MeetingSchedulerGrid`

- Visual time grid with participants and available slots.
- UX:
  - Hover highlights best slots.
  - Selected slot marked with accent border/fill.

### 6.4 `TimeSlotPill`

- Compact suggestion pill, e.g. `Tomorrow 3–3:30 PM`.
- UX:
  - Click to select; selected gets solid background.

---

## 7. Tasks Components

### 7.1 `ProjectList` (LeftPane)

- Rows:
  - Project name.
  - Open tasks count badge.
- UX:
  - Favorite projects pinned to top with star icon.

### 7.2 `TaskBoard` (CenterCanvas)

- Kanban layout:
  - Columns: Backlog, In Progress, Done (minimum set).
- Each column:
  - Header with title + count.
  - `+ Add task` entry.
- UX:
  - Drag & drop to move tasks.
  - Keyboard navigation where possible.

### 7.3 `TaskCard`

- Content:
  - Title, assignee avatar, due date pill.
  - Priority/status badges.
- UX:
  - Double‑click (or Enter) opens `TaskDetailPanel`.
  - Hover quick actions: Mark done, change priority.

### 7.4 `TaskDetailPanel` (RightPane)

- Fields:
  - Title, description, assignee, due date, status, labels.
  - Linked context (emails, meetings, CRM objects).
- UX:
  - Inline editing (no modal).

### 7.5 `TaskQuickAdd`

- Small inline input:
  - Placeholder: “Add task…”
- UX:
  - Press Enter to create task in current column/project.

---

## 8. Plugin / Integration Components

### 8.1 `PluginChip` (BottomBar / RightPane)

- Small pill with plugin icon and short name (e.g. `CRM`, `Jira`).
- UX:
  - Click opens `PluginPanel`.
  - Optionally acts as toggle for “enabled in this session”.

### 8.2 `PluginPanel` (RightPane)

- Header:
  - Plugin name, status dot, settings icon.
- Body sections:
  - Lists, metrics, or activity logs.
- UX:
  - Simple list layouts; avoid heavy visual complexity.

### 8.3 `ContextLinkCard`

- Generic card for external objects:
  - `CRM Contact`, `Deal`, `Ticket`, `Channel`, etc.
- UX:
  - “Open in external app” icon.
  - Button to add/remove from active context.

---

## 9. Icon Inventory

### 9.1 Global / System Icons

- `app-logo`
- `home`
- `search`
- `settings`
- `user`
- `user-circle`
- `bell` (notifications)
- `help-circle`
- `info`
- `chevron-up`
- `chevron-down`
- `chevron-left`
- `chevron-right`
- `more-horizontal` (`⋯`)
- `x` (close)
- `check`
- `arrow-right`
- `arrow-left`
- `refresh`
- `filter`
- `calendar`

### 9.2 Mail Icons

- `inbox`
- `send`
- `paper-plane`
- `reply`
- `reply-all`
- `forward`
- `archive-box`
- `trash`
- `flag`
- `star`
- `mail`
- `attachment`
- `tag`
- `folder`
- `draft`
- `shield-alert` / `spam`
- `mail-open`

### 9.3 Meetings Icons

- `video`
- `video-off`
- `calendar-days`
- `clock`
- `link`
- `repeat`
- `users`
- `pin`
- `location`
- `presentation` (optional)

### 9.4 Tasks Icons

- `check-circle`
- `circle`
- `list-todo`
- `kanban`
- `flag` (priority)
- `alert-triangle` (blocked)
- `timer` (due soon)
- `target` (goal/milestone)

### 9.5 Plugins / Integrations Icons

- `puzzle-piece`
- `plug`
- `database`
- `chart-bar`
- `chart-line`
- `crm` (custom/generic CRM icon)
- `ticket`
- `message-circle`
- `hash` (channel)
- `phone`
- `cloud`

### 9.6 AI / Context Icons

- `sparkles`
- `wand`
- `brain`
- `shield-check`
- `eye`
- `eye-off`
- `history`

---

This document defines the minimalist UI/UX component set and icon inventory for dhii Mail. Styling tokens (colors, radii, spacing, typography scales) can be layered on top of these definitions, and A2UI schemas can map directly to these components.