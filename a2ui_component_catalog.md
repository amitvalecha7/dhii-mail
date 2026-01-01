# A2UI Component Catalog for dhii Mail

## Overview

This document defines the complete A2UI component catalog for dhii Mail, including standard A2UI components, custom dhii Mail components, and their validation schemas.

## Standard A2UI Components (Trusted Catalog)

These components are part of the core A2UI specification and are considered trusted.

### Button Component
```json
{
  "component_id": "button",
  "schema": {
    "type": "object",
    "properties": {
      "label": {"type": "string", "maxLength": 50},
      "variant": {"type": "string", "enum": ["primary", "secondary", "danger", "success"]},
      "size": {"type": "string", "enum": ["small", "medium", "large"]},
      "disabled": {"type": "boolean"},
      "icon": {"type": "string", "maxLength": 50},
      "loading": {"type": "boolean"}
    },
    "required": ["label"],
    "additionalProperties": false
  },
  "actions": ["click", "focus", "blur"],
  "description": "Interactive button for user actions"
}
```

### Text Component
```json
{
  "component_id": "text",
  "schema": {
    "type": "object",
    "properties": {
      "content": {"type": "string", "maxLength": 1000},
      "variant": {"type": "string", "enum": ["body", "heading1", "heading2", "heading3", "caption", "error"]},
      "size": {"type": "string", "enum": ["small", "medium", "large"]},
      "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
      "align": {"type": "string", "enum": ["left", "center", "right", "justify"]},
      "weight": {"type": "string", "enum": ["normal", "bold", "light"]}
    },
    "required": ["content"],
    "additionalProperties": false
  },
  "actions": [],
  "description": "Text display component with formatting options"
}
```

### Container Component
```json
{
  "component_id": "container",
  "schema": {
    "type": "object",
    "properties": {
      "orientation": {"type": "string", "enum": ["vertical", "horizontal"]},
      "spacing": {"type": "string", "enum": ["none", "small", "medium", "large"]},
      "padding": {"type": "string", "enum": ["none", "small", "medium", "large"]},
      "alignment": {"type": "string", "enum": ["start", "center", "end", "stretch"]},
      "wrap": {"type": "boolean"},
      "background_color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
      "border": {"type": "boolean"},
      "border_radius": {"type": "string", "enum": ["none", "small", "medium", "large"]}
    },
    "required": [],
    "additionalProperties": false
  },
  "actions": [],
  "description": "Layout container for organizing components"
}
```

### Form Component
```json
{
  "component_id": "form",
  "schema": {
    "type": "object",
    "properties": {
      "fields": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string", "pattern": "^[a-zA-Z0-9_]+$"},
            "type": {"type": "string", "enum": ["text", "email", "password", "textarea", "select", "checkbox", "radio"]},
            "label": {"type": "string", "maxLength": 100},
            "placeholder": {"type": "string", "maxLength": 200},
            "required": {"type": "boolean"},
            "options": {
              "type": "array",
              "items": {"type": "string"},
              "maxItems": 50
            },
            "validation": {
              "type": "object",
              "properties": {
                "min_length": {"type": "integer", "minimum": 0},
                "max_length": {"type": "integer", "minimum": 1},
                "pattern": {"type": "string"}
              }
            }
          },
          "required": ["name", "type", "label"],
          "additionalProperties": false
        },
        "maxItems": 20
      },
      "submit_label": {"type": "string", "maxLength": 50},
      "cancel_label": {"type": "string", "maxLength": 50},
      "show_cancel": {"type": "boolean"},
      "validation": {"type": "string", "enum": ["realtime", "submit", "none"]}
    },
    "required": ["fields"],
    "additionalProperties": false
  },
  "actions": ["submit", "cancel", "field_change"],
  "description": "Form component for user input collection"
}
```

### Image Component
```json
{
  "component_id": "image",
  "schema": {
    "type": "object",
    "properties": {
      "src": {"type": "string", "format": "uri", "maxLength": 500},
      "alt": {"type": "string", "maxLength": 200},
      "width": {"type": "integer", "minimum": 1, "maximum": 2000},
      "height": {"type": "integer", "minimum": 1, "maximum": 2000},
      "fit": {"type": "string", "enum": ["contain", "cover", "fill", "none"]},
      "border_radius": {"type": "string", "enum": ["none", "small", "medium", "large", "circle"]}
    },
    "required": ["src", "alt"],
    "additionalProperties": false
  },
  "actions": ["click", "load", "error"],
  "description": "Image display component with sizing options"
}
```

### Icon Component
```json
{
  "component_id": "icon",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string", "pattern": "^[a-z-]+$", "maxLength": 50},
      "size": {"type": "string", "enum": ["small", "medium", "large"]},
      "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
      "variant": {"type": "string", "enum": ["filled", "outlined", "rounded"]}
    },
    "required": ["name"],
    "additionalProperties": false
  },
  "actions": ["click"],
  "description": "Icon component for visual indicators"
}
```

## Custom dhii Mail Components (Validated Catalog)

These components are specific to dhii Mail functionality and require validation.

### Email Summary Card
```json
{
  "component_id": "email_summary_card",
  "schema": {
    "type": "object",
    "properties": {
      "folder_name": {"type": "string", "maxLength": 50},
      "unread_count": {"type": "integer", "minimum": 0, "maximum": 99999},
      "total_count": {"type": "integer", "minimum": 0, "maximum": 999999},
      "last_sync": {"type": "string", "format": "date-time"},
      "icon": {"type": "string", "maxLength": 50},
      "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
      "trend": {"type": "string", "enum": ["up", "down", "stable", "none"]},
      "trend_value": {"type": "integer"}
    },
    "required": ["folder_name", "unread_count", "total_count"],
    "additionalProperties": false
  },
  "actions": ["click", "refresh"],
  "description": "Summary card showing email folder statistics"
}
```

### Message Thread Card
```json
{
  "component_id": "message_thread_card",
  "schema": {
    "type": "object",
    "properties": {
      "subject": {"type": "string", "maxLength": 200},
      "participants": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string", "maxLength": 100},
            "email": {"type": "string", "format": "email", "maxLength": 200},
            "avatar": {"type": "string", "format": "uri", "maxLength": 500}
          },
          "required": ["email"],
          "additionalProperties": false
        },
        "maxItems": 10
      },
      "last_message": {"type": "string", "maxLength": 500},
      "timestamp": {"type": "string", "format": "date-time"},
      "unread": {"type": "boolean"},
      "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
      "has_attachments": {"type": "boolean"},
      "message_count": {"type": "integer", "minimum": 1},
      "labels": {
        "type": "array",
        "items": {"type": "string", "maxLength": 50},
        "maxItems": 10
      },
      "starred": {"type": "boolean"}
    },
    "required": ["subject", "participants", "last_message", "timestamp"],
    "additionalProperties": false
  },
  "actions": ["click", "archive", "delete", "mark_unread", "star", "label"],
  "description": "Card representing an email conversation thread"
}
```

### Compose Editor Card
```json
{
  "component_id": "compose_editor_card",
  "schema": {
    "type": "object",
    "properties": {
      "recipients": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "email": {"type": "string", "format": "email", "maxLength": 200},
            "name": {"type": "string", "maxLength": 100},
            "type": {"type": "string", "enum": ["to", "cc", "bcc"]}
          },
          "required": ["email", "type"],
          "additionalProperties": false
        },
        "maxItems": 50
      },
      "subject": {"type": "string", "maxLength": 200},
      "body": {"type": "string", "maxLength": 10000},
      "body_format": {"type": "string", "enum": ["text", "html", "markdown"]},
      "attachments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "filename": {"type": "string", "maxLength": 255},
            "size": {"type": "integer", "minimum": 0},
            "type": {"type": "string", "maxLength": 100},
            "upload_progress": {"type": "number", "minimum": 0, "maximum": 100}
          },
          "required": ["filename"],
          "additionalProperties": false
        },
        "maxItems": 10
      },
      "templates": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string", "maxLength": 100},
            "name": {"type": "string", "maxLength": 100},
            "preview": {"type": "string", "maxLength": 200}
          }
        }
      },
      "signature": {"type": "string", "maxLength": 1000},
      "auto_save_enabled": {"type": "boolean"},
      "last_saved": {"type": "string", "format": "date-time"}
    },
    "required": [],
    "additionalProperties": false
  },
  "actions": ["send", "save_draft", "add_attachment", "discard", "apply_template"],
  "description": "Email composition editor with rich formatting"
}
```

### Video Meeting Card
```json
{
  "component_id": "video_meeting_card",
  "schema": {
    "type": "object",
    "properties": {
      "meeting_id": {"type": "string", "pattern": "^[a-zA-Z0-9-]+$", "maxLength": 100},
      "title": {"type": "string", "maxLength": 200},
      "description": {"type": "string", "maxLength": 500},
      "start_time": {"type": "string", "format": "date-time"},
      "duration": {"type": "integer", "minimum": 1, "maximum": 480},
      "participants": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string", "maxLength": 100},
            "email": {"type": "string", "format": "email", "maxLength": 200},
            "status": {"type": "string", "enum": ["invited", "accepted", "declined", "joined"]},
            "role": {"type": "string", "enum": ["host", "participant"]},
            "avatar": {"type": "string", "format": "uri", "maxLength": 500}
          },
          "required": ["email"],
          "additionalProperties": false
        },
        "maxItems": 100
      },
      "status": {"type": "string", "enum": ["scheduled", "active", "ended", "cancelled"]},
      "recording_enabled": {"type": "boolean"},
      "transcription_enabled": {"type": "boolean"},
      "password": {"type": "string", "maxLength": 50},
      "join_url": {"type": "string", "format": "uri", "maxLength": 500},
      "host_url": {"type": "string", "format": "uri", "maxLength": 500}
    },
    "required": ["meeting_id", "title", "start_time"],
    "additionalProperties": false
  },
  "actions": ["join", "start", "end", "invite", "copy_link", "enable_recording"],
  "description": "Video meeting card with Jitsi Meet integration"
}
```

### Security Status Card
```json
{
  "component_id": "security_status_card",
  "schema": {
    "type": "object",
    "properties": {
      "overall_status": {"type": "string", "enum": ["secure", "warning", "critical"]},
      "last_scan": {"type": "string", "format": "date-time"},
      "threats_detected": {"type": "integer", "minimum": 0},
      "encryption_status": {"type": "string", "enum": ["enabled", "disabled", "partial"]},
      "two_factor_enabled": {"type": "boolean"},
      "last_login_ip": {"type": "string", "format": "ipv4"},
      "last_login_time": {"type": "string", "format": "date-time"},
      "failed_login_attempts": {"type": "integer", "minimum": 0},
      "active_sessions": {"type": "integer", "minimum": 0},
      "security_score": {"type": "integer", "minimum": 0, "maximum": 100},
      "recommendations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string", "maxLength": 100},
            "title": {"type": "string", "maxLength": 200},
            "description": {"type": "string", "maxLength": 500},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "action_url": {"type": "string", "format": "uri", "maxLength": 500}
          },
          "required": ["id", "title", "priority"],
          "additionalProperties": false
        },
        "maxItems": 10
      }
    },
    "required": ["overall_status", "security_score"],
    "additionalProperties": false
  },
  "actions": ["view_details", "run_scan", "enable_2fa", "view_sessions"],
  "description": "Security status overview card"
}
```

### Marketing Campaign Card
```json
{
  "component_id": "marketing_campaign_card",
  "schema": {
    "type": "object",
    "properties": {
      "campaign_id": {"type": "string", "pattern": "^[a-zA-Z0-9-]+$", "maxLength": 100},
      "name": {"type": "string", "maxLength": 200},
      "description": {"type": "string", "maxLength": 500},
      "status": {"type": "string", "enum": ["draft", "scheduled", "active", "paused", "completed", "cancelled"]},
      "created_date": {"type": "string", "format": "date-time"},
      "start_date": {"type": "string", "format": "date-time"},
      "end_date": {"type": "string", "format": "date-time"},
      "target_audience": {
        "type": "object",
        "properties": {
          "total_recipients": {"type": "integer", "minimum": 0},
          "segments": {
            "type": "array",
            "items": {"type": "string", "maxLength": 100}
          },
          "filters": {
            "type": "array",
            "items": {"type": "string", "maxLength": 100}
          }
        }
      },
      "metrics": {
        "type": "object",
        "properties": {
          "emails_sent": {"type": "integer", "minimum": 0},
          "emails_delivered": {"type": "integer", "minimum": 0},
          "open_rate": {"type": "number", "minimum": 0, "maximum": 100},
          "click_rate": {"type": "number", "minimum": 0, "maximum": 100},
          "unsubscribe_rate": {"type": "number", "minimum": 0, "maximum": 100},
          "bounce_rate": {"type": "number", "minimum": 0, "maximum": 100},
          "revenue": {"type": "number", "minimum": 0},
          "roi": {"type": "number"}
        }
      },
      "template": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "maxLength": 100},
          "name": {"type": "string", "maxLength": 100},
          "type": {"type": "string", "enum": ["newsletter", "promotional", "transactional", "announcement"]}
        }
      },
      "ab_test": {
        "type": "object",
        "properties": {
          "enabled": {"type": "boolean"},
          "variants": {"type": "integer", "minimum": 2, "maximum": 5},
          "split_percentage": {"type": "number", "minimum": 0, "maximum": 100}
        }
      }
    },
    "required": ["campaign_id", "name", "status"],
    "additionalProperties": false
  },
  "actions": ["view_details", "edit", "duplicate", "pause", "resume", "archive", "view_analytics"],
  "description": "Marketing campaign performance card"
}
```

### System Health Card
```json
{
  "component_id": "system_health_card",
  "schema": {
    "type": "object",
    "properties": {
      "service_name": {"type": "string", "maxLength": 100},
      "status": {"type": "string", "enum": ["healthy", "degraded", "down", "unknown"]},
      "uptime_percentage": {"type": "number", "minimum": 0, "maximum": 100},
      "last_check": {"type": "string", "format": "date-time"},
      "response_time": {"type": "integer", "minimum": 0},
      "cpu_usage": {"type": "number", "minimum": 0, "maximum": 100},
      "memory_usage": {"type": "number", "minimum": 0, "maximum": 100},
      "disk_usage": {"type": "number", "minimum": 0, "maximum": 100},
      "active_connections": {"type": "integer", "minimum": 0},
      "error_rate": {"type": "number", "minimum": 0},
      "alerts": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string", "maxLength": 100},
            "level": {"type": "string", "enum": ["info", "warning", "error", "critical"]},
            "message": {"type": "string", "maxLength": 500},
            "timestamp": {"type": "string", "format": "date-time"}
          },
          "required": ["id", "level", "message"],
          "additionalProperties": false
        },
        "maxItems": 10
      }
    },
    "required": ["service_name", "status"],
    "additionalProperties": false
  },
  "actions": ["view_details", "restart_service", "acknowledge_alert"],
  "description": "System health monitoring card"
}
```

### Progress Indicator Card
```json
{
  "component_id": "progress_indicator_card",
  "schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string", "maxLength": 200},
      "description": {"type": "string", "maxLength": 500},
      "progress_percentage": {"type": "number", "minimum": 0, "maximum": 100},
      "current_step": {"type": "integer", "minimum": 1},
      "total_steps": {"type": "integer", "minimum": 1},
      "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "failed", "cancelled"]},
      "estimated_time_remaining": {"type": "integer", "minimum": 0},
      "start_time": {"type": "string", "format": "date-time"},
      "estimated_completion": {"type": "string", "format": "date-time"},
      "steps": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string", "maxLength": 100},
            "name": {"type": "string", "maxLength": 200},
            "description": {"type": "string", "maxLength": 500},
            "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "failed", "skipped"]},
            "duration": {"type": "integer", "minimum": 0}
          },
          "required": ["id", "name", "status"],
          "additionalProperties": false
        },
        "maxItems": 20
      },
      "can_cancel": {"type": "boolean"},
      "can_retry": {"type": "boolean"}
    },
    "required": ["title", "progress_percentage", "status"],
    "additionalProperties": false
  },
  "actions": ["cancel", "retry", "view_details"],
  "description": "Progress indicator card for long-running operations"
}
```

## Component Validation Rules

### Property Validation
1. **Type Checking**: All properties must match their defined types
2. **Length Constraints**: String properties have maximum length limits
3. **Format Validation**: Email, URI, and date-time formats are validated
4. **Range Constraints**: Numeric properties have minimum/maximum values
5. **Enum Validation**: Properties with enum values must match exactly

### Security Validation
1. **Input Sanitization**: All string properties are sanitized for XSS protection
2. **Pattern Validation**: Regular expressions validate property formats
3. **Size Limits**: Arrays and strings have maximum size constraints
4. **Property Whitelisting**: Only defined properties are allowed (no additional properties)

### Action Validation
1. **Permission Checking**: Actions are validated against user permissions
2. **Rate Limiting**: Action frequency is limited per user
3. **Parameter Validation**: Action parameters are validated before processing

## Component Implementation Examples

### Email Summary Card Implementation
```python
class EmailSummaryCard:
    def __init__(self, folder_data: dict):
        self.folder_data = folder_data
    
    def to_a2ui_component(self) -> dict:
        return {
            "id": f"email_summary_{self.folder_data['id']}",
            "type": "email_summary_card",
            "properties": {
                "folder_name": self.folder_data["name"],
                "unread_count": self.folder_data["unread_count"],
                "total_count": self.folder_data["total_count"],
                "last_sync": self.folder_data["last_sync"].isoformat(),
                "icon": self.get_folder_icon(self.folder_data["type"]),
                "color": self.get_folder_color(self.folder_data["type"]),
                "trend": self.calculate_trend(self.folder_data),
                "trend_value": self.folder_data.get("trend_value", 0)
            },
            "actions": [
                {"name": "click", "label": "View Folder"},
                {"name": "refresh", "label": "Refresh"}
            ]
        }
```

### Message Thread Card Implementation
```python
class MessageThreadCard:
    def __init__(self, thread_data: dict):
        self.thread_data = thread_data
    
    def to_a2ui_component(self) -> dict:
        return {
            "id": f"thread_{self.thread_data['id']}",
            "type": "message_thread_card",
            "properties": {
                "subject": self.thread_data["subject"],
                "participants": self.format_participants(self.thread_data["participants"]),
                "last_message": self.thread_data["last_message"][:500],
                "timestamp": self.thread_data["last_message_time"].isoformat(),
                "unread": self.thread_data["has_unread"],
                "priority": self.thread_data.get("priority", "normal"),
                "has_attachments": self.thread_data["has_attachments"],
                "message_count": self.thread_data["message_count"],
                "labels": self.thread_data.get("labels", []),
                "starred": self.thread_data.get("starred", False)
            },
            "actions": [
                {"name": "click", "label": "Open"},
                {"name": "archive", "label": "Archive"},
                {"name": "delete", "label": "Delete"},
                {"name": "mark_unread", "label": "Mark Unread"},
                {"name": "star", "label": "Star"}
            ]
        }
```

## Component Catalog Management

### Catalog Registration
```python
class A2UIComponentCatalog:
    def __init__(self):
        self.standard_components = {}
        self.custom_components = {}
    
    def register_component(self, component_id: str, schema: dict, component_type: str = "custom"):
        """Register a component in the catalog."""
        if component_type == "standard":
            self.standard_components[component_id] = schema
        else:
            self.custom_components[component_id] = schema
    
    def get_component_schema(self, component_id: str) -> dict:
        """Get component schema from catalog."""
        return (self.standard_components.get(component_id) or 
                self.custom_components.get(component_id))
    
    def validate_component(self, component_data: dict) -> bool:
        """Validate component data against schema."""
        component_type = component_data.get("type")
        schema = self.get_component_schema(component_type)
        
        if not schema:
            return False
        
        # Validate properties
        properties = component_data.get("properties", {})
        return self.validate_properties(properties, schema["schema"])
```

This component catalog provides the foundation for building secure, validated A2UI interfaces for dhii Mail while maintaining consistency and preventing security vulnerabilities.