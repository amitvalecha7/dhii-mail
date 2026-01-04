# 📐 A2UI JSON Schema Contract (v1.0)
*The "Liquid Glass" Protocol Definition.*

**Status**: DRAFT
**Owner**: Solution Architect (SA-1)
**Issue**: #52

---

## 1. Core Envelope
All responses from the Orchestrator MUST adhere to this structure.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "component": { "$ref": "#/definitions/AppShell" },
    "state_info": { 
      "type": "object",
      "properties": {
        "current_state": { "type": "string" },
        "available_transitions": { "type": "array", "items": { "type": "string" } }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" }
  },
  "required": ["component", "state_info"]
}
```

## 2. Structural Components

### `AppShell`
The root container. Mobile clients render this as a `TabNavigator` or `Stack`.
```json
{
  "definitions": {
    "AppShell": {
      "type": "object",
      "properties": {
        "type": { "const": "app_shell" },
        "panes": { 
          "type": "array", 
          "items": { "$ref": "#/definitions/Pane" } 
        },
        "navigation": { "$ref": "#/definitions/NavigationDetails" }
      },
      "required": ["type", "panes"]
    }
  }
}
```

### `Pane`
A column or surface.
```json
{
  "definitions": {
    "Pane": {
      "type": "object",
      "properties": {
        "type": { "const": "pane" },
        "id": { "type": "string" },
        "width": { "type": "string", "description": "CSS width or flex weight" },
        "cards": { 
          "type": "array", 
          "items": { "$ref": "#/definitions/Card" } 
        },
        "style": { "$ref": "#/definitions/StyleOverrides" }
      },
      "required": ["type", "cards"]
    }
  }
}
```

### `Card`
The atomic unit of content.
```json
{
  "definitions": {
    "Card": {
      "type": "object",
      "properties": {
        "type": { "const": "card" },
        "id": { "type": "string" },
        "title": { "type": "string" },
        "summary": { "type": "string" },
        "content_blocks": { 
          "type": "array", 
          "items": { "$ref": "#/definitions/ContentBlock" } 
        },
        "actions": { 
          "type": "array", 
          "items": { "$ref": "#/definitions/Action" } 
        }
      },
      "required": ["type", "id"]
    }
  }
}
```

## 3. Custom Component Extensions ("Liquid Glass")
*Defined in `A2UI_CUSTOM_COMPONENT_REGISTRY.md` - Formally Specified Here.*

### `custom:draggable_source`
Wraps content to make it draggable.
```json
{
  "if": { "properties": { "type": { "const": "custom:draggable_source" } } },
  "then": {
    "properties": {
      "payload_type": { "type": "string", "enum": ["email", "task", "file"] },
      "payload_data": { "type": "object" },
      "child": { "$ref": "#/definitions/ContentBlock" }
    },
    "required": ["payload_type", "payload_data", "child"]
  }
}
```

### `custom:frosted_glass`
A visual container with blur effect.
```json
{
  "if": { "properties": { "type": { "const": "custom:frosted_glass" } } },
  "then": {
    "properties": {
      "blur_amount": { "type": "string", "default": "10px" },
      "tint_color": { "type": "string", "default": "rgba(255,255,255,0.1)" },
      "children": { "type": "array", "items": { "$ref": "#/definitions/ContentBlock" } }
    }
  }
}
```

### `custom:floating_bubble`
Overlays like "PiP Video" or "Ghostwriter".
```json
{
  "if": { "properties": { "type": { "const": "custom:floating_bubble" } } },
  "then": {
    "properties": {
      "position": { 
        "type": "string", 
        "enum": ["top-right", "bottom-right", "bottom-center"] 
      },
      "content_url": { "type": "string", "format": "uri" },
      "expanded_view": { "$ref": "#/definitions/Card" }
    }
  }
}
```

## 4. Mobile Compatibility Rules
To ensure `SA-1` "Mobile Compatible" mandate:
1.  **No Fixed Widths**: `Pane.width` must be treated as `max-width` on Desktop and ignored (100%) on Mobile.
2.  **Touch Targets**: All `actions` must render with min-height `44px`.
3.  **Hidden Hover**: Do NOT rely on hover states for critical info. All data in `summary` must be visible by default.
