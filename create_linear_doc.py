import os
import sys
from typing import Dict, Any

import requests

LINEAR_API_URL = "https://api.linear.app/graphql"


def graphql_request(api_key: str, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        LINEAR_API_URL,
        headers=headers,
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def get_project_id(api_key: str, project_name: str) -> str:
    query = """
    query {
      projects(first: 100) {
        nodes {
          id
          name
        }
      }
    }
    """
    data = graphql_request(api_key, query)
    for proj in data["projects"]["nodes"]:
        if proj["name"] == project_name:
            return proj["id"]
    raise RuntimeError(f"Project '{project_name}' not found")


def create_document(api_key: str, project_id: str, title: str, content: str) -> str:
    mutation = """
    mutation DocumentCreate($input: DocumentCreateInput!) {
      documentCreate(input: $input) {
        success
        document {
          id
          title
          url
        }
      }
    }
    """
    input_data: Dict[str, Any] = {
        "title": title,
        "content": content,
        "projectId": project_id,
    }
    data = graphql_request(api_key, mutation, {"input": input_data})
    doc = data["documentCreate"]["document"]
    print(f"Created document '{doc['title']}' at {doc.get('url')}")
    return doc["id"]


DOC_TITLE = "Dhii-Mail Architecture – Kernel, Mail, Calendar & Tasks Design"

DOC_CONTENT = """# Dhii-Mail Architecture – Kernel, Mail, Calendar & Tasks Design

This document summarizes the key design contracts across the Kernel, Mail, Calendar, and Tasks layers for the `Dhii-Mail SaaS – v1 Architecture & Delivery` project.

---

## 1. Kernel Service (K1–K6)

### 1.1 Kernel "Brain" API (K1)
- **Endpoints**
  - `POST /api/kernel/intent` → accepts `KernelIntentRequest`, returns `KernelIntentAck` with `correlation_id`.
  - `WebSocket /api/kernel/stream` → streams `A2UIEnvelope` messages keyed by `correlation_id`.
- **Core models**
  - `KernelIntentRequest` (sessionId, tenantId, userId, channel, locale, timezone, message).
  - `KernelIntentAck` (requestId, accepted, correlationId).
  - `A2UIEnvelope` (id, type, schemaVersion, correlationId, timestamp, payload).
- **Notes**
  - All LLM calls and orchestration live in the Kernel, not in the frontend.

### 1.2 Intent Router (K2)
- Intent taxonomy: `mail.*`, `calendar.*`, `tasks.*`, `workspace.*`, `kernel.*`, `plugin.*`.
- Pydantic models: `IntentNamespace`, `IntentName`, params models (e.g. `MailListParams`, `MailReplyParams`), `KernelResolvedIntent`.
- Router contract: `IntentRouter.parse_and_route(request, context) -> KernelResolvedIntent`.

### 1.3 Context Engine (K3)
- Models: `ContextItemKind`, `ContextItem`, `KernelContext`.
- Storage:
  - Redis: `ctx:session:{tenant_id}:{user_id}:{session_id}` for short-term/session context.
  - Postgres: `user_preferences` for long-term preferences.
- API: `ContextStore.get_for_prompt(session_id, tenant_id, user_id, limit) -> KernelContext`.

### 1.4 Permission & Policy Engine (K4)
- Models: `Action`, `Resource`, `Subject`, `PolicyRule`.
- DB: `policy_rules` table storing allow/deny rules per tenant/role.
- API: `PermissionEngine.is_allowed(subject, action, resource, context?) -> bool`.

### 1.5 Tooling & Orchestration (K5)
- Models: `ToolDefinition`, `ToolCall`, `ToolResult`.
- Executor: `ToolExecutor.execute(call, ctx, intent) -> ToolResult`.
- Kernel tools wrap Mail/Calendar/Tasks/Linear/Plugins behind this abstraction.

### 1.6 Observability & Limits (K6)
- Logging fields: `service='kernel'`, `request_id`, `correlation_id`, `tenant_id`, `user_id`, `session_id`, `event`.
- Spans: `kernel.intent`, `kernel.tool`, `kernel.llm`.
- Limits: `KernelLimits` (max tool calls, max tokens, timeouts).
- Health: `/api/kernel/health`, `/api/kernel/ready`.

---

## 2. Mail (A1/B3)

### 2.1 Mail domain & API (A1.1)
- Models:
  - `MailAddress` (name?, email).
  - `MailMessage` (id, threadId, tenantId, userId, subject, from, to/cc/bcc, sentAt, receivedAt, snippet, bodyHtml/bodyText, folder, isRead, labels).
  - `MailThread` (id, tenantId, userId, subject, participants, lastMessageAt, snippet, folder, labels).
- REST API `/api/mail`:
  - `GET /threads` → list `MailThread` with filters (folder, label, q, limit, cursor).
  - `GET /threads/{thread_id}` → `{ thread, messages }`.
  - `POST /threads/{thread_id}/reply` → `{ status, messageId }`.
  - `POST /threads/{thread_id}/actions` → `{ status: 'ok' }`.

### 2.2 Mail integration (B3.1)
- `mail_accounts` table storing provider tokens/settings.
- `MailSyncWorker.initial_sync` / `incremental_sync` for IMAP/API sync.
- `MailProviderAdapter` for Gmail, O365, generic IMAP/SMTP.

---

## 3. Calendar (A3/B4)

### 3.1 Calendar domain & API (A3.1)
- Models:
  - `Attendee` (name?, email, responseStatus).
  - `CalendarEvent` (id, calendarId, tenantId, userId, title, description, start, end, allDay, location, attendees, organizer, status, recurrence, conferenceLink).
- REST API `/api/calendar`:
  - `GET /events` (from, to, calendarId?, limit?, cursor?) → `CalendarEvent[]`.
  - `POST /events` → `{ event }`.
  - `PATCH /events/{event_id}` → `{ event }`.
  - `DELETE /events/{event_id}` → `{ status: 'ok' }`.

### 3.2 Calendar integration (B4.1)
- `calendar_accounts` table storing provider connections.
- `CalendarSyncWorker.initial_sync` / `incremental_sync`.
- `CalendarProviderAdapter` for Google, Microsoft 365, CalDAV.

---

## 4. Tasks (A4/B5)

### 4.1 Tasks domain & API (A4.1)
- Models:
  - `TaskStatus` (todo, in_progress, done, cancelled).
  - `TaskSource` (manual, email, calendar, linear).
  - `Task` (id, tenantId, userId, title, description, status, priority, dueDate, createdAt, updatedAt, source, sourceRef, labels).
- REST API `/api/tasks`:
  - `GET /api/tasks` (status?, label?, source?, q?, limit?, cursor?) → `{ items: Task[], nextCursor }`.
  - `GET /api/tasks/{task_id}` → `{ task }`.
  - `POST /api/tasks` → `{ task }`.
  - `PATCH /api/tasks/{task_id}` → `{ task }`.
  - Optional `POST /api/tasks/{task_id}/actions` (start/complete/cancel) → `{ status, task }`.

### 4.2 Tasks backend & Linear sync (B5.1)
- DB:
  - `tasks` table (core Task fields).
  - `task_linear_sync` table linking tasks to Linear issues.
- Services:
  - `TaskLinearSyncService.ensure_synced_task(...)` and `sync_from_linear(...)`.
- Kernel contracts:
  - `TasksCreateParams`, `TasksUpdateParams` Pydantic models mapped to `/api/tasks`.

---

## 5. Dependency guidelines (requirements.txt)

Across these layers, dependencies should remain minimal:
- Core: `fastapi`, `pydantic`, `sqlalchemy`, `httpx`, `redis`, `uvicorn[standard]`.
- LLM provider: exactly one SDK (e.g. `openai` or `anthropic`) for Kernel.
- Observability: `structlog` or `python-json-logger`; optional OpenTelemetry packages.
- Integrations: `authlib`, `caldav` only where necessary and justified.

For each epic's design issue (K1.1, K2.1, K3.1, K4.1, K5.1, K6.1, A1.1, B3.1, A3.1, B4.1, etc.), see the Linear issues for full model definitions and step-by-step checklists.
"""


def main():
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("ERROR: Please set LINEAR_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    project_name = "Dhii-Mail SaaS – v1 Architecture & Delivery"
    print(f"Resolving project '{project_name}'...")
    project_id = get_project_id(api_key, project_name)
    print(f"Project ID: {project_id}")

    print("Creating architecture document...")
    create_document(api_key, project_id, DOC_TITLE, DOC_CONTENT)
    print("Done.")


if __name__ == "__main__":
    main()
