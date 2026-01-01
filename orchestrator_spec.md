# Orchestrator Specification (dhii Mail / A2UI Workspace)

## 1. Purpose & Scope

The **Orchestrator** is the central brain of the dhii Mail AI workspace. It is responsible for:

- Understanding **user intent** and **current context**.
- Mapping any intent across **N domains** (mail, meetings, tasks, CRM, ERP, chat, devops, etc.) into a **finite set of UI patterns**.
- Building and streaming **A2UI messages** using a **finite, versioned component catalog**.
- Coordinating **backend capabilities** (core services + plugins) and enforcing **state machine** and **autonomy** rules.

The orchestrator does **not**:

- Render UI directly.
- Execute arbitrary UI code at runtime.
- Allow components outside the approved catalog.

Instead, it produces **declarative UI descriptions** (A2UI) and delegates rendering to the client, which uses native web components.

This specification is **domain-agnostic by design**. It must support:

- Any number of domains: `D1 ... Dn` (Mail, Calendar, Tasks, CRM, ERP, Analytics, DevOps, Support, Finance, HR, etc.).
- Any number of use cases / user stories per domain: `U1 ... Um`.
- Complex cross-domain journeys (e.g., "From this email, create a task, log a CRM activity, and open a Jira ticket").


## 2. Core Guarantees

The orchestrator guarantees that:

1. **Finite Component Catalog**
   - It will **never** emit A2UI components that are not part of the **approved catalog**.
   - The catalog is **versioned** and **backwards-compatible** as much as possible.

2. **Infinite Compositions**
   - It may combine catalog components in **arbitrarily complex ways** based on:
     - The user prompt.
     - The current context stack.
     - Available backend capabilities and plugins.
   - New user prompt ⇒ new combination/arrangement of **existing** components (e.g., `FormCard`, `ListCard`, `InfoCard`, `ProgressBar`, etc.), **not** new component types.

3. **Single Source of Truth for Logic**
   - All decisions about:
     - Which components to use.
     - Which data to show.
     - Which actions to wire.
     - When to ask for confirmation.
   - are made by the orchestrator, **not** by the client or plugins.

4. **State Machine Compliance**
   - All interactions follow the global state machine:
     - `IDLE → INTENT_CAPTURED → CONTEXT_RESOLVED → AI_PROCESSING → A2UI_RENDERED → USER_DECISION → ACTION_EXECUTED → STATE_UPDATED → IDLE`.
   - No transitions are skipped; autonomy levels control which transitions require explicit user confirmation.


## 3. Conceptual Model

### 3.1 Domains

A **domain** is a logical area of functionality with its own entities, actions, and data models. Examples:

- Communication: Mail, Chat, SMS, WhatsApp, Slack, Teams.
- Meetings & Scheduling: Calendar, Video calls, Rooms, Shifts.
- Work Management: Tasks, Projects, Sprints, Tickets.
- Revenue: CRM, CPQ, Billing, Subscriptions.
- Operations: ERP, Inventory, Logistics, Procurement.
- Product & Engineering: Issue tracking, CI/CD, Deployments, Incidents.
- Analytics & BI: Dashboards, Metrics, Reports.
- HR: People, Time off, Performance, Payroll.
- Support & CX: Helpdesk, Live chat, Knowledge base.

Each domain is represented internally as a **Domain Module** with:

- **Entities**: e.g., `EmailThread`, `Meeting`, `Task`, `Deal`, `Ticket`.
- **Actions**: e.g., `send_email`, `schedule_meeting`, `create_task`, `log_activity`.
- **Data schemas** for reading/writing.

The orchestrator is domain-agnostic: it only requires that each domain module exposes a **capability contract**.

### 3.2 Capabilities

A **Capability** is a function the orchestrator can invoke. Each capability has:

- `id`: unique identifier (e.g., `mail.search_threads`, `tasks.create_task`).
- `domain`: owning domain (e.g., `mail`, `tasks`).
- `inputSchema`: typed parameters.
- `outputSchema`: typed results, including references to entities.
- `sideEffects`: description of what it may change (for logging/autonomy).

Capabilities are used to:

- Fetch context: search emails, list tasks, get meeting info.
- Execute actions: send, schedule, update, delete, trigger workflows.

### 3.3 Component Catalog

A **Component Catalog** is a finite set of A2UI component types the orchestrator is allowed to emit.

#### 3.3.1 Categories

1. **Layout & Containers**
   - `Card`, `Panel`, `Row`, `Column`, `Tabs`, `Modal`, `Drawer`.

2. **Lists & Collections**
   - `List`, `ListItem`, `Table`, `Timeline`.

3. **Forms & Inputs**
   - `FormCard` (container + fields array).
   - Field types:
     - `TextField`, `Textarea`, `NumberField`.
     - `Checkbox`, `Switch`.
     - `Select`, `MultiSelect`, `RadioGroup`.
     - `DatePicker`, `TimePicker`, `DateTimePicker`.
     - `FileInput`.
     - `TagInput`.

4. **Status & Feedback**
   - `ProgressBar`.
   - `InlineStatus` / `StatusBanner`.
   - `Toast` / `Snackbar`.
   - `Skeleton`.

5. **Domain Shells** (thin wrappers over primitives)
   - `MailThreadView`, `MailMessageCard`, `MailFolderList`.
   - `MeetingCard`, `MeetingSchedulerGrid`, `MeetingList`.
   - `TaskCard`, `TaskBoard`, `ProjectList`.
   - `PluginPanel`, `ContextLinkCard`.

6. **Chat & Context**
   - `ChatThread`, `ChatMessage`, `ChatComposer`.
   - `ContextChipsBar`.

> Note: This catalog is finite and versioned. New types can be added only through a **catalog evolution process**, not at runtime.


## 4. Orchestrator Pipeline

For any incoming user interaction (chat message, button click, etc.), the orchestrator follows this pipeline.

### 4.1 Step 0 – Input

Inputs include:

- `userMessage`: natural language text (for chat).
- `uiEvent`: e.g., button clicked, field changed, form submitted.
- `sessionState`: current session id, autonomy level, user identity, etc.
- `contextStack`: list of entities currently in focus (emails, tasks, meetings, CRM objects, etc.).

### 4.2 Step 1 – Intent Understanding

The orchestrator (via AI or rules) determines:

- **Primary intent**: what the user wants to achieve.
  - Examples: `summarize_inbox`, `schedule_meeting`, `create_task`, `log_crm_activity`, `upload_file`, `deploy_service`.
- **Target domains**: which domain modules are relevant.
  - Single domain (e.g., mail only) or cross-domain (e.g., mail + tasks + CRM).
- **Parameters**: major parameters embedded in text.
  - E.g., time ranges, recipients, labels, environments, priorities.

Output of this step is an **Intent Object**:

- `intentId` (string).
- `domains[]` (list).
- `parameters` (structured data, possibly partial/incomplete).

### 4.3 Step 2 – Flow Archetype Classification

The orchestrator maps the intent to one or more **Flow Archetypes**. These are domain-independent patterns of interaction.

Common archetypes:

1. **Search & Browse**
   - Find and show a list of items.
   - Examples: search emails, list tasks, find contacts, query logs.

2. **Detail Inspect**
   - Show a detailed view of a single entity.
   - Examples: open an email thread, show a task, show a CRM deal.

3. **Form / Edit**
   - Present fields to view/edit data.
   - Examples: compose email, create task, update preferences, change settings.

4. **Long-Running Job / Progress**
   - Track a multi-step or time-consuming operation.
   - Examples: upload/download, bulk sync, analytics run, deployment.

5. **Multi-Step / Wizard**
   - Complex flows broken into steps.
   - Examples: onboarding, multi-stage configuration, campaign setup.

6. **Dashboard / Summary**
   - Aggregate information and key metrics.
   - Examples: inbox overview, team workload, pipeline health.

7. **Approval / Confirmation**
   - Present a concise summary and require explicit confirmation.
   - Examples: bulk delete, send to 1000 recipients, production deploy.

An intent may map to **one or more archetypes**, e.g.: "Upload a file and attach it to this email" = Long-Running Job + Detail Inspect.

### 4.4 Step 3 – Domain Capability Planning

For each intent and its archetypes, the orchestrator plans **capability invocations** across domains.

Output: a **Plan** consisting of ordered steps:

- Read operations (context gathering):
  - e.g., `mail.search_threads`, `crm.get_contact`, `tasks.search_tasks`.
- Write operations (actions):
  - e.g., `mail.send_email`, `tasks.create_task`, `deployments.trigger`.
- Long-running jobs (jobs/tasks):
  - e.g., `files.upload`, `analytics.run_report`, `sync.run_full_sync`.

The plan is **pure logic**; no UI decisions yet.

### 4.5 Step 4 – UI Pattern Selection (from Catalog)

Given the **archetypes**, the orchestrator selects which **UI patterns** to use. Each archetype has one or more **UI recipes** defined in terms of the component catalog.

#### 4.5.1 Example Recipes

- **Search & Browse (generic)**  
  Components:
  - `Card` with `SearchBar` + filters.
  - `List` of results (`ListItem` for each entity).

- **Detail Inspect (generic)**  
  Components:
  - `Card` with entity summary.
  - `Timeline` of related activity.
  - `InlineStatus` for current state.

- **Form / Edit (generic)**  
  Components:
  - `FormCard` with fields array.

- **Long-Running Job / Progress**  
  Components:
  - `Card` or `Panel` with `List` of `JobItem`s.
  - Each `JobItem` includes `ProgressBar` + status text.

- **Approval / Confirmation**  
  Components:
  - `Card` summarizing the action.
  - Two buttons: primary confirm, secondary cancel.

These recipes are **domain-agnostic**. The orchestrator simply plugs in **domain-specific data**.

### 4.6 Step 5 – Data & Action Binding

The orchestrator:

1. Executes/plans necessary **read capabilities** to populate UI:
   - Example: user: "Show me all high-priority Jira tickets for Project X".
   - Orchestrator:
     - Calls `pm.search_tickets({ project: X, priority: high })`.
     - Maps results into a `List` of domain-agnostic `ListItem`s or domain-specific `TicketCard`s.

2. Fills each chosen component from the catalog with:
   - **Data props** (title, description, items, values, progress...)
   - **Action props** (buttons, menu actions) wired to intents:
     - e.g., button: `label: "Create task"`, `intent: "tasks.create_task_from_email"`.

3. Assigns **identifiers** so subsequent UI events map back to correct entities and plans.

### 4.7 Step 6 – A2UI Emission & Streaming

The orchestrator serializes the selected components and their props into A2UI messages and streams them to the client.

- Initial response: base layout (chat + first set of cards).
- Subsequent updates: new cards, updated props (e.g., `ProgressBar` value), or removal of old components.

All messages use only **component types from the catalog**.

### 4.8 Step 7 – User Decision & Action Execution

Upon user interaction (click, submit, etc.):

1. Client sends `uiEvent` back to orchestrator with:
   - Component id.
   - Action id / intent id.
   - Input data (e.g., form values).

2. Orchestrator:
   - Validates state (does this action make sense in current state?).
   - Enforces autonomy rules:
     - Assist: suggest only.
     - Recommend: pre-fill UI, require explicit send/confirm.
     - Act: may auto-execute low-risk tasks, still confirm dangerous actions.

3. If confirmed, orchestrator executes the **write capabilities** from the plan.

4. `STATE_UPDATED`:
   - Orchestrator updates context, logs events, and emits new A2UI messages representing the updated world.


## 5. "N Domains" and "N Use Cases" Logic

The orchestrator is deliberately built so that adding new domains (`D_(n+1)`) and new use cases (`U_(m+1)`) follows a **repeatable pattern**, instead of changing its core.

### 5.1 Adding a New Domain (D)

To add a new domain (e.g., `hr`, `finance`, `iot`, `learning`), we:

1. **Define Domain Entities & Capabilities**
   - Example (HR):
     - Entities: `Employee`, `TimeOffRequest`, `Review`.
     - Capabilities: `hr.search_employees`, `hr.create_timeoff_request`, `hr.approve_timeoff`.

2. **Register Capabilities with Orchestrator**
   - Provide metadata for each capability:
     - Inputs, outputs, side effects, domain, permissions.

3. **Map Domain Intents to Archetypes**
   - E.g., "Submit time off" → Form / Edit + Confirmation.
   - E.g., "Show my team" → Search & Browse + Detail Inspect.

4. **Define Optional Domain Shell Components**
   - E.g., `EmployeeCard`, `TimeOffRequestCard` built on top of primitives.
   - These components are added to the **catalog** via a versioned update.

5. **Update the Intent Router / LLM System Prompts**
   - Teach the orchestrator how to route new intents to new capabilities and UI recipes.

No core orchestrator code needs to change beyond new registrations and recipes; the patterns stay the same.

### 5.2 Supporting N Use Cases per Domain

A **use case** or **user story** is a specific narrative, e.g.:

- "As a sales rep, I want to see all deals closing this month and email all owners" (CRM).
- "As a manager, I want to review all pending time-off requests" (HR).
- "As an SRE, I want to see incidents across services and roll back bad releases" (DevOps).

For each use case `U` in domain `D`:

1. Define the **intent(s)** and **parameters**.
2. Map to **archetypes**.
3. Compose a **plan** (capability steps) for reads + writes.
4. Assign **UI recipes** from the catalog:
   - Search & Browse → `List` + filters.
   - Detail Inspect → `Card` + `Timeline`.
   - Form → `FormCard`.
   - Progress → `ProgressBar` inside `Card`.

As long as the domain’s needs can be expressed as combinations of:

- Listing things,
- Viewing details,
- Editing/creating forms,
- Tracking long-running jobs,
- Showing summaries and approvals,

...the orchestrator can support arbitrarily many user stories using the **same finite component set**.


## 6. Example: Generic Upload/Download Across Domains

This pattern appears in many domains:

- Mail: uploading attachments, downloading emails as .eml or .zip.
- CRM: uploading contracts.
- Files/Storage: syncing documents.
- DevOps: downloading logs, artifacts.
- Analytics: exporting reports.

### 6.1 Components Used

- `FileTransferCard` (domain-generic shell):
  - `title`, `items[]`.
- `FileTransferItem` (inside list):
  - `fileName`, `size`, `direction`, `progress`, `status`.
- `ProgressBar` (embedded or global).
- `Toast` / `InlineStatus`.

### 6.2 Flow

1. Intent: "Upload this PDF and link to the last email".
2. Archetypes: Long-Running Job + Detail Inspect.
3. Plan:
   - `files.upload(file, destination=crm)`.
   - `mail.link_attachment_to_thread(emailId, fileId)`.
4. UI Recipe:
   - New `FileTransferCard` in A2UI center panel.
   - Each progress update → new A2UI message updating `progress` + `status`.

This entire pattern re-uses the same components for every domain that uploads or downloads, without needing domain-specific upload UIs.


## 7. Safety, Autonomy, and Auditability

### 7.1 Autonomy Levels

The orchestrator enforces autonomy via levels:

- `assist` – Suggest only; user must perform all writes explicitly.
- `recommend` – Pre-fill UIs (forms, drafts), but require explicit confirmation.
- `act` – Automatically execute certain safe actions, but **never** high-risk operations without confirmation.

Each capability is annotated with a **risk profile**; the orchestrator uses this to decide when a confirmation UI (e.g., `ApprovalCard`) is required.

### 7.2 Human-in-the-Loop

- Dangerous actions (bulk delete, large sends, production deployments, financial transfers) always:
  - Go through the `Approval / Confirmation` archetype.
  - Show a concise summary, impacted objects, and consequences.

### 7.3 Audit Trail

- Every state transition and capability invocation is logged:
  - `who`, `what`, `when`, `which autonomy level`, `which contexts`.
- A2UI actions are traceable back to:
  - Intent, domain, capability, and user confirmation.


## 8. Catalog Evolution Process

The finite catalog can grow over time, but only via a **controlled process**:

1. Identify a pattern that cannot be expressed cleanly with existing components.
2. Propose a new component type (e.g., `GanttChart`, `OrgChart`, `Heatmap`).
3. Specify:
   - Props schema.
   - Allowed actions.
   - Accessibility and responsive behavior.
4. Implement and test as a web component.
5. Bump catalog version; update orchestrator and agent prompts to know about the new type.

At no point does the orchestrator or A2UI client allow arbitrary new component types at runtime.


## 9. Summary

- The orchestrator operates over **N domains** and **N use cases** using a **finite, carefully designed component catalog**.
- It:
  - Understands intentions and context.
  - Selects archetypes.
  - Plans domain capability calls.
  - Chooses UI recipes built from catalog components.
  - Binds data and actions.
  - Streams A2UI for a fluid, dynamic center panel.
- This design:
  - Keeps the user experience **fluid and conversational**.
  - Keeps the UI **safe, consistent, and maintainable**.
  - Allows new domains and use cases to be added via configuration, recipes, and new capabilities—not by rewriting the core orchestrator.
