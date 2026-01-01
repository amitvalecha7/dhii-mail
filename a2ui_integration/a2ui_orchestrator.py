"""
A2UI Orchestrator - Central UI controller for all-A2UI architecture
Handles conversion of all application states to A2UI component schemas
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .a2ui_components_extended import A2UIComponents, A2UITemplates
from .a2ui_state_machine import A2UIStateMachine, UIState
from .a2ui_command_palette import A2UICommandPalette
from .a2ui_appshell import A2UIAppShell

logger = logging.getLogger(__name__)

class A2UIOrchestrator:
    """Central orchestrator for A2UI-based UI rendering"""
    
    def __init__(self):
        self.components = A2UIComponents()
        self.templates = A2UITemplates()
        self.state_machine = A2UIStateMachine()
        self.command_palette = A2UICommandPalette()
        self.appshell = A2UIAppShell()
        self.user_context = {}
        
    def render_ui(self, state: UIState, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render complete UI based on state and context"""
        self.user_context = context or {}
        
        # Use state machine to handle the transition (only if different state)
        current_state = self.state_machine.get_current_state()
        if current_state != state:
            success = self.state_machine.transition_to(state, "render_ui", context)
            if not success:
                logger.warning(f"State transition failed, staying in current state: {self.state_machine.get_current_state().value}")
                state = self.state_machine.get_current_state()
        
        logger.info(f"Rendering A2UI for state: {state.value}")
        
        # Route to appropriate renderer
        renderers = {
            UIState.DASHBOARD: self._render_dashboard,
            UIState.EMAIL_INBOX: self._render_email_inbox,
            UIState.EMAIL_COMPOSE: self._render_email_compose,
            UIState.EMAIL_DETAIL: self._render_email_detail,
            UIState.CALENDAR_VIEW: self._render_calendar,
            UIState.MEETING_LIST: self._render_meeting_list,
            UIState.MEETING_DETAIL: self._render_meeting_detail,
            UIState.MEETING_BOOK: self._render_meeting_book,
            UIState.TASK_BOARD: self._render_task_board,
            UIState.ANALYTICS: self._render_analytics,
            UIState.SETTINGS: self._render_settings,
            UIState.CHAT: self._render_chat,
        }
        
        renderer = renderers.get(state, self._render_dashboard)
        content_result = renderer()
        
        # Update AppShell active tab based on state
        self._update_appshell_tab(state)
        
        # Create AppShell layout
        appshell_layout = self.appshell.create_layout_component("three_pane")
        
        # Update main pane with the actual content
        main_content = content_result.get("component", {})
        self.appshell.update_pane_content("main_pane", main_content)
        
        # Update sidebar pane with navigation based on state
        sidebar_content = self._create_sidebar_content(state)
        self.appshell.update_pane_content("sidebar_pane", sidebar_content)
        
        # Update details pane with contextual content
        details_content = self._create_details_content(state)
        self.appshell.update_pane_content("details_pane", details_content)
        
        # Recreate AppShell with updated content
        ui_result = self.appshell.create_layout_component("three_pane")
        
        # Add state machine info to the result
        ui_result["state_info"] = self.state_machine.get_state_info()
        
        return ui_result
    
    def _render_dashboard(self) -> Dict[str, Any]:
        """Render main dashboard with A2UI components"""
        # Welcome card
        welcome_card = self.components.create_card(
            title=f"Welcome {self.user_context.get('name', 'User')}",
            content="Here's your workspace overview",
            actions=[
                {"label": "View Emails", "action": "navigate_email_inbox"},
                {"label": "Check Calendar", "action": "navigate_calendar"},
                {"label": "Book Meeting", "action": "navigate_meeting_book"}
            ]
        )
        
        # Quick stats
        stats_data = [
            {"label": "Unread Emails", "value": self.user_context.get("unread_count", 0)},
            {"label": "Today's Meetings", "value": self.user_context.get("today_meetings", 0)},
            {"label": "Pending Tasks", "value": self.user_context.get("pending_tasks", 0)}
        ]
        
        stats_chart = self.components.create_chart(
            chart_type="bar",
            data=stats_data,
            title="Quick Stats"
        )
        
        # Recent activity
        recent_activity = self.components.create_list(
            items=self.user_context.get("recent_activity", []),
            title="Recent Activity"
        )
        
        # Main layout
        layout = self.components.create_layout(
            orientation="vertical",
            components=[
                welcome_card,
                self.components.create_layout(
                    orientation="horizontal",
                    components=[stats_chart, recent_activity]
                )
            ]
        )
        
        return {
            "ui_type": "dashboard",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_email_inbox(self) -> Dict[str, Any]:
        """Render email inbox with A2UI components"""
        emails = self.user_context.get("emails", [])
        
        # Email list table
        email_table = self.components.create_table(
            headers=["From", "Subject", "Date", "Status"],
            rows=[
                [
                    email.get("from", ""),
                    email.get("subject", ""),
                    email.get("date", ""),
                    email.get("status", "unread")
                ]
                for email in emails[:10]  # Show first 10 emails
            ],
            table_id="email_inbox_table"
        )
        
        # Email actions toolbar
        toolbar = self.components.create_toolbar(
            actions=[
                {"label": "Compose", "action": "email_compose"},
                {"label": "Refresh", "action": "email_refresh"},
                {"label": "Search", "action": "email_search"}
            ]
        )
        
        # Filter sidebar
        filters = self.components.create_card(
            title="Filters",
            content="",
            actions=[
                {"label": "Unread", "action": "filter_unread"},
                {"label": "Today", "action": "filter_today"},
                {"label": "Important", "action": "filter_important"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="horizontal",
            components=[
                filters,
                self.components.create_layout(
                    orientation="vertical",
                    components=[toolbar, email_table]
                )
            ]
        )
        
        return {
            "ui_type": "email_inbox",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_email_compose(self) -> Dict[str, Any]:
        """Render email compose interface"""
        form_fields = [
            {"type": "text", "name": "to", "label": "To", "required": True},
            {"type": "text", "name": "subject", "label": "Subject", "required": True},
            {"type": "textarea", "name": "body", "label": "Message", "required": True},
            {"type": "file", "name": "attachments", "label": "Attachments"}
        ]
        
        compose_form = self.components.create_form(
            fields=form_fields,
            submit_action="send_email",
            form_id="email_compose_form"
        )
        
        # Template selector
        templates = self.components.create_dropdown(
            options=["Business", "Personal", "Meeting Request"]
        )
        
        layout = self.components.create_layout(
            orientation="vertical",
            components=[
                templates,
                compose_form
            ]
        )
        
        return {
            "ui_type": "email_compose",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_email_detail(self) -> Dict[str, Any]:
        """Render email detail view"""
        email_data = self.user_context.get("email_detail", {
            "from": "sender@example.com",
            "to": "user@example.com", 
            "subject": "Sample Email Subject",
            "date": "2024-01-01",
            "content": "This is a sample email content for demonstration purposes."
        })
        
        # Email header card
        header_card = self.components.create_card(
            title=email_data.get("subject", "No Subject"),
            content=f"From: {email_data.get('from', 'Unknown')}\nTo: {email_data.get('to', 'Unknown')}\nDate: {email_data.get('date', 'Unknown')}",
            actions=[
                {"label": "Reply", "action": "reply_email"},
                {"label": "Forward", "action": "forward_email"},
                {"label": "Delete", "action": "delete_email"}
            ]
        )
        
        # Email content
        content_card = self.components.create_card(
            title="Email Content",
            content=email_data.get("content", "No content available")
        )
        
        # Action toolbar
        toolbar = self.components.create_toolbar(
            actions=[
                {"label": "Back to Inbox", "action": "navigate_email_inbox"},
                {"label": "Mark as Read", "action": "mark_read"},
                {"label": "Mark as Unread", "action": "mark_unread"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="vertical",
            components=[
                toolbar,
                header_card,
                content_card
            ]
        )
        
        return {
            "ui_type": "email_detail",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_calendar(self) -> Dict[str, Any]:
        """Render calendar view"""
        # Calendar grid
        calendar_grid = self.components.create_calendar(
            events=self.user_context.get("calendar_events", [])
        )
        
        # Event list sidebar
        event_list = self.components.create_list(
            items=self.user_context.get("upcoming_events", []),
            title="Upcoming Events"
        )
        
        # Calendar controls
        controls = self.components.create_toolbar(
            actions=[
                {"label": "Today", "action": "calendar_today"},
                {"label": "Month", "action": "calendar_month"},
                {"label": "Week", "action": "calendar_week"},
                {"label": "New Event", "action": "calendar_new_event"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="horizontal",
            components=[
                self.components.create_layout(
                    orientation="vertical",
                    components=[controls, calendar_grid]
                ),
                event_list
            ]
        )
        
        return {
            "ui_type": "calendar",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_meeting_list(self) -> Dict[str, Any]:
        """Render meeting list view"""
        meetings = self.user_context.get("meetings", [])
        
        meeting_table = self.components.create_table(
            headers=["Title", "Date", "Time", "Participants", "Status"],
            rows=[
                [
                    meeting.get("title", ""),
                    meeting.get("date", ""),
                    meeting.get("time", ""),
                    ", ".join(meeting.get("participants", [])),
                    meeting.get("status", "scheduled")
                ]
                for meeting in meetings
            ],
            table_id="meeting_list_table"
        )
        
        actions = self.components.create_toolbar(
            actions=[
                {"label": "Book Meeting", "action": "meeting_book"},
                {"label": "Refresh", "action": "meeting_refresh"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="vertical",
            components=[actions, meeting_table]
        )
        
        return {
            "ui_type": "meeting_list",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_meeting_detail(self) -> Dict[str, Any]:
        """Render meeting detail view"""
        meeting_data = self.user_context.get("meeting_detail", {
            "title": "Sample Meeting",
            "date": "2024-01-01",
            "time": "10:00 AM",
            "duration": "1 hour",
            "participants": ["user@example.com", "attendee@example.com"],
            "location": "Conference Room A",
            "agenda": "Sample agenda for demonstration purposes.",
            "status": "scheduled"
        })
        
        # Meeting header card
        header_card = self.components.create_card(
            title=meeting_data.get("title", "No Title"),
            content=f"Date: {meeting_data.get('date', 'Unknown')}\nTime: {meeting_data.get('time', 'Unknown')}\nDuration: {meeting_data.get('duration', 'Unknown')}\nLocation: {meeting_data.get('location', 'Unknown')}",
            actions=[
                {"label": "Join Meeting", "action": "join_meeting"},
                {"label": "Reschedule", "action": "reschedule_meeting"},
                {"label": "Cancel", "action": "cancel_meeting"}
            ]
        )
        
        # Participants list
        participants_card = self.components.create_card(
            title="Participants",
            content=f"Total: {len(meeting_data.get('participants', []))}",
            actions=[
                {"label": "Add Participant", "action": "add_participant"},
                {"label": "Send Update", "action": "send_meeting_update"}
            ]
        )
        
        # Agenda and details
        agenda_card = self.components.create_card(
            title="Agenda",
            content=meeting_data.get("agenda", "No agenda available")
        )
        
        # Action toolbar
        toolbar = self.components.create_toolbar(
            actions=[
                {"label": "Back to Meetings", "action": "navigate_meeting_list"},
                {"label": "Edit Details", "action": "edit_meeting"},
                {"label": "Share Notes", "action": "share_meeting_notes"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="vertical",
            components=[
                toolbar,
                header_card,
                self.components.create_layout(
                    orientation="horizontal",
                    components=[participants_card, agenda_card]
                )
            ]
        )
        
        return {
            "ui_type": "meeting_detail",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_meeting_book(self) -> Dict[str, Any]:
        """Render meeting booking interface"""
        # Meeting details form
        form_fields = [
            {"type": "text", "name": "title", "label": "Meeting Title", "required": True},
            {"type": "date", "name": "date", "label": "Date", "required": True},
            {"type": "time", "name": "start_time", "label": "Start Time", "required": True},
            {"type": "time", "name": "end_time", "label": "End Time", "required": True},
            {"type": "text", "name": "participants", "label": "Participants (comma-separated emails)", "required": True},
            {"type": "textarea", "name": "agenda", "label": "Agenda", "required": False}
        ]
        
        booking_form = self.components.create_form(
            fields=form_fields,
            submit_action="book_meeting",
            form_id="meeting_book_form"
        )
        
        # Available time slots
        available_slots = self.components.create_card(
            title="Available Time Slots",
            content="Select from available slots or propose custom time",
            actions=[
                {"label": "10:00 AM", "action": "select_time_10am"},
                {"label": "2:00 PM", "action": "select_time_2pm"},
                {"label": "4:00 PM", "action": "select_time_4pm"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="horizontal",
            components=[
                booking_form,
                available_slots
            ]
        )
        
        return {
            "ui_type": "meeting_book",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_task_board(self) -> Dict[str, Any]:
        """Render task board view"""
        tasks = self.user_context.get("tasks", [])
        
        # Kanban columns
        columns = ["To Do", "In Progress", "Done"]
        kanban_columns = []
        
        for column in columns:
            column_tasks = [task for task in tasks if task.get("status") == column]
            column_component = self.components.create_card(
                title=column,
                content="",
                actions=[
                    {"label": task.get("title", ""), "action": f"task_detail_{task.get('id', '')}"}
                    for task in column_tasks
                ]
            )
            kanban_columns.append(column_component)
        
        # Task creation form
        task_form = self.components.create_form(
            fields=[
                {"type": "text", "name": "title", "label": "Task Title", "required": True},
                {"type": "textarea", "name": "description", "label": "Description"},
                {"type": "select", "name": "priority", "label": "Priority", "options": ["Low", "Medium", "High"]}
            ],
            submit_action="create_task",
            form_id="task_create_form"
        )
        
        layout = self.components.create_layout(
            orientation="vertical",
            components=[
                self.components.create_layout(
                    orientation="horizontal",
                    components=kanban_columns
                ),
                task_form
            ]
        )
        
        return {
            "ui_type": "task_board",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_analytics(self) -> Dict[str, Any]:
        """Render analytics dashboard"""
        # Email analytics
        email_chart = self.components.create_chart(
            chart_type="line",
            data=self.user_context.get("email_analytics", []),
            title="Email Activity"
        )
        
        # Meeting analytics
        meeting_chart = self.components.create_chart(
            chart_type="pie",
            data=self.user_context.get("meeting_analytics", []),
            title="Meeting Distribution"
        )
        
        # Task analytics
        task_chart = self.components.create_chart(
            chart_type="bar",
            data=self.user_context.get("task_analytics", []),
            title="Task Completion"
        )
        
        # Summary cards
        summary_cards = self.components.create_layout(
            orientation="horizontal",
            components=[
                self.components.create_card("Total Emails", "1,234"),
                self.components.create_card("Meetings This Week", "12"),
                self.components.create_card("Tasks Completed", "45")
            ]
        )
        
        layout = self.components.create_layout(
            orientation="vertical",
            components=[
                summary_cards,
                self.components.create_layout(
                    orientation="horizontal",
                    components=[email_chart, meeting_chart, task_chart]
                )
            ]
        )
        
        return {
            "ui_type": "analytics",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_settings(self) -> Dict[str, Any]:
        """Render settings interface"""
        # User preferences form
        settings_form = self.components.create_form(
            fields=[
                {"type": "text", "name": "name", "label": "Full Name"},
                {"type": "email", "name": "email", "label": "Email Address"},
                {"type": "select", "name": "timezone", "label": "Timezone", "options": ["UTC", "EST", "PST", "CST"]},
                {"type": "checkbox", "name": "notifications", "label": "Enable Notifications"},
                {"type": "checkbox", "name": "auto_sync", "label": "Auto-sync Calendar"}
            ],
            submit_action="update_settings",
            form_id="settings_form"
        )
        
        # Integration settings
        integrations = self.components.create_card(
            title="Integrations",
            content="Manage your connected accounts and services",
            actions=[
                {"label": "Google Calendar", "action": "configure_google_calendar"},
                {"label": "Email Accounts", "action": "configure_email_accounts"},
                {"label": "CRM Integration", "action": "configure_crm"}
            ]
        )
        
        layout = self.components.create_layout(
            orientation="horizontal",
            components=[
                settings_form,
                integrations
            ]
        )
        
        return {
            "ui_type": "settings",
            "layout": layout,
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
    
    def _render_chat(self) -> Dict[str, Any]:
        """Render chat interface as A2UI component"""
        return {
            "ui_type": "chat",
            "layout": self._get_chat_component(),
            "navigation": self._get_navigation_bar()
        }
    
    def _get_navigation_bar(self) -> Dict[str, Any]:
        """Get standard navigation bar"""
        return self.components.create_navigation(
            items=[
                {"label": "Dashboard", "action": "navigate_dashboard", "icon": "home"},
                {"label": "Email", "action": "navigate_email_inbox", "icon": "email"},
                {"label": "Calendar", "action": "navigate_calendar", "icon": "calendar"},
                {"label": "Meetings", "action": "navigate_meetings", "icon": "meeting"},
                {"label": "Tasks", "action": "navigate_tasks", "icon": "task"},
                {"label": "Analytics", "action": "navigate_analytics", "icon": "analytics"},
                {"label": "Settings", "action": "navigate_settings", "icon": "settings"}
            ]
        )
    
    def _get_chat_component(self) -> Dict[str, Any]:
        """Get chat component for integration"""
        return self.components.create_chat(
            messages=self.user_context.get("chat_messages", []),
            input_placeholder="Type your message...",
            send_action="send_chat_message"
        )
    
    def handle_action(self, action: str, data: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """Handle user actions and return updated UI"""
        logger.info(f"Handling action: {action} with data: {data}")
        
        # Navigation actions
        navigation_map = {
            "navigate_dashboard": UIState.DASHBOARD,
            "navigate_email_inbox": UIState.EMAIL_INBOX,
            "navigate_calendar": UIState.CALENDAR_VIEW,
            "navigate_meetings": UIState.MEETING_LIST,
            "navigate_tasks": UIState.TASK_BOARD,
            "navigate_analytics": UIState.ANALYTICS,
            "navigate_settings": UIState.SETTINGS,
            "email_compose": UIState.EMAIL_COMPOSE,
            "meeting_book": UIState.MEETING_BOOK,
        }
        
        if action in navigation_map:
            target_state = navigation_map[action]
            current_state = self.state_machine.get_current_state()
            
            # If already in target state, just re-render
            if current_state == target_state:
                return self.render_ui(target_state, data)
            
            success = self.state_machine.transition_to(target_state, action, data)
            if success:
                return self.render_ui(target_state, data)
            else:
                # Return current state UI with error information
                current_ui = self.render_ui(self.state_machine.get_current_state(), self.user_context)
                current_ui["transition_error"] = {
                    "status": "transition_failed",
                    "action": action,
                    "target_state": target_state.value,
                    "current_state": self.state_machine.get_current_state().value,
                    "available_transitions": [state.value for state in self.state_machine.get_available_transitions()]
                }
                return current_ui
        
        # Handle command palette actions
        if action == "open_command_palette":
            palette_component = self.command_palette.get_palette_component("", self.user_context)
            current_ui = self.render_ui(self.state_machine.get_current_state(), self.user_context)
            current_ui["command_palette"] = palette_component
            return current_ui
        
        if action == "search_commands":
            query = data.get("query", "") if data else ""
            palette_component = self.command_palette.get_palette_component(query, self.user_context)
            current_ui = self.render_ui(self.state_machine.get_current_state(), self.user_context)
            current_ui["command_palette"] = palette_component
            return current_ui
        
        if action == "execute_command":
            command_id = data.get("command_id") if data else None
            if command_id:
                result = self.command_palette.execute_command(command_id, self.user_context)
                if result.get("success"):
                    # Execute the command's action
                    command_action = result.get("action")
                    if command_action:
                        return self.handle_action(command_action, result.get("data"))
                # Return current UI with command result
                current_ui = self.render_ui(self.state_machine.get_current_state(), self.user_context)
                current_ui["command_result"] = result
                return current_ui
        
        # Handle other actions (email send, meeting book, etc.)
        # These would integrate with your business logic
        
        # For now, return current UI with action acknowledgment
        current_ui = self.render_ui(self.state_machine.get_current_state(), self.user_context)
        current_ui["action_acknowledgment"] = {
            "status": "action_handled",
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return current_ui
    
    def get_state_machine_info(self) -> Dict[str, Any]:
        """Get comprehensive state machine information"""
        return self.state_machine.get_state_info()
    
    def _update_appshell_tab(self, state: UIState) -> None:
        """Update AppShell active tab based on current state"""
        tab_mapping = {
            UIState.DASHBOARD: "home",
            UIState.EMAIL_INBOX: "email",
            UIState.EMAIL_DETAIL: "email",
            UIState.EMAIL_COMPOSE: "email",
            UIState.CALENDAR_VIEW: "calendar",
            UIState.MEETING_LIST: "meetings",
            UIState.MEETING_DETAIL: "meetings",
            UIState.MEETING_BOOK: "meetings",
            UIState.TASK_BOARD: "tasks",
            UIState.ANALYTICS: "analytics",
            UIState.SETTINGS: "settings",
            UIState.CHAT: "home"  # Default to home for chat
        }
        
        from a2ui_integration.a2ui_appshell import RibbonTabType
        
        tab_type_str = tab_mapping.get(state, "home")
        tab_type_enum = RibbonTabType(tab_type_str)
        self.appshell.set_active_tab(tab_type_enum)
    
    def _create_sidebar_content(self, state: UIState) -> Dict[str, Any]:
        """Create sidebar content based on current state"""
        # Create navigation menu
        nav_items = [
            {"id": "dashboard", "title": "Dashboard", "icon": "dashboard", "action": "navigate_dashboard", "active": state == UIState.DASHBOARD},
            {"id": "email", "title": "Email", "icon": "email", "action": "navigate_email", "active": state in [UIState.EMAIL_INBOX, UIState.EMAIL_DETAIL, UIState.EMAIL_COMPOSE]},
            {"id": "calendar", "title": "Calendar", "icon": "calendar", "action": "navigate_calendar", "active": state == UIState.CALENDAR_VIEW},
            {"id": "meetings", "title": "Meetings", "icon": "meetings", "action": "navigate_meetings", "active": state in [UIState.MEETING_LIST, UIState.MEETING_DETAIL, UIState.MEETING_BOOK]},
            {"id": "tasks", "title": "Tasks", "icon": "tasks", "action": "navigate_tasks", "active": state == UIState.TASK_BOARD},
            {"id": "analytics", "title": "Analytics", "icon": "analytics", "action": "navigate_analytics", "active": state == UIState.ANALYTICS},
            {"id": "settings", "title": "Settings", "icon": "settings", "action": "navigate_settings", "active": state == UIState.SETTINGS},
        ]
        
        return self.components.create_list(
            items=[
                {
                    "id": item["id"],
                    "title": item["title"],
                    "subtitle": "",
                    "icon": item["icon"],
                    "action": item["action"],
                    "active": item["active"]
                }
                for item in nav_items
            ]
        )
    
    def _create_details_content(self, state: UIState) -> Dict[str, Any]:
        """Create details pane content based on current state"""
        if state == UIState.EMAIL_INBOX:
            return self.components.create_card(
                title="Email Tips",
                content="Select an email to view details and actions. Use keyboard shortcuts for faster navigation."
            )
        elif state == UIState.CALENDAR_VIEW:
            return self.components.create_card(
                title="Calendar Info",
                content="Click on events to view details. Drag to reschedule. Use the ribbon for quick actions."
            )
        elif state == UIState.MEETING_LIST:
            return self.components.create_card(
                title="Meeting Info",
                content="Select a meeting to view participants and details. Join meetings directly from here."
            )
        else:
            return self.components.create_card(
                title="Quick Actions",
                content="Use the command palette (Cmd+K) for quick navigation. Customize your workspace in settings."
            )
    
    def rollback_state(self) -> Dict[str, Any]:
        """Rollback to previous state"""
        success = self.state_machine.rollback_to_previous()
        if success:
            return {
                "status": "rollback_success",
                "new_state": self.state_machine.get_current_state().value,
                "ui_update": self.render_ui(self.state_machine.get_current_state(), self.user_context)
            }
        else:
            return {
                "status": "rollback_failed",
                "current_state": self.state_machine.get_current_state().value
            }
    
    def get_available_actions(self) -> List[str]:
        """Get available actions based on current state"""
        current_state = self.state_machine.get_current_state()
        
        # Map states to available actions
        state_actions = {
            UIState.DASHBOARD: ["navigate_email_inbox", "navigate_calendar", "navigate_meetings", "navigate_tasks", "navigate_analytics", "navigate_settings"],
            UIState.EMAIL_INBOX: ["email_compose", "email_refresh", "email_search", "navigate_dashboard", "navigate_calendar"],
            UIState.EMAIL_DETAIL: ["email_reply", "email_forward", "email_delete", "navigate_email_inbox"],
            UIState.EMAIL_COMPOSE: ["email_send", "email_save_draft", "email_cancel", "navigate_email_inbox"],
            UIState.CALENDAR_VIEW: ["meeting_book", "meeting_view", "navigate_dashboard", "navigate_email_inbox"],
            UIState.MEETING_LIST: ["meeting_book", "meeting_view", "navigate_dashboard", "navigate_calendar"],
            UIState.MEETING_DETAIL: ["meeting_edit", "meeting_cancel", "meeting_reschedule", "navigate_meeting_list"],
            UIState.MEETING_BOOK: ["meeting_save", "meeting_cancel", "navigate_meeting_list", "navigate_calendar"],
            UIState.TASK_BOARD: ["task_create", "task_edit", "task_complete", "navigate_dashboard"],
            UIState.ANALYTICS: ["analytics_export", "analytics_refresh", "navigate_dashboard"],
            UIState.SETTINGS: ["settings_save", "settings_reset", "navigate_dashboard"],
            UIState.CHAT: ["send_chat_message", "clear_chat", "navigate_dashboard"]
        }
        
        return state_actions.get(current_state, ["navigate_dashboard"])