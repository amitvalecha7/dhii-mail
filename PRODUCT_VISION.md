# 👁️ Product Vision: The "Liquid Workspace"
*Defining the North Star for Dhii-Mail (Issue #51)*

**Status**: DRAFT
**Owner**: Product Owner (PO)

---

## 1. The Core Philosophy
**Dhii-Mail is not an email client.** It is a **Liquid Workspace** that aggregates your digital life (Communication, Schedule, Deals, Tasks) into a single, fluid interface.

### The "Liquid Glass" Metaphor
Legacy apps are rigid containers (Outlook, Salesforce, Trello).
**Dhii-Mail is Liquid.**
*   The UI adapts to the *content*, not the tool.
*   An email from a client isn't just text; it *becomes* a Deal Card.
*   A calendar invite isn't just a block; it *becomes* a Video Conference bubble.

## 2. Core Values
1.  **Fluidity First**: No context switching. Everything is an `A2UI Component` in a unified stream.
2.  **Privacy by Design**: The "Kernel" runs locally. Your data is yours.
3.  **Speed as a Feature**: < 100ms interactions. Optimistic UI always.
4.  **AI-First, UI-Second**: The UI is a derivative of the AI's understanding of intent.

## 3. Target User Personas
### 👩‍💻 The "Flow" Professional
*   **Role**: Founder / Executive / High-Output Individual.
*   **Pain**: Drowning in tabs (Gmail, Slack, HubSpot, Jira).
*   **Need**: A "Command Center" where they can approve a PR, sign a contract, and reply to an email without changing windows.

### 🧪 The "Plugin" Hacker
*   **Role**: Developer / Integrator.
*   **Need**: A hackable workspace. They want to write a Python script that turns their "Server Only" logs into a visual dashboard in their inbox.

## 4. Key Differentiators
| Feature | Legacy Mail (Gmail/Outlook) | Dhii-Mail (Liquid) |
| :--- | :--- | :--- |
| **Interface** | Static HTML Lists | **Dynamic A2UI Canvas** |
| **Extensibility** | Web Add-ins (Limited) | **Full Python Kernel (Unlimited)** |
| **Intelligence** | "Smart Reply" (Text) | **"Agentic Actions" (Work)** |
| **Data Model** | Siloed API | **Shared Knowledge Graph** |

## 5. Strategic Pillars (Technical Foundation)
### A. The A2UI Standard
The universal language for Agents to talk to Humans. A standardized JSON schema that describes UI intent, not pixel placement.

### B. The Skill Store
A marketplace of capabilities. Developers build plugins (Skills) that the Kernel can discover, load, and orchestrate.

### C. Enterprise-Grade Trust
Observability, Security, and Governance are not afterthoughts. Deep APM integration and structured logging are built-in.
