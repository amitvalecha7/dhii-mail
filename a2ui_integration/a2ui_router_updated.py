"""
A2UI Router - Updated for All-A2UI Architecture
Handles all A2UI endpoints with orchestrator-based rendering
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

from .a2ui_orchestrator import A2UIOrchestrator, UIState
from .a2ui_components_extended import A2UIComponents, A2UITemplates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/a2ui", tags=["a2ui"])

# Global orchestrator instance
orchestrator = A2UIOrchestrator()

# Request/Response Models
class UIRequest(BaseModel):
    state: str
    context: Optional[Dict[str, Any]] = {}
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = {}

class UIResponse(BaseModel):
    ui_type: str
    layout: Dict[str, Any]
    navigation: Dict[str, Any]
    chat_component: Optional[Dict[str, Any]] = None
    timestamp: str

def create_ui_response_from_orchestrator(ui_data: Dict[str, Any]) -> UIResponse:
    """Convert orchestrator output to UIResponse format"""
    # Extract AppShell component from the new structure
    appshell_component = ui_data.get("component", {}).get("AppShell", {})
    
    # Create response compatible with UIResponse model
    layout = {
        "type": "appshell",
        "component": ui_data.get("component", {}),
        "state_info": ui_data.get("state_info", {})
    }
    
    return UIResponse(
        ui_type="appshell",
        layout=layout,
        navigation={"type": "appshell"},
        chat_component=None,
        timestamp=datetime.now().isoformat()
    )

# All-A2UI Dashboard Routes
@router.get("/dashboard", response_model=UIResponse)
async def get_dashboard(user_id: Optional[str] = None):
    """Get complete A2UI dashboard"""
    try:
        context = {
            "name": "User",
            "unread_count": 5,
            "today_meetings": 3,
            "pending_tasks": 7,
            "recent_activity": [
                "Meeting with team at 2 PM",
                "Email from John about project",
                "Task completed: Review documents"
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.DASHBOARD, context)
        return create_ui_response_from_orchestrator(ui_data)
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ui/action")
async def handle_ui_action(request: UIRequest):
    """Handle A2UI actions and return updated UI"""
    try:
        # Convert string state to UIState enum
        state = UIState(request.state)
        
        # Handle action if provided
        if request.action:
            result = orchestrator.handle_action(request.action, request.data)
            return result
        
        # Otherwise just render the requested state
        ui_data = orchestrator.render_ui(state, request.context)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error handling UI action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Email A2UI Routes
@router.get("/email/inbox", response_model=UIResponse)
async def get_email_inbox():
    """Get A2UI email inbox interface"""
    try:
        context = {
            "emails": [
                {
                    "from": "john@example.com",
                    "subject": "Project Update",
                    "date": "2024-01-01",
                    "status": "unread"
                },
                {
                    "from": "jane@example.com", 
                    "subject": "Meeting Tomorrow",
                    "date": "2024-01-01",
                    "status": "read"
                }
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.EMAIL_INBOX, context)
        return create_ui_response_from_orchestrator(ui_data)
    except Exception as e:
        logger.error(f"Error rendering email inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/compose", response_model=UIResponse)
async def get_email_compose():
    """Get A2UI email compose interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.EMAIL_COMPOSE)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering email compose: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Calendar A2UI Routes
@router.get("/calendar", response_model=UIResponse)
async def get_calendar():
    """Get A2UI calendar interface"""
    try:
        context = {
            "calendar_events": [
                {"title": "Team Meeting", "date": "2024-01-01", "time": "14:00"},
                {"title": "Client Call", "date": "2024-01-02", "time": "10:00"}
            ],
            "upcoming_events": [
                "Team Meeting - Today 2 PM",
                "Client Call - Tomorrow 10 AM"
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.CALENDAR_VIEW, context)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Meeting A2UI Routes
@router.get("/meetings", response_model=UIResponse)
async def get_meetings():
    """Get A2UI meetings interface"""
    try:
        context = {
            "meetings": [
                {
                    "title": "Project Review",
                    "date": "2024-01-01",
                    "time": "14:00-15:00",
                    "participants": ["john@example.com", "jane@example.com"],
                    "status": "scheduled"
                }
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.MEETING_LIST, context)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meetings/book", response_model=UIResponse)
async def get_meeting_book():
    """Get A2UI meeting booking interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.MEETING_BOOK)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering meeting book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Task A2UI Routes
@router.get("/tasks", response_model=UIResponse)
async def get_tasks():
    """Get A2UI task board interface"""
    try:
        context = {
            "tasks": [
                {"id": "1", "title": "Review documents", "status": "To Do"},
                {"id": "2", "title": "Update proposal", "status": "In Progress"},
                {"id": "3", "title": "Send report", "status": "Done"}
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.TASK_BOARD, context)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics A2UI Routes
@router.get("/analytics", response_model=UIResponse)
async def get_analytics():
    """Get A2UI analytics dashboard"""
    try:
        context = {
            "email_analytics": [
                {"label": "Sent", "value": 45},
                {"label": "Received", "value": 67}
            ],
            "meeting_analytics": [
                {"label": "Completed", "value": 12},
                {"label": "Scheduled", "value": 8}
            ],
            "task_analytics": [
                {"label": "Completed", "value": 23},
                {"label": "Pending", "value": 15}
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.ANALYTICS, context)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Settings A2UI Routes
@router.get("/settings", response_model=UIResponse)
async def get_settings():
    """Get A2UI settings interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.SETTINGS)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat A2UI Routes
@router.get("/chat", response_model=UIResponse)
async def get_chat():
    """Get A2UI chat interface"""
    try:
        context = {
            "chat_messages": [
                {"role": "user", "content": "Hello, can you help me schedule a meeting?"},
                {"role": "assistant", "content": "I'd be happy to help you schedule a meeting. What date and time would work for you?"}
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.CHAT, context)
        return UIResponse(
            ui_type=ui_data["ui_type"],
            layout=ui_data["layout"],
            navigation=ui_data["navigation"],
            chat_component=ui_data.get("chat_component"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error rendering chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Component Library Routes
@router.get("/components")
async def get_component_library():
    """Get available A2UI components"""
    try:
        components = A2UIComponents()
        return {
            "components": [
                "Card", "Form", "Table", "Chart", "Modal", 
                "List", "Button", "Input", "TextArea", "Select",
                "DatePicker", "TimePicker", "FileUpload", "Toggle",
                "ProgressBar", "Badge", "Alert", "Navigation",
                "Layout", "Toolbar", "Dropdown", "Calendar", "Chat"
            ],
            "templates": [
                "Email Dashboard", "Meeting Dashboard", "Calendar View",
                "Settings Panel", "Analytics Dashboard", "Marketing Dashboard"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting component library: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Main A2UI Interface Route
@router.get("/interface")
async def get_a2ui_interface():
    """Get complete A2UI interface"""
    try:
        # Start with dashboard as default
        return await get_dashboard()
    except Exception as e:
        logger.error(f"Error rendering A2UI interface: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Action endpoint for handling UI interactions
@router.post("/ui/action")
async def handle_ui_action(request: Dict[str, Any]):
    """Handle UI actions from the A2UI interface"""
    try:
        state = request.get("state", "dashboard")
        action = request.get("action")
        data = request.get("data", {})
        
        logger.info(f"Handling action: {action} in state: {state}")
        
        # Process action through orchestrator
        result = orchestrator.handle_action(action, data)
        
        # Return updated UI state
        if result.get("navigate"):
            # Navigate to new state
            new_state = result["navigate"]
            return await get_ui_state(new_state)
        else:
            # Return current state with updates
            return await get_ui_state(state)
            
    except Exception as e:
        logger.error(f"Error handling UI action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to get UI state
async def get_ui_state(state: str):
    """Get UI state by name"""
    state_map = {
        "dashboard": get_dashboard,
        "email_inbox": get_email_inbox,
        "calendar": get_calendar,
        "meetings": get_meetings,
        "tasks": get_tasks,
        "analytics": get_analytics,
        "settings": get_settings,
        "chat": get_chat
    }
    
    # Map state names to functions
    if state in state_map:
        return await state_map[state]()
    else:
        # Default to dashboard
        return await get_dashboard()

# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "a2ui", "timestamp": datetime.now().isoformat()}