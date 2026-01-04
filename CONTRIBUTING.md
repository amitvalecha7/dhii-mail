# Contributing to Dhii Mail

Welcome to the **Dhii Mail** project! We are building the "Liquid Workspace"—an AI-native, fluid interface that adapts to user intent.

This guide will help you set up your development environment and understand our architectural standards.

## 📚 Strategic Context

Before diving into code, please familiarize yourself with our core strategic documents:

- **[Product Vision](PRODUCT_VISION.md)**: Understanding the "Liquid Workspace" and "Glass Wall" concepts.
- **[Roadmap](ROADMAP_Q1.md)**: Our phased execution plan for Q1 2026.
- **[Security Manifesto](SECURITY_MANIFESTO.md)**: Our commitment to local-first privacy and safety.

## 🛠 Prerequisites

Ensure you have the following installed:

- **Node.js** (v18+)
- **Python** (v3.10+)
- **Git**

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dhii-mail/dhii-mail.git
    cd dhii-mail
    ```

2.  **Install Dependencies:**
    ```bash
    # Frontend / Core SDK
    npm install

    # Backend / Middleware
    pip install -r requirements.txt
    ```

## 🏗 Architecture & Standards

We follow strict architectural contracts to ensure modularity and security.

### Key Specifications
- **[A2UI Schema](A2UI_SCHEMA.md)**: The universal protocol for Agent-to-UI rendering. All UI components must comply with this schema.
- **[Orchestrator API](ORCHESTRATOR_API.md)**: The bridge between the client and the AI agents.
- **[Plugin Governance](PLUGIN_GOVERNANCE.md)**: Rules for the capability-based security model.
- **[UI Guidelines](UI_GUIDELINES.md)**: Design system and motion principles for the "Liquid Glass" feel.

### Directory Structure
- `/a2ui_integration`: Core Kernel and SDK logic.
- `/middleware`: Python-based backend services (APM, Auth).
- `/plugins`: Community and first-party plugins (sandboxed).

## workflow Development Workflow

1.  **Branching**:
    - Use `feature/` for new capabilities.
    - Use `fix/` for bug repairs.
    - Use `chore/` for maintenance.

2.  **Commits**:
    - We follow [Conventional Commits](https://www.conventionalcommits.org/).
    - Example: `feat: add new calendar agent component`

3.  **Pull Requests**:
    - All PRs must pass CI checks (linting, tests).
    - Link PRs to relevant GitHub Issues.

## 🧪 Testing

- **Unit Tests**: Run `npm test` for JS/TS and `pytest` for Python.
- **Integration**: Ensure A2UI components render correctly in the test harness.

---

Thank you for contributing to the future of intelligent communication!
