"""
A2UI Orchestrator v2 - Kernel-based Architecture
Refactored orchestrator that uses the new kernel and plugin system
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.kernel import Kernel
from ..core.renderer import A2UIAdjacencyRenderer
from ..core.types import UIState, PluginType

logger = logging.getLogger(__name__)


class A2UIOrchestratorV2:
    """Refactored orchestrator using kernel-based architecture"""
    
    def __init__(self):
        self.kernel = Kernel()
        self.renderer = A2UIAdjacencyRenderer()
        self.user_context = {}
        
        # Initialize plugins
        self._initialize_plugins()
    
    def _initialize_plugins(self):
        """Initialize core plugins"""
        try:
            from plugins.email import EmailPlugin, EMAIL_PLUGIN_CONFIG
            from plugins.calendar import CalendarPlugin, CALENDAR_PLUGIN_CONFIG
            
            # Register email plugin
            email_plugin = EmailPlugin()
            self.kernel.register_plugin(EMAIL_PLUGIN_CONFIG)
            self.kernel.enable_plugin(EMAIL_PLUGIN_CONFIG.id)
            
            # Register calendar plugin
            calendar_plugin = CalendarPlugin()
            self.kernel.register_plugin(CALENDAR_PLUGIN_CONFIG)
            self.kernel.enable_plugin(CALENDAR_PLUGIN_CONFIG.id)
            
            logger.info("Core plugins initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize plugins: {e}")
    
    async def render_ui(self, state: UIState, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render UI using kernel-based architecture"""
        self.user_context = context or {}
        
        logger.info(f"Rendering A2UI v2 for state: {state.value}")
        
        # Route to appropriate renderer based on state
        renderers = {
            UIState.DASHBOARD: self._render_dashboard_v2,
            UIState.EMAIL_INBOX: self._render_email_inbox_v2,
            UIState.EMAIL_COMPOSE: self._render_email_compose_v2,
            UIState.CALENDAR_VIEW: self._render_calendar_v2,
            UIState.PLUGIN_STORE: self._render_plugin_store_v2,
        }
        
        renderer = renderers.get(state, self._render_dashboard_v2)
        
        # Get adjacency operations from renderer
        operations = await renderer()
        
        # Convert operations to A2UI JSON
        a2ui_json = json.dumps({
            "operations": [self._operation_to_dict(op) for op in operations],
            "timestamp": datetime.now().isoformat(),
            "state": state.value
        })
        
        return {
            "a2ui_json": a2ui_json,
            "operations": operations,
            "state": state.value,
            "user_context": self.user_context
        }
    
    def _operation_to_dict(self, operation) -> Dict[str, Any]:
        """Convert AdjacencyOperation to dictionary"""
        return {
            "operation": operation.operation,
            "node_id": operation.node_id,
            "node_type": operation.node_type,
            "parent_id": operation.parent_id,
            "properties": operation.properties,
            "position": operation.position
        }
    
    async def _render_dashboard_v2(self) -> List:
        """Render dashboard using kernel capabilities"""
        operations = []
        
        # Get user info from context
        user_name = self.user_context.get('name', 'User')
        
        # Get plugin statistics
        plugins = await self.kernel.list_plugins()
        enabled_plugins = [p for p in plugins if p.status.value == 'enabled']
        
        # Create dashboard context
        dashboard_context = {
            "title": f"Welcome {user_name}",
            "user_name": user_name,
            "plugins": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "status": p.status.value,
                    "type": p.type.value
                }
                for p in enabled_plugins
            ],
            "stats": {
                "total_plugins": len(plugins),
                "enabled_plugins": len(enabled_plugins),
                "plugin_types": len(set(p.type.value for p in plugins))
            }
        }
        
        # Use renderer to create adjacency operations
        operations = self.renderer.render_dashboard(dashboard_context)
        
        return operations
    
    async def _render_email_inbox_v2(self) -> List:
        """Render email inbox using kernel capabilities"""
        operations = []
        
        try:
            # Execute email receive capability
            result = await self.kernel.execute_capability(
                "email.receive",
                {
                    "folder": "INBOX",
                    "limit": 10,
                    "unread_only": False
                }
            )
            
            emails = result.get("emails", [])
            
            # Create email inbox context
            inbox_context = {
                "emails": emails,
                "count": result.get("count", 0),
                "title": "Email Inbox"
            }
            
            # Create adjacency operations for email inbox
            operations = self._create_email_inbox_operations(inbox_context)
            
        except Exception as e:
            logger.error(f"Failed to render email inbox: {e}")
            # Return error operations
            operations = self.renderer.render_error(f"Failed to load emails: {str(e)}")
        
        return operations
    
    def _create_email_inbox_operations(self, context: Dict[str, Any]) -> List:
        """Create adjacency operations for email inbox"""
        operations = []
        
        # Main container
        container_id = "email_inbox_container"
        container_props = {
            "className": "email-inbox-container",
            "style": {
                "display": "grid",
                "gridTemplateColumns": "250px 1fr",
                "gap": "16px",
                "padding": "16px"
            }
        }
        
        container_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("container", container_props)
        ])[0]
        operations.append(container_op)
        
        # Sidebar
        sidebar_id = "email_sidebar"
        sidebar_props = {
            "className": "email-sidebar",
            "style": {
                "backgroundColor": "#f8f9fa",
                "padding": "16px",
                "borderRadius": "8px"
            }
        }
        
        sidebar_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("section", sidebar_props)
        ])[0]
        sidebar_op.parent_id = container_id
        operations.append(sidebar_op)
        
        # Main content
        main_id = "email_main"
        main_props = {
            "className": "email-main-content",
            "style": {
                "backgroundColor": "#ffffff",
                "padding": "16px",
                "borderRadius": "8px",
                "border": "1px solid #e0e0e0"
            }
        }
        
        main_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("section", main_props)
        ])[0]
        main_op.parent_id = container_id
        operations.append(main_op)
        
        # Add email list
        emails = context.get("emails", [])
        for i, email in enumerate(emails):
            email_card_id = f"email_card_{i}"
            email_props = {
                "className": "email-card",
                "style": {
                    "padding": "12px",
                    "marginBottom": "8px",
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "4px",
                    "cursor": "pointer"
                },
                "onClick": {
                    "action": "view_email",
                    "emailId": email.get("id")
                }
            }
            
            email_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("card", email_props)
            ])[0]
            email_op.parent_id = main_id
            email_op.position = i
            operations.append(email_op)
            
            # Add email subject
            subject_id = f"email_subject_{i}"
            subject_props = {
                "text": email.get("subject", "No Subject"),
                "style": {"fontWeight": "bold", "marginBottom": "4px"}
            }
            
            subject_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("text", subject_props)
            ])[0]
            subject_op.parent_id = email_card_id
            operations.append(subject_op)
            
            # Add email sender
            sender_id = f"email_sender_{i}"
            sender_props = {
                "text": f"From: {email.get('sender', 'Unknown')}",
                "style": {"color": "#666", "fontSize": "14px"}
            }
            
            sender_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("text", sender_props)
            ])[0]
            sender_op.parent_id = email_card_id
            operations.append(sender_op)
        
        return operations
    
    async def _render_email_compose_v2(self) -> List:
        """Render email compose interface using kernel capabilities"""
        operations = []
        
        # Create compose form context
        compose_context = {
            "title": "Compose Email",
            "fields": [
                {"name": "to", "type": "email", "label": "To", "required": True},
                {"name": "cc", "type": "email", "label": "CC"},
                {"name": "bcc", "type": "email", "label": "BCC"},
                {"name": "subject", "type": "text", "label": "Subject", "required": True},
                {"name": "body", "type": "textarea", "label": "Message", "required": True}
            ],
            "actions": [
                {"label": "Send", "action": "send_email", "type": "primary"},
                {"label": "Save Draft", "action": "save_draft", "type": "secondary"},
                {"label": "Cancel", "action": "cancel_compose", "type": "secondary"}
            ]
        }
        
        # Create adjacency operations for compose form
        operations = self._create_compose_form_operations(compose_context)
        
        return operations
    
    def _create_compose_form_operations(self, context: Dict[str, Any]) -> List:
        """Create adjacency operations for email compose form"""
        operations = []
        
        # Main form container
        form_id = "compose_form_container"
        form_props = {
            "className": "compose-form-container",
            "style": {
                "maxWidth": "800px",
                "margin": "0 auto",
                "padding": "16px"
            }
        }
        
        form_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("form", form_props)
        ])[0]
        operations.append(form_op)
        
        # Add form fields
        fields = context.get("fields", [])
        for i, field in enumerate(fields):
            field_id = f"form_field_{field['name']}"
            field_props = {
                "name": field['name'],
                "type": field['type'],
                "label": field['label'],
                "required": field.get('required', False),
                "style": {"marginBottom": "16px"}
            }
            
            field_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("input", field_props)
            ])[0]
            field_op.parent_id = form_id
            field_op.position = i
            operations.append(field_op)
        
        # Add action buttons
        actions = context.get("actions", [])
        button_container_id = "form_actions"
        button_container_props = {
            "className": "form-actions",
            "style": {
                "display": "flex",
                "gap": "8px",
                "marginTop": "16px"
            }
        }
        
        container_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("container", button_container_props)
        ])[0]
        container_op.parent_id = form_id
        operations.append(container_op)
        
        for i, action in enumerate(actions):
            button_id = f"action_button_{action['action']}"
            button_props = {
                "text": action['label'],
                "type": action.get('type', 'secondary'),
                "onClick": {
                    "action": action['action']
                },
                "style": {"minWidth": "100px"}
            }
            
            button_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("button", button_props)
            ])[0]
            button_op.parent_id = button_container_id
            button_op.position = i
            operations.append(button_op)
        
        return operations
    
    async def _render_calendar_v2(self) -> List:
        """Render calendar view using kernel capabilities"""
        operations = []
        
        try:
            # Get current date range
            from datetime import datetime, timedelta
            
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=7)
            
            # Execute calendar get events capability
            result = await self.kernel.execute_capability(
                "calendar.get_events",
                {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            events = result.get("events", [])
            
            # Create calendar context
            calendar_context = {
                "events": events,
                "count": result.get("count", 0),
                "date_range": f"{start_date} to {end_date}",
                "title": "Calendar"
            }
            
            # Create adjacency operations for calendar view
            operations = self._create_calendar_operations(calendar_context)
            
        except Exception as e:
            logger.error(f"Failed to render calendar: {e}")
            # Return error operations
            operations = self.renderer.render_error(f"Failed to load calendar: {str(e)}")
        
        return operations
    
    def _create_calendar_operations(self, context: Dict[str, Any]) -> List:
        """Create adjacency operations for calendar view"""
        operations = []
        
        # Main calendar container
        container_id = "calendar_container"
        container_props = {
            "className": "calendar-container",
            "style": {
                "padding": "16px",
                "maxWidth": "1200px",
                "margin": "0 auto"
            }
        }
        
        container_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("container", container_props)
        ])[0]
        operations.append(container_op)
        
        # Calendar header
        header_id = "calendar_header"
        header_props = {
            "className": "calendar-header",
            "style": {
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "16px"
            }
        }
        
        header_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("section", header_props)
        ])[0]
        header_op.parent_id = container_id
        operations.append(header_op)
        
        # Add header title
        title_id = "calendar_title"
        title_props = {
            "text": context.get("title", "Calendar"),
            "level": 2,
            "style": {"margin": "0"}
        }
        
        title_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("heading", title_props)
        ])[0]
        title_op.parent_id = header_id
        operations.append(title_op)
        
        # Add event count
        count_id = "event_count"
        count_props = {
            "text": f"{context.get('count', 0)} events",
            "style": {"color": "#666"}
        }
        
        count_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("text", count_props)
        ])[0]
        count_op.parent_id = header_id
        operations.append(count_op)
        
        # Add events list
        events = context.get("events", [])
        events_list_id = "events_list"
        events_list_props = {
            "className": "events-list",
            "style": {
                "display": "grid",
                "gap": "8px"
            }
        }
        
        list_op = self.renderer.build_adjacency_list([
            self.renderer.create_component("list", events_list_props)
        ])[0]
        list_op.parent_id = container_id
        operations.append(list_op)
        
        for i, event in enumerate(events):
            event_card_id = f"event_card_{i}"
            event_props = {
                "className": "event-card",
                "style": {
                    "padding": "12px",
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "4px",
                    "backgroundColor": "#f8f9fa"
                }
            }
            
            event_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("card", event_props)
            ])[0]
            event_op.parent_id = events_list_id
            event_op.position = i
            operations.append(event_op)
            
            # Add event title
            event_title_id = f"event_title_{i}"
            event_title_props = {
                "text": event.get("title", "Untitled Event"),
                "style": {"fontWeight": "bold", "marginBottom": "4px"}
            }
            
            event_title_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("text", event_title_props)
            ])[0]
            event_title_op.parent_id = event_card_id
            operations.append(event_title_op)
            
            # Add event time
            event_time_id = f"event_time_{i}"
            start_time = event.get("start_time", "")
            end_time = event.get("end_time", "")
            event_time_props = {
                "text": f"{start_time} - {end_time}",
                "style": {"color": "#666", "fontSize": "14px"}
            }
            
            event_time_op = self.renderer.build_adjacency_list([
                self.renderer.create_component("text", event_time_props)
            ])[0]
            event_time_op.parent_id = event_card_id
            operations.append(event_time_op)
        
        return operations
    
    async def _render_plugin_store_v2(self) -> List:
        """Render plugin store using kernel capabilities"""
        operations = []
        
        try:
            # Get all plugins
            plugins = await self.kernel.list_plugins()
            
            # Create plugin store context
            store_context = {
                "plugins": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "version": p.version,
                        "type": p.type.value,
                        "status": p.status.value,
                        "author": p.author
                    }
                    for p in plugins
                ],
                "title": "Skill Store"
            }
            
            # Use renderer to create plugin store operations
            operations = self.renderer.render_plugin_store(store_context)
            
        except Exception as e:
            logger.error(f"Failed to render plugin store: {e}")
            # Return error operations
            operations = self.renderer.render_error(f"Failed to load plugin store: {str(e)}")
        
        return operations
    
    async def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """Search across all enabled plugins"""
        try:
            return await self.kernel.search(query)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability through the kernel"""
        try:
            return await self.kernel.execute_capability(capability_id, params)
        except Exception as e:
            logger.error(f"Capability execution failed: {e}")
            return {"error": str(e)}