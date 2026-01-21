# Dhii-Mail SaaS Architecture & Delivery Plan
## 1. Vision and Success Criteria
Define and ship a multi-tenant, AI-native email–calendar–tasks SaaS (“dhii-mail”) built as an "AI Operating System" with a Liquid Glass A2UI front-end, an agentic Kernel, pluggable domain apps (Mail/Calendar/Tasks/Meetings), a robust backend of services, and an extensible plugin marketplace, running on secure, scalable cloud infrastructure.
Success is defined as:
* A paying customer can sign up, connect their email/calendar, and use an AI-powered workspace to manage communication and tasks end-to-end.
* The system is multi-tenant, secure, observable, and deployable via CI/CD.
* The architecture supports adding new AI models and plugins without re-architecting the core.
We will deliver this in incremental phases while keeping the long-term architecture in mind.
## 2. Delivery Phases (High-Level Roadmap)
1. **Phase 0 – Foundations & Hardening**
    * Stabilize repository, dependencies, Docker & CI.
    * Document current state; establish coding standards and contribution workflow.
2. **Phase 1 – Minimal Viable AI Mail Workspace**
    * Wire existing A2UI frontend to the Kernel and Mail backend.
    * Implement core auth, session, and a single-tenant deployment.
    * Deliver AI-assisted inbox triage and basic reply drafting using external LLMs.
3. **Phase 2 – Calendar & Tasks Integration**
    * Add Calendar and Tasks backends and wire into Kernel as capabilities.
    * Enable natural-language scheduling and task creation from email.
4. **Phase 3 – Multi-Tenancy, Billing, and Permissions**
    * Introduce tenants, RBAC, usage limits, and billing integration.
5. **Phase 4 – Plugin Marketplace & Extensibility**
    * Build plugin host, registry, and developer onboarding.
6. **Phase 5 – Scale, Observability, and Hardening**
    * SLOs, autoscaling, incident response, and production operations.
Each phase is decomposed into workstreams aligned with the six architectural layers.
## 3. Layer 1 – Frontend (A2UI / "Liquid Glass" Shell)
### 3.1 Objectives
* Provide a single-page, real-time "Liquid Glass" workspace that renders AI-driven intents as composable UI components.
* Support streaming updates (e.g., token-by-token LLM output, incremental list updates).
* Ensure the frontend is multi-tenant aware and securely authenticated.
### 3.2 Epics and Outcomes
#### Epic F1: A2UI Protocol Definition and Schema
* **Outcome:** A versioned, documented A2UI schema that both frontend and Kernel use to communicate UI state and actions.
* Tasks:
    * Define core A2UI entities: `Session`, `Intent`, `Panel`, `Widget`, `Action`, `StatePatch`.
    * Specify JSON schemas and TypeScript types for all A2UI messages.
    * Document event model (e.g., user events, system events, error events).
    * Define compatibility/versioning strategy for schema evolution.
#### Epic F2: WorkspaceShell 2.0 (Runtime UI Engine)
* **Outcome:** A production-ready React-based shell that can render arbitrary A2UI layouts and react to streaming updates.
* Tasks:
    * Refactor current `WorkspaceShell` into a modular layout engine (panels, widgets, regions).
    * Implement a state store (e.g., Zustand/Redux) to keep A2UI session state.
    * Implement a generic `WidgetHost` that renders widgets from schema (e.g., lists, tables, forms, charts, conversation threads).
    * Add support for dynamic layout changes (open/close panels, resize, drag-and-drop where appropriate).
    * Implement optimistic UI updates and rollback based on Kernel responses.
#### Epic F3: Real-Time Transport (SSE/WebSocket) for Intent Streams
* **Outcome:** Stable, reconnecting real-time channel between frontend and Kernel for intents and UI updates.
* Tasks:
    * Evaluate SSE vs WebSocket for bi-directional messaging; choose and implement.
    * Implement connection lifecycle handling (connect, reconnect, backoff, offline state UI).
    * Define client-side message router that dispatches incoming A2UI frames to the store.
    * Implement backpressure and message buffering to avoid UI freezes.
#### Epic F4: Authentication & Session Management
* **Outcome:** Secure login/logout flow, persisted sessions, and tenant-aware context in the UI.
* Tasks:
    * Implement login UI (email/password + SSO placeholder) wired to backend auth.
    * Store and refresh access tokens securely (HTTP-only cookies or secure storage strategy).
    * Display current tenant/account context and allow workspace switch.
    * Implement logout, session expiry handling, and "re-auth" flows.
#### Epic F5: Frontend Observability & UX Quality
* **Outcome:** Instrumented frontend with error tracking, performance metrics, and UX polish.
* Tasks:
    * Integrate Sentry/LogRocket (or equivalent) for JS error monitoring.
    * Add performance tracing for key flows (render latency, time-to-first-intent, etc.).
    * Implement a global notification/toast system and standardized error messages.
    * Add responsive layout and accessibility improvements.
## 4. Layer 2 – Kernel (Agentic Core / "The Brain")
### 4.1 Objectives
* Central orchestrator that translates user input + context into intents and actions.
* Provides a tool-calling layer over backend services and plugins.
* Maintains short-term and long-term context per user and per conversation.
### 4.2 Epics and Outcomes
#### Epic K1: Kernel Service Skeleton & API Surface
* **Outcome:** A dedicated `kernel` service exposing `/api/a2ui/*` endpoints and WebSocket/SSE for intent streaming.
* Tasks:
    * Define API contracts: `/api/a2ui/session`, `/api/a2ui/intent`, `/api/a2ui/events`.
    * Implement request/response DTOs with Pydantic models aligned to A2UI schema.
    * Implement a basic `KernelController` that accepts user messages and returns static intents (for bootstrapping).
#### Epic K2: Intent Parsing & Routing Engine
* **Outcome:** A robust, testable engine that converts user messages and UI events into structured intents.
* Tasks:
    * Port/replace `geminiService` logic from frontend into backend with LLM-agnostic design.
    * Define intent taxonomy (e.g., `mail.search`, `mail.summarize_thread`, `calendar.create_event`).
    * Implement LLM prompt templates and parsing logic (e.g., JSON-based function calling or tool calling).
    * Implement a routing table that maps intent types to handler functions/capabilities.
#### Epic K3: Context Engine & Memory
* **Outcome:** A context subsystem that stores and retrieves per-session, per-user, and cross-session memory.
* Tasks:
    * Design data model for `Conversation`, `ContextItem`, `UserProfile`, `Preferences`.
    * Implement in-memory context store + Redis-backed persistence.
    * Implement context retrieval and summarization via LLM for long histories.
    * Add APIs for explicit user control over memory (view, clear, pin, redact).
#### Epic K4: Permission & Policy Engine
* **Outcome:** A central policy engine that enforces what actions agents are allowed to perform for a given user/tenant.
* Tasks:
    * Define permission model: actions, resources, scopes (e.g., `mail.read`, `mail.send`, `calendar.write`).
    * Design policy language (role-based + attribute-based rules) and persistence in DB.
    * Implement middleware in the Kernel that checks policies before invoking tools.
    * Add audit logging for all privileged actions (e.g., sending emails, modifying calendars).
#### Epic K5: Tooling & Orchestration Layer
* **Outcome:** Unified interface for calling backend services and plugins from LLM tool calls.
* Tasks:
    * Define `Tool` abstraction (name, input schema, output schema, idempotency, side-effect classification).
    * Implement adapters for core services: Mail, Calendar, Tasks, Linear, etc.
    * Implement a tool execution pipeline: validation, auth, retries, error mapping to UI.
    * Add support for multi-step "plans" (agent proposes plan → user approves → Kernel executes steps with progress updates to UI).
#### Epic K6: Kernel Observability & Safety
* **Outcome:** Full visibility into agent decisions and robust safeguards.
* Tasks:
    * Instrument Kernel with structured logging (intents, tool calls, errors) with PII redaction.
    * Implement tracing around LLM calls and tool invocations.
    * Add configurable limits on token usage, tool call depth, and execution time per session.
    * Implement circuit breakers and fallback behavior when models or services fail.
## 5. Layer 3 – Application Layer (Mail, Calendar, Tasks, Meetings)
### 5.1 Objectives
* Provide robust domain-specific capabilities that the Kernel can orchestrate.
* Replace mock UIs with real data from backend services (Mail, Calendar, Tasks, Meetings).
### 5.2 Epics and Outcomes
#### Epic A1: Mail Application
* **Outcome:** A fully functional mail workspace: list/search, read, tag, archive, reply, and basic rules.
* Tasks:
    * Define domain models: `Mailbox`, `Message`, `Thread`, `Label`, `Attachment`.
    * Implement Mail widget components (list, thread view, compose, filters) wired to real APIs.
    * Implement search UI (filters by folder, sender, date, label).
    * Implement in-mail actions (archive, star, mark as read/unread, move to folder).
    * Integrate AI actions: summarize thread, extract tasks, draft reply.
#### Epic A2: Calendar & Meetings Application
* **Outcome:** Interactive calendar UI with daily/weekly/monthly views and AI-assisted scheduling.
* Tasks:
    * Implement calendar views and event editors in A2UI widgets.
    * Integrate with Calendar backend to fetch, create, update, and delete events.
    * Implement "Find a time" flow: user asks for a meeting, Kernel calls calendar capability to propose slots.
    * Display availability suggestions and allow user to confirm or adjust.
#### Epic A3: Tasks Application
* **Outcome:** Task board integrated with email and calendar.
* Tasks:
    * Define `Task`, `Project`, `Label`, `DueDate` data models.
    * Implement list/board views for tasks (backlog, today, upcoming, completed).
    * Implement "create task from email" and "create task from natural language" flows.

#### Epic A4: Cross-App Orchestration Patterns
* **Outcome:** Predefined cross-app flows (e.g., "triage inbox into tasks and calendar").
* Tasks:
    * Define common workflows: triage, follow-up scheduling, meeting prep/post-mortem.
    * Implement Kernel sequences that chain mail → calendar → tasks calls.
    * Expose these as top-level intents (e.g., `plan.my_day`, `clear_inbox`, `prepare_for_meeting`).
## 6. Layer 4 – Backend Services (Core API, Integrations)
### 6.1 Objectives
* Provide secure, well-structured REST/GraphQL APIs for all domain operations.
* Encapsulate third-party integrations behind stable contracts.
### 6.2 Epics and Outcomes
#### Epic B1: Core API & Domain Models
* **Outcome:** A coherent set of FastAPI services with versioned endpoints and strong typing.
* Tasks:
    * Design database schema for tenants, users, mail, calendar, tasks, plugins, and audit logs.
    * Implement models and repositories using SQLAlchemy 2.0 and migrations via Alembic.
    * Implement core endpoints: `/auth/*`, `/users/*`, `/tenants/*`, `/mail/*`, `/calendar/*`, `/tasks/*`.
    * Add OpenAPI documentation and ensure compatibility with A2UI and Kernel.
#### Epic B2: Authentication & Authorization
* **Outcome:** Secure, multi-tenant-aware auth with role-based access control.
* Tasks:
    * Implement user registration, login, password reset, and email verification.
    * Implement JWT or PASETO-based access/refresh tokens with rotation and revocation.
    * Implement roles (Owner, Admin, Member) and enforce them in API endpoints.
#### Epic B3: Mail Backend (IMAP/SMTP + Provider APIs)
* **Outcome:** Reliable mail ingestion and sending for major providers.
* Tasks:
    * Implement OAuth flows for Gmail and Microsoft 365 (via Google/Microsoft SDKs).
    * Implement IMAP sync pipeline (initial sync + incremental changes).
    * Implement SMTP or provider-specific send endpoints.
    * Implement a local message cache in Postgres with minimal normalized schema.
#### Epic B4: Calendar Backend (Google/Microsoft/CalDAV)
* **Outcome:** Bi-directional sync for events with major calendar providers.
* Tasks:
    * Implement OAuth flows and token storage for Google Calendar and Microsoft Graph.
    * Implement event list, create, update, delete, and attendee management.
    * Handle time zones, recurrence rules, and reminders.
#### Epic B5: Tasks & Linear Integration
* **Outcome:** Task management API with optional sync to Linear.
* Tasks:
    * Wrap existing `linear_client.py` with FastAPI endpoints.
    * Map internal `Task` model to Linear issues and synchronize state.
    * Implement configuration UI/API for connecting a workspace to a Linear team.
#### Epic B6: Background Jobs and Scheduling
* **Outcome:** Scalable background processing for sync, LLM calls, and periodic jobs.
* Tasks:
    * Choose and integrate a job queue (Celery/RQ/Arq) with Redis as broker.
    * Implement workers for mail/calendar sync, LLM summarization, and indexing.
    * Implement job monitoring dashboards and retry/alerting logic.
## 7. Layer 5 – Plugin Layer & Marketplace
### 7.1 Objectives
* Enable third-party and internal teams to add new capabilities without modifying core code.
* Provide a safe, auditable execution environment for plugins.
### 7.2 Epics and Outcomes
#### Epic P1: Plugin Model & Registry
* **Outcome:** A formal plugin model and registry service that tracks all installed plugins per tenant.
* Tasks:
    * Define plugin metadata schema: name, description, capabilities, configuration schema, scopes.
    * Implement plugin registration APIs and UI in the Settings app.
    * Implement enable/disable and versioning model for plugins.
#### Epic P2: Plugin Execution Runtime
* **Outcome:** A sandboxed execution environment for plugins.
* Tasks:
    * Decide plugin execution model (out-of-process HTTP, serverless functions, or containerized tasks).
    * Implement a plugin runner with timeouts, resource limits, and observability.
    * Implement authentication/authorization for plugin callbacks.
#### Epic P3: Developer Experience & SDKs
* **Outcome:** Simple SDKs and documentation so external developers can build plugins.
* Tasks:
    * Design and implement a minimal Plugin SDK (Python/TypeScript) exposing handlers and config.
    * Create example plugins: CRM connector, knowledge base search, simple webhook forwarder.
    * Publish docs and templates (GitHub repo + docs site).
#### Epic P4: Plugin Marketplace UI
* **Outcome:** In-app marketplace where admins can browse, install, and configure plugins.
* Tasks:
    * Implement Marketplace UI in the Settings section of the frontend.
    * Implement filters, search, categories, and detail pages for plugins.
    * Implement installation and configuration flows with validation.
## 8. Layer 6 – Infrastructure, DevOps, and Operations
### 8.1 Objectives
* Provide a production-grade, secure, and maintainable deployment platform for dhii-mail.
* Support staging and production environments with CI/CD.
### 8.2 Epics and Outcomes
#### Epic I1: Containerization & Local Developer Experience
* **Outcome:** Reliable docker-compose based local environment mirroring production topology.
* Tasks:
    * Finalize Dockerfiles for frontend, kernel, backend, plugin host, mail server, and supporting services.
    * Stabilize requirements and base images (Python 3.11, Node 20, Postgres, Redis, Nginx).
    * Provide `make`/scripts to start, stop, and reset local environment.
    * Document onboarding steps for new developers.
#### Epic I2: Continuous Integration & Quality Gates
* **Outcome:** Automated build, test, lint pipeline that runs on every PR and is required for merge.
* Tasks:
    * Set up CI workflows (GitHub Actions or equivalent) for backend, frontend, and kernel.
    * Run unit tests, integration tests, linters (ruff, mypy, eslint, jest) on every push.
    * Enforce coverage thresholds and style checks.
#### Epic I3: Continuous Delivery & Environments
* **Outcome:** Automated deployment to staging and production environments.
* Tasks:
    * Define infrastructure-as-code (Terraform or similar) for core resources.
    * Set up staging environment mirroring production (DB, Redis, app services, monitoring).
    * Implement blue/green or rolling deployments.
#### Epic I4: Observability & Operations
* **Outcome:** End-to-end visibility into system health and performance.
* Tasks:
    * Integrate metrics (Prometheus/Grafana), logging (ELK or Loki), and tracing (OpenTelemetry).
    * Define SLOs for latency, error rate, and availability.
    * Implement alerting and on-call runbooks.
#### Epic I5: Security & Compliance Baseline
* **Outcome:** Reasonable security posture for a multi-tenant SaaS.
* Tasks:
    * Implement secrets management (Vault/SSM) and rotate credentials.
    * Harden Docker images (minimal base images, non-root, read-only FS where possible).
    * Implement encryption at rest and in transit (TLS, database encryption options).
    * Create an initial threat model and remediation backlog.
## 9. Cross-Cutting Concerns & Governance
### Epic X1: Product & UX Alignment
* **Outcome:** A living product spec and design system that keeps engineering aligned with the vision.
* Tasks:
    * Maintain a product requirements document (PRD) for each major feature.
    * Establish a design system (components, typography, spacing, colors) for the Liquid Glass UI.
    * Set up regular design/engineering review cycles.
### Epic X2: Data & Analytics
* **Outcome:** Insight into user behavior and product performance.
* Tasks:
    * Define core product metrics (activation, retention, task completion, time-to-inbox-zero).
    * Instrument events in frontend and backend for these metrics.
    * Build initial dashboards for product and ops.
### Epic X3: Documentation & Knowledge Base
* **Outcome:** High-quality internal documentation and a basic customer-facing help center.
* Tasks:
    * Maintain architecture diagrams and ADRs (Architecture Decision Records).
    * Document all public APIs and plugin contracts.
    * Build a simple docs site (e.g., MkDocs) deployed alongside the app.
***
This plan is intentionally high-level but decomposed into epics and tasks with explicit outcomes. In the next step, we will map these epics and key tasks into Linear as issues, ensuring each line item has a clear, outcome-oriented description suitable for tracking progress in the SaaS delivery roadmap.