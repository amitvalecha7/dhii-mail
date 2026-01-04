# Orchestrator API & Action Protocol (Issue #53)

**Status**: DRAFT  
**Version**: 1.0.0  
**Last Updated**: 2026-01-04

---

## 1. Overview

The **Orchestrator** is the "Brain" of the UI. It acts as the bridge between the Dumb Client (Browser) and the Smart Agents (Kernel).
It implements a **Stateful Request-Response Loop**:
1.  **User Event**: Click, Type, Navigate.
2.  **Orchestrator**: Routes event to the active Plugin/Agent.
3.  **Agent**: Computes logic, updates state.
4.  **Renderer**: Generates a new A2UI Graph.
5.  **Diff Engine**: Sends minimal operations to the Client.

## 2. The Action Protocol

Communication happens via a single WebSocket endpoint or REST fallback: `POST /api/a2ui/action`.

### Request Payload (Client -> Server)

```json
{
  "action": "schedule_meeting",
  "context": {
    "route": "/dashboard",
    "selection": null,
    "user_id": "user_123",
    "timezone": "UTC",
    "screen_size": "desktop"
  },
  "payload": {
    "attendees": ["john@example.com"],
    "date": "2026-02-01"
  },
  "component_id": "card_quick_actions" 
}
```

### Response Payload (Server -> Client)

The server NEVER returns raw data. It returns **UI Operations** (see [A2UI_SCHEMA.md](./A2UI_SCHEMA.md)).

```json
{
  "status": "success",
  "a2ui_json": "{...}", // Stringified Operations
  "side_effects": [
    {
      "type": "toast",
      "message": "Meeting Scheduled!",
      "variant": "success"
    },
    {
      "type": "navigate",
      "to": "/calendar"
    }
  ]
}
```

## 3. The "Context" Object

The Context is the "Short-term Memory" of the session. It is passed to every Agent.

| Field | Description | Source |
| :--- | :--- | :--- |
| `route` | Current active view (e.g., `/email/inbox`). | Client Router |
| `selection` | Currently selected item IDs. | Client State |
| `user_prefs` | Theme, density, language. | User Settings |
| `capabilities` | What the client device can do (camera, mic). | Browser API |

## 4. Lifecycle of an Interaction

### Example: "Clicking 'Reply' on an Email"

1.  **UI Event**: User clicks `<Button onClick={{ action: "reply", email_id: "123" }} />`.
2.  **Transport**: Client sends payload `{ action: "reply", payload: { "email_id": "123" } }` to Orchestrator.
3.  **Routing**: Orchestrator sees current state is `EMAIL_INBOX`. Routes to `EmailAgent`.
4.  **Agent Logic**:
    *   `EmailAgent` fetches email "123".
    *   `EmailAgent` generates a "Draft Reply" object.
    *   `EmailAgent` changes UI State to `EMAIL_COMPOSE`.
5.  **Rendering**:
    *   Renderer sees state `EMAIL_COMPOSE`.
    *   Generates A2UI Components for a Form (To, Subject, Body).
6.  **Response**:
    *   Orchestrator sends `[ { op: "insert", type: "form", ... } ]` to Client.
7.  **Client Update**:
    *   Client renders the form. User sees the reply screen instantly.

## 5. Error Handling

If an Agent crashes or throws an error:

1.  Orchestrator catches the exception.
2.  Orchestrator does **NOT** crash the UI.
3.  Orchestrator returns a "Recovery Op":
    ```json
    {
      "side_effects": [
        { "type": "toast", "variant": "error", "message": "Email Agent timed out." }
      ]
    }
    ```
