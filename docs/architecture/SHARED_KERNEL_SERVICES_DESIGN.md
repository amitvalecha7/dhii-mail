# 🧩 Shared Kernel Services Design

## 🎯 Objective
To identify overlapping requirements across plugins (Email, Calendar, Tasks, etc.) and centralize them into **Kernel Services**. This prevents "bloat" where every plugin re-implements core logic like Database connections or Auth.

---

## 🏗️ 1. The Database Strategy: "Federated with Shared Access"

### The Problem
If every plugin opens its own `sqlite3` connection, we can't do JOINs (e.g., "Show emails linked to this meeting") and we waste resources.

### The Solution: `Kernel.DatabaseService`
The Kernel exposes a **ORM Provider** (SQLAlchemy) that plugins hook into.

*   **Shared Schema Registry**: When a plugin loads, it registers its Models (Tables) with the Kernel.
    *   *Email Plugin* registers: `emails`, `folders`
    *   *Calendar Plugin* registers: `events`, `attendees`
*   **Unified Session**: The Kernel provides a `get_session()` capability. This allows **Cross-Plugin Queries**.
    *   *Example*: "Find all `events` (Calendar) where `organizer_email` matches a `sender` (Email)."
*   **Migration Management**: The Kernel runs a unified `alembic` migration process, checking `version` strings in each plugin's `manifest.json`.

```python
# plugins/email/plugin.py
def on_load(kernel):
    # Plugins don't open DBs. They define Models.
    kernel.db.register_models(EmailModel, FolderModel)

# Accessing Data
session = kernel.db.get_session()
emails = session.query(EmailModel).all()
```

---

## 🔑 2. Identity & Authentication Service

### The Problem
Plugins shouldn't handle User Login or Token parsing. External Integrations (Jira, Gmail) need secure token storage.

### The Solution: `Kernel.IdentityService`
*   **User Context**: Injects `current_user` into every Plugin method.
*   **Secrets Vault**: A secure store for API Keys (OpenAI, Gmail OAuth, Jira Tokens).
    *   *Jira Plugin* asks: `kernel.vault.get_token("jira_oauth")`
    *   *Kernel* checks: "Does User have permission?" -> Returns Token.

---

## 🧠 3. Intelligence Service (Vector DB & AI)

### The Problem
If the "Email Plugin" learns that "John is the CEO", the "Calendar Plugin" needs to know that too (to prioritize his meetings).

### The Solution: `Kernel.MemoryService` (Vector Store)
*   **Shared Embeddings**: A single Vector Database (Chroma/FAISS) managed by the Kernel.
*   **Memory Scopes**:
    *   `Global`: "User likes morning meetings" (Accessible to all).
    *   `Plugin-Private`: "Draft content XYZ" (Accessible only to Email).
*   **Agent usage**: The AI Agent queries the *Shared Memory* before calling *any* plugin tool.

---

## 📡 4. Event Bus (The "Nervous System")

### The Problem
Plugins need to react to each other without importing each other's code (tight coupling).

### The Solution: `Kernel.EventBus`
A Publish/Subscribe system.

*   **Standard Events**:
    *   `entity.created` (e.g., `email.created`, `event.created`)
    *   `user.interaction` (e.g., `button.clicked`)
*   **Flow**:
    1.  **Email Plugin**: Receives urgent mail -> `kernel.bus.publish("email.urgent_received", {subject: "Server Down"})`
    2.  **SMS Plugin**: Subscribed to `email.urgent_received` -> Sends SMS.
    3.  **Calendar Plugin**: Subscribed to `email.urgent_received` -> Blocks out time for "Firefighting".

---

## 🎨 5. UI Component Library (A2UI)

### The Problem
We don't want the Email Plugin rendering "Blue Cards" and the Calendar Plugin rendering "Red Cards". Inconsistent UX.

### The Solution: `Kernel.ComponentFactory`
*   **Standard Components**: The Kernel provides the *exact* Python classes for `Card`, `List`, `Button`.
*   **Theme Enforcement**: Plugins pass *content*, Kernel applies *style*.
*   *Plugin Code*:
    ```python
    # Bad: return {"type": "div", "style": "color: blue"}
    # Good: return kernel.ui.Card(title="Hello", variant="primary")
    ```

---

## 📝 Summary of Shared Responsibilities

| Component | Managed By Plugin | Managed By Kernel (Shared) |
| :--- | :--- | :--- |
| **Database** | Table Definitions (Models) | Connection, Session, Migrations, JOINs |
| **Auth** | Resource Permissions | User Login, Session, OAuth Token Vault |
| **AI/LLM** | Prompt Templates | LLM Client, Vector Memory, Context Window |
| **UI** | View Logic (Layout) | Theme, Component Classes, AppShell |
| **Events** | Triggers specific to Domain | Message Broker, Subscription Registry |
