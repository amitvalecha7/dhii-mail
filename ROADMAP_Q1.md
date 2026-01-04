# 🗺️ Product Roadmap (Q1 2026)
*Tactical Execution Plan for the "Liquid Workspace"*

**Status**: DRAFT
**Owner**: Product Owner (PO)

---

## 📅 Sprint 1: The Crystal Foundation (Current)
*Goal: Stabilize the Core Engine and Define the Rules.*

*   [x] **Core Kernel Refactor**: Verify Python Plugin System (Issue #23).
*   [x] **Shared Services**: DB, Auth, EventBus for Plugins (Issue #24).
*   [x] **The Schema**: Define `A2UI_SCHEMA.md` (Issue #52).
*   [ ] **The Factory**: Build `component_factory.py` (Issue #55 - Done).
*   [ ] **API Contract**: Document `ORCHESTRATOR_CONTRACT.md` (Issue #53).

## 📅 Sprint 2: The Ecosystem Explosion (Next)
*Goal: Populate the Empty Shell with "Life".*

*   **Communication OS**:
    *   [ ] **Hyper-Mail**: The Email Plugin (Issue #35).
    *   [ ] **Chrono-Cal**: The Calendar Plugin (Issue #36).
*   **Business OS**:
    *   [ ] **Deal-Flow**: The CRM Plugin (Issue #40).
    *   [ ] **Task-Master**: The Project Plugin (Issue #42).

## 📅 Sprint 3: The "Magic" Layer (Future)
*Goal: AI Agents that work *for* you.*

*   [ ] **Agentic Component Factory**: Fully automated UI generation from text.
*   [ ] **"Ghostwriter"**: AI that drafts emails contextually (Issue #46).
*   [ ] **"Analyst"**: AI that visualizes spreadsheet data as A2UI Charts (Issue #47).

---
## 🎯 Acceptance Criteria for Q1
1.  **Zero "App Switching"**: A user can manage Leads, Emails, and Tasks in one view.
2.  **Dev Speed**: A new Plugin can be scaffolded in < 5 minutes using the Factory.
3.  **Stability**: Kernel handles 100+ active plugins without crashing.
