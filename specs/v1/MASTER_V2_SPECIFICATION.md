# Dhii-Mail V2: Master Specification

> **Version**: 2.0.0
> **Scope**: Architecture, Framework, Application Layer, Components, Features.
> **Status**: **Approved for Implementation**.

---

## 1. High-Level Architecture (The 4 Layers)

The system is organized into four distinct horizontal layers.

### Layer 1: Transport (The Senses)
*   **Role**: Active Data Synchronization.
*   **Mechanism**: Background AsyncIO Workers.
*   **Components**:
    *   **Email Sync**: IMAP Polling (5-min interval).
    *   **Calendar Sync**: CalDAV/Google API Polling.
    *   **Real-time**:: WebSockets for immediate notifications.

### Layer 2: Intelligence (The Brain)
*   **Role**: Data Processing & Insight Generation.
*   **Mechanism**: Event-Driven Pipelines.
*   **Components**:
    *   **Analysis Service**: LLM Summarization of incoming data.
    *   **Context Engine**: Entity Extraction (Dates, People, Urgency).
    *   **Neural Loop**: Ambiguity Resolution (asking the user for clarification).

### Layer 3: Application (The Face)
*   **Role**: Dynamic UI Orchestration.
*   **Mechanism**: "Symphony" Orchestrator + "Liquid Glass" Host.
*   **Components**:
    *   **Intent Engine**: Maps User Prompt -> Plugin Capability.
    *   **Layout Composer**: Generates A2UI JSON Trees.
    *   **Component Host**: Generic React Frontend that renders JSON.

### Layer 4: Persistence (The Memory)
*   **Role**: Reliable Data Storage.
*   **Mechanism**: SQLite (Local) + Encrypted Secrets.
*   **Components**:
    *   `email.db`, `calendar.db`, `core.db`.
    *   `SecretStore`: Fernet-encrypted credentials.

---

## 2. Plugin Framework 2.0 (The Contract)

A strict, Async-First, and Type-Safe interface for all extensions.

### 2.1 Core Interface
```python
class PluginInterface(ABC):
    async def on_load(self, config: Dict): ...
    async def on_ready(self): ...
    async def health_check(self) -> HealthStatus: ...
    
    @property
    def capabilities(self) -> List[PluginCapability]: ...

    async def execute_capability(
        self, 
        id: str, 
        params: Dict, 
        context: ExecutionContext
    ) -> Any: ...
```

### 2.2 Schemas & Safety
*   **Pydantic Models**: Inputs and Outputs must be defined as Pydantic classes for auto-validation.
*   **Sandboxing**: Plugins run with restricted imports (No `os`, `sys`, `subprocess`).
*   **Resilience**: Circuit Breakers prevent one plugin from crashing the Kernel.

---

## 3. Application Layer 2.0 (A2UI)

### 3.1 The "Symphony" Orchestrator (Backend)
*   **Function**: Receives a User Prompt ("Help me prepare for the meeting").
*   **Process**:
    1.  **Intent**: Identifies needed capabilities (Email Search, Calendar Lookup).
    2.  **Execution**: Calls Plugins in parallel.
    3.  **Synthesis**: Aggregates results.
    4.  **Composition**: Returns an A2UI JSON Tree.

### 3.2 Component Catalog (Logical)
The Frontend is a "Dumb Host" that only knows how to render these primitives:

*   **Containers**:
    *   `AppShell`: Top-level window manager.
    *   `Pane`: Vertical column.
    *   `Grid`: 2D Layout.

*   **Data Displays**:
    *   `Card`: Basic unit of content.
    *   `List`: Linear collection of items.
    *   `Table`: Row/Column data.
    *   `StatsGrid`: Key-Value metrics (e.g., "5 Unread").

*   **Interactions**:
    *   `Action`: Button/Link triggering a Plugin Capability.
    *   `Input`: Text/Form field.

---

## 4. Auth Flow Summary

Authentication is centralized in the Kernel, not Plugins.

1.  **Frontend**: User provides `password`.
2.  **Kernel**: Verifies against `auth.db` (Hashed).
3.  **Session**: Issues a JWT (Stateless).
4.  **Plugin Access**: Plugins do not handle User Auth; they use stored Credentials (Encrypted) to access external APIs (Gmail, Outlook).

---

## 5. Core Features & Plugins

| Plugin | Features | 2.0 Status |
| :--- | :--- | :--- |
| **Email** | Send, Receive, Search, Threading | **Issue #90** (Migrating) |
| **Calendar** | Sync Events, Resolve Conflicts, Availability | **Issue #81** (Planned) |
| **Intelligence** | Summarize, Prioritize, Extract Action Items | **Issue #78** (Planned) |
| **CRM** | Contact Management, Deal Tracking | Future |
| **Tasks** | Todo Lists, Deadlines | Future |

---

## 6. Implementation Roadmap (GitHub Issues)

### Phase 6.1: Framework 2.0 Foundation
*   **#85**: Core Contracts & Types (`PluginInterface`, `ExecutionContext`)
*   **#88**: Kernel PluginManager v2 (Async Lifecycle)
*   **#89**: Dev Tools CLI (`create`, `validate`, `bundle`)
*   **#90**: Migrate Email Plugin to v2

### Phase 5: V1 Critical Path
*   **Transport Layer**:
    *   #82: Email Sync Engine (✅ Implemented)
    *   #81: Calendar Sync Engine
*   **Intelligence Layer**:
    *   #78: Intelligence Data Processor (LLM Analysis)
*   **Application Layer**:
    *   #84: Symphony Orchestrator (Backend)
    *   #83: Liquid Glass Component Host (Frontend)
*   **Persistence Layer**:
    *   #80: Persistence Migration (SQLite + Encrypted Secrets)

### Phase 2-4: Plugin Ecosystem (30+ Issues)
*   **Core OS**: Email (#35 ✅), Calendar (#36 ✅), Meetings (#37 ✅)
*   **Bridges**: WhatsApp (#38 ✅), Teams (#39 ✅)
*   **Business**: CRM (#40 ✅), Finance (#41), Projects (#42), Legal (#43), Marketing (#50)
*   **Social**: Dhii-Connect (#44), Sync-Chat (#45)
*   **Creative**: Writer (#46), Pixel (#47), Brand (#48)
*   **Dev Tools**: Dev-Hub (#49)

### Infrastructure & Architecture (Completed)
*   #1: A2UI Standard Router ✅
*   #2: Replace Custom Frontend ✅
*   #23: Core Kernel Refactor ✅
*   #24: Shared Services ✅
*   #34: Lazy Loading ✅
*   #65: Glass Wall Sandbox ✅
*   #76: React Frontend Integration ✅

---

## 7. Project Structure 2.0 (Physical Layout)

```text
a2ui_integration/
├── framework/       # The V2 SDK (Types, Contracts)
├── core/            # The Runtime Kernel
├── cli/             # Developer Tools
└── plugins/         # Feature Implementations
    └── email/
        ├── manifest.json
        ├── plugin.py (V2)
        └── models.py
```
