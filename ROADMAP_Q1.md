# Product Roadmap: Q1 2026

## 🎯 Objective
Establish the **Dhii Mail Core Kernel** as a stable, observable, and extensible platform, and define the **A2UI Standard** to enable the rapid development of the Plugin Ecosystem.

---

## ✅ Phase 1: Foundation & Core Services (Completed)
**Focus**: Building the bedrock. A robust, modular Kernel that supports dynamic plugins and deep observability.

- **[COMPLETED] Core Kernel Architecture** (Issue #23)
  - Plugin Lifecycle Management (Load/Unload/Reload).
  - Dependency Injection & Service Registry.
- **[COMPLETED] Shared Services Layer** (Issue #24)
  - Centralized Database (SQLAlchemy), Auth (PASETO), and Event Bus.
- **[COMPLETED] Observability Suite** (Issue #24, #25, #26)
  - Structured Logging with Correlation IDs.
  - Health Monitoring (Liveness/Readiness Probes).
  - Centralized Error Tracking & APM Middleware.

## ✅ Phase 2: A2UI Integration & Frontend (Completed)
**Focus**: Proving the "AI-First" UI model. Transitioning from static templates to dynamic graph generation.

- **[COMPLETED] A2UI Orchestrator Refactor** (Issue #31/25)
  - Shift to Adjacency List Model (`ComponentGraph`) for O(1) updates.
  - Performance benchmarking and optimization.
- **[COMPLETED] Frontend Modernization** (Issue #32/26)
  - Migration to `@a2ui/lit` web components.
  - Implementation of the `MeetingAssistantApp` as a reference client.

---

## ✅ Phase 3: Strategy & Standardization (Completed)
**Focus**: Documenting the "Laws of the Land". Ensuring all future development adheres to strict contracts.

- **[COMPLETED] Product Vision & Roadmap** (Issue #50)
  - Defining the North Star and Q1 goals.
- **[COMPLETED] A2UI Schema Contract** (Issue #51)
  - Formalizing the JSON Schema for AppShell, Cards, and Panes.
- **[COMPLETED] Plugin SDK Governance** (Issue #52)
  - Defining sandbox rules, memory limits, and import restrictions.
- **[COMPLETED] Orchestrator API Contract** (Issue #53)
  - Documenting the protocol for Agent-to-UI communication.

## 🚧 Phase 4: The Plugin Ecosystem (In Progress)
**Focus**: Expanding capabilities. Building the "Apps" that run on the OS.

- **[COMPLETED] Universal Plugin SDK** (Issue #21)
  - Developer tools for building Dhii Mail plugins.
- **[IN PROGRESS] Domain Plugins**
  - **Hyper-Mail**: Next-gen email experience (Issue #35) - [COMPLETED].
  - **Chrono-Calendar**: AI-managed scheduling (Issue #36) - [COMPLETED].
  - **Holo-Meet**: Meeting intelligence (Issue #37) - [COMPLETED].
  - **Deal-Flow CRM**: Sales pipeline integration (Issue #40) - [COMPLETED].
- **[PLANNED] Skill Store** (Issue #22)
  - Registry and marketplace for discovering plugins.

---

## 📈 Success Metrics (KPIs)
1.  **System Stability**: 99.9% Kernel Uptime (excluding plugin crashes).
2.  **Performance**: <50ms Overhead for A2UI Graph Generation.
3.  **Adoption**: 5+ Core Plugins fully migrated to the new Architecture.
4.  **Developer Experience**: <15 minutes to scaffold a new Plugin "Hello World".
