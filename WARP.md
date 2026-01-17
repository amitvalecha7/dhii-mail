# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Purpose & Licensing

Dhii-Mail is an intelligent email and meeting management platform built around the **A2UI (Adaptive Agent User Interface)** architecture and a "Liquid Workspace" UI paradigm. The system unifies multiple interaction modes (inbox, calendar, chat, analytics) into a single AppShell-driven experience with a keyboard-first command palette.

**Licensing is extremely restrictive.** Per `README.md` and `LICENSE`, this codebase is proprietary and intended for **exclusive private use by Amit Valecha**. When operating in this repo:
- Do not surface source code or proprietary implementation details outside this environment unless the user explicitly requests it.
- Assume all architectural documents and implementation details are confidential.

## Core Commands & Workflows

### 1. Python Backend (FastAPI / Kernel services)

All Python commands assume you are running from the repo root (`dhii-mail`) with an active virtual environment.

**Environment setup**
- Create and activate a virtual environment (adjust for your shell/OS):
  - Create: `python -m venv venv`
  - Activate (Unix-like): `source venv/bin/activate`
  - Activate (Windows PowerShell): `venv\Scripts\Activate.ps1`
- Install dependencies:
  - `pip install -r requirements.txt`

**Run the main application kernel (monolithic FastAPI app)**

This is the primary entry point described in `README.md` and `BACKEND_ARCHITECTURE.md`:
- `python main.py --port 8005`

Key behavior:
- Serves the main FastAPI application on `http://localhost:8005`.
- OpenAPI docs: `http://localhost:8005/docs`.

**Run supporting backend services directly (when needed)**

The backend can also be split into focused services, each implemented as its own FastAPI app:
- Chat / AI intent server (see `chat_api_v2.py`):
  - `python chat_api_v2.py`  (designed to run on port `8006`)
- Authentication server (see `auth_api.py`):
  - `python auth_api.py`     (designed to run on port `8007`)

These are useful when debugging specific concerns (chat pipeline vs. auth) without running the entire stack via Docker.

### 2. A2UI React AppShell Client (`a2ui_integration/client`)

The unified A2UI front-end is a Vite-based React app that consumes JSON A2UI layouts from the kernel.

From the repo root:
- `cd a2ui_integration/client`

**Install Node dependencies**
- `npm install`

**Run the dev server**
- `npm run dev`

This starts the Vite dev server for the AppShell. It is configured (via `docker-compose.yml` and client code) to talk to the kernel service; in full-stack mode the `frontend` container points to `kernel:8005`.

**Build and preview production assets**
- Build: `npm run build`
- Preview built bundle: `npm run preview`

Note: `CONTRIBUTING.md` mentions `npm test`, but the current `a2ui_integration/client/package.json` does **not** define a `test` script. Add one there before relying on `npm test`.

### 3. Full Stack via Docker Compose

To bring up the full microservice-style stack (kernel, frontend, registry, gateway, DB, Redis, and mock orchestrator) use the provided `docker-compose.yml` from the repo root:

- Start the stack:
  - `docker-compose up`
- Start in detached mode:
  - `docker-compose up -d`
- Tear down:
  - `docker-compose down`

Key services and ports (see `docker-compose.yml` for full details):
- `db` (PostgreSQL): `5432:5432`
- `redis` (Redis cache / pubsub): `6379:6379`
- `mock-orchestrator` (Flask-based mock A2UI orchestrator for frontend dev): `8000:8000`
- `kernel` (main FastAPI backend, built from repo): `8005:8005`
- `frontend` (AppShell web client built from `a2ui_integration/client`): `3001:3001`
- `plugin-registry` (Flask-based plugin registry service): `5000:5000`
- `api-gateway` (gateway / edge service): `8080:8080`

When working on cross-service flows (e.g., plugins behind the Glass Wall, registry, and gateway routing), prefer running the stack via Docker Compose so that inter-service URLs and environment variables match the architecture docs.

### 4. Testing & Quality

This project ships both ad-hoc Python test scripts and a more structured `pytest`-based testing architecture.

**Targeted integration tests (from `README.md`)**
Run from the repo root with the virtualenv active:
- AppShell integration:
  - `python test_appshell_integration.py`
- Command palette integration:
  - `python test_command_palette_integration.py`
- A2UI state machine validation:
  - `python test_state_machine.py`

Use these when validating changes that touch A2UI orchestration, navigation flows, or command handling.

**Pytest test suite (from `BACKEND_ARCHITECTURE.md`)**

The backend architecture doc standardizes on `pytest` as the primary test runner:
- Run all tests discovered in the repo:
  - `pytest`
- Run a single file:
  - `pytest test_api_endpoints.py`
- Run a single test or subset by expression:
  - `pytest test_auth_api.py -k "login"`

Coverage (backend):
- `pytest --cov=dhii_mail --cov-report=html`

When adding new tests, prefer `pytest` conventions (`test_*.py`, `Test*` classes, and fixtures), so they integrate cleanly with the existing and documented structure.

**Static analysis & linting (Python)**

`requirements.txt` includes a comprehensive set of quality tools (ruff, black, flake8, mypy, bandit, etc.). Common commands that align with these dependencies are:
- Format code:
  - `black .`
  - `isort .`
- Lint:
  - `ruff .`
  - `flake8 .`
- Static types on core modules:
  - `mypy .`

When updating CI or running local pre-flight checks, prefer these tools rather than adding new ones.

## High-Level Architecture & Code Structure

### 1. A2UI / Liquid Workspace Model

The core conceptual architecture is captured in `README.md`, `ARCHITECTURE.md`, and `A2UI_SCHEMA.md`:

- **Liquid Workspace**: The UI is a dynamic composition of panes and cards generated from backend-provided JSON, not a static set of screens.
- **A2UI Protocol**: The backend (Kernel / orchestrator) sends JSON schemas describing UI layout and components; the AppShell client renders them without embedding business logic.
- **Glass Wall**: A security boundary between the core kernel and plugins. Plugins are treated as untrusted; all interaction is mediated and capability-scoped.

The unification work (phases 16–21 in `README.md`) replaces earlier dual-UI approaches (Glass UI vs. A2UI dashboard) with a single, validated A2UI state machine plus orchestrator.

### 2. Major Code Areas

High-level, the repository is organized into these important areas (see the files/directories directly for details):

- **A2UI Core (`a2ui_integration/`)**
  - Houses the A2UI state machine, orchestrator, AppShell framework, command palette, and router.
  - Key modules referenced in `README.md` include:
    - `a2ui_state_machine.py` (11-state FSM controlling UI state and transitions).
    - `a2ui_orchestrator.py` (translates intents + context into A2UI JSON layouts).
    - `a2ui_appshell.py` (three-pane layout and common shell chrome).
    - `a2ui_command_palette.py` (keyboard-first command system with fuzzy search).
    - `a2ui_router_updated.py` (FastAPI routing for A2UI endpoints such as `/api/a2ui/dashboard`, `/api/a2ui/email/inbox`, etc.).

- **Backend Core / Kernel (root-level Python modules)**
  - `main.py`: Main FastAPI application, configured as the dhii Mail API (port 8005) with OpenAPI docs, CORS, and security middleware.
  - `ai_engine.py`: Central AI engine responsible for email and chat intelligence (sentiment, classification, summarization, threat analysis, etc.).
  - Domain managers that encapsulate specific functional areas:
    - `email_manager.py`: IMAP/SMTP integration and email lifecycle (fetch, classify, move, delete, etc.).
    - `calendar_manager.py`: Calendar and scheduling logic (events, free/busy, invitations).
    - `video_manager.py`: Video conferencing abstraction (meeting lifecycle, streaming hooks).
    - `marketing_manager.py`: Campaign management, audiences, and analytics.
    - `security_manager.py`: Auth, permissions, threat detection, and security audits.
    - `database.py` / `database_manager.py`: Persistence layer for users, email accounts, emails, and analytics, typically backed by PostgreSQL in production and SQLite in dev.
    - `websocket_manager.py`: Real-time notifications and WebSocket message routing.

- **Microservices & Middleware (`middleware/` + Docker stack)**
  - `middleware/registry`: Plugin registry service (Flask-based) built into the `plugin-registry` Docker service.
  - `middleware/gateway`: API gateway / edge service built into `api-gateway`.
  - `mock_server`: Mock orchestrator used by the `mock-orchestrator` service for frontend development when the full kernel is not running.

- **Front-end AppShell (`a2ui_integration/client`)**
  - Vite + React app (see `package.json`) that implements the AppShell UI and consumes A2UI schemas.
  - Primarily a "dumb" renderer: the backend determines layout and content; the client focuses on rendering panes, cards, and command palette interactions.

### 3. Data & Control Flow

**A2UI loop (from `ARCHITECTURE.md`):**
1. User interacts with the AppShell (click, keyboard, or command palette).
2. The client sends an event (e.g., `{"type": "submit", "payload": "Schedule meeting"}`) to the kernel.
3. The kernel orchestrates:
   - Interprets intent (via `ai_engine.py` and intent processors).
   - Consults relevant domain managers (email, calendar, marketing, etc.).
   - Optionally executes plugins through the plugin governance layer and the Glass Wall.
4. The kernel returns an A2UI JSON schema describing the updated layout, components, and state.
5. The AppShell re-renders without a full page reload.

**Microservice deployment (via Docker Compose):**
- The `kernel` service encapsulates main backend logic and orchestrator.
- The `frontend` service serves the AppShell, configured to target the kernel.
- The `plugin-registry` manages plugin manifests and assets.
- The `api-gateway` provides a single public entry point and handles routing, TLS termination (in production), and aggregation of kernel/registry responses.
- `db` and `redis` provide persistence and caching for stateful operations.

### 4. Security Model

Security is multi-layered and central to the architecture:
- **Glass Wall**: Plugins are always executed in sandboxed environments with explicit capabilities; the kernel sanitizes and redacts data crossing this boundary.
- **Authentication & Authorization**:
  - JWT/PASETO tokens, password hashing (bcrypt/Argon2), and permission checks implemented primarily in `security_manager.py` and `auth_api.py`.
- **Transport & API Security**:
  - FastAPI middleware configures security headers (`X-Frame-Options`, `X-Content-Type-Options`, HSTS, etc.) as documented in `BACKEND_ARCHITECTURE.md`.
- **Observability & Auditing**:
  - Structured logging (e.g., via `structlog`, `loguru`) and metrics (Prometheus, tracing) are wired through middleware and helpers to enable monitoring without leaking sensitive payloads.

### 5. Testing Strategy

The architecture docs describe a multi-layer testing approach:
- **Unit tests**: For core managers (email, auth, chat, security, etc.), typically following `test_*` naming conventions.
- **Integration tests**: For API endpoints, WebSockets, and multi-service flows (including A2UI orchestration).
- **Performance & load tests**: Stress, load, and endurance tests to validate scalability characteristics.

In practice, many tests are currently implemented as `test_*.py` files at the repo root (e.g., `test_api_endpoints.py`, `test_auth_api*.py`), complemented by the targeted integration scripts listed in `README.md`. Prefer adding new tests to the pytest suite and reusing existing patterns.

---

Future Warp agents should rely on this file for:
- Choosing the right dev workflow (bare FastAPI vs. Docker Compose, direct Python scripts vs. pytest).
- Understanding where to place new features (which manager, which A2UI component, which service).
- Respecting the strict licensing and security constraints when generating or transforming code.
