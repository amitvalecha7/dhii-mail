Dhii Dynamic Interface — Complete UI Specification
Protocol Runtime Design Document (v2.0)
Status: FROZEN
Derived from: Dynamic Interface 3.0 + SPEC.md v1.2 + Chunk Mapping v1.0
Audience: Designers, Frontend Engineers, AI Coding Agents, Orchestrator Engineers

Table of Contents
Design Philosophy (Protocol-Aligned)
Authority & Boundary Model
App Shell Contract
Layout Specification
A2UI Chunk Type Taxonomy
Orchestrator Output → UI Chunk Mapping
Intent Dock Specification (Left Ribbon)
Streaming Canvas Specification
Composer Bar Specification (Prompt Bar)
UI State Machine
Multi-Tenant UI Behavior
Design Tokens
Responsive Behavior
User Onboarding Flow (Chat-Only, Protocol-Driven)
Error States & Graceful Degradation
Forbidden Implementation Patterns
Accessibility
SSE Stream Protocol
File Structure
1. Design Philosophy (Protocol-Aligned)
1.1 Core Principle
The UI is a protocol runtime, not an application.

text

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   The UI renders structured output (A2UI).                      │
│   The UI captures user intent.                                  │
│   The UI exposes transparency and control.                      │
│                                                                 │
│   The UI NEVER:                                                 │
│   • Decides workflows                                           │
│   • Mutates domain state                                        │
│   • Bypasses orchestration                                      │
│   • Infers tenant or permission context                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
1.2 Design Intent vs. Protocol Behavior
Aspect	Design Intent (What Users See)	Protocol Behavior (How It Works)
Ribbon	Quick access panel	Intent emission surface
Canvas	Dynamic workspace	A2UI chunk renderer
Prompt	Chat input	Intent capture interface
Cards	Rich UI elements	Protocol-defined chunk types
Navigation	None (single surface)	Intent → Orchestrator → Stream
1.3 Absolute Laws
If any code violates these, it must be deleted or refactored.

#	Law
1	Center canvas renders A2UI chunks only
2	Frontend contains zero business logic
3	Plugins never render UI directly
4	All actions go through the Orchestrator
5	No page-based routing
6	No static dashboards
7	No silent execution
8	User confirmation always wins
9	UI never resolves tenant or role logic
10	UI state is derived, ephemeral, non-authoritative
2. Authority & Boundary Model
2.1 Layer Responsibilities
text

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   USER                                                          │
│   └── Final authority                                           │
│                                                                 │
│   TENANT                                                        │
│   └── Governance & policy boundary                              │
│                                                                 │
│   AI                                                            │
│   └── Authorized reasoning agent (user-scoped, tenant-bound)    │
│                                                                 │
│   ORCHESTRATOR                                                  │
│   └── Decision & coordination authority                         │
│                                                                 │
│   UI                                                            │
│   └── Deterministic renderer + intent capture                   │
│                                                                 │
│   PLUGINS                                                       │
│   └── Delegated capabilities (invisible to UI)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
2.2 Information Flow
text

User Intent (Composer)
        │
        ▼
┌───────────────────┐
│    Orchestrator   │ ← Tenant context, User-Verse, Policies
└─────────┬─────────┘
          │
          ▼
    A2UI Chunks (Stream)
          │
          ▼
┌───────────────────┐
│   UI Runtime      │ ← Renders deterministically
└───────────────────┘
          │
          ▼
    User sees result
          │
          ▼
    User confirms/rejects action
          │
          ▼
    Intent emitted back to Orchestrator
3. App Shell Contract
3.1 Default State (Focus-First)
text

┌──────────────────────────────────────────────────────────────────────────┐
│  TOP BAR                                                                 │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  ⚡ Dhii    │  Workspace ▼  │  Tenant ▼  │  🔍 Search  │  👤  │  ⚙  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                                                                          │
│                                                                          │
│                     CENTER CANVAS (A2UI CHUNKS)                          │
│                                                                          │
│                                                                          │
│                                                                          │
│                                                                          │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    INLINE COMPOSER                                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│  BOTTOM DOCK                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  [Plugins] [Tools] [Integrations] [Rules] [Saved] [Settings]       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
Key Rule: The UI displays tenant context but never interprets it.

3.2 Alternative Layout (Left Dock)
Based on original design preference, left-docked intent panel is also valid:

text

┌──────────────────────────────────────────────────────────────────────────┐
│  TOP BAR (Workspace · Tenant · Search · User · Settings)                 │
├─────────────────┬────────────────────────────────────────────────────────┤
│                 │                                                        │
│  INTENT DOCK    │              CENTER CANVAS                             │
│  (Left Panel)   │              (A2UI Chunks)                             │
│                 │                                                        │
│  • Emits        │                                                        │
│    intents      │                                                        │
│  • Never        │                                                        │
│    navigates    │                                                        │
│                 │                                                        │
│                 │                                                        │
│                 ├────────────────────────────────────────────────────────┤
│                 │  COMPOSER BAR (Intent Capture)                         │
└─────────────────┴────────────────────────────────────────────────────────┘
Both layouts are valid. Behavior is identical.

4. Layout Specification
4.1 Dimension Specifications
Element	Desktop	Tablet	Mobile
Top Bar Height	56px	56px	56px
Intent Dock Width	260px	72px (icons)	0 (Bottom Dock)
Composer Height	72px	72px	64px
Bottom Dock Height	56px	56px	64px
Canvas Padding	32px	24px	16px
Max Canvas Content	1200px	100%	100%
4.2 Z-Index Hierarchy
text

Top Bar:          z-index: 100
Bottom Dock:      z-index: 100
Composer:         z-index: 90
Intent Dock:      z-index: 80
Canvas Content:   z-index: 1
Skeleton/Shimmer: z-index: 2
Tooltips:         z-index: 200
Toasts:           z-index: 300
4.3 Runtime Interpretation Rules
Zone	Visual Purpose	Protocol Behavior
TOP BAR	System state display	Never executes logic
INTENT DOCK	Quick access surface	Emits intents only, never navigates
CENTER CANVAS	Dynamic workspace	Renders A2UI stream only
COMPOSER	Chat input	Captures intent, does not trigger direct actions
BOTTOM DOCK	Tool access	Emits intents only
Critical: The layout is static; the content is fully dynamic.

5. A2UI Chunk Type Taxonomy
5.1 Allowed Chunk Types
Only the following chunk types may be rendered. Any unknown chunk → render ErrorCard.

Informational Chunks
Chunk Type	Purpose	Orchestrator Intent
TextBlock	Conversational text, explanations	explain, summarize, reason
MarkdownBlock	Rich formatted text	explain, document
Data Display Chunks
Chunk Type	Purpose	Orchestrator Intent
AggregatedCard	Multi-source insights (dashboard replacement)	overview, status, insights
DataTable	Tabular data	list, show, browse
ListCard	Vertical list of items	list, enumerate
StatCard	Single metric display	metric, count, measure
ChartCard	Visualizations	visualize, compare, trend
CalendarCard	Date/event display	schedule, events
ContextCard	Plugin-backed enrichment	enrich, correlate
Interactive Chunks
Chunk Type	Purpose	Orchestrator Intent
EditorCard	Editable content (forms without forms)	draft, edit, modify
ActionGroup	Action proposals	suggest_action, recommend
ConfirmationCard	Human-in-the-loop safety	confirm, approve, authorize
ClarificationCard	Ambiguity resolution	clarify, disambiguate
System Chunks
Chunk Type	Purpose	Orchestrator Intent
SkeletonCard	Loading placeholder	(optimistic UI)
ErrorCard	Error state	error, failure
EmptyCard	Empty state	no_results
Configuration Chunks (Streamed to Canvas)
Chunk Type	Purpose	Orchestrator Intent
ConfigCard	Settings display/edit	configure, setup
IntegrationCard	Integration setup	connect, authenticate
RuleCard	Rule display/edit	rule, constraint
5.2 Chunk JSON Schema (Envelope)
Every orchestrator response conforms to:

JSON

{
  "request_id": "uuid",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "state": "STREAMING | WAITING_FOR_CONFIRMATION | COMPLETED | ERROR",
  "explanation": "optional natural language",
  "chunks": [
    { "...ordered UI chunks..." }
  ]
}
Rules:

chunks order is authoritative
UI must render in order
UI must not reorder, merge, or drop chunks
UI must not infer missing chunks
5.3 Individual Chunk Schemas
TextBlock
JSON

{
  "type": "TextBlock",
  "chunk_id": "uuid",
  "content": "Here is a summary of today's priority items.",
  "tone": "neutral | advisory | warning",
  "collapsible": true
}
UI Behavior:

Render as conversational text
Collapsible after completion
No actions allowed within chunk
AggregatedCard (Dashboard Replacement)
JSON

{
  "type": "AggregatedCard",
  "chunk_id": "uuid",
  "title": "Today's Focus Areas",
  "sources": ["email", "tasks", "calendar"],
  "items": [
    { 
      "label": "Urgent Emails", 
      "value": 3, 
      "trend": { "direction": "up", "value": "2" },
      "source_plugin": "email",
      "action_intent": "show_urgent_emails"
    },
    { 
      "label": "Overdue Tasks", 
      "value": 2,
      "source_plugin": "tasks",
      "action_intent": "show_overdue_tasks"
    }
  ],
  "importance": 0.9
}
UI Behavior:

Replaces static dashboards
Renders as a single unified card
Supports partial rendering if some sources fail
Clicking item emits action_intent
DataTable
JSON

{
  "type": "DataTable",
  "chunk_id": "uuid",
  "title": "Recent Emails",
  "columns": [
    { "key": "sender", "label": "Sender", "sortable": true },
    { "key": "subject", "label": "Subject" },
    { "key": "priority", "label": "Priority" }
  ],
  "rows": [
    { "id": "row-1", "sender": "John", "subject": "Invoice follow-up", "priority": "High" }
  ],
  "selectable": true,
  "selection_intent": "select_email",
  "pagination": { "page": 1, "total_pages": 5 }
}
UI Behavior:

Read-only by default
Selection emits intent events
No inline mutation unless accompanied by EditorCard
StatCard
JSON

{
  "type": "StatCard",
  "chunk_id": "uuid",
  "title": "Total Revenue",
  "value": "$1.2M",
  "trend": { "direction": "up", "value": "12%" },
  "icon": "dollar-sign",
  "source_plugin": "crm",
  "importance": 0.8
}
EditorCard
JSON

{
  "type": "EditorCard",
  "chunk_id": "uuid",
  "title": "Draft Reply",
  "entity": "email_reply",
  "entity_id": "email-123",
  "content": "Dear John,\n\nThank you for your email...",
  "editable": true,
  "field_type": "richtext | plaintext | structured",
  "max_length": 5000,
  "submit_intent": "finalize_draft"
}
UI Behavior:

Inline editing only
Changes are local until confirmation
No auto-save to backend
Emits submit_intent when user finalizes
ActionGroup
JSON

{
  "type": "ActionGroup",
  "chunk_id": "uuid",
  "context": "email_reply",
  "actions": [
    {
      "id": "send_email",
      "label": "Send Reply",
      "intent": "execute_send_email",
      "risk": "medium",
      "style": "primary"
    },
    {
      "id": "save_draft",
      "label": "Save Draft",
      "intent": "execute_save_draft",
      "risk": "low",
      "style": "secondary"
    },
    {
      "id": "discard",
      "label": "Discard",
      "intent": "execute_discard",
      "risk": "low",
      "style": "ghost"
    }
  ]
}
UI Behavior:

No action executed automatically
Clicking emits corresponding intent
Risk indicator must be shown
High-risk actions require ConfirmationCard
ConfirmationCard
JSON

{
  "type": "ConfirmationCard",
  "chunk_id": "uuid",
  "message": "Send this email to John?",
  "context_summary": "Re: Invoice follow-up - 3 paragraphs, 1 attachment",
  "action_id": "send_email",
  "confirm_intent": "confirm_send_email",
  "cancel_intent": "cancel_send_email",
  "risk": "medium",
  "timeout_seconds": null
}
UI Behavior:

Blocks further execution
Requires explicit user confirmation
Cannot be auto-accepted
Must show what is being confirmed
ClarificationCard
JSON

{
  "type": "ClarificationCard",
  "chunk_id": "uuid",
  "message": "Which email do you want to reply to?",
  "context": {
    "original_intent": "reply_to_email",
    "missing_params": ["email_id"]
  },
  "options": [
    { "label": "Invoice follow-up from John", "value": "email-123" },
    { "label": "Meeting request from Sarah", "value": "email-456" }
  ],
  "allow_free_input": true,
  "input_placeholder": "Or describe the email...",
  "selection_intent": "clarify_email_selection"
}
UI Behavior:

Must halt execution flow
User selection emits new intent
No fallback guessing
Free input allowed if specified
ContextCard
JSON

{
  "type": "ContextCard",
  "chunk_id": "uuid",
  "title": "Contact Context",
  "source_plugin": "crm",
  "summary": "John is a key client with an open deal worth $50K.",
  "details": [
    { "label": "Company", "value": "Acme Corp" },
    { "label": "Deal Stage", "value": "Negotiation" },
    { "label": "Last Contact", "value": "2 days ago" }
  ],
  "collapsible": true,
  "expanded": false
}
UI Behavior:

Displays provenance (source_plugin)
Collapsible
Read-only
Provides context for user decisions
ConfigCard
JSON

{
  "type": "ConfigCard",
  "chunk_id": "uuid",
  "title": "Email SMTP Configuration",
  "section": "integrations.email.smtp",
  "fields": [
    { 
      "key": "host", 
      "label": "SMTP Host", 
      "type": "text", 
      "value": "smtp.gmail.com",
      "required": true
    },
    { 
      "key": "port", 
      "label": "Port", 
      "type": "number", 
      "value": 587,
      "required": true
    },
    { 
      "key": "username", 
      "label": "Username", 
      "type": "email", 
      "value": "user@company.com",
      "required": true
    },
    { 
      "key": "password", 
      "label": "App Password", 
      "type": "password", 
      "value": null,
      "required": true,
      "placeholder": "Enter app password"
    }
  ],
  "save_intent": "save_smtp_config",
  "test_intent": "test_smtp_config",
  "cancel_intent": "cancel_config"
}
UI Behavior:

Renders as form-like card
Changes are local until explicit save
Save emits save_intent to Orchestrator
Orchestrator confirms and updates state
IntegrationCard
JSON

{
  "type": "IntegrationCard",
  "chunk_id": "uuid",
  "integration": {
    "id": "google-calendar",
    "name": "Google Calendar",
    "icon": "calendar",
    "status": "not_connected | pending | connected | error",
    "auth_type": "oauth2 | api_key | credentials"
  },
  "description": "Connect your Google Calendar to view and manage events.",
  "permissions": [
    "View your calendar events",
    "Create and modify events",
    "Check availability"
  ],
  "connect_intent": "connect_google_calendar",
  "disconnect_intent": "disconnect_google_calendar",
  "configure_intent": "configure_google_calendar"
}
RuleCard
JSON

{
  "type": "RuleCard",
  "chunk_id": "uuid",
  "rule": {
    "id": "rule-123",
    "name": "No Friday Meetings",
    "scope": "calendar.scheduling",
    "condition_summary": "Block meetings on Fridays",
    "enabled": true,
    "created_at": "2024-01-15T10:00:00Z"
  },
  "editable": true,
  "edit_intent": "edit_rule",
  "toggle_intent": "toggle_rule",
  "delete_intent": "delete_rule"
}
SkeletonCard
JSON

{
  "type": "SkeletonCard",
  "chunk_id": "uuid",
  "predicted_type": "DataTable | StatCard | AggregatedCard",
  "predicted_layout": {
    "rows": 5,
    "columns": 3
  },
  "replaces_with": "chunk-uuid-to-replace"
}
UI Behavior:

Shows shimmer loading animation
Replaced when actual chunk arrives
Maintains layout stability
ErrorCard
JSON

{
  "type": "ErrorCard",
  "chunk_id": "uuid",
  "error": {
    "code": "PLUGIN_TIMEOUT",
    "source_plugin": "salesforce",
    "message": "Salesforce took too long to respond"
  },
  "retry_intent": "retry_salesforce_fetch",
  "skip_intent": "skip_salesforce_data",
  "fallback": {
    "type": "TextBlock",
    "content": "Based on cached data from yesterday, your pipeline was at $1.1M"
  }
}
6. Orchestrator Output → UI Chunk Mapping
6.1 Core Rule
The backend never sends UI. It sends structured intent-aligned output. The UI renders it as protocol-defined chunks.

6.2 Intent → Chunk Mapping Table
Orchestrator Intent	Primary Chunk Type	Secondary Chunks
explain	TextBlock	—
summarize	TextBlock	AggregatedCard
overview	AggregatedCard	StatCard, TextBlock
list	DataTable, ListCard	—
show	DataTable, ContextCard	—
draft	EditorCard	ContextCard
edit	EditorCard	—
suggest_action	ActionGroup	ConfirmationCard
confirm	ConfirmationCard	—
clarify	ClarificationCard	—
configure	ConfigCard	TextBlock
connect	IntegrationCard	TextBlock
rule	RuleCard	TextBlock
error	ErrorCard	TextBlock (fallback)
enrich	ContextCard	—
6.3 State-Driven Rendering Rules
Orchestrator State	UI Behavior
STREAMING	Render chunks as they arrive, show progress
WAITING_FOR_CONFIRMATION	Disable composer execution, focus on ConfirmationCard
COMPLETED	Enable composer, optionally collapse resolved chunks
ERROR	Render ErrorCard, enable retry
UI must mirror, not override, backend state.

7. Intent Dock Specification (Left Ribbon)
7.1 Purpose
The Intent Dock is an intent emission surface, not a navigation panel.

text

┌─────────────────────────────────────────┐
│  ⚡ Dhii                                │ ← Logo (emits: go_home)
├─────────────────────────────────────────┤
│                                         │
│  🏠 Home                                │ ← Emits: clear_canvas
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  INTEGRATIONS                           │
│  ─────────────────────────────────────  │
│  ● Salesforce                        ⚙️ │ ← Emits: open_config(salesforce)
│  ● Google Calendar                   ⚙️ │ ← Emits: open_config(gcal)
│  ⚠️ Email                            ⚙️ │ ← Emits: open_config(email)
│  ○ Slack                              + │ ← Emits: open_integration(slack)
│  + Add Integration                      │ ← Emits: browse_integrations
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  MY RULES                               │
│  ─────────────────────────────────────  │
│  🚫 No Friday meetings                  │ ← Emits: open_rule(rule-123)
│  📧 Daily digest @ 9am                  │ ← Emits: open_rule(rule-456)
│  + Add Rule                             │ ← Emits: create_rule
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  SAVED VIEWS                            │
│  ─────────────────────────────────────  │
│  📊 Sales Dashboard                     │ ← Emits: execute_saved(view-1)
│  📅 Weekly Agenda                       │ ← Emits: execute_saved(view-2)
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  ⚙️ SETTINGS                            │
│  ─────────────────────────────────────  │
│  👤 Profile                             │ ← Emits: open_settings(profile)
│  🔑 API Keys                            │ ← Emits: open_settings(api_keys)
│  🔔 Notifications                       │ ← Emits: open_settings(notif)
│  🎨 Appearance                          │ ← Emits: open_settings(appearance)
│  🛡️ Privacy                             │ ← Emits: open_settings(privacy)
│                                         │
├─────────────────────────────────────────┤
│  📜 History                             │ ← Emits: open_history
│  ❓ Help                                │ ← Emits: open_help
└─────────────────────────────────────────┘
7.2 Intent Emission Protocol
User Action	Emitted Intent	Orchestrator Response
Click Integration	open_config(integration_id)	Streams ConfigCard to Canvas
Click ⚙️ icon	open_config(integration_id)	Same as above
Click + (Add)	browse_integrations	Streams IntegrationCard list
Click Rule	open_rule(rule_id)	Streams editable RuleCard
Click Saved View	execute_saved(view_id)	Re-executes prompt, streams result
Click Settings item	open_settings(section)	Streams ConfigCard for section
Hover on item	(none)	Tooltip shows status/last sync
7.3 Status Indicators
Status	Visual	Meaning
connected	🟢 Green dot	Integration active
not_connected	⚪ Grey dot	Not set up
error	🟠 Orange dot	Needs attention
syncing	🔵 Pulsing dot	Currently syncing
pending	🟡 Yellow dot	Auth in progress
7.4 Collapsed State (Tablet/Mobile)
text

┌────────┐
│  ⚡    │
├────────┤
│  🏠    │
├────────┤
│  🔌    │ ← Integrations (badge shows count)
├────────┤
│  📋    │ ← Rules
├────────┤
│  📊    │ ← Saved Views
├────────┤
│  ⚙️    │ ← Settings
├────────┤
│  📜    │
│  ❓    │
└────────┘
8. Streaming Canvas Specification
8.1 Canvas Principle
The Canvas is the execution surface — it renders what the Orchestrator emits.

The Canvas:

Mirrors orchestrator state
Does not drive orchestrator state
Renders chunks in order
Never reorders or filters chunks
8.2 Canvas States
State: IDLE (Home)
text

┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                                                              │
│                         ⚡                                   │
│                                                              │
│              Good morning, Alex.                             │
│                                                              │
│              What would you like to do?                      │
│                                                              │
│    ┌─────────────────┐  ┌─────────────────┐                  │
│    │ 📊 Show my      │  │ 📅 What's on    │                  │
│    │    overview     │  │    my calendar? │                  │
│    └─────────────────┘  └─────────────────┘                  │
│                                                              │
│    ┌─────────────────┐  ┌─────────────────┐                  │
│    │ ✉️ Summarize    │  │ ⚙️ Configure    │                  │
│    │    my emails    │  │    settings     │                  │
│    └─────────────────┘  └─────────────────┘                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
Note: Quick actions emit intents, not direct commands.

State: STREAMING (Skeleton → Hydration)
text

T=0ms    Intent captured
         ┌────────────────────────────────────────┐
         │  ⏳ Understanding...                    │
         └────────────────────────────────────────┘

T=150ms  Skeleton emitted
         ┌────────────────────────────────────────┐
         │  💬 "Show my overview"                 │
         ├────────────────────────────────────────┤
         │  ┌─────────────┐  ┌─────────────┐      │
         │  │ ░░░░░░░░░░░ │  │ ░░░░░░░░░░░ │      │  ← Shimmer
         │  │ ░░░░░░░     │  │ ░░░░░░░     │      │
         │  └─────────────┘  └─────────────┘      │
         │                                        │
         │  ┌───────────────────────────────────┐ │
         │  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │
         │  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │
         │  └───────────────────────────────────┘ │
         └────────────────────────────────────────┘

T=600ms  First chunk hydrates
         ┌────────────────────────────────────────┐
         │  💬 "Show my overview"                 │
         ├────────────────────────────────────────┤
         │  ┌─────────────┐  ┌─────────────┐      │
         │  │ 📧 Emails   │  │ ░░░░░░░░░░░ │      │  ← Partial
         │  │ 5 unread    │  │ ░░░░░░░     │      │
         │  └─────────────┘  └─────────────┘      │
         └────────────────────────────────────────┘

T=1200ms All chunks rendered
         ┌────────────────────────────────────────┐
         │  💬 "Show my overview"                 │
         ├────────────────────────────────────────┤
         │  ┌─────────────┐  ┌─────────────┐      │
         │  │ 📧 Emails   │  │ 📅 Today    │      │
         │  │ 5 unread    │  │ 3 meetings  │      │
         │  └─────────────┘  └─────────────┘      │
         │                                        │
         │  ┌───────────────────────────────────┐ │
         │  │ 📊 Today's Focus                  │ │
         │  │ • Urgent email from John          │ │
         │  │ • Overdue task: Proposal review   │ │
         │  └───────────────────────────────────┘ │
         └────────────────────────────────────────┘
State: WAITING_FOR_CONFIRMATION
text

┌──────────────────────────────────────────────────────────────┐
│  💬 "Send the reply to John"                                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 📧 Email Preview                                      │   │
│  │                                                       │   │
│  │ To: john@acme.com                                     │   │
│  │ Subject: Re: Invoice follow-up                        │   │
│  │                                                       │   │
│  │ Dear John,                                            │   │
│  │ Thank you for your email. I've reviewed the invoice   │   │
│  │ and everything looks correct...                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ ⚠️ Confirm Action                                     │   │
│  │                                                       │   │
│  │ Send this email to John at john@acme.com?             │   │
│  │                                                       │   │
│  │ Risk: Medium (external recipient)                     │   │
│  │                                                       │   │
│  │     ┌──────────────┐  ┌──────────────────────┐        │   │
│  │     │  Cancel      │  │  ✓ Confirm & Send    │        │   │
│  │     └──────────────┘  └──────────────────────┘        │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  💬 [Composer disabled during confirmation]          [...]   │
└──────────────────────────────────────────────────────────────┘
State: CONFIG (Settings/Integration in Canvas)
When user clicks integration in Intent Dock:

text

┌──────────────────────────────────────────────────────────────┐
│  ⚙️ Configure Email Integration                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  📧 SMTP Configuration                                │   │
│  │                                                       │   │
│  │  SMTP Host                                            │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │ smtp.gmail.com                                  │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  Port                                                 │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │ 587                                             │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  Username                                             │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │ alex@company.com                                │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  App Password                                         │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │ ••••••••••••••••                                │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │      ┌────────────┐  ┌─────────────────────┐          │   │
│  │      │  Cancel    │  │  Save & Test ✓      │          │   │
│  │      └────────────┘  └─────────────────────┘          │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  💡 You can also say: "Set my SMTP host to smtp.gmail.com"   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
State: ERROR (Graceful Degradation)
text

┌──────────────────────────────────────────────────────────────┐
│  💬 "Show my sales pipeline and meetings"                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────────────┐    │
│  │ ⚠️ Salesforce Error │  │ 📅 Today's Meetings         │    │
│  │                     │  │                             │    │
│  │ Connection timeout  │  │ 10:00 AM - Team Standup     │    │
│  │                     │  │ 2:00 PM - Client Call       │    │
│  │ ┌─────────────────┐ │  │ 4:00 PM - Sprint Review     │    │
│  │ │ 🔄 Retry        │ │  │                             │    │
│  │ └─────────────────┘ │  │                             │    │
│  │                     │  │                             │    │
│  │ Using cached data:  │  │                             │    │
│  │ Pipeline ~$1.1M     │  │                             │    │
│  │ (2 hours ago)       │  │                             │    │
│  └─────────────────────┘  └─────────────────────────────┘    │
│                                                              │
│  ℹ️ Partial results shown. Some data unavailable.            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
9. Composer Bar Specification (Prompt Bar)
9.1 Purpose
The Composer captures user intent. It does not execute actions directly.

9.2 Structure
text

┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   ┌────┐  ┌───────────────────────────────────────────────────┐  ┌────┐  │
│   │ 📎 │  │ Ask anything or describe what you need...         │  │ ➤  │  │
│   └────┘  └───────────────────────────────────────────────────┘  └────┘  │
│                                                                          │
│   📌 Quick: [Today's overview] [Unread emails] [Set up email]           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
9.3 States
State	Visual	Behavior
idle	Placeholder visible	Send button disabled
typing	Text visible	Send button enabled
submitting	Spinner in send	Input disabled
streaming	"Stop" button	Input disabled, can abort
waiting_confirmation	Greyed out	Must resolve confirmation first
error	Red border	Error message below
9.4 Intent Emission (Not Direct Action)
text

User types: "Send an email to John about the invoice"
            │
            ▼
Composer emits: {
  "type": "user_intent",
  "raw_text": "Send an email to John about the invoice",
  "timestamp": "ISO-8601"
}
            │
            ▼
Orchestrator receives, processes, streams A2UI response
The Composer never:

Parses intent locally
Triggers plugin calls
Modifies state directly
9.5 Quick Actions
Quick actions either:

Pre-fill the composer (user still confirms)
Emit intent directly (for known safe actions)
JSON

// Pre-fill example
{ "action": "prefill", "text": "Show my calendar for today" }

// Direct intent example
{ "action": "emit_intent", "intent": "show_overview" }
10. UI State Machine
10.1 Core State Machine
text

                    ┌──────────────┐
                    │    IDLE      │
                    │   (Home)     │
                    └──────┬───────┘
                           │ User submits intent
                           ▼
                    ┌──────────────┐
                    │   INTENT     │
                    │  CAPTURED    │
                    └──────┬───────┘
                           │ Orchestrator begins
                           ▼
                    ┌──────────────┐
                    │ ORCHESTRATING│
                    │  (Skeleton)  │
                    └──────┬───────┘
                           │ Chunks arrive
                           ▼
                    ┌──────────────┐
                    │  STREAMING   │ ◄────────┐
                    │  (Hydrating) │          │
                    └──────┬───────┘          │
                           │                  │ More chunks
              ┌────────────┼────────────┐     │
              │            │            │     │
              ▼            ▼            ▼     │
       ┌──────────┐ ┌──────────┐ ┌──────────┐ │
       │ COMPLETE │ │CONFIRMING│ │ CLARIFY  │ │
       └────┬─────┘ └────┬─────┘ └────┬─────┘ │
            │            │            │       │
            │      User confirms      │       │
            │            │            │       │
            │            ▼            │       │
            │     ┌──────────┐        │       │
            │     │ EXECUTING│        │       │
            │     └────┬─────┘        │       │
            │          │              │       │
            └──────────┼──────────────┘       │
                       │                      │
                       ▼                      │
                ┌──────────────┐              │
                │    IDLE      │──────────────┘
                └──────────────┘   (new intent)
10.2 State Definitions
State	Description	UI Behavior
IDLE	No active request	Show home/welcome, composer enabled
INTENT_CAPTURED	Intent sent to orchestrator	Show "thinking" indicator
ORCHESTRATING	Orchestrator processing	Show skeleton placeholders
STREAMING	Chunks arriving	Hydrate skeletons progressively
COMPLETE	All chunks received	Show final state, composer enabled
CONFIRMING	Awaiting user confirmation	Focus on ConfirmationCard, composer disabled
CLARIFYING	Awaiting user clarification	Focus on ClarificationCard, composer enabled
EXECUTING	Confirmed action in progress	Show execution indicator
ERROR	Error occurred	Show ErrorCard, enable retry
11. Multi-Tenant UI Behavior
11.1 Core Principle
The UI displays tenant context but never interprets it.

11.2 Tenant Display
text

┌──────────────────────────────────────────────────────────────────────────┐
│  ⚡ Dhii    │  Personal Workspace ▼  │  Acme Corp ▼  │  🔍  │  👤  │  ⚙  │
└──────────────────────────────────────────────────────────────────────────┘
                        │                      │
                        │                      └── Current Tenant
                        └── Current Workspace
11.3 Tenant Switching
text

┌────────────────────────┐
│  Switch Tenant         │
├────────────────────────┤
│  ✓ Acme Corp           │  ← Current
│    Beta Inc            │
│    Personal            │
├────────────────────────┤
│  + Join Tenant         │
└────────────────────────┘
Behavior:

User clicks tenant selector
UI shows tenant list (from state)
User selects tenant
UI emits: switch_tenant(tenant_id)
Orchestrator validates, reloads context
Canvas clears, new tenant context loads
11.4 What UI Must NOT Do
Forbidden Action	Why
Filter data by tenant	Orchestrator responsibility
Hide actions based on role	Orchestrator responsibility
Infer permissions	Orchestrator responsibility
Cache cross-tenant data	Security violation
Auto-switch tenants	User must explicitly choose
12. Design Tokens
12.1 Colors
Light Mode
CSS

:root {
  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --bg-tertiary: #F3F4F6;
  --bg-canvas: #FFFFFF;
  --bg-dock: #F9FAFB;
  
  /* Text */
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --text-tertiary: #9CA3AF;
  
  /* Borders */
  --border-default: #E5E7EB;
  --border-hover: #D1D5DB;
  --border-focus: #3B82F6;
  
  /* Semantic */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  
  /* Status */
  --status-connected: #10B981;
  --status-disconnected: #9CA3AF;
  --status-error: #F59E0B;
  --status-syncing: #3B82F6;
  
  /* Skeleton */
  --skeleton-base: #E5E7EB;
  --skeleton-shimmer: #F3F4F6;
  
  /* Risk Indicators */
  --risk-low: #10B981;
  --risk-medium: #F59E0B;
  --risk-high: #EF4444;
}
Dark Mode
CSS

[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1F2937;
  --bg-tertiary: #374151;
  --bg-canvas: #111827;
  --bg-dock: #1F2937;
  
  --text-primary: #F9FAFB;
  --text-secondary: #D1D5DB;
  --text-tertiary: #9CA3AF;
  
  --border-default: #374151;
  --border-hover: #4B5563;
  --border-focus: #60A5FA;
}
12.2 Typography
CSS

:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
}
12.3 Spacing & Sizing
CSS

:root {
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}
12.4 Animations
CSS

:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes chunk-enter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.skeleton {
  background: linear-gradient(90deg, var(--skeleton-base) 25%, var(--skeleton-shimmer) 50%, var(--skeleton-base) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.chunk-enter {
  animation: chunk-enter var(--duration-normal) var(--ease-out);
}
13. Responsive Behavior
13.1 Breakpoints
CSS

--bp-sm: 640px;
--bp-md: 768px;
--bp-lg: 1024px;
--bp-xl: 1280px;
13.2 Layout Adaptation
Breakpoint	Intent Dock	Canvas	Composer
Mobile (<640px)	Hidden → Bottom Dock	Full width	Sticky bottom
Tablet (768-1023px)	Collapsed (72px)	Flex remaining	Sticky bottom
Desktop (≥1024px)	Expanded (260px)	Flex remaining	Sticky bottom
13.3 Mobile Layout
text

┌────────────────────────────────────────┐
│  TOP BAR (Tenant · ☰ · 👤)             │
├────────────────────────────────────────┤
│                                        │
│          CENTER CANVAS                 │
│          (Full width)                  │
│                                        │
│                                        │
│                                        │
├────────────────────────────────────────┤
│  COMPOSER                              │
├────────────────────────────────────────┤
│  BOTTOM DOCK                           │
│  [🔌] [📋] [📊] [⚙️] [📜]              │
└────────────────────────────────────────┘
14. User Onboarding Flow (Chat-Only, Protocol-Driven)
14.1 Onboarding Principle
All onboarding is delivered via A2UI chunks. No separate wizard. No static pages.

14.2 Flow Diagram
text

                    ┌──────────────────┐
                    │   FIRST LAUNCH   │
                    │  (Empty tenant)  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   ASK NAME       │
                    │  (TextBlock +    │
                    │   EditorCard)    │
                    └────────┬─────────┘
                             │ Name captured
                             ▼
                    ┌──────────────────┐
                    │  OFFER TOOLS     │
                    │  (ActionGroup)   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ CALENDAR │  │  EMAIL   │  │  SKIP    │
        │  (Int-   │  │  (Config │  │          │
        │  Card)   │  │   Card)  │  │          │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
             └─────────────┼─────────────┘
                           │ Tool connected/skipped
                           ▼
                    ┌──────────────────┐
                    │   SHOW TIPS      │
                    │  (TextBlock +    │
                    │   ActionGroup)   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    COMPLETE      │
                    │   (Normal UI)    │
                    └──────────────────┘
14.3 Step 0: Initial Canvas
Orchestrator emits on first load (empty tenant):

JSON

{
  "state": "STREAMING",
  "chunks": [
    {
      "type": "TextBlock",
      "content": "Welcome to Dhii!\n\nI'm your AI-powered workspace. Let's get you set up.",
      "tone": "neutral"
    },
    {
      "type": "ClarificationCard",
      "message": "What's your name?",
      "allow_free_input": true,
      "input_placeholder": "Type your name...",
      "selection_intent": "onboarding_set_name"
    }
  ]
}
Canvas renders:

text

┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              ⚡ Welcome to Dhii!                             │
│                                                              │
│              I'm your AI-powered workspace.                  │
│              Let's get you set up.                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  What's your name?                                     │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ Type your name...                                │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                      ┌──────────────┐  │  │
│  │                                      │  Continue →  │  │  │
│  │                                      └──────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
14.4 Step 1: Name Captured → Offer Tools
User enters "Alex" → UI emits intent → Orchestrator responds:

JSON

{
  "state": "STREAMING",
  "chunks": [
    {
      "type": "TextBlock",
      "content": "Nice to meet you, Alex! 👋\n\nI can help you manage emails, calendar, tasks, CRM, and more — all from this chat.\n\nLet's connect your first tool.",
      "tone": "neutral"
    },
    {
      "type": "ActionGroup",
      "context": "onboarding_tools",
      "actions": [
        { "id": "gcal", "label": "📅 Google Calendar", "intent": "onboard_connect_gcal", "style": "secondary" },
        { "id": "email", "label": "📧 Email (SMTP)", "intent": "onboard_connect_email", "style": "secondary" },
        { "id": "salesforce", "label": "📊 Salesforce", "intent": "onboard_connect_salesforce", "style": "secondary" },
        { "id": "slack", "label": "💬 Slack", "intent": "onboard_connect_slack", "style": "secondary" },
        { "id": "skip", "label": "⏭ Skip — I'll explore first", "intent": "onboard_skip_tools", "style": "ghost" }
      ]
    }
  ]
}
Canvas renders:

text

┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              Nice to meet you, Alex! 👋                      │
│                                                              │
│              I can help you manage emails, calendar,         │
│              tasks, CRM, and more — all from this chat.      │
│                                                              │
│              Let's connect your first tool.                  │
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐              │
│  │ 📅 Google Calendar │  │ 📧 Email (SMTP)    │              │
│  └────────────────────┘  └────────────────────┘              │
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐              │
│  │ 📊 Salesforce      │  │ 💬 Slack           │              │
│  └────────────────────┘  └────────────────────┘              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ ⏭ Skip — I'll explore first                          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
14.5 Step 2a: User Clicks "Email (SMTP)"
Orchestrator streams:

JSON

{
  "state": "STREAMING",
  "chunks": [
    {
      "type": "TextBlock",
      "content": "Let's set up your email. You can either connect via OAuth or configure SMTP manually.",
      "tone": "neutral"
    },
    {
      "type": "ActionGroup",
      "context": "email_setup_choice",
      "actions": [
        { "id": "gmail_oauth", "label": "Connect via Gmail (Recommended)", "intent": "onboard_gmail_oauth", "style": "primary" },
        { "id": "outlook_oauth", "label": "Connect via Outlook", "intent": "onboard_outlook_oauth", "style": "secondary" },
        { "id": "smtp_manual", "label": "Configure SMTP manually", "intent": "onboard_smtp_manual", "style": "ghost" }
      ]
    }
  ]
}
14.6 Step 2b: User Says SMTP Details in Chat
User types: "Use smtp.gmail.com port 587, my email is alex@startup.io"

Orchestrator detects config intent, responds:

JSON

{
  "state": "WAITING_FOR_CONFIRMATION",
  "chunks": [
    {
      "type": "TextBlock",
      "content": "Got it! Here's what I'll configure:",
      "tone": "neutral"
    },
    {
      "type": "ConfigCard",
      "title": "SMTP Configuration",
      "section": "integrations.email.smtp",
      "fields": [
        { "key": "host", "label": "SMTP Host", "type": "text", "value": "smtp.gmail.com", "editable": true },
        { "key": "port", "label": "Port", "type": "number", "value": 587, "editable": true },
        { "key": "username", "label": "Email", "type": "email", "value": "alex@startup.io", "editable": true },
        { "key": "password", "label": "App Password", "type": "password", "value": null, "required": true, "placeholder": "Required to send emails" }
      ],
      "save_intent": "save_smtp_config",
      "cancel_intent": "cancel_smtp_config"
    },
    {
      "type": "ConfirmationCard",
      "message": "Save this email configuration?",
      "action_id": "save_smtp",
      "confirm_intent": "confirm_save_smtp",
      "cancel_intent": "cancel_save_smtp",
      "risk": "low"
    }
  ]
}
14.7 Step 3: Tools Configured → Show Tips
JSON

{
  "state": "STREAMING",
  "chunks": [
    {
      "type": "TextBlock",
      "content": "Great! You're all set to start, Alex.\n\nHere are a few things you can try:",
      "tone": "neutral"
    },
    {
      "type": "ActionGroup",
      "context": "onboarding_tips",
      "actions": [
        { "id": "tip1", "label": "\"What's on my calendar today?\"", "intent": "execute_calendar_today", "style": "ghost" },
        { "id": "tip2", "label": "\"Summarize my unread emails\"", "intent": "execute_email_summary", "style": "ghost" },
        { "id": "tip3", "label": "\"Never schedule meetings before 10am\"", "intent": "execute_create_rule", "style": "ghost" },
        { "id": "tip4", "label": "\"Add my OpenAI API key: sk-xxx\"", "intent": "execute_add_api_key", "style": "ghost" }
      ]
    },
    {
      "type": "TextBlock",
      "content": "💡 Tip: Click any item in the left panel to configure it, or just ask me in chat!",
      "tone": "advisory",
      "collapsible": true
    },
    {
      "type": "ActionGroup",
      "context": "onboarding_complete",
      "actions": [
        { "id": "done", "label": "✓ Got it, let's go!", "intent": "complete_onboarding", "style": "primary" }
      ]
    }
  ]
}
14.8 Step 4: Onboarding Complete
User clicks "Got it" → Orchestrator marks onboarding complete → Normal IDLE state:

text

┌─────────────────┬────────────────────────────────────────────────────────┐
│                 │                                                        │
│  INTEGRATIONS   │                                                        │
│  ─────────────  │                     ⚡                                 │
│  ● Calendar  ⚙️ │                                                        │
│  ⚠️ Email    ⚙️ │          Good morning, Alex!                           │
│  + Add more     │                                                        │
│                 │          What would you like to do?                    │
│  MY RULES       │                                                        │
│  ─────────────  │  ┌────────────────┐  ┌────────────────┐                │
│  (empty)        │  │ Today's agenda │  │ Check emails   │                │
│                 │  └────────────────┘  └────────────────┘                │
│  SAVED VIEWS    │                                                        │
│  ─────────────  │                                                        │
│  (empty)        │                                                        │
│                 │                                                        │
├─────────────────┴────────────────────────────────────────────────────────┤
│  💬 Ask me anything...                                           [Send]  │
└──────────────────────────────────────────────────────────────────────────┘
14.9 Progressive Feature Discovery
After onboarding, the system continues to educate contextually via inline TextBlock tips:

First Rule Created
JSON

{
  "type": "TextBlock",
  "content": "💡 Did you know? This rule now appears in your sidebar under \"My Rules\". You can click it anytime to edit or disable.",
  "tone": "advisory",
  "collapsible": true
}
First API Key Saved
JSON

{
  "type": "TextBlock",
  "content": "💡 API keys are encrypted and stored securely. You can manage all keys in Settings → API Keys.",
  "tone": "advisory",
  "collapsible": true
}
15. Error States & Graceful Degradation
15.1 Error Handling Principle
Errors are surfaced as ErrorCard chunks. The UI never hides failures.

15.2 Error Types
Error Type	Chunk Response	UI Behavior
Network failure	ErrorCard with retry	Show connection status, retry button
Plugin timeout	ErrorCard with fallback	Show fallback data if available
Validation error	ClarificationCard	Ask user to correct input
Permission denied	ErrorCard	Explain limitation, no retry
Unknown error	ErrorCard	Generic message, support link
15.3 Partial Failure (Graceful Degradation)
When some plugins fail but others succeed:

JSON

{
  "state": "COMPLETED",
  "chunks": [
    {
      "type": "StatCard",
      "title": "Today's Meetings",
      "value": "3",
      "source_plugin": "calendar"
    },
    {
      "type": "ErrorCard",
      "error": {
        "code": "PLUGIN_TIMEOUT",
        "source_plugin": "email",
        "message": "Email service timed out"
      },
      "retry_intent": "retry_email_fetch",
      "fallback": {
        "type": "TextBlock",
        "content": "Last known: 5 unread emails (2 hours ago)"
      }
    }
  ]
}
16. Forbidden Implementation Patterns
16.1 Core Prohibitions
Pattern	Forbidden As	Must Be Implemented As
Dashboard	Static page	AggregatedCard chunk
Page navigation	Router	Intent → Stream
Settings page	Static form	ConfigCard chunk
Plugin UI	Embedded iframe	Plugin-backed chunks
Workflow	UI state machine	Orchestrator states
Auto-action	Silent execution	ConfirmationCard
Form	Static React form	EditorCard/ConfigCard
Permission check	Frontend logic	Orchestrator response
Tenant filter	Frontend query	Orchestrator scope
16.2 Why This Matters
Without these constraints:

❌ Backend engineers overstep into UI
❌ Frontend engineers add business logic
❌ AI agents hallucinate components
❌ Enterprise trust erodes
❌ Multi-tenant security breaks
With these constraints:

✅ Responsibilities are clean
✅ AI output is safe
✅ UI remains evolvable
✅ Plugins stay invisible
✅ Audit trails are complete
17. Accessibility
17.1 Requirements
Requirement	Implementation
Keyboard Navigation	Full tab navigation, arrow keys in lists
Screen Reader	ARIA labels on all chunks
Focus Management	Visible focus rings, logical tab order
Color Contrast	WCAG AA (4.5:1 text)
Motion	Respect prefers-reduced-motion
Text Scaling	Support up to 200% zoom
17.2 ARIA Patterns
HTML

<!-- Chunk container -->
<article 
  role="region" 
  aria-label="Sales Pipeline, $1.2 million"
  data-chunk-id="chunk-123"
>
  ...
</article>

<!-- Action button with risk -->
<button 
  aria-label="Send email to John. Risk level: medium."
  data-risk="medium"
>
  Send Reply
</button>

<!-- Confirmation dialog -->
<div 
  role="alertdialog" 
  aria-modal="true"
  aria-labelledby="confirm-title"
  aria-describedby="confirm-desc"
>
  <h2 id="confirm-title">Confirm Send</h2>
  <p id="confirm-desc">Send this email to john@acme.com?</p>
</div>
17.3 Keyboard Shortcuts
Shortcut	Action
/	Focus composer
Escape	Cancel current action / close overlay
Enter	Submit (single line)
Cmd+Enter	Submit (multi-line)
↑ in composer	Previous history
Tab	Navigate chunks
18. SSE Stream Protocol
18.1 Connection
JavaScript

// Frontend
const eventSource = new EventSource(
  `/api/stream?prompt=${encodeURIComponent(prompt)}&tenant=${tenantId}`
);

// Backend (Python FastAPI)
@app.get("/api/stream")
async def stream(prompt: str, tenant: str, user: User = Depends(get_user)):
    async def event_generator():
        async for chunk in orchestrator.process(prompt, tenant, user):
            yield {
                "event": "chunk",
                "data": json.dumps(chunk.dict())
            }
        yield {"event": "done", "data": "{}"}
    return EventSourceResponse(event_generator())
18.2 Event Types
Event	Payload	UI Action
chunk	A2UI chunk JSON	Render/hydrate chunk
state	State change	Update UI state
done	Empty	Mark stream complete
error	Error details	Render ErrorCard
18.3 Chunk Processing
TypeScript

eventSource.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  
  // Validate chunk type is known
  if (!KNOWN_CHUNK_TYPES.includes(chunk.type)) {
    renderErrorCard({ message: `Unknown chunk type: ${chunk.type}` });
    return;
  }
  
  // Render in order
  appendToCanvas(chunk);
};
19. File Structure
text

src/
├── app/
│   ├── layout.tsx              # Root layout (shell)
│   ├── page.tsx                # Main app entry
│   └── api/
│       └── stream/
│           └── route.ts        # SSE proxy to Python backend
│
├── components/
│   ├── shell/
│   │   ├── TopBar.tsx
│   │   ├── IntentDock.tsx
│   │   ├── Canvas.tsx
│   │   ├── Composer.tsx
│   │   └── BottomDock.tsx
│   │
│   ├── chunks/                 # A2UI chunk renderers
│   │   ├── ChunkResolver.tsx   # Maps type → component
│   │   ├── TextBlock.tsx
│   │   ├── AggregatedCard.tsx
│   │   ├── DataTable.tsx
│   │   ├── StatCard.tsx
│   │   ├── EditorCard.tsx
│   │   ├── ActionGroup.tsx
│   │   ├── ConfirmationCard.tsx
│   │   ├── ClarificationCard.tsx
│   │   ├── ConfigCard.tsx
│   │   ├── IntegrationCard.tsx
│   │   ├── RuleCard.tsx
│   │   ├── ContextCard.tsx
│   │   ├── ErrorCard.tsx
│   │   └── SkeletonCard.tsx
│   │
│   ├── dock/
│   │   ├── DockSection.tsx
│   │   ├── DockItem.tsx
│   │   └── StatusIndicator.tsx
│   │
│   └── primitives/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Badge.tsx
│       └── Tooltip.tsx
│
├── hooks/
│   ├── useStream.ts            # SSE connection manager
│   ├── useIntentEmitter.ts     # Intent dispatch
│   ├── useCanvasState.ts       # Canvas state (derived)
│   └── useOnboarding.ts        # Onboarding state
│
├── stores/
│   ├── appStore.ts             # Zustand - UI state only
│   ├── tenantStore.ts          # Current tenant context
│   └── types.ts
│
├── lib/
│   ├── a2ui-schema.ts          # TypeScript types for chunks
│   ├── intent-types.ts         # Intent type definitions
│   ├── stream-client.ts        # SSE utilities
│   └── utils.ts
│
└── styles/
    ├── tokens.css
    └── globals.css
Appendix: AI Coding Agent Instructions
text

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                    MANDATORY INSTRUCTIONS FOR AI AGENTS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are building a MULTI-TENANT UI RUNTIME, not an application.

MUST:
• Render only validated A2UI JSON chunks
• Emit intents for all user actions
• Display tenant context without interpreting it
• Treat all state as derived and ephemeral

MUST NOT:
• Infer tenant or role logic in the frontend
• Add business logic to React components
• Bypass the Orchestrator for any action
• Create static pages, dashboards, or forms
• Execute actions without user confirmation
• Filter or hide data based on frontend logic

All chunks are rendered in order.
All actions are tenant-scoped and user-approved.
The UI is a protocol host, not an application.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary Checklist
Section	Status
Design Philosophy (Protocol-Aligned)	✅
Authority & Boundary Model	✅
App Shell Contract	✅
Layout Specification	✅
A2UI Chunk Type Taxonomy	✅
Orchestrator → UI Mapping	✅
Intent Dock Specification	✅
Streaming Canvas Specification	✅
Composer Bar Specification	✅
UI State Machine	✅
Multi-Tenant UI Behavior	✅
Design Tokens	✅
Responsive Behavior	✅
User Onboarding (Protocol-Driven)	✅
Error States	✅
Forbidden Patterns	✅
Accessibility	✅
SSE Stream Protocol	✅
File Structure	✅
AI Agent Instructions	✅
Document Status: FROZEN

This specification is ready for:

✅ Designer handoff
✅ Frontend implementation
✅ Backend contract alignment
✅ AI agent development
✅ Enterprise architecture review
