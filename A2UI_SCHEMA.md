# A2UI Schema Contract (Issue #51)

**Status**: DRAFT  
**Version**: 1.0.0  
**Last Updated**: 2026-01-04

---

## 1. Overview

The **A2UI (Agent-to-UI)** Standard is a protocol for Agents (running in the Kernel) to communicate intent to the UI (running in the Browser). Unlike traditional REST APIs that return data, A2UI returns **UI Operations**.

It uses an **Adjacency List Model** to represent the UI as a graph of components. This allows for O(1) updates (inserting a card, updating a status) without re-rendering the entire tree.

## 2. The Protocol

The server responds with a JSON object containing a list of `operations`.

### Response Format
```json
{
  "a2ui_json": "stringified_json_of_operations",
  "operations": [
    {
      "operation": "insert",
      "node_id": "card_123",
      "node_type": "card",
      "parent_id": "pane_main",
      "properties": {
        "title": "New Deal",
        "status": "active"
      },
      "position": 0
    }
  ],
  "state": "dashboard",
  "timestamp": "2026-01-04T12:00:00Z"
}
```

## 3. Operations

| Operation | Description | Required Fields |
| :--- | :--- | :--- |
| `insert` | Adds a new node to the graph. | `node_id`, `node_type`, `parent_id`, `properties` |
| `update` | Updates properties of an existing node. | `node_id`, `properties` |
| `delete` | Removes a node (and its children). | `node_id` |
| `move` | Moves a node to a new parent or position. | `node_id`, `parent_id`, `position` |

## 4. Component Schema

### Core Components

#### `AppShell`
The root container.
- **Type**: `app_shell`
- **Properties**:
  - `theme`: "light" | "dark"
  - `layout`: "grid" | "flex"

#### `Pane`
A vertical column or horizontal section.
- **Type**: `pane`
- **Properties**:
  - `width`: CSS string (e.g., "300px")
  - `title`: String (optional header)

#### `Card`
The atomic unit of information.
- **Type**: `card`
- **Properties**:
  - `title`: String
  - `summary`: String
  - `actions`: List of Action Objects
  - `priority`: Integer (0-100)

#### `Text`
Simple text display.
- **Type**: `text`
- **Properties**:
  - `text`: String
  - `style`: CSS Object

### Interactive Components

#### `Button`
- **Type**: `button`
- **Properties**:
  - `text`: String
  - `onClick`: Action Object
  - `variant`: "primary" | "secondary" | "danger"

#### `Input`
- **Type**: `input`
- **Properties**:
  - `name`: String
  - `type`: "text" | "email" | "date"
  - `label`: String
  - `value`: String

## 5. Action Object
Defines what happens when a user interacts with a component.

```json
{
  "action": "schedule_meeting",
  "params": {
    "attendees": ["john@example.com"],
    "duration": 30
  },
  "feedback": "Scheduling..."
}
```

## 6. Example: Rendering a Dashboard

```json
[
  {
    "operation": "insert",
    "node_id": "root",
    "node_type": "app_shell",
    "properties": {}
  },
  {
    "operation": "insert",
    "node_id": "main_pane",
    "node_type": "pane",
    "parent_id": "root",
    "properties": { "width": "100%" }
  },
  {
    "operation": "insert",
    "node_id": "welcome_card",
    "node_type": "card",
    "parent_id": "main_pane",
    "properties": {
      "title": "Welcome Back",
      "summary": "You have 3 pending tasks."
    }
  }
]
```
