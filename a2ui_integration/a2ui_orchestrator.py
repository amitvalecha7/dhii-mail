"""
A2UI Orchestrator - Central UI controller for all-A2UI architecture
Handles conversion of all application states to A2UI component schemas
"""

import json
import logging
import os
import re
import asyncio
import aiohttp
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel
import httpx

from a2ui_integration.a2ui_components_extended import A2UIComponents, A2UITemplates
from a2ui_integration.a2ui_state_machine import A2UIStateMachine, UIState, StateTransition
from a2ui_integration.a2ui_command_palette import A2UICommandPalette
from a2ui_integration.a2ui_appshell import A2UIAppShell
from a2ui_integration.data_structures import ComponentGraph
from dataclasses import dataclass
from typing import TYPE_CHECKING
from a2ui_integration.neural_loop_ai_engine import EnhancedNeuralLoopEngine, NeuralLoopContext as EnhancedNeuralLoopContext, IntentType, AmbiguityType
from a2ui_integration.backend_ui_mapping_contract import BackendUIMappingContract, OrchestratorOutput, IntentType as MappingIntentType

if TYPE_CHECKING:
    from tenant_manager import TenantContext

logger = logging.getLogger(__name__)

class OrchestratorState(Enum):
    """Symphony Orchestrator states for Neural Loop processing"""
    IDLE = "idle"
    INTENT_PROCESSING = "intent_processing"
    AMBIGUITY_RESOLUTION = "ambiguity_resolution"
    OPTIMISTIC_EXECUTION = "optimistic_execution"
    COMPOSITION = "composition"
    ERROR_RECOVERY = "error_recovery"

@dataclass
class NeuralLoopContext:
    """Context for Neural Loop processing"""
    user_intent: str
    raw_input: str
    detected_intent: Optional[Dict[str, Any]] = None
    missing_parameters: List[str] = None
    clarification_questions: List[str] = None
    plugin_capabilities: List[Dict[str, Any]] = None
    execution_results: Dict[str, Any] = None
    ui_skeleton: Optional[Dict[str, Any]] = None
    error_context: Optional[Dict[str, Any]] = None

@dataclass  
class OptimisticExecutionResult:
    """Result of optimistic execution for latency hiding"""
    skeleton_component: Dict[str, Any]
    final_component: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0
    success: bool = True

# AI Models (Consolidated from ai_engine.py)
class AIIntent(BaseModel):
    """Represents detected user intent"""
    intent: str
    confidence: float
    entities: Dict[str, Any] = {}
    response_type: str = "text"
    requires_clarification: bool = False
    ambiguity_reason: Optional[str] = None

class AIResponse(BaseModel):
    """Complete AI response with UI components"""
    message: str
    intent: AIIntent
    actions: List[Dict[str, Any]] = []
    ui_components: Optional[Dict[str, Any]] = None
    requires_user_input: bool = False
    session_data: Dict[str, Any] = {}

class A2UIOrchestrator:
    """Central orchestrator for A2UI-based UI rendering"""
    
    def __init__(self):
        self.components = A2UIComponents()
        self.templates = A2UITemplates()
        self.state_machine = A2UIStateMachine()
        self.command_palette = A2UICommandPalette()
        self.appshell = A2UIAppShell()
        self.user_context = {}
        
        # Neural Loop processing state
        self.neural_loop_state = OrchestratorState.IDLE
        self.current_loop: Optional[NeuralLoopContext] = None
        
        # AI Engine functionality (consolidated from ai_engine.py)
        self.system_prompt = """You are dhii, an AI assistant specialized in email and calendar management.
You help users with scheduling meetings, sending emails, managing calendars, and organizing their digital workspace.
Be helpful, professional, and provide clear actionable responses."""
        self.use_openrouter = os.getenv('USE_OPENROUTER', 'false').lower() == 'true'
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        self.conversation_history = []
        
        # Neural Loop handlers
        self.loop_handlers = {
            OrchestratorState.INTENT_PROCESSING: self._handle_intent_processing,
            OrchestratorState.AMBIGUITY_RESOLUTION: self._handle_ambiguity_resolution,
            OrchestratorState.OPTIMISTIC_EXECUTION: self._handle_optimistic_execution,
            OrchestratorState.COMPOSITION: self._handle_composition,
            OrchestratorState.ERROR_RECOVERY: self._handle_error_recovery
        }
        
        # Tenant-aware methods
        self.tenant_context = None
        # Enhanced Neural Loop engine
        self.neural_loop_engine = EnhancedNeuralLoopEngine()
        
        # Backend→UI Mapping Contract (New Design Spec v1.2)
        self.mapping_contract = BackendUIMappingContract()
        
    def render_ui(self, state: UIState, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render complete UI based on state and context"""
        self.user_context = context or {}
        
        # Use state machine to handle the transition (only if different state)
        current_state = self.state_machine.get_current_state()
        if current_state != state:
            success = self.state_machine.transition_to(state, "render_ui", context)
            if not success:
                # For API-driven transitions, allow direct state setting for navigation
                # This handles cases where users navigate directly to specific views via URL
                logger.info(f"API-driven state change: {current_state.value} -> {state.value}")
                # Create a direct transition record
                transition = StateTransition(
                    from_state=current_state,
                    to_state=state,
                    action="api_navigation",
                    context=context or {},
                    timestamp=datetime.now(),
                    user_id=None
                )
                self.state_machine.state_history.append(transition)
                self.state_machine.current_state = state
        
        logger.info(f"Rendering A2UI for state: {state.value}")
        
        # Route to appropriate renderer
        renderers = {
            UIState.DASHBOARD: self._render_aggregated_dashboard,  # New Design Spec compliant
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
        
        # Build complete adjacency list with AppShell
        graph = ComponentGraph()
        
        # Create AppShell root node
        appshell_id = graph.add_node("AppShell", {
            "layout": "three_pane",
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        })
        
        # Add main content
        main_content = content_result.get("component", {})
        main_content_id = graph.add_node("ContentPane", {
            "pane": "main_pane",
            "content": main_content
        })
        graph.add_child(appshell_id, main_content_id)
        
        # Add sidebar content
        sidebar_content = self._create_sidebar_content(state)
        sidebar_content_id = graph.add_node("ContentPane", {
            "pane": "sidebar_pane", 
            "content": sidebar_content
        })
        graph.add_child(appshell_id, sidebar_content_id)
        
        # Add details content
        details_content = self._create_details_content(state)
        details_content_id = graph.add_node("ContentPane", {
            "pane": "details_pane",
            "content": details_content
        })
        graph.add_child(appshell_id, details_content_id)
        
        # Return A2UI-compliant adjacency list format
        return {
            "adjacencyList": graph.to_adjacency_list(),
            "state_info": self.state_machine.get_state_info()
        }
    
    def _render_aggregated_dashboard(self) -> Dict[str, Any]:
        """Render dashboard using AggregatedCard (New Design Spec v1.2 compliant)"""
        # Get tenant and user context for mapping contract
        tenant_id = self.tenant_context.get("tenant_id", "default") if self.tenant_context else "default"
        user_id = self.user_context.get("user_id", "default")
        
        # Create chunks using mapping contract
        welcome_chunk = self.create_text_block_chunk(
            content=f"Welcome back, {self.user_context.get('name', 'User')}! Here's your workspace overview.",
            tone="neutral",
            collapsible=True,
            completed=False
        )
        
        advisory_chunk = self.create_text_block_chunk(
            content="You have 3 urgent items requiring attention.",
            tone="advisory",
            collapsible=False,
            completed=False
        )
        
        aggregated_chunk = self.create_aggregated_card_chunk(
            title="Today's Focus Areas",
            sources=["email", "tasks", "calendar"],
            items=[
                {"label": "Urgent Emails", "value": self.user_context.get('pendingEmails', 0)},
                {"label": "Overdue Tasks", "value": self.user_context.get('overdueTasks', 0)},
                {"label": "Today's Meetings", "value": self.user_context.get('meetingsToday', 0)},
                {"label": "Pending Actions", "value": self.user_context.get('pendingActions', 0)}
            ],
            multiple_sources=True,
            partial_rendering=True,
            importance_based_layout=True
        )
        
        # Create compliant orchestrator output
        output = self.create_orchestrator_output(
            tenant_id=tenant_id,
            user_id=user_id,
            state="COMPLETED",
            chunks=[welcome_chunk, advisory_chunk, aggregated_chunk],
            explanation="Dashboard overview with focus areas and workspace summary"
        )
        
        # Convert to UI format (this would be handled by the UI runtime)
        return {
            "orchestrator_output": output.dict(),
            "adjacency_list": self._chunks_to_adjacency_list(output.chunks)
        }
    
    def _chunks_to_adjacency_list(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert chunks to adjacency list format for UI rendering"""
        graph = ComponentGraph()
        
        # Add each chunk as a node
        chunk_nodes = []
        for chunk in chunks:
            if chunk["type"] == "TextBlock":
                node_id = graph.add_node("TextBlock", chunk)
            elif chunk["type"] == "AggregatedCard":
                node_id = graph.add_node("AggregatedCard", chunk)
            else:
                # Default to Card for unknown types
                node_id = graph.add_node("Card", chunk)
            chunk_nodes.append(node_id)
        
        # Create layout
        layout_id = graph.add_node("Layout", {
            "type": "dashboard",
            "orientation": "vertical"
        })
        
        # Add chunks to layout
        for node_id in chunk_nodes:
            graph.add_child(layout_id, node_id)
        
        return graph.to_adjacency_list()
        
        # Add components to layout
        graph.add_child(layout_id, welcome_text_id)
        graph.add_child(layout_id, advisory_text_id)
        graph.add_child(layout_id, aggregated_card_id)
        
        return graph.to_json()
    
    def _render_dashboard(self) -> Dict[str, Any]:
        """Render main dashboard with A2UI components (Legacy - will be deprecated)"""
        graph = ComponentGraph()
        
        # Welcome card
        welcome_card_id = graph.add_node("Card", {
            "title": f"Welcome {self.user_context.get('name', 'User')}",
            "content": "Here's your workspace overview",
            "actions": [
                {"label": "View Emails", "action": "navigate_email_inbox"},
                {"label": "Check Calendar", "action": "navigate_calendar"},
                {"label": "Book Meeting", "action": "navigate_meeting_book"}
            ]
        })
        
        # Quick stats
        stats_data = [
            {"label": "Unread Emails", "value": self.user_context.get("unread_count", 0)},
            {"label": "Today's Meetings", "value": self.user_context.get("today_meetings", 0)},
            {"label": "Pending Tasks", "value": self.user_context.get("pending_tasks", 0)}
        ]
        
        stats_chart_id = graph.add_node("Chart", {
            "chart_type": "bar",
            "data": stats_data,
            "title": "Quick Stats"
        })
        
        # Recent activity
        recent_activity_id = graph.add_node("List", {
            "items": self.user_context.get("recent_activity", []),
            "title": "Recent Activity"
        })
        
        # Inner Layout (Horizontal)
        inner_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        graph.add_child(inner_layout_id, stats_chart_id)
        graph.add_child(inner_layout_id, recent_activity_id)
        
        # Main Layout (Vertical)
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical"
        })
        graph.add_child(main_layout_id, welcome_card_id)
        graph.add_child(main_layout_id, inner_layout_id)
        
        graph.set_root(main_layout_id)
        
        # Return adjacency list format
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_email_inbox(self) -> Dict[str, Any]:
        """Render email inbox with A2UI components"""
        graph = ComponentGraph()
        emails = self.user_context.get("emails", [])
        
        # Email list table
        email_table_id = graph.add_node("Table", {
            "headers": ["From", "Subject", "Date", "Status"],
            "rows": [
                [
                    email.get("from", ""),
                    email.get("subject", ""),
                    email.get("date", ""),
                    email.get("status", "unread")
                ]
                for email in emails[:10]  # Show first 10 emails
            ],
            "table_id": "email_inbox_table"
        })
        
        # Email actions toolbar
        toolbar_id = graph.add_node("Toolbar", {
            "actions": [
                {"label": "Compose", "action": "email_compose"},
                {"label": "Refresh", "action": "email_refresh"},
                {"label": "Search", "action": "email_search"}
            ]
        })
        
        # Filter sidebar
        filters_id = graph.add_node("Card", {
            "title": "Filters",
            "content": "",
            "actions": [
                {"label": "Unread", "action": "filter_unread"},
                {"label": "Today", "action": "filter_today"},
                {"label": "Important", "action": "filter_important"}
            ]
        })
        
        # Right layout (Toolbar + Table)
        right_layout_id = graph.add_node("Layout", {
            "orientation": "vertical"
        })
        graph.add_child(right_layout_id, toolbar_id)
        graph.add_child(right_layout_id, email_table_id)
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        graph.add_child(main_layout_id, filters_id)
        graph.add_child(main_layout_id, right_layout_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_email_compose(self) -> Dict[str, Any]:
        """Render email compose interface"""
        graph = ComponentGraph()
        
        form_fields = [
            {"type": "text", "name": "to", "label": "To", "required": True},
            {"type": "text", "name": "subject", "label": "Subject", "required": True},
            {"type": "textarea", "name": "body", "label": "Message", "required": True},
            {"type": "file", "name": "attachments", "label": "Attachments"}
        ]
        
        compose_form_id = graph.add_node("Form", {
            "fields": form_fields,
            "submit_action": "send_email",
            "form_id": "email_compose_form"
        })
        
        # Template selector
        templates_id = graph.add_node("Dropdown", {
            "options": ["Business", "Personal", "Meeting Request"]
        })
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical"
        })
        graph.add_child(main_layout_id, templates_id)
        graph.add_child(main_layout_id, compose_form_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_email_detail(self) -> Dict[str, Any]:
        """Render email detail view with New Design Spec v1.2 components"""
        graph = ComponentGraph()
        
        email_data = self.user_context.get("email_detail", {
            "from": "sender@example.com",
            "to": "user@example.com", 
            "subject": "Sample Email Subject",
            "date": "2024-01-01",
            "content": "This is a sample email content for demonstration purposes."
        })
        
        # Email header using TextBlock
        header_text_id = graph.add_node("TextBlock", {
            "content": f"Subject: {email_data.get('subject', 'No Subject')}\nFrom: {email_data.get('from', 'Unknown')}\nTo: {email_data.get('to', 'Unknown')}\nDate: {email_data.get('date', 'Unknown')}",
            "tone": "neutral",
            "collapsible": False,
            "completed": False
        })
        
        # Email content using TextBlock
        content_text_id = graph.add_node("TextBlock", {
            "content": email_data.get("content", "No content available"),
            "tone": "neutral",
            "collapsible": True,
            "completed": False
        })
        
        # AggregatedCard for email actions
        actions_card_id = graph.add_node("AggregatedCard", {
            "title": "Email Actions",
            "sources": ["email"],
            "items": [
                {"label": "Reply", "value": "reply_email"},
                {"label": "Forward", "action": "forward_email"},
                {"label": "Delete", "action": "delete_email"}
            ],
            "multiple_sources": False,
            "partial_rendering": True,
            "importance_based_layout": True
        })
        
        # Action toolbar
        toolbar_id = graph.add_node("Toolbar", {
            "actions": [
                {"label": "Back to Inbox", "action": "navigate_email_inbox"},
                {"label": "Mark as Read", "action": "mark_read"},
                {"label": "Mark as Unread", "action": "mark_unread"}
            ]
        })
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical"
        })
        graph.add_child(main_layout_id, toolbar_id)
        graph.add_child(main_layout_id, header_text_id)
        graph.add_child(main_layout_id, content_text_id)
        graph.add_child(main_layout_id, actions_card_id)
        
        graph.set_root(main_layout_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_calendar(self) -> Dict[str, Any]:
        """Render calendar view"""
        graph = ComponentGraph()
        
        # Calendar grid
        calendar_grid_id = graph.add_node("Calendar", {
            "events": self.user_context.get("calendar_events", [])
        })
        
        # Event list sidebar
        event_list_id = graph.add_node("List", {
            "items": self.user_context.get("upcoming_events", []),
            "title": "Upcoming Events"
        })
        
        # Calendar controls
        controls_id = graph.add_node("Toolbar", {
            "actions": [
                {"label": "Today", "action": "calendar_today"},
                {"label": "Month", "action": "calendar_month"},
                {"label": "Week", "action": "calendar_week"},
                {"label": "New Event", "action": "calendar_new_event"}
            ]
        })
        
        # Left layout (Controls + Calendar)
        left_layout_id = graph.add_node("Layout", {
            "orientation": "vertical"
        })
        graph.add_child(left_layout_id, controls_id)
        graph.add_child(left_layout_id, calendar_grid_id)
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        graph.add_child(main_layout_id, left_layout_id)
        graph.add_child(main_layout_id, event_list_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_meeting_list(self) -> Dict[str, Any]:
        """Render meeting list view (Grid of Glass Cards)"""
        graph = ComponentGraph()
        meetings = self.user_context.get("meetings", [])
        
        # Action toolbar
        actions_id = graph.add_node("Toolbar", {
            "actions": [
                {"label": "Book Meeting", "action": "meeting_book", "icon": "add"},
                {"label": "Refresh", "action": "meeting_refresh", "icon": "refresh"}
            ]
        })
        
        # Grid Layout for Meeting Cards
        grid_id = graph.add_node("Grid", {
            "columns": 3,
            "gap": "medium",
            "title": "Upcoming Meetings"
        })

        if not meetings:
            empty_state_id = graph.add_node("Card", {
                "title": "No Meetings",
                "content": "You have no upcoming meetings scheduled.",
                "variant": "glass"
            })
            graph.add_child(grid_id, empty_state_id)
        else:
            for meeting in meetings:
                # Format card content
                participants = meeting.get("participants", [])
                participant_text = ", ".join(participants[:2])
                if len(participants) > 2:
                    participant_text += f" +{len(participants)-2} more"
                    
                card_content = (
                    f"📅 {meeting.get('date', '')} at {meeting.get('time', '')}\n"
                    f"⏱️ {meeting.get('duration', '')} mins\n"
                    f"👥 {participant_text}"
                )
                
                meeting_card_id = graph.add_node("Card", {
                    "title": meeting.get("title", "Untitled"),
                    "content": card_content,
                    "variant": "glass",
                    "status": meeting.get("status", "scheduled"),
                    "actions": [
                        {"label": "Details", "action": "view_meeting", "params": {"id": meeting.get("id")}},
                        {"label": "Join", "action": "join_meeting", "params": {"id": meeting.get("id")}}
                    ]
                })
                graph.add_child(grid_id, meeting_card_id)
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical",
            "padding": "medium"
        })
        graph.add_child(main_layout_id, actions_id)
        graph.add_child(main_layout_id, grid_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_meeting_detail(self) -> Dict[str, Any]:
        """Render meeting detail view (Glass Card)"""
        graph = ComponentGraph()
        
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
        
        # Meeting header card (Glass Variant)
        header_card_id = graph.add_node("Card", {
            "title": meeting_data.get("title", "No Title"),
            "content": (
                f"📅 Date: {meeting_data.get('date', 'Unknown')}\n"
                f"⏰ Time: {meeting_data.get('time', 'Unknown')} ({meeting_data.get('duration', '60')} mins)\n"
                f"📍 Location: {meeting_data.get('location', 'Unknown')}\n"
                f"📊 Status: {meeting_data.get('status', 'scheduled')}"
            ),
            "variant": "glass",
            "actions": [
                {"label": "Join Meeting", "action": "join_meeting"},
                {"label": "Reschedule", "action": "reschedule_meeting"},
                {"label": "Cancel", "action": "cancel_meeting"}
            ]
        })
        
        # Participants list
        participants_card_id = graph.add_node("Card", {
            "title": "Participants",
            "content": "\n".join([f"• {p}" for p in meeting_data.get('participants', [])]),
            "variant": "glass",
            "actions": [
                {"label": "Add Participant", "action": "add_participant"},
                {"label": "Email All", "action": "email_participants"}
            ]
        })
        
        # Agenda and details
        agenda_card_id = graph.add_node("Card", {
            "title": "Agenda",
            "content": meeting_data.get("agenda", "No agenda available"),
            "variant": "glass"
        })
        
        # Action toolbar
        toolbar_id = graph.add_node("Toolbar", {
            "actions": [
                {"label": "Back to Meetings", "action": "navigate_meeting_list", "icon": "arrow_back"},
                {"label": "Edit Details", "action": "edit_meeting", "icon": "edit"},
                {"label": "Share Notes", "action": "share_meeting_notes", "icon": "share"}
            ]
        })
        
        # Bottom layout (Participants + Agenda)
        bottom_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal",
            "gap": "medium"
        })
        graph.add_child(bottom_layout_id, participants_card_id)
        graph.add_child(bottom_layout_id, agenda_card_id)
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical",
            "padding": "medium"
        })
        graph.add_child(main_layout_id, toolbar_id)
        graph.add_child(main_layout_id, header_card_id)
        graph.add_child(main_layout_id, bottom_layout_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_meeting_book(self) -> Dict[str, Any]:
        """Render meeting booking interface (Form)"""
        graph = ComponentGraph()
        
        # Action toolbar
        toolbar_id = graph.add_node("Toolbar", {
            "actions": [
                {"label": "Cancel", "action": "navigate_meeting_list", "icon": "close"}
            ]
        })

        # Meeting details form
        form_fields = [
            {"type": "text", "name": "title", "label": "Meeting Title", "required": True, "placeholder": "Weekly Sync"},
            {"type": "date", "name": "date", "label": "Date", "required": True},
            {"type": "time", "name": "start_time", "label": "Start Time", "required": True},
            {"type": "number", "name": "duration", "label": "Duration (minutes)", "required": True, "default": 60},
            {"type": "text", "name": "participants", "label": "Participants", "required": True, "placeholder": "email1@dhii.ai, email2@dhii.ai"},
            {"type": "textarea", "name": "agenda", "label": "Agenda", "required": False, "rows": 4}
        ]
        
        booking_form_id = graph.add_node("Form", {
            "title": "Book New Meeting",
            "fields": form_fields,
            "submit_action": "book_meeting",
            "submit_label": "Schedule Meeting",
            "form_id": "meeting_book_form",
            "variant": "glass"
        })
        
        # Available time slots (Sidebar helper)
        available_slots_id = graph.add_node("Card", {
            "title": "Suggested Times",
            "content": "Based on team availability",
            "variant": "glass",
            "actions": [
                {"label": "10:00 AM", "action": "select_time", "params": {"time": "10:00"}},
                {"label": "2:00 PM", "action": "select_time", "params": {"time": "14:00"}},
                {"label": "4:00 PM", "action": "select_time", "params": {"time": "16:00"}}
            ]
        })
        
        # Content Layout
        content_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal",
            "gap": "medium"
        })
        graph.add_child(content_layout_id, booking_form_id)
        graph.add_child(content_layout_id, available_slots_id)

        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical",
            "padding": "medium"
        })
        graph.add_child(main_layout_id, toolbar_id)
        graph.add_child(main_layout_id, content_layout_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_task_board(self) -> Dict[str, Any]:
        """Render task board view"""
        graph = ComponentGraph()
        tasks = self.user_context.get("tasks", [])
        
        # Kanban columns
        columns = ["To Do", "In Progress", "Done"]
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        
        for column in columns:
            column_tasks = [task for task in tasks if task.get("status") == column]
            
            # Create a layout for the column content
            column_layout_id = graph.add_node("Layout", {
                "orientation": "vertical"
            })
            
            # Column header
            header_id = graph.add_node("Card", {
                "title": f"{column} ({len(column_tasks)})",
                "content": ""
            })
            graph.add_child(column_layout_id, header_id)
            
            # Tasks in column
            for task in column_tasks:
                task_card_id = graph.add_node("Card", {
                    "title": task.get("title", "Untitled"),
                    "content": task.get("description", ""),
                    "actions": [
                        {"label": "View", "action": f"task_detail_{task.get('id', '')}"},
                        {"label": "Move", "action": f"task_move_{task.get('id', '')}"}
                    ]
                })
                graph.add_child(column_layout_id, task_card_id)
            
            graph.add_child(main_layout_id, column_layout_id)
            
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_analytics(self) -> Dict[str, Any]:
        """Render analytics dashboard"""
        graph = ComponentGraph()
        
        # Email analytics
        email_chart_id = graph.add_node("Chart", {
            "chart_type": "line",
            "data": self.user_context.get("email_analytics", []),
            "title": "Email Activity"
        })
        
        # Meeting analytics
        meeting_chart_id = graph.add_node("Chart", {
            "chart_type": "pie",
            "data": self.user_context.get("meeting_analytics", []),
            "title": "Meeting Distribution"
        })
        
        # Task analytics
        task_chart_id = graph.add_node("Chart", {
            "chart_type": "bar",
            "data": self.user_context.get("task_analytics", []),
            "title": "Task Completion"
        })
        
        # Summary cards
        summary_cards_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        
        # Helper to add card node
        def add_summary_card(title, content):
            return graph.add_node("Card", {"title": title, "content": content})
            
        graph.add_child(summary_cards_layout_id, add_summary_card("Total Emails", "1,234"))
        graph.add_child(summary_cards_layout_id, add_summary_card("Meetings This Week", "12"))
        graph.add_child(summary_cards_layout_id, add_summary_card("Tasks Completed", "45"))
        
        # Charts layout
        charts_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        graph.add_child(charts_layout_id, email_chart_id)
        graph.add_child(charts_layout_id, meeting_chart_id)
        graph.add_child(charts_layout_id, task_chart_id)
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "vertical"
        })
        graph.add_child(main_layout_id, summary_cards_layout_id)
        graph.add_child(main_layout_id, charts_layout_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_settings(self) -> Dict[str, Any]:
        """Render settings interface"""
        graph = ComponentGraph()
        
        # User preferences form
        settings_form_id = graph.add_node("Form", {
            "fields": [
                {"type": "text", "name": "name", "label": "Full Name"},
                {"type": "email", "name": "email", "label": "Email Address"},
                {"type": "select", "name": "timezone", "label": "Timezone", "options": ["UTC", "EST", "PST", "CST"]},
                {"type": "checkbox", "name": "notifications", "label": "Enable Notifications"},
                {"type": "checkbox", "name": "auto_sync", "label": "Auto-sync Calendar"}
            ],
            "submit_action": "update_settings",
            "form_id": "settings_form"
        })
        
        # Integration settings
        integrations_id = graph.add_node("Card", {
            "title": "Integrations",
            "content": "Manage your connected accounts and services",
            "actions": [
                {"label": "Google Calendar", "action": "configure_google_calendar"},
                {"label": "Email Accounts", "action": "configure_email_accounts"},
                {"label": "CRM Integration", "action": "configure_crm"}
            ]
        })
        
        # Main layout
        main_layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        graph.add_child(main_layout_id, settings_form_id)
        graph.add_child(main_layout_id, integrations_id)
        
        graph.set_root(main_layout_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component()
        }
        
        return {
            "adjacencyList": graph.to_adjacency_list()
        }
    
    def _render_chat(self) -> Dict[str, Any]:
        """Render chat interface as A2UI component"""
        graph = ComponentGraph()
        
        chat_id = graph.add_node("Chat", {
            "messages": self.user_context.get("chat_messages", []),
            "input_placeholder": "Type your message...",
            "send_action": "send_chat_message"
        })
        
        graph.set_root(chat_id)
        
        # Create unified AppShell component
        component = {
            "type": "appshell",
            "layout": graph.to_json(),
            "navigation": self._get_navigation_bar(),
            "chat_component": self._get_chat_component() # Keep this for the global chat component if needed
        }
        
        return {
            "component": component,
            "state_info": self.state_machine.get_state_info()
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
    
    # Neural Loop Processing Methods (Merged from SymphonyOrchestrator)
    
    async def process_user_intent(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Neural Loop processing
        Intent -> Clarification -> Composition -> Feedback -> Learning
        """
        self.user_context = context
        self.current_loop = NeuralLoopContext(
            user_intent=user_input,
            raw_input=user_input,
            missing_parameters=[],
            clarification_questions=[],
            plugin_capabilities=[]
        )
        
        # Start Neural Loop
        self.neural_loop_state = OrchestratorState.INTENT_PROCESSING
        
        # Execute the complete Neural Loop
        try:
            # Process intent
            intent_result = await self._handle_intent_processing()
            if not intent_result.get("success"):
                return intent_result
            
            # Handle composition
            composition_result = await self._handle_composition()
            return composition_result
            
        except Exception as e:
            logger.error(f"Neural Loop processing error: {e}")
            self.neural_loop_state = OrchestratorState.ERROR_RECOVERY
            return await self._handle_error_recovery()
    
    async def process_dashboard_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced dashboard handler with tenant isolation and user-verse boundaries"""
        self.user_context = context
        self.current_loop = NeuralLoopContext(
            user_intent="dashboard",
            raw_input="show dashboard",
            missing_parameters=[],
            clarification_questions=[],
            plugin_capabilities=[]
        )
        
        # Apply tenant filtering if tenant context is available
        if self.tenant_context:
            context = self._filter_components_by_tenant_features(context)
            
            # Apply user-verse boundaries for dashboard data
            current_user_id = self.tenant_context.get("user_id")
            if current_user_id:
                # Get user-scoped dashboard data
                dashboard_data_types = ["emails", "meetings", "tasks", "analytics"]
                scoped_data = {}
                
                for data_type in dashboard_data_types:
                    scoped_result = self.get_user_scoped_data(current_user_id, data_type)
                    scoped_data[data_type] = scoped_result
                
                # Merge scoped data into context
                context.update(scoped_data)
                context["user_verse_enforced"] = True
                context["access_level"] = "own"  # Users always access their own dashboard
        
        # Create dashboard UI with enhanced isolation
        graph = ComponentGraph()
        
        # Main dashboard card with tenant info
        tenant_name = context.get("tenant_name", "Your Workspace")
        dashboard_card = graph.add_node("Card", {
            "title": f"📊 {tenant_name} Dashboard",
            "content": f"Welcome back, {context.get('name', 'User')}!",
            "variant": "primary",
            "tenant_id": context.get("tenant_id", "unknown"),
            "user_verse_enforced": context.get("user_verse_enforced", False)
        })
        
        # Tenant features indicator
        if context.get("tenant_features"):
            features_card = graph.add_node("Card", {
                "title": "🔧 Available Features",
                "content": f"Features: {', '.join(context.get('tenant_features', []))}",
                "variant": "info",
                "size": "small"
            })
            graph.add_child(dashboard_card, features_card)
        
        # User-verse boundary indicator
        if context.get("user_verse_enforced"):
            boundary_card = graph.add_node("Card", {
                "title": "🔒 User-Verse Boundaries",
                "content": f"Access Level: {context.get('access_level', 'own')}",
                "variant": "success",
                "size": "small"
            })
            graph.add_child(dashboard_card, boundary_card)
        
        # Stats section with user-scoped data
        stats_data = context.get('stats', {})
        tenant_data = context.get('tenant_data', {})
        
        # Use user-scoped stats if available
        emails_data = context.get('emails', {})
        meetings_data = context.get('meetings', {})
        tasks_data = context.get('tasks', {})
        
        if emails_data.get('can_access'):
            email_count = emails_data.get('count', 0)
        else:
            email_count = stats_data.get('pendingEmails', 0)
            
        if meetings_data.get('can_access'):
            meeting_count = meetings_data.get('count', 0)
        else:
            meeting_count = stats_data.get('meetings', 0)
            
        if tasks_data.get('can_access'):
            task_count = tasks_data.get('count', 0)
        else:
            task_count = stats_data.get('tasks', 0)
        
        stats_content = f"📧 Emails: {email_count} | 🤝 Meetings: {meeting_count} | ✅ Tasks: {task_count}"
        
        if tenant_data:
            stats_content += f" | 📊 Tenant Data: {len(tenant_data.get('items', []))} items"
        
        stats_card = graph.add_node("Card", {
            "title": "📈 Quick Stats",
            "content": stats_content,
            "variant": "info"
        })
        
        # Recent activity
        recent_activity = context.get('recent_activity', [])
        if recent_activity:
            activity_content = "Recent Activity:\n" + "\n".join(f"• {activity}" for activity in recent_activity)
            activity_card = graph.add_node("Card", {
                "title": "📝 Recent Activity",
                "content": activity_content,
                "variant": "secondary"
            })
            graph.add_child(dashboard_card, activity_card)
        
        # Upcoming events
        upcoming_events = context.get('upcoming_events', [])
        if upcoming_events:
            events_content = "Upcoming:\n" + "\n".join(f"• {event}" for event in upcoming_events)
            events_card = graph.add_node("Card", {
                "title": "📅 Upcoming Events",
                "content": events_content,
                "variant": "secondary"
            })
            graph.add_child(dashboard_card, events_card)
        
        graph.add_child(dashboard_card, stats_card)
        
        # Create tenant-isolated response
        ui_data = graph.to_json()
        
        if self.tenant_context:
            return self.create_tenant_isolated_response(ui_data, context)
        else:
            return {
                'type': 'final_response',
                'ui': ui_data,
                'timestamp': datetime.now().isoformat(),
                'intent': 'dashboard'
            }
    
    async def _handle_intent_processing(self) -> Dict[str, Any]:
        """Enhanced intent processing using Neural Loop AI engine"""
        try:
            user_input = self.current_loop.raw_input
            
            # Create enhanced Neural Loop context
            enhanced_context = EnhancedNeuralLoopContext(
                user_input=user_input,
                session_history=self.conversation_history[-5:],  # Last 5 messages
                user_context=self.user_context,
                tenant_context=self.tenant_context or {},
                timestamp=datetime.now(),
                intent_candidates=[]
            )
            
            # Process with enhanced Neural Loop engine
            result = self.neural_loop_engine.process_user_input(user_input, enhanced_context)
            
            if result["type"] == "clarification_required":
                # Store clarification state
                self.current_loop.clarification_questions = result["clarification_questions"]
                self.current_loop.detected_intent = {
                    "intent": result["selected_intent"].intent_type.value,
                    "confidence": result["selected_intent"].confidence,
                    "reasoning": result["reasoning"],
                    "requires_clarification": True
                }
                self.neural_loop_state = OrchestratorState.AMBIGUITY_RESOLUTION
                
                return {
                    "success": True, 
                    "intent": result["selected_intent"].intent_type.value,
                    "clarification_needed": True,
                    "clarification_questions": result["clarification_questions"]
                }
            
            elif result["type"] == "intent_resolved":
                selected_intent = result["selected_intent"]
                self.current_loop.detected_intent = {
                    "intent": selected_intent.intent_type.value,
                    "confidence": selected_intent.confidence,
                    "reasoning": selected_intent.reasoning,
                    "entities": [{"type": e.entity_type, "value": e.value, "confidence": e.confidence} for e in selected_intent.entities]
                }
                self.neural_loop_state = OrchestratorState.COMPOSITION
                
                return {
                    "success": True, 
                    "intent": selected_intent.intent_type.value,
                    "confidence": selected_intent.confidence,
                    "reasoning": selected_intent.reasoning
                }
            
            else:
                # Fallback to simple detection
                return await self._handle_simple_intent_processing()
            
        except Exception as e:
            logger.error(f"Enhanced intent processing error: {e}")
            # Fallback to simple processing
            return await self._handle_simple_intent_processing()
    
    async def _handle_simple_intent_processing(self) -> Dict[str, Any]:
        """Fallback simple intent processing"""
        try:
            user_input = self.current_loop.raw_input.lower()
            
            if "dashboard" in user_input or "home" in user_input:
                intent = "dashboard"
            elif "email" in user_input:
                intent = "email"
            elif "calendar" in user_input or "event" in user_input:
                intent = "calendar"
            elif "meeting" in user_input:
                intent = "meeting"
            elif "task" in user_input:
                intent = "task"
            elif "analytics" in user_input or "report" in user_input:
                intent = "analytics"
            else:
                intent = "general"
            
            self.current_loop.detected_intent = {"intent": intent, "confidence": 0.8}
            self.neural_loop_state = OrchestratorState.COMPOSITION
            
            return {"success": True, "intent": intent}
            
        except Exception as e:
            logger.error(f"Simple intent processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_ambiguity_resolution(self) -> Dict[str, Any]:
        """Enhanced ambiguity resolution using Neural Loop clarification system"""
        try:
            clarification_questions = self.current_loop.clarification_questions or []
            
            # Create clarification UI with multiple questions
            clarification_content = "I need some clarification to help you better:\n\n"
            for i, question in enumerate(clarification_questions, 1):
                clarification_content += f"{i}. {question}\n"
            
            # Add suggested responses
            suggested_responses = []
            if "email" in str(clarification_questions).lower():
                suggested_responses.extend(["Compose email", "Read inbox", "Check sent emails"])
            if "meeting" in str(clarification_questions).lower():
                suggested_responses.extend(["Schedule meeting", "View calendar", "Check availability"])
            if "task" in str(clarification_questions).lower():
                suggested_responses.extend(["Create task", "View tasks", "Update task"])
            
            # Default suggestions
            if not suggested_responses:
                suggested_responses = ["Show dashboard", "Help", "Cancel"]
            
            return {
                "type": "clarification_request",
                "response": clarification_content.strip(),
                "ui": {
                    "component": {
                        "Card": {
                            "title": {"literalString": "❓ I Need More Information"},
                            "content": {"literalString": clarification_content.strip()},
                            "actions": [
                                {"type": "button", "label": response, "action": f"clarify_{i}"}
                                for i, response in enumerate(suggested_responses)
                            ],
                            "variant": "warning"
                        }
                    }
                },
                "suggested_responses": suggested_responses,
                "clarification_questions": clarification_questions
            }
            
        except Exception as e:
            logger.error(f"Ambiguity resolution error: {e}")
            # Fallback to generic clarification
            return {
                "type": "clarification_request",
                "response": "I need more information to help you. Could you please clarify what you'd like to do?",
                "ui": {"component": {"Card": {"title": {"literalString": "❓ Clarification Needed"}, "content": {"literalString": "Please provide more details about what you'd like to do."}, "actions": [], "variant": "warning"}}}
            }
    
    async def _handle_optimistic_execution(self) -> Dict[str, Any]:
        """Execute optimistically to hide latency"""
        # Create a skeleton UI while processing
        skeleton = {
            "type": "loading_response",
            "response": "Processing your request...",
            "ui": {"component": {"Card": {"title": {"literalString": "⏳ Processing"}, "content": {"literalString": "Please wait while I process your request..."}, "actions": [], "variant": "info"}}}
        }
        
        return skeleton
    
    async def _handle_composition(self) -> Dict[str, Any]:
        """Enhanced composition using Neural Loop detected intent and entities"""
        try:
            detected_intent = self.current_loop.detected_intent or {}
            intent = detected_intent.get("intent", "general")
            confidence = detected_intent.get("confidence", 0.0)
            entities = detected_intent.get("entities", [])
            reasoning = detected_intent.get("reasoning", "")
            
            logger.info(f"Composing response for intent: {intent} (confidence: {confidence:.2f})")
            
            if intent == "dashboard":
                # Render tenant-aware dashboard
                dashboard_ui = self.render_ui(UIState.DASHBOARD, self.user_context)
                response_text = "Here's your personalized dashboard"
                if self.tenant_context:
                    response_text += f" for {self.tenant_context.get('tenant_name', 'your workspace')}"
                
                return {
                    "type": "final_response",
                    "response": response_text,
                    "ui": dashboard_ui.get("component", {}),
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "reasoning": reasoning
                }
                
            elif intent == "email":
                # Compose email-specific response
                email_entities = [e for e in entities if e.get("type") == "email_address"]
                recipient_info = f" to {email_entities[0]['value']}" if email_entities else ""
                
                return {
                    "type": "final_response",
                    "response": f"I'll help you compose an email{recipient_info}. What would you like to say?",
                    "ui": {"component": {"Card": {"title": {"literalString": "✉️ Email Composer"}, "content": {"literalString": "Ready to help you write your email"}, "actions": [{"type": "button", "label": "Compose New Email", "action": "compose_email"}], "variant": "info"}}},
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "reasoning": reasoning
                }
                
            elif intent == "calendar":
                # Compose calendar-specific response
                date_entities = [e for e in entities if e.get("type") == "date"]
                date_info = f" for {date_entities[0]['value']}" if date_entities else ""
                
                return {
                    "type": "final_response",
                    "response": f"I'll show you your calendar{date_info}. What would you like to do?",
                    "ui": {"component": {"Card": {"title": {"literalString": "📅 Calendar View"}, "content": {"literalString": "Ready to show your calendar"}, "actions": [{"type": "button", "label": "View Calendar", "action": "view_calendar"}], "variant": "info"}}},
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "reasoning": reasoning
                }
                
            elif intent == "meeting":
                # Compose meeting-specific response
                participant_entities = [e for e in entities if e.get("type") == "person"]
                participants_info = f" with {', '.join([e['value'] for e in participant_entities])}" if participant_entities else ""
                
                return {
                    "type": "final_response",
                    "response": f"I'll help you schedule a meeting{participants_info}. When would you like to meet?",
                    "ui": {"component": {"Card": {"title": {"literalString": "🤝 Meeting Scheduler"}, "content": {"literalString": "Ready to help schedule your meeting"}, "actions": [{"type": "button", "label": "Schedule Meeting", "action": "schedule_meeting"}], "variant": "info"}}},
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "reasoning": reasoning
                }
                
            else:
                # Generic response for other intents with entity awareness
                entity_summary = ""
                if entities:
                    entity_summary = f" I detected: {', '.join([f'{e['type']}: {e['value']}' for e in entities])}"
                
                return {
                    "type": "final_response",
                    "response": f"I understand you want to work with {intent}.{entity_summary} Here's what I can show you:",
                    "ui": {"component": {"Card": {"title": {"literalString": f"🎯 {intent.title()}"}, "content": {"literalString": f"Showing {intent} interface with your context"}, "actions": [], "variant": "success"}}},
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "reasoning": reasoning
                }
                
        except Exception as e:
            logger.error(f"Enhanced composition error: {e}")
            # Fallback to simple composition
            intent = self.current_loop.detected_intent.get("intent", "general")
            return {
                "type": "final_response",
                "response": f"I understand you want to work with {intent}. Here's what I can show you:",
                "ui": {"component": {"Card": {"title": {"literalString": f"🎯 {intent.title()}"}, "content": {"literalString": f"Showing {intent} interface"}, "actions": [], "variant": "success"}}},
                "intent": intent
            }
    
    async def _handle_error_recovery(self) -> Dict[str, Any]:
        """Handle errors gracefully"""
        return {
            "type": "error_response",
            "response": "Sorry, I encountered an error processing your request.",
            "ui": {"component": {"Card": {"title": {"literalString": "❌ Error"}, "content": {"literalString": "Something went wrong. Please try again."}, "actions": [], "variant": "error"}}}
        }

    # Streaming Transport Support
    async def process_streaming_event(self, event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process streaming events for real-time UI updates"""
        try:
            event_type = event.get("type")
            user_id = context.get("user_id", "anonymous")
            
            logger.info(f"Processing streaming event: {event_type} for user {user_id}")
            
            if event_type == "skeleton":
                # Process optimistic skeleton for immediate UI feedback
                skeleton_composition = event.get("composition", {})
                enhanced_ui = await self._enhance_skeleton_ui(skeleton_composition, context)
                
                return {
                    "type": "skeleton_response",
                    "ui": enhanced_ui,
                    "progress": {"stage": "skeleton", "percentage": 25},
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
            elif event_type == "composition":
                # Process final composition with actual data
                final_composition = event.get("composition", {})
                enhanced_ui = await self._enhance_final_ui(final_composition, context)
                
                return {
                    "type": "composition_response", 
                    "ui": enhanced_ui,
                    "progress": {"stage": "composition", "percentage": 75},
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
            elif event_type == "update":
                # Process incremental updates
                update_data = event.get("data", {})
                
                return {
                    "type": "update_response",
                    "ui": update_data,
                    "progress": {"stage": "updating", "percentage": event.get("progress", 50)},
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
            elif event_type == "progress":
                # Handle progress updates
                progress_data = event.get("progress", {})
                
                return {
                    "type": "progress_response",
                    "progress": progress_data,
                    "message": event.get("message", "Processing..."),
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
            else:
                # Generic event processing
                return {
                    "type": "generic_response",
                    "event": event,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
        except Exception as e:
            logger.error(f"Error processing streaming event: {e}")
            return {
                "type": "error_response",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "user_id": context.get("user_id", "anonymous")
            }
    
    async def _enhance_skeleton_ui(self, skeleton: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance skeleton UI with user-specific optimizations"""
        try:
            user_id = context.get("user_id", "anonymous")
            
            # Add loading indicators and progressive enhancement
            enhanced_skeleton = {
                "component": {
                    "Card": {
                        "title": {"literalString": "🔄 Loading..."},
                        "content": {"literalString": "Please wait while we prepare your interface"},
                        "actions": [],
                        "variant": "loading",
                        "skeleton": True,
                        "progressive": True
                    }
                },
                "metadata": {
                    "user_id": user_id,
                    "stage": "skeleton",
                    "estimated_completion": "2-3 seconds"
                }
            }
            
            # Merge with provided skeleton if available
            if skeleton:
                enhanced_skeleton.update(skeleton)
                
            return enhanced_skeleton
            
        except Exception as e:
            logger.error(f"Error enhancing skeleton UI: {e}")
            return skeleton  # Return original skeleton on error
    
    async def _enhance_final_ui(self, final_ui: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance final UI with user-specific optimizations"""
        try:
            user_id = context.get("user_id", "anonymous")
            user_name = context.get("user_name", "User")
            
            # Add personalization and optimization hints
            enhanced_final = {
                "component": final_ui.get("component", {}),
                "metadata": {
                    "user_id": user_id,
                    "stage": "final",
                    "personalized": True,
                    "cached": False,
                    "render_optimized": True
                },
                "performance": {
                    "render_time_ms": 0,  # Will be filled by client
                    "cached_components": 0,
                    "fresh_components": 0
                }
            }
            
            # Add user-specific welcome message if it's a dashboard
            if "dashboard" in str(final_ui).lower():
                enhanced_final["welcome_message"] = f"Welcome back, {user_name}!"
                
            return enhanced_final
            
        except Exception as e:
            logger.error(f"Error enhancing final UI: {e}")
            return final_ui  # Return original final UI on error
    
    # AI Engine Methods (Consolidated from ai_engine.py)
    async def process_ai_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Process user message and return AI response with UI components"""
        if context is None:
            context = {}
        
        # Detect intent
        intent = self.detect_intent(message)
        
        # Generate response based on intent and context
        response_message = await self._generate_ai_response(message, intent, context)
        
        # Generate actions based on intent
        actions = self._generate_ai_actions(intent, context)
        
        # Generate UI components based on intent
        ui_components = self._generate_ai_ui_components(intent, context)
        
        # Determine if user input is required
        requires_user_input = self._requires_user_input(intent)
        
        # Update session data
        session_data = self._update_session_data(intent, context)
        
        return AIResponse(
            message=response_message,
            intent=intent,
            actions=actions,
            ui_components=ui_components,
            requires_user_input=requires_user_input,
            session_data=session_data
        )
    
    def detect_intent(self, message: str) -> AIIntent:
        """Detect user intent from message using pattern matching"""
        message_lower = message.lower().strip()
        
        # Intent patterns (consolidated from ai_engine.py)
        intent_patterns = {
            "schedule_meeting": [
                r"schedule.*meeting", r"book.*meeting", r"set.*meeting", 
                r"meeting.*with", r"meet.*with", r"appointment.*with"
            ],
            "send_email": [
                r"send.*email", r"email.*to", r"write.*email", 
                r"compose.*email", r"mail.*to", r"message.*to"
            ],
            "check_calendar": [
                r"check.*calendar", r"view.*calendar", r"what.*schedule",
                r"my.*calendar", r"upcoming.*events", r"today.*schedule"
            ],
            "manage_contacts": [
                r"add.*contact", r"contact.*list", r"find.*contact",
                r"contact.*info", r"phone.*book", r"address.*book"
            ],
            "help": [
                r"help", r"what.*can.*you.*do", r"assist", 
                r"guide", r"support", r"instructions"
            ],
            "greeting": [
                r"hello", r"hi", r"hey", r"good.*morning", 
                r"good.*afternoon", r"good.*evening"
            ],
            "goodbye": [
                r"bye", r"goodbye", r"see.*you", r"talk.*later", 
                r"done", r"finish"
            ]
        }
        
        # Entity extraction patterns
        entity_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "date": r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|tomorrow|today|next\s+week)\b",
            "time": r"\b(?:\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm))\b"
        }
        
        # Check for matching intents
        detected_intents = []
        for intent_name, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_intents.append(intent_name)
                    break
        
        # Extract entities
        entities = {}
        for entity_name, pattern in entity_patterns.items():
            matches = re.findall(pattern, message_lower)
            if matches:
                entities[entity_name] = matches
        
        # Determine primary intent
        if detected_intents:
            primary_intent = detected_intents[0]
            confidence = min(0.9, 0.6 + (0.1 * len(detected_intents)))  # Base 0.6 + bonus for multiple matches
        else:
            primary_intent = "unknown"
            confidence = 0.3
        
        # Check for ambiguity
        requires_clarification = False
        ambiguity_reason = None
        
        if len(detected_intents) > 2:
            requires_clarification = True
            ambiguity_reason = "Multiple possible intents detected"
        elif not entities and primary_intent in ["schedule_meeting", "send_email"]:
            requires_clarification = True
            ambiguity_reason = "Missing required information (contacts, dates, etc.)"
        
        return AIIntent(
            intent=primary_intent,
            confidence=confidence,
            entities=entities,
            response_type="text",
            requires_clarification=requires_clarification,
            ambiguity_reason=ambiguity_reason
        )
    
    async def _generate_ai_response(self, message: str, intent: AIIntent, context: Dict[str, Any]) -> str:
        """Generate AI response based on intent and context"""
        
        # Try OpenRouter first if enabled
        if self.use_openrouter and self.openrouter_api_key:
            try:
                return await self._generate_openrouter_response(message, context)
            except Exception as e:
                logger.warning(f"OpenRouter failed, falling back to pattern-based: {e}")
        
        # Fallback to pattern-based responses
        return self._generate_pattern_based_response(message, intent, context)
    
    async def _generate_openrouter_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response using OpenRouter API"""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dhii-mail.com",
            "X-Title": "dhii-mail"
        }
        
        # Build conversation history
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-5:])  # Last 5 messages
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.openrouter_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _generate_pattern_based_response(self, message: str, intent: AIIntent, context: Dict[str, Any]) -> str:
        """Generate response using pattern-based logic"""
        
        intent_responses = {
            "schedule_meeting": [
                "I'd be happy to help you schedule a meeting!",
                "Let me help you set up that meeting.",
                "I can help you schedule a meeting. Who would you like to meet with?"
            ],
            "send_email": [
                "I can help you compose and send an email.",
                "Let me help you write that email.",
                "I'd be happy to help you send an email. Who is the recipient?"
            ],
            "check_calendar": [
                "Let me check your calendar for you.",
                "I'll show you your upcoming schedule.",
                "Here's what's on your calendar."
            ],
            "manage_contacts": [
                "I can help you manage your contacts.",
                "Let me help you with your contact list.",
                "What would you like to do with your contacts?"
            ],
            "help": [
                "I'm dhii, your AI assistant for email and calendar management. I can help you:",
                "• Schedule meetings and appointments",
                "• Send and manage emails", 
                "• Check your calendar",
                "• Manage your contacts",
                "What would you like to do?"
            ],
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hello! I'm here to help with your email and calendar needs."
            ],
            "goodbye": [
                "Goodbye! Have a great day!",
                "See you later! Feel free to reach out if you need anything.",
                "Take care! I'm here whenever you need help."
            ],
            "unknown": [
                "I'm not sure I understand. Could you please rephrase that?",
                "Could you clarify what you'd like help with?",
                "I can help with email, calendar, and contact management. What would you like to do?"
            ]
        }
        
        # Handle clarification requests
        if intent.requires_clarification:
            if intent.ambiguity_reason == "Multiple possible intents detected":
                return "I noticed you might be asking about several things. Could you clarify what you'd like help with specifically?"
            elif intent.ambiguity_reason == "Missing required information (contacts, dates, etc.)":
                return f"I'd be happy to help you {intent.intent.replace('_', ' ')}. Could you provide more details like who, when, or what?"
        
        # Return appropriate response
        responses = intent_responses.get(intent.intent, intent_responses["unknown"])
        return random.choice(responses)
    
    def _generate_ai_actions(self, intent: AIIntent, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate available actions based on intent"""
        actions = []
        
        if intent.intent == "schedule_meeting":
            actions.extend([
                {
                    "type": "calendar",
                    "action": "suggest_times",
                    "label": "Suggest Meeting Times",
                    "description": "Show available time slots"
                },
                {
                    "type": "calendar", 
                    "action": "check_availability",
                    "label": "Check Availability",
                    "description": "Check calendar conflicts"
                }
            ])
        elif intent.intent == "send_email":
            actions.extend([
                {
                    "type": "email",
                    "action": "compose",
                    "label": "Compose Email",
                    "description": "Open email composer"
                },
                {
                    "type": "email",
                    "action": "templates",
                    "label": "Email Templates",
                    "description": "Show email templates"
                }
            ])
        elif intent.intent == "check_calendar":
            actions.extend([
                {
                    "type": "calendar",
                    "action": "view_today",
                    "label": "Today's Schedule",
                    "description": "Show today's events"
                },
                {
                    "type": "calendar",
                    "action": "view_week",
                    "label": "This Week",
                    "description": "Show this week's schedule"
                }
            ])
        elif intent.intent == "manage_contacts":
            actions.extend([
                {
                    "type": "contacts",
                    "action": "view_all",
                    "label": "View Contacts",
                    "description": "Show all contacts"
                },
                {
                    "type": "contacts",
                    "action": "add_new",
                    "label": "Add Contact",
                    "description": "Add new contact"
                }
            ])
        
        # Always add help action
        actions.append({
            "type": "system",
            "action": "help",
            "label": "Help",
            "description": "Show available commands"
        })
        
        return actions
    
    def _generate_ai_ui_components(self, intent: AIIntent, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate UI components based on intent"""
        
        if intent.intent == "check_calendar":
            return {
                "type": "calendar_view",
                "component": "CalendarDashboard",
                "props": {
                    "view": "week",
                    "date": "today"
                }
            }
        elif intent.intent == "schedule_meeting":
            return {
                "type": "meeting_scheduler",
                "component": "MeetingScheduler",
                "props": {
                    "mode": "suggest_times"
                }
            }
        elif intent.intent == "send_email":
            return {
                "type": "email_composer",
                "component": "EmailComposer", 
                "props": {
                    "mode": "compose",
                    "template": None
                }
            }
        elif intent.intent == "manage_contacts":
            return {
                "type": "contact_manager",
                "component": "ContactManager",
                "props": {
                    "mode": "view_all"
                }
            }
        
        return None
    
    def _requires_user_input(self, intent: AIIntent) -> bool:
        """Determine if user input is required based on intent"""
        return intent.requires_clarification or intent.intent == "unknown"
    
    def _update_session_data(self, intent: AIIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update session data with intent information"""
        return {
            "last_intent": intent.intent,
            "last_confidence": intent.confidence,
            "entities": intent.entities,
            "timestamp": datetime.now().isoformat(),
            "requires_followup": intent.requires_clarification
        }
    
    # Tenant-Aware Methods for Multi-Tenant Isolation
    def set_tenant_context(self, tenant_context: Dict[str, Any]) -> None:
        """Set tenant context for multi-tenant operations"""
        self.tenant_context = tenant_context
        logger.info(f"Tenant context set: {tenant_context.get('tenant_id', 'unknown')}")
    
    def get_tenant_scoped_context(self) -> Dict[str, Any]:
        """Get tenant-scoped context for UI rendering"""
        if not self.tenant_context:
            return {}
        
        return {
            "tenant_id": self.tenant_context.get("tenant_id"),
            "tenant_name": self.tenant_context.get("tenant_name"),
            "user_roles": self.tenant_context.get("user_roles", []),
            "user_permissions": self.tenant_context.get("user_permissions", []),
            "tenant_features": self.tenant_context.get("tenant_features", []),
            "is_tenant_admin": "tenant_admin" in self.tenant_context.get("user_permissions", []),
            "can_access_advanced_features": "advanced_analytics" in self.tenant_context.get("tenant_features", [])
        }
    
    def render_tenant_dashboard(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render tenant-specific dashboard with proper isolation"""
        tenant_context = self.get_tenant_scoped_context()
        
        # Merge tenant context with user context
        merged_context = {**context, **tenant_context}
        
        # Filter components based on tenant features
        filtered_context = self._filter_components_by_tenant_features(merged_context)
        
        # Render dashboard with filtered context
        return self.render_ui(UIState.DASHBOARD, filtered_context)
    
    # User-Verse Boundary Methods for Enhanced Security
    def _enforce_user_verse_boundaries(self, target_user_id: str, data_type: str) -> Dict[str, Any]:
        """
        Enforce user-verse boundaries for data access
        
        Args:
            target_user_id: The target user whose data is being accessed
            data_type: Type of data being accessed (emails, meetings, etc.)
        
        Returns:
            User-verse context with access permissions
        """
        if not self.tenant_context:
            logger.warning("No tenant context available for user-verse boundary enforcement")
            return {"can_access": False, "reason": "No tenant context"}
        
        # Get current user ID from tenant context
        current_user_id = self.tenant_context.get("user_id")
        if not current_user_id:
            logger.warning("No user ID in tenant context")
            return {"can_access": False, "reason": "No user context"}
        
        # Get user roles from tenant context
        user_roles = self.tenant_context.get("user_roles", [])
        
        # Import tenant manager for boundary enforcement
        from tenant_manager import tenant_manager
        
        try:
            # Create a mock TenantUser for boundary checking
            from tenant_manager import TenantUser
            current_user = TenantUser(
                id=current_user_id,
                tenant_id=self.tenant_context.get("tenant_id"),
                email=self.tenant_context.get("user_email", "unknown@dhii.ai"),
                name=self.tenant_context.get("user_name", "Unknown User"),
                username=self.tenant_context.get("user_username", "unknown"),
                roles=user_roles,
                permissions=self.tenant_context.get("user_permissions", [])
            )
            
            # Check user-verse boundaries
            user_verse_context = tenant_manager.create_user_verse_context(
                current_user, target_user_id
            )
            
            # Add data type information
            user_verse_context["data_type"] = data_type
            user_verse_context["enforcement_timestamp"] = datetime.now().isoformat()
            
            logger.info(f"User-verse boundary enforced: {current_user_id} -> {target_user_id} "
                       f"for {data_type}: {user_verse_context['can_access']}")
            
            return user_verse_context
            
        except Exception as e:
            logger.error(f"Error enforcing user-verse boundaries: {e}")
            return {"can_access": False, "reason": f"Enforcement error: {str(e)}"}
    
    def get_user_scoped_data(self, target_user_id: str, data_type: str) -> Dict[str, Any]:
        """
        Get user-scoped data with proper boundary enforcement
        
        Args:
            target_user_id: Target user whose data is being accessed
            data_type: Type of data (emails, meetings, tasks, etc.)
        
        Returns:
            Filtered data based on user-verse boundaries
        """
        # Enforce user-verse boundaries first
        boundary_context = self._enforce_user_verse_boundaries(target_user_id, data_type)
        
        if not boundary_context["can_access"]:
            logger.warning(f"Access denied by user-verse boundaries: {boundary_context['reason']}")
            return {
                "data": [],
                "count": 0,
                "access_denied": True,
                "reason": boundary_context["reason"],
                "boundary_context": boundary_context
            }
        
        # Get current user context for filtering
        current_user_id = self.tenant_context.get("user_id")
        tenant_id = self.tenant_context.get("tenant_id")
        
        # Filter existing user context data based on boundaries
        if target_user_id == current_user_id:
            # User accessing their own data - return full context
            return {
                "data": self.user_context.get(f"{data_type}", []),
                "count": len(self.user_context.get(f"{data_type}", [])),
                "access_level": "own",
                "boundary_context": boundary_context
            }
        elif boundary_context.get("permission_level") == "tenant":
            # Tenant admin accessing user data - return filtered view
            return {
                "data": self._filter_data_for_admin_access(data_type, target_user_id),
                "count": len(self._filter_data_for_admin_access(data_type, target_user_id)),
                "access_level": "tenant_admin",
                "boundary_context": boundary_context
            }
        else:
            # Should not reach here due to boundary enforcement
            return {
                "data": [],
                "count": 0,
                "access_denied": True,
                "reason": "Unexpected access level",
                "boundary_context": boundary_context
            }
    
    def _filter_data_for_admin_access(self, data_type: str, target_user_id: str) -> List[Dict[str, Any]]:
        """
        Filter data for tenant admin access (privacy-preserving)
        
        Args:
            data_type: Type of data to filter
            target_user_id: Target user whose data is being filtered
        
        Returns:
            Filtered data appropriate for admin viewing
        """
        # This is a privacy-preserving filter for admin access
        # In a real implementation, this would query the database with proper filtering
        
        if data_type == "emails":
            # Admin can see email metadata but not content
            return [
                {
                    "id": f"email_{i}",
                    "from": "redacted@dhii.ai",
                    "subject": f"[User {target_user_id[:8]}...] Email Subject {i}",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "status": "read",
                    "admin_view": True
                }
                for i in range(5)
            ]
        elif data_type == "meetings":
            # Admin can see meeting metadata
            return [
                {
                    "id": f"meeting_{i}",
                    "title": f"[User {target_user_id[:8]}...] Meeting {i}",
                    "start_time": "2024-01-01T14:00:00Z",
                    "duration": 60,
                    "participants_count": 3,
                    "admin_view": True
                }
                for i in range(3)
            ]
        elif data_type == "tasks":
            # Admin can see task overview
            return [
                {
                    "id": f"task_{i}",
                    "title": f"[User {target_user_id[:8]}...] Task {i}",
                    "status": "in_progress",
                    "priority": "medium",
                    "due_date": "2024-01-15",
                    "admin_view": True
                }
                for i in range(4)
            ]
        else:
            return []
    
    def render_user_scoped_ui(self, target_user_id: str, ui_state: UIState, 
                            additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Render UI with user-verse boundary enforcement
        
        Args:
            target_user_id: Target user for UI rendering
            ui_state: UI state to render
            additional_context: Additional context for rendering
        
        Returns:
            UI components with boundary enforcement applied
        """
        # Determine data types based on UI state
        data_types = self._get_data_types_for_state(ui_state)
        
        # Enforce boundaries for each data type
        scoped_data = {}
        for data_type in data_types:
            scoped_data[data_type] = self.get_user_scoped_data(target_user_id, data_type)
        
        # Create filtered context
        filtered_context = {**self.user_context, **(additional_context or {})}
        filtered_context.update(scoped_data)
        
        # Add boundary information to context
        boundary_info = {
            "user_verse_enforced": True,
            "target_user_id": target_user_id,
            "access_level": "own" if target_user_id == self.tenant_context.get("user_id") else "admin"
        }
        filtered_context.update(boundary_info)
        
        # Render UI with filtered context
        return self.render_ui(ui_state, filtered_context)
    
    def _get_data_types_for_state(self, ui_state: UIState) -> List[str]:
        """Get relevant data types for a given UI state"""
        state_data_mapping = {
            UIState.DASHBOARD: ["emails", "meetings", "tasks", "analytics"],
            UIState.EMAIL_LIST: ["emails"],
            UIState.EMAIL_DETAIL: ["emails"],
            UIState.CALENDAR: ["meetings", "events"],
            UIState.MEETING_LIST: ["meetings"],
            UIState.MEETING_DETAIL: ["meetings"],
            UIState.TASK_LIST: ["tasks"],
            UIState.ANALYTICS: ["analytics"],
            UIState.CHAT: ["messages"],
            UIState.SETTINGS: ["preferences"]
        }
        return state_data_mapping.get(ui_state, [])
    
    def _filter_components_by_tenant_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Filter UI components based on tenant features and permissions"""
        tenant_features = context.get("tenant_features", [])
        user_permissions = context.get("user_permissions", [])
        
        # Base features available to all tenants
        base_features = ["email", "calendar", "basic_analytics"]
        
        # Advanced features requiring specific tenant capabilities
        advanced_features = ["ai", "advanced_analytics", "crm", "automation"]
        
        # Filter available features
        available_features = []
        
        # Always include base features
        for feature in base_features:
            if feature in tenant_features or feature == "email":  # Email is always available
                available_features.append(feature)
        
        # Include advanced features only if tenant has them
        for feature in advanced_features:
            if feature in tenant_features:
                available_features.append(feature)
        
        # Filter navigation items based on available features
        navigation_items = []
        if "email" in available_features:
            navigation_items.extend(["inbox", "compose", "sent"])
        if "calendar" in available_features:
            navigation_items.extend(["calendar", "meetings"])
        if "basic_analytics" in available_features or "advanced_analytics" in available_features:
            navigation_items.append("analytics")
        if "crm" in available_features:
            navigation_items.append("crm")
        
        # Create filtered context
        filtered_context = context.copy()
        filtered_context["available_features"] = available_features
        filtered_context["navigation_items"] = navigation_items
        filtered_context["is_limited_tenant"] = len(tenant_features) < len(base_features + advanced_features)
        
        return filtered_context
    
    def validate_tenant_access(self, required_permission: str = None, required_feature: str = None) -> bool:
        """Validate tenant access for specific permission or feature"""
        if not self.tenant_context:
            logger.warning("No tenant context available for access validation")
            return False
        
        # Check tenant feature availability
        if required_feature:
            tenant_features = self.tenant_context.get("tenant_features", [])
            if required_feature not in tenant_features:
                logger.warning(f"Tenant lacks required feature: {required_feature}")
                return False
        
        # Check user permission
        if required_permission:
            user_permissions = self.tenant_context.get("user_permissions", [])
            if required_permission not in user_permissions:
                logger.warning(f"User lacks required permission: {required_permission}")
                return False
        
        return True
    
    def get_tenant_specific_data(self, data_type: str) -> Dict[str, Any]:
        """Get tenant-specific data with proper isolation"""
        if not self.tenant_context:
            return {"error": "No tenant context available"}
        
        tenant_id = self.tenant_context.get("tenant_id")
        if not tenant_id:
            return {"error": "No tenant ID in context"}
        
        # Mock tenant-specific data (replace with actual database queries)
        tenant_data = {
            "emails": {
                "total": 0,
                "unread": 0,
                "sent_today": 0,
                "items": []
            },
            "meetings": {
                "total": 0,
                "today": 0,
                "this_week": 0,
                "upcoming": []
            },
            "tasks": {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "overdue": 0
            },
            "analytics": {
                "email_open_rate": 0,
                "meeting_attendance": 0,
                "task_completion_rate": 0
            }
        }
        
        # Add tenant isolation metadata
        tenant_data["tenant_info"] = {
            "tenant_id": tenant_id,
            "tenant_name": self.tenant_context.get("tenant_name", "Unknown"),
            "user_roles": self.tenant_context.get("user_roles", []),
            "features": self.tenant_context.get("tenant_features", [])
        }
        
        return tenant_data.get(data_type, {"error": "Unknown data type"})
    
    def create_tenant_isolated_response(self, ui_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create tenant-isolated response with proper scoping"""
        tenant_context = self.get_tenant_scoped_context()
        
        # Add tenant metadata to response
        response = {
            "ui": ui_data,
            "tenant_context": tenant_context,
            "isolation_level": "tenant",
            "timestamp": datetime.now().isoformat(),
            "session_info": {
                "tenant_id": tenant_context.get("tenant_id"),
                "user_roles": tenant_context.get("user_roles"),
                "permissions": tenant_context.get("user_permissions")
            }
        }
        
        # Add security headers for tenant isolation
        response["security"] = {
            "tenant_scoped": True,
            "data_isolation": "strict",
            "access_control": "role_based"
        }
        
        return response
    
    def create_orchestrator_output(self, tenant_id: str, user_id: str, state: str, 
                                   chunks: List[Dict[str, Any]], 
                                   explanation: str = None) -> OrchestratorOutput:
        """Create compliant orchestrator output following New Design Spec v1.2 mapping contract"""
        # Validate chunks against mapping contract
        for chunk in chunks:
            if not self.mapping_contract.validate_chunk(chunk):
                # Create error chunk for invalid chunks
                error_chunk = {
                    "type": "ErrorCard",
                    "title": "Rendering Error",
                    "message": f"Invalid chunk format: {chunk.get('type', 'unknown')}",
                    "severity": "error"
                }
                # Replace invalid chunk with error card
                chunks[chunks.index(chunk)] = error_chunk
        
        # Create compliant orchestrator output
        output = OrchestratorOutput(
            tenant_id=tenant_id,
            user_id=user_id,
            state=state,
            explanation=explanation,
            chunks=chunks
        )
        
        # Final validation
        if not self.mapping_contract.validate_orchestrator_output(output):
            logger.warning("Orchestrator output failed final validation")
        
        return output
    
    def create_text_block_chunk(self, content: str, tone: str = "neutral", 
                               collapsible: bool = True, completed: bool = False) -> Dict[str, Any]:
        """Create TextBlock chunk (New Design Spec v1.2 compliant)"""
        return {
            "type": "TextBlock",
            "content": content,
            "tone": tone,
            "collapsible": collapsible,
            "completed": completed
        }
    
    def create_aggregated_card_chunk(self, title: str, sources: List[str], 
                                     items: List[Dict[str, Any]], 
                                     multiple_sources: bool = True,
                                     partial_rendering: bool = True,
                                     importance_based_layout: bool = True) -> Dict[str, Any]:
        """Create AggregatedCard chunk (New Design Spec v1.2 compliant)"""
        return {
            "type": "AggregatedCard",
            "title": title,
            "sources": sources,
            "items": items,
            "multiple_sources": multiple_sources,
            "partial_rendering": partial_rendering,
            "importance_based_layout": importance_based_layout
        }