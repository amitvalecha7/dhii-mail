"""
A2UI Component Library - Extended Components
Comprehensive UI component library for A2UI integration
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class A2UIComponents:
    """Extended A2UI component library"""
    
    @staticmethod
    def create_card(title: str, content: str, actions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a card component with title, content, and actions"""
        return {
            "component": {
                "Card": {
                    "title": {"literalString": title},
                    "content": {"literalString": content},
                    "actions": actions or []
                }
            }
        }
    
    @staticmethod
    def create_form(fields: List[Dict[str, Any]], submit_action: str, form_id: str = "form") -> Dict[str, Any]:
        """Create a form component with multiple field types"""
        return {
            "component": {
                "Form": {
                    "id": form_id,
                    "fields": fields,
                    "submitAction": submit_action,
                    "styles": {
                        "padding": "16px",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                    }
                }
            }
        }
    
    @staticmethod
    def create_table(headers: List[str], rows: List[List[str]], table_id: str = "table") -> Dict[str, Any]:
        """Create a table component with sortable columns"""
        return {
            "component": {
                "Table": {
                    "id": table_id,
                    "headers": headers,
                    "rows": rows,
                    "sortable": True,
                    "searchable": True,
                    "styles": {
                        "borderCollapse": "collapse",
                        "width": "100%",
                        "marginTop": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_chart(chart_type: str, data: Dict[str, Any], title: str = "Chart") -> Dict[str, Any]:
        """Create a chart component (line, bar, pie, etc.)"""
        return {
            "component": {
                "Chart": {
                    "type": chart_type,
                    "title": {"literalString": title},
                    "data": data,
                    "styles": {
                        "height": "300px",
                        "width": "100%",
                        "marginTop": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_modal(title: str, content: str, actions: List[Dict[str, Any]], modal_id: str = "modal") -> Dict[str, Any]:
        """Create a modal dialog component"""
        return {
            "component": {
                "Modal": {
                    "id": modal_id,
                    "title": {"literalString": title},
                    "content": {"literalString": content},
                    "actions": actions,
                    "styles": {
                        "overlayColor": "rgba(0,0,0,0.5)",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "padding": "24px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_tabs(tabs: List[Dict[str, Any]], tab_id: str = "tabs") -> Dict[str, Any]:
        """Create a tabbed interface component"""
        return {
            "component": {
                "Tabs": {
                    "id": tab_id,
                    "tabs": tabs,
                    "styles": {
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "backgroundColor": "#f9fafb"
                    }
                }
            }
        }
    
    @staticmethod
    def create_calendar(events: List[Dict[str, Any]], calendar_id: str = "calendar") -> Dict[str, Any]:
        """Create a calendar component with events"""
        return {
            "component": {
                "Calendar": {
                    "id": calendar_id,
                    "events": events,
                    "view": "month",
                    "styles": {
                        "height": "400px",
                        "width": "100%",
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_timeline(items: List[Dict[str, Any]], timeline_id: str = "timeline") -> Dict[str, Any]:
        """Create a timeline component for chronological data"""
        return {
            "component": {
                "Timeline": {
                    "id": timeline_id,
                    "items": items,
                    "styles": {
                        "borderLeft": "2px solid #3b82f6",
                        "paddingLeft": "16px",
                        "marginTop": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_progress_bar(progress: float, title: str = "Progress") -> Dict[str, Any]:
        """Create a progress bar component"""
        return {
            "component": {
                "ProgressBar": {
                    "title": {"literalString": title},
                    "progress": progress,
                    "styles": {
                        "height": "8px",
                        "backgroundColor": "#e5e7eb",
                        "borderRadius": "4px",
                        "fillColor": "#3b82f6"
                    }
                }
            }
        }
    
    @staticmethod
    def create_alert(message: str, alert_type: str = "info", alert_id: str = "alert") -> Dict[str, Any]:
        """Create an alert/notification component"""
        colors = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
        
        return {
            "component": {
                "Alert": {
                    "id": alert_id,
                    "message": {"literalString": message},
                    "type": alert_type,
                    "styles": {
                        "backgroundColor": colors.get(alert_type, "#3b82f6"),
                        "color": "#ffffff",
                        "padding": "12px 16px",
                        "borderRadius": "6px",
                        "marginTop": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_breadcrumb(items: List[str]) -> Dict[str, Any]:
        """Create a breadcrumb navigation component"""
        return {
            "component": {
                "Breadcrumb": {
                    "items": [{"literalString": item} for item in items],
                    "styles": {
                        "fontSize": "14px",
                        "color": "#6b7280",
                        "marginBottom": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_dropdown(options: List[Dict[str, Any]], placeholder: str = "Select an option") -> Dict[str, Any]:
        """Create a dropdown/select component"""
        return {
            "component": {
                "Dropdown": {
                    "options": options,
                    "placeholder": {"literalString": placeholder},
                    "styles": {
                        "width": "100%",
                        "padding": "8px 12px",
                        "border": "1px solid #d1d5db",
                        "borderRadius": "6px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_search_box(placeholder: str = "Search...", search_action: str = "search") -> Dict[str, Any]:
        """Create a search box component"""
        return {
            "component": {
                "SearchBox": {
                    "placeholder": {"literalString": placeholder},
                    "searchAction": search_action,
                    "styles": {
                        "width": "100%",
                        "padding": "12px 16px",
                        "border": "1px solid #d1d5db",
                        "borderRadius": "24px",
                        "fontSize": "14px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_file_upload(accept: str = "*", upload_action: str = "upload") -> Dict[str, Any]:
        """Create a file upload component"""
        return {
            "component": {
                "FileUpload": {
                    "accept": accept,
                    "uploadAction": upload_action,
                    "styles": {
                        "border": "2px dashed #d1d5db",
                        "borderRadius": "8px",
                        "padding": "24px",
                        "textAlign": "center",
                        "backgroundColor": "#f9fafb"
                    }
                }
            }
        }
    
    @staticmethod
    def create_meeting_scheduler(meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a specialized meeting scheduler component"""
        return {
            "component": {
                "MeetingScheduler": {
                    "title": {"literalString": meeting_data.get("title", "Schedule Meeting")},
                    "duration": meeting_data.get("duration", 30),
                    "availableSlots": meeting_data.get("available_slots", []),
                    "participants": meeting_data.get("participants", []),
                    "styles": {
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "padding": "16px",
                        "backgroundColor": "#ffffff"
                    }
                }
            }
        }
    
    @staticmethod
    def create_email_composer(recipients: List[str] = None, subject: str = "", body: str = "") -> Dict[str, Any]:
        """Create an email composer component"""
        return {
            "component": {
                "EmailComposer": {
                    "recipients": recipients or [],
                    "subject": {"literalString": subject},
                    "body": {"literalString": body},
                    "styles": {
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "backgroundColor": "#ffffff",
                        "minHeight": "300px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_list(items: List[Dict[str, Any]], title: str = "List", list_id: str = "list") -> Dict[str, Any]:
        """Create a list component with items"""
        return {
            "component": {
                "List": {
                    "id": list_id,
                    "title": {"literalString": title},
                    "items": items,
                    "styles": {
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "backgroundColor": "#ffffff",
                        "padding": "16px",
                        "marginTop": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_toolbar(actions: List[Dict[str, Any]], toolbar_id: str = "toolbar") -> Dict[str, Any]:
        """Create a toolbar component with action buttons"""
        return {
            "component": {
                "Toolbar": {
                    "id": toolbar_id,
                    "actions": actions,
                    "styles": {
                        "display": "flex",
                        "gap": "8px",
                        "padding": "12px",
                        "backgroundColor": "#f9fafb",
                        "borderRadius": "6px",
                        "marginBottom": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_layout(orientation: str, components: List[Dict[str, Any]], layout_id: str = "layout") -> Dict[str, Any]:
        """Create a layout component for organizing other components"""
        return {
            "component": {
                "Layout": {
                    "id": layout_id,
                    "orientation": orientation,
                    "components": components,
                    "styles": {
                        "display": "flex" if orientation == "horizontal" else "block",
                        "flexDirection": "row" if orientation == "horizontal" else "column",
                        "gap": "16px",
                        "marginTop": "16px"
                    }
                }
            }
        }
    
    @staticmethod
    def create_navigation(items: List[Dict[str, Any]], nav_id: str = "navigation") -> Dict[str, Any]:
        """Create a navigation bar component"""
        return {
            "component": {
                "Navigation": {
                    "id": nav_id,
                    "items": items,
                    "styles": {
                        "display": "flex",
                        "gap": "16px",
                        "padding": "12px 24px",
                        "backgroundColor": "#ffffff",
                        "borderBottom": "1px solid #e5e7eb",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                    }
                }
            }
        }
    
    @staticmethod
    def create_chat(messages: List[Dict[str, Any]], input_placeholder: str = "Type a message...", send_action: str = "send_message", chat_id: str = "chat") -> Dict[str, Any]:
        """Create a chat component"""
        return {
            "component": {
                "Chat": {
                    "id": chat_id,
                    "messages": messages,
                    "inputPlaceholder": {"literalString": input_placeholder},
                    "sendAction": send_action,
                    "styles": {
                        "height": "400px",
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "backgroundColor": "#ffffff",
                        "display": "flex",
                        "flexDirection": "column"
                    }
                }
            }
        }
    
    @staticmethod
    def create_dashboard_widget(widget_type: str, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a dashboard widget component"""
        return {
            "component": {
                "DashboardWidget": {
                    "type": widget_type,
                    "title": {"literalString": title},
                    "data": data,
                    "styles": {
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "padding": "16px",
                        "backgroundColor": "#ffffff",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                    }
                }
            }
        }
    
    @staticmethod
    def create_command_palette(items: List[Dict[str, Any]], query: str = "", palette_id: str = "command_palette") -> Dict[str, Any]:
        """Create a command palette component"""
        return {
            "component": {
                "CommandPalette": {
                    "id": palette_id,
                    "query": query,
                    "items": items,
                    "placeholder": "Type a command or search...",
                    "empty_state": {
                        "title": "No commands found",
                        "description": "Try different keywords or check your spelling"
                    },
                    "categories": [
                        {"name": "navigation", "display_name": "Navigation", "icon": "navigation"},
                        {"name": "action", "display_name": "Actions", "icon": "action"},
                        {"name": "search", "display_name": "Search", "icon": "search"},
                        {"name": "system", "display_name": "System", "icon": "system"},
                        {"name": "email", "display_name": "Email", "icon": "email"},
                        {"name": "calendar", "display_name": "Calendar", "icon": "calendar"},
                        {"name": "meeting", "display_name": "Meetings", "icon": "meeting"},
                        {"name": "settings", "display_name": "Settings", "icon": "settings"}
                    ],
                    "keyboard_shortcuts": {
                        "cmd+k": "open_command_palette",
                        "cmd+shift+f": "global_search",
                        "cmd+f": "quick_search",
                        "cmd+n": "email_compose",
                        "cmd+r": "email_refresh",
                        "cmd+shift+m": "meeting_book"
                    },
                    "styles": {
                        "width": "600px",
                        "maxHeight": "400px",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "boxShadow": "0 10px 25px rgba(0,0,0,0.1)",
                        "border": "1px solid #e5e7eb",
                        "position": "fixed",
                        "top": "50%",
                        "left": "50%",
                        "transform": "translate(-50%, -50%)",
                        "zIndex": 1000
                    }
                }
            }
        }

# Pre-built component templates for common use cases
class A2UITemplates:
    """Pre-built component templates"""
    
    @staticmethod
    def meeting_dashboard(meetings: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a complete meeting dashboard"""
        return [
            A2UIComponents.create_dashboard_widget("stats", stats, "Meeting Statistics"),
            A2UIComponents.create_table(
                headers=["Title", "Date", "Time", "Participants", "Status"],
                rows=[[
                    m.get("title", ""),
                    m.get("date", ""),
                    m.get("time", ""),
                    str(len(m.get("participants", []))),
                    m.get("status", "scheduled")
                ] for m in meetings[:5]],
                table_id="upcoming-meetings"
            ),
            A2UIComponents.create_alert(f"You have {len(meetings)} upcoming meetings", "info")
        ]
    
    @staticmethod
    def email_interface(emails: List[Dict[str, Any]], folders: List[str]) -> List[Dict[str, Any]]:
        """Create a complete email interface"""
        return [
            A2UIComponents.create_tabs([
                {"label": "Inbox", "content": A2UIComponents.create_table(
                    headers=["From", "Subject", "Date", "Priority"],
                    rows=[[
                        e.get("from", ""),
                        e.get("subject", ""),
                        e.get("date", ""),
                        e.get("priority", "normal")
                    ] for e in emails[:10]]
                )},
                {"label": "Sent", "content": A2UIComponents.create_alert("No sent emails", "info")},
                {"label": "Drafts", "content": A2UIComponents.create_alert("No drafts", "info")}
            ]),
            A2UIComponents.create_email_composer()
        ]
    
    @staticmethod
    def calendar_view(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a calendar interface"""
        return [
            A2UIComponents.create_calendar(events),
            A2UIComponents.create_timeline([
                {
                    "title": e.get("title", ""),
                    "date": e.get("date", ""),
                    "description": e.get("description", "")
                } for e in events[:5]
            ])
        ]
    
    @staticmethod
    def settings_panel(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a settings panel"""
        form_fields = []
        for key, value in settings.items():
            field_type = "text"
            if isinstance(value, bool):
                field_type = "checkbox"
            elif isinstance(value, int):
                field_type = "number"
            
            form_fields.append({
                "name": key,
                "type": field_type,
                "label": key.replace("_", " ").title(),
                "default": value
            })
        
        return [
            A2UIComponents.create_form(
                fields=form_fields,
                submit_action="update_settings",
                form_id="settings-form"
            ),
            A2UIComponents.create_alert("Settings saved successfully", "success")
        ]