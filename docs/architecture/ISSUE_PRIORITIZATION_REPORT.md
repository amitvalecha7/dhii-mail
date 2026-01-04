# 📋 Strategic Issue Prioritization & Roadmap

## 🎯 Executive Summary
The path to the **"Unified Product Vision" (Kernel + Liquid Glass)** requires a strict order of operations. We cannot build "Liquid Glass UI" (#19) until the "Frontend Client" (#2) is replaced. We cannot Repace the Client until the "Backend Kernel" (#23) sends standard JSON.

---

## 🏗️ Phase 1: The Foundation (Kernel & Standards)
*Build the "Operating System" first.*

| Priority | Issue | Title | Reason |
| :--- | :--- | :--- | :--- |
| **P0** | **#23** | **Major Refactor: Kernel + Plugin Migration** | The root task. Defines `Core Types`, `PluginLoader`, and `Folder Structure`. |
| **P0** | **#24** | **Shared Kernel Services (DB, Auth)** | Plugins cannot function without a shared Database session and Event Bus. |
| **P0** | **#15** | **Implement Streaming Transport** | Essential for the "Real-time" feel of the new AI features. |

> **Action**: These must be done **sequentially** starting now.

---

## 🌉 Phase 2: The Bridge (Frontend & Rendering)
*Make the UI talk to the new Kernel.*

| Priority | Issue | Title | Reason |
| :--- | :--- | :--- | :--- |
| **P1** | **#2** | **Replace Custom Frontend with `@a2ui/lit`** | The current frontend *will break* when #23 is done. We need the official A2UI renderer to display the new "Adjacency List" JSON. |
| **P1** | **#1** | **Refactor Orchestrator** | *Note: This is effectively merged into #23, but checking it off ensures the "Routing" logic is correct.* |

---

## 📦 Phase 3: Content Migration (Plugins)
*Move existing logic into the new "Homes".*

| Priority | Issue | Title | Reason |
| :--- | :--- | :--- | :--- |
| **P2** | **#16** | **Marketing DB Persistence** | Implement this *as part of* the migration of Marketing Manager to `/plugins/marketing/`. |
| **P2** | **#18** | **Consolidate AI Agents** | Move `ai_engine.py` logic into `plugins/core/ai/`. |
| **P2** | **#17** | **Tool Registry** | *Superseded by #23 (Plugin Manifests).* Can be closed/merged. |

---

## ✨ Phase 4: Innovation (The "Liquid Glass" Vision)
*Build the user-facing features on top.*

| Priority | Issue | Title | Reason |
| :--- | :--- | :--- | :--- |
| **P3** | **#19** | **Liquid Glass UI Theme** | Visual styling applied to the standard components from Phase 2. |
| **P3** | **#20** | **generative 'Context Cards'** | AI Logic that injects cards into the Stream. |
| **P3** | **#21** | **Universal Plugin Search** | Relies on Kernel Search Service (Phase 1). |
| **P3** | **#22** | **Skill Store Interface** | The admin panel for the new `PluginManager`. |

---

## 🛠️ Recommended Immediate Actions
1.  **Mark #23 & #24 as "In Progress"**.
2.  **Close #17** (Tool Registry) as "Superseded by #23".
3.  **Merge #1** (Orchestrator) into #23's scope.
4.  **Begin coding #23**: Create `a2ui_integration/core/` directory.
