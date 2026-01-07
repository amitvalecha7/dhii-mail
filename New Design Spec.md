Excellent. Below is the **clean, final upgrade of your spec to `v1.2`**, with **multi-tenant rules added explicitly**, without breaking or weakening any of the v1.1 principles.

This is written to be:

* **enterprise-sale ready**
* **SOC2 / ISO friendly**
* **AI-coding-agent safe**
* **future-proof for B2B, B2B2C, and mixed tenancy**

You can **replace your current `SPEC.md` entirely** with this version.

---

# 📘 SPEC.md

## Dhii — UI Runtime & Platform Specification (v1.2)

**Status:** FROZEN
**Audience:** Engineers, AI Coding Agents, Architects
**Scope:** UI Runtime, Interaction Model, Security, Data & Multi-Tenant Model
**Applies to:** `dhii-mail` and all current/future Dhii modules

> **IMPORTANT**
> This document encodes both **rules and intent**.
> Any deviation requires explicit architectural review.

---

## 0. Purpose of This Document

Dhii is **not a traditional SaaS application**.

It is a **multi-tenant, user-centric, AI-orchestrated operating layer** where:

* AI reasons across a **User-Verse**
* Humans remain the final authority
* Tenants provide governance boundaries
* The Orchestrator coordinates decisions
* The UI renders protocol output deterministically
* Plugins act as delegated capabilities

This specification exists to:

* prevent architectural drift
* enable safe AI-driven development
* support enterprise and regulated environments
* give AI coding agents unambiguous constraints

---

## 1. Core Philosophy (NON-NEGOTIABLE)

### 1.1 UI Runtime Principle

> The frontend is a **protocol runtime**, not an application.

The UI:

* renders structured output (A2UI)
* captures user intent
* exposes transparency and control

The UI **never**:

* decides workflows
* mutates domain state
* bypasses orchestration
* infers tenant or permission context

---

### 1.2 Authority & Boundary Model

| Layer        | Responsibility                           |
| ------------ | ---------------------------------------- |
| User         | Final authority                          |
| Tenant       | Governance & policy boundary             |
| AI           | Authorized reasoning agent (user-scoped) |
| Orchestrator | Decision & coordination authority        |
| UI           | Deterministic renderer                   |
| Plugins      | Delegated capabilities                   |

---

### 1.3 Absolute Laws

If any code violates these, it **must be deleted or refactored**.

1. Center canvas renders **A2UI only**
2. Frontend contains **zero business logic**
3. Plugins never render UI
4. All actions go through the Orchestrator
5. No page-based routing
6. No static dashboards
7. No silent execution
8. User confirmation always wins
9. UI never resolves tenant or role logic

---

## 2. App Shell Contract (v1.2)

*(unchanged structurally from v1.1, tenant-agnostic by design)*

### 2.1 Default State (Focus-First)

```
┌──────────────────────────────────────────────┐
│ Top Bar (Workspace · Tenant · Search · ⚙)   │
├──────────────────────────────────────────────┤
│                                              │
│           CENTER CANVAS (A2UI)                │
│           + Inline Composer                   │
│                                              │
│                                              │
├──────────────────────────────────────────────┤
│ Bottom Dock (Plugins · Tools · Injectors)    │
└──────────────────────────────────────────────┘
```

**Key rule:**
The UI **displays** tenant context but **never interprets it**.

---

## 3. Multi-Tenant Model (NEW — v1.2)

### 3.1 Tenant Definition

A **Tenant** is:

* an organizational boundary
* a policy enforcement unit
* a data isolation domain

Examples:

* Company
* Department
* Client workspace
* Project-based tenant

---

### 3.2 Tenant → User → User-Verse

```
Tenant
 ├── Users
 │    ├── User-Verse
 │    │    ├── Emails
 │    │    ├── Tasks
 │    │    ├── Meetings
 │    │    ├── Plugin Data
 │    │    └── AI Artifacts
```

Rules:

* A user may belong to multiple tenants
* Each tenant has **isolated policy & data**
* User-Verse is **scoped per tenant**

---

### 3.3 Tenant Context Resolution

Tenant resolution happens **only in the Orchestrator**.

UI responsibilities:

* Display current tenant
* Allow tenant switching (explicit)
* Reflect policy outcomes

UI **must not**:

* infer permissions
* filter data
* hide actions proactively

---

## 4. Role & Permission Model (Tenant-Scoped)

### 4.1 Roles (Examples)

Roles are **tenant-defined**, not hard-coded.

Common patterns:

* Owner
* Admin
* Member
* Viewer
* External Collaborator

---

### 4.2 Permission Enforcement

Permissions are enforced at:

* Orchestrator
* Plugin boundary
* Data access layer

Never at:

* React component level
* UI state level

---

## 5. User-Verse Security Model (Tenant-Aware)

### 5.1 Core Principle

> **User-Verse exists within a Tenant boundary.**

AI, plugins, and actions operate within:

```
(User + Tenant + Consent)
```

---

### 5.2 Consent Model (Tenant-Scoped)

Users grant consent:

* per plugin
* per capability
* per tenant

AI may:

* reason across domains
* suggest actions
* correlate data

AI may **never**:

* override tenant policy
* cross tenant boundaries
* act without user approval

---

## 6. Cross-User & External Sharing (Tenant-Safe)

### 6.1 Internal Sharing (Same Tenant)

* Role-based access
* Shared objects:

  * tasks
  * summaries
  * conversations
  * AI artifacts

---

### 6.2 External Sharing (Cross-Tenant / Outside Ecosystem)

Supported via **Delegated Access Objects**.

Characteristics:

* Secure, signed links
* Time-bound
* Scope-bound
* Revocable
* Fully auditable

External users:

* do not inherit tenant privileges
* cannot see tenant metadata
* operate in a sandboxed view

---

## 7. Data Isolation Rules (v1.2)

### Enforced Isolation

* Tenant ↔ Tenant (hard boundary)
* User ↔ User (within tenant)
* Plugin ↔ Plugin (capability-scoped)
* External ↔ Internal (delegated only)

### Allowed Correlation

* Cross-plugin correlation within same User-Verse
* AI summarization across domains (with consent)

---

## 8. Forbidden Implementation Patterns

*(With Intent & Approved Replacements)*

*(UNCHANGED from v1.1 — applies per tenant)*

> These restrictions prohibit **frontend-owned, static implementations**,
> not user experiences.

(Sections 8.1 – 8.8 remain identical to v1.1)

---

## 9. Audit, Compliance & Explainability (NEW)

### 9.1 Mandatory Audit Trails

Every tenant must support:

* Who acted
* On what
* When
* Under which tenant
* With what consent
* Via AI or manually

---

### 9.2 Explainable AI (Tenant-Scoped)

For any AI suggestion or action:

* Context used must be visible
* Reasoning must be explainable
* User must be able to trace decision chain

---

## 10. AI Coding Agent Instructions (MANDATORY)

> You are building a **multi-tenant UI runtime**, not an application.
> You must not infer tenant or role logic in the frontend.
> Render only validated A2UI JSON.
> Never embed business logic in React components.
> Never bypass the Orchestrator.
> All actions are tenant-scoped and user-approved.

---

### End of SPEC.md (v1.2)

---

## What v1.2 Gives You (Executive Summary)

With this version you now have:

* ✅ **True multi-tenant isolation**
* ✅ **User-centric AI reasoning**
* ✅ **Enterprise-safe sharing**
* ✅ **Clear audit & compliance posture**
* ✅ **AI-coding-agent-proof constraints**

This spec is now strong enough to:

* sell to enterprises
* pass architecture review boards
* onboard multiple engineering teams
* survive aggressive AI-assisted development

---
###Spec.md (v1.2a)
### Some Fundamental changes in UI
📘 Dhii UI Protocol Runtime Specification
(Derived from Dynamic Interface 3.0 Design Document)

Status: FROZEN
Version: 1.0 (Protocolized)
Derived from: Dynamic Interface 3.0 Design Spec 

Design Document


Audience: Frontend engineers, AI coding agents, orchestrator engineers

0. Purpose of This Specification

This document defines how the existing UI design is rendered as a protocol runtime.

It does not redesign the UI.
It defines how and why the UI behaves the way it does.

Key shift

The Design Document defines what users see

This document defines how that UI is produced, governed, and constrained

1. Core Runtime Philosophy (Overlay on Design)

The Design Philosophy remains intact (Chat-First, Unified Canvas, Stream-Native, etc.) 

Design Document

We add runtime authority rules:

1.1 UI as Protocol Host

The UI is a deterministic renderer of protocol output.

It does not own workflows

It does not decide navigation

It does not infer intent

It does not mutate domain state

It renders what the Orchestrator emits.

1.2 Authority Model (Implicit in Design, Now Explicit)
Layer	Responsibility
User	Final authority
AI	Reasoning + proposal
Orchestrator	Decision & sequencing
UI	Rendering + intent capture
Plugins	Capability execution

This model governs all existing UI flows.

2. Layout Specification → Runtime Interpretation

The Master Layout Grid from the Design Document remains unchanged 

Design Document

.

Runtime Interpretation Rules

HEADER

Displays system state

Never executes logic

LEFT RIBBON

Emits navigation intents

Never navigates directly

MAIN CANVAS

Renders A2UI stream only

PROMPT BAR

Captures intent

Does not trigger direct actions

The layout is static; the content is fully dynamic.

3. Component Library → Protocol Components

All components listed in the Design Document remain valid 

Design Document

.
This section defines protocol constraints for them.

3.1 Canvas Components (Protocol Rules)

For all Canvas components (StatCard, DataTable, ChartCard, FormCard, etc.):

Required

Must be rendered from A2UI JSON

Must be stateless

Must support partial hydration (streaming)

Forbidden

Direct API calls

Internal business logic

Cross-component coordination

3.2 AggregatedCard (Protocol Clarification)

The existing AggregatedCard becomes the official replacement for dashboards.

Protocol guarantees:

Multiple source_plugin allowed

Partial rendering on plugin failure

Importance-based layout allowed

This aligns with the Design’s intent without introducing static dashboards.

4. A2UI JSON Schema → Contract Boundary

The A2UI schema defined in the Design Document is authoritative 

Design Document

.

Protocol Meaning

Every chunk = a UI instruction

Order matters

UI must not reorder

UI must not infer missing chunks

The UI behaves like a browser rendering HTML.

5. Left Ribbon → Intent Emitter (Not Navigation)

The Left Ribbon structure remains unchanged 

Design Document

.

Runtime Semantics
User Action	Runtime Meaning
Click Integration	Emit open_config(integration_id) intent
Click Rule	Emit open_rule(rule_id) intent
Click Saved View	Emit execute_prompt(prompt_id)
Click Settings	Emit open_settings(section)

Ribbon never switches views directly.
The Canvas responds via streamed A2UI.

6. Streaming Canvas → Execution Surface

All Canvas states defined in the Design Document remain intact 

Design Document

.

Runtime Guarantees

Skeletons = optimistic placeholders

Streaming = partial orchestration completion

Completion = orchestrator finished or paused

The Canvas mirrors orchestrator state, it does not drive it.

7. Prompt Bar → Intent Capture Interface

The Prompt Bar remains visually unchanged 

Design Document

.

Protocol Rules

Input → Intent

No implicit execution

Attachments are context, not commands

Quick Actions:

Either pre-fill prompt

Or emit explicit intents

8. Interaction Patterns → State Machine Binding

All interaction patterns map to the same UI state machine:

IDLE
 → INTENT_CAPTURED
 → ORCHESTRATION_RUNNING
 → STREAMING_RENDER
 → USER_CONFIRMATION (optional)
 → ACTION_EXECUTED
 → STATE_UPDATED
 → IDLE


The Design’s flows are views of this state machine.

9. State Management → Read Model Only

The global state shape defined in the Design Document is preserved 

Design Document

.

Critical Constraint

Frontend state is:

derived

ephemeral

non-authoritative

No state mutation is final until confirmed by orchestrator output.

10. Forbidden Patterns (Contextualized)

These are implementation bans, not UX bans.

UX Concept	Forbidden As	Must Be Rendered As
Dashboard	Static screen	AggregatedCard
Page	Route	Canvas stream
Plugin UI	Embedded app	Plugin-backed cards
Workflow	UI logic	Orchestrator states
Auto action	Silent exec	ConfirmationCard
Form	Static form	FormCard via A2UI

This preserves all Design UX while enforcing protocol safety.

11. What This Enables (Strategic)

By protocolizing the existing design:

AI coding agents can build safely

Backend can evolve without UI rewrites

Plugins remain composable

Enterprise auditability is preserved

UX stays fluid and non-fragmented

12. Final Verdict

No redesign required.
Your Design Document is now:

A first-class UI protocol specification

The UI becomes:

predictable like HTML

flexible like chat

safe like enterprise software

Recommended Next Step (Optional)

If you want, next I can:

Produce a machine-readable A2UI contract file (a2ui.schema.json)

Generate AI-agent lint rules (“reject PR if rule violated”)

Create a mapping doc: Backend Orchestrator Output → UI Chunk Types

Just tell me how deep you want to formalize it.

Sources
Create a mapping doc: Backend Orchestrator Output → UI Chunk Types

Perfect. This is the right artifact at the right time.
What you’re asking for is essentially the ABI between your backend brain and your UI runtime.

Below is a clean, authoritative mapping document you can keep alongside SPEC.md and hand directly to backend engineers and AI coding agents.

📗 Backend Orchestrator Output → UI Chunk Mapping
(Dhii UI Runtime Contract v1.0)

Status: FROZEN
Audience: Backend engineers, Orchestrator authors, AI coding agents
Depends on: SPEC.md v1.2, Design Document (Dynamic Interface 3.0)
Purpose: Ensure deterministic, safe, explainable UI rendering from backend output

0. Core Rule (Non-Negotiable)

The backend never sends UI.
It sends structured intent-aligned output.
The UI renders it as protocol-defined chunks.

This document defines:

what the orchestrator is allowed to emit

how the UI must render it

what the UI must never infer

Think of this like HTML tags + browser rules, but for Dhii.

1. Orchestrator Output Envelope (Mandatory)

Every orchestrator response must conform to this envelope.

{
  "request_id": "uuid",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "state": "STREAMING | WAITING_FOR_CONFIRMATION | COMPLETED | ERROR",
  "explanation": "optional natural language",
  "chunks": [ /* ordered UI chunks */ ]
}

Rules

chunks order is authoritative

UI must render in order

UI must not reorder, merge, or drop chunks

UI must not infer missing chunks

2. Chunk Taxonomy (Allowed UI Chunk Types)

Only the following chunk types may be emitted.

Any unknown chunk → render error card.

3. Mapping: Orchestrator Intent → UI Chunk Types
3.1 Informational Reasoning
Orchestrator Intent

explain

summarize

reason

clarify

Chunk Type

TextBlock

{
  "type": "TextBlock",
  "content": "Here is a summary of today’s priority items.",
  "tone": "neutral | advisory | warning"
}


UI behavior

Render as conversational text

Collapsible after completion

No actions allowed

3.2 Aggregated Insights (Dashboard Replacement)
Orchestrator Intent

overview

status

insights

priorities

Chunk Type

AggregatedCard

{
  "type": "AggregatedCard",
  "title": "Today’s Focus Areas",
  "sources": ["email", "tasks", "calendar"],
  "items": [
    { "label": "Urgent Emails", "value": 3 },
    { "label": "Overdue Tasks", "value": 2 }
  ]
}


UI behavior

Replaces dashboards

Renders as a single card

Supports partial rendering if some sources fail

3.3 Data Presentation
Orchestrator Intent

list

show

browse

compare

Chunk Type

DataTable or ListCard

{
  "type": "DataTable",
  "columns": ["Sender", "Subject", "Priority"],
  "rows": [
    ["John", "Invoice follow-up", "High"]
  ]
}


UI behavior

Read-only by default

Selection emits intent events

No inline mutation unless accompanied by an Editor chunk

3.4 Editable Content (Forms Without Forms)
Orchestrator Intent

draft

edit

modify

prepare

Chunk Type

EditorCard

{
  "type": "EditorCard",
  "entity": "email_reply",
  "content": "Draft response text here",
  "editable": true
}


UI behavior

Inline editing only

Changes are local until confirmation

No auto-save to backend

3.5 Action Proposals (Human-in-the-Loop)
Orchestrator Intent

suggest_action

recommend

propose

Chunk Type

ActionGroup

{
  "type": "ActionGroup",
  "actions": [
    {
      "id": "send_email",
      "label": "Send Reply",
      "risk": "medium"
    }
  ]
}


UI behavior

No action executed automatically

Clicking emits ACTION_CONFIRMED

Risk indicator must be shown

3.6 Confirmation & Safety
Orchestrator Intent

confirm

approve

authorize

Chunk Type

ConfirmationCard

{
  "type": "ConfirmationCard",
  "message": "Send this email to John?",
  "action_id": "send_email"
}


UI behavior

Blocks further execution

Requires explicit user confirmation

Cannot be auto-accepted

3.7 Plugin-Backed Data
Orchestrator Intent

enrich

fetch_context

correlate

Chunk Type

ContextCard

{
  "type": "ContextCard",
  "source_plugin": "crm",
  "summary": "John is a key client with an open deal."
}


UI behavior

Displays provenance

Collapsible

Read-only

3.8 Errors & Ambiguity
Orchestrator Intent

error

ambiguity

missing_context

Chunk Type

ClarificationCard

{
  "type": "ClarificationCard",
  "message": "Which email do you want to reply to?",
  "options": ["Email A", "Email B"]
}


UI behavior

Must halt execution flow

User selection emits new intent

No fallback guessing

4. State-Driven Rendering Rules
Orchestrator State	UI Behavior
STREAMING	Render chunks as they arrive
WAITING_FOR_CONFIRMATION	Disable composer execution
COMPLETED	Collapse resolved chunks
ERROR	Render ClarificationCard

UI must mirror, not override, backend state.

5. What the Orchestrator Must NEVER Emit

❌ UI layout instructions
❌ Styling hints
❌ Positioning metadata
❌ Cross-chunk dependencies
❌ Conditional UI logic

The orchestrator speaks intent, not presentation.

6. What the UI Must NEVER Do

❌ Infer missing chunks
❌ Combine chunks
❌ Reorder chunks
❌ Execute actions implicitly
❌ Bypass confirmation

UI is a renderer, not a co-author.

7. End-to-End Example (Concrete)
User

“Draft a polite reply and send it”

Orchestrator Output

TextBlock – explanation

EditorCard – draft reply

ActionGroup – “Send”

ConfirmationCard – final approval

UI Result

User edits draft

Clicks Send

Confirms

Orchestrator executes

UI updates state

No shortcuts. No ambiguity.

8. Why This Mapping Exists

Without this document:

backend engineers overstep into UI

frontend engineers add logic

AI agents hallucinate components

enterprise trust erodes

With this document:

responsibilities are clean

AI output is safe

UI remains evolvable

plugins stay invisible

9. Final Principle (Anchor)

Backend emits meaning.
UI renders meaning.
Humans decide meaning.

This mapping is the contract that makes Dhii scalable.

The UI runtime may use Vite as a build tool.
Build tools must not influence UI behavior, state, or protocol interpretation.


### Next (Optional but High-Value) - Thsi si for Phase 2


* map **v1.2 → SOC2 / ISO 27001 controls**
* define **tenant migration & lifecycle rules**
* design **billing & quota boundaries**
* generate **tenant-aware AI test cases**


