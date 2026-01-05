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
    component: Dict[str, Any]
    state_info: Dict[str, Any]
    timestamp: str
    data: Optional[Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

def create_ui_response_from_orchestrator(ui_data: Dict[str, Any], data: Dict[str, Any] = None) -> UIResponse:
    """Convert orchestrator output to UIResponse format"""
    return UIResponse(
        component=ui_data.get("component", {}),
        state_info=ui_data.get("state_info", {}),
        timestamp=datetime.now().isoformat(),
        data=data or {}
    )

# All-A2UI Dashboard Routes
@router.get("/dashboard", response_model=UIResponse)
async def get_dashboard(user_id: Optional[str] = None):
    """Get complete A2UI dashboard"""
    try:
        context = {
            "name": "User",
            "stats": {
                "meetings": 3,
                "pendingEmails": 5,
                "activeVideo": 2,
                "campaigns": 1
            },
            "recent_activity": [
                "Meeting with team at 2 PM",
                "Email from John about project",
                "Task completed: Review documents"
            ],
            "upcoming_events": [
                "Team Sync - 14:00",
                "Client Call - 16:00"
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.DASHBOARD, context)
        return create_ui_response_from_orchestrator(ui_data, data=context)
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
        return create_ui_response_from_orchestrator(ui_data)
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
        return create_ui_response_from_orchestrator(ui_data, data=context)
    except Exception as e:
        logger.error(f"Error rendering email inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/compose", response_model=UIResponse)
async def get_email_compose():
    """Get A2UI email compose interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.EMAIL_COMPOSE)
        return create_ui_response_from_orchestrator(ui_data)
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
        return create_ui_response_from_orchestrator(ui_data, data=context)
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
        return create_ui_response_from_orchestrator(ui_data)
    except Exception as e:
        logger.error(f"Error rendering meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meetings/book", response_model=UIResponse)
async def get_meeting_book():
    """Get A2UI meeting booking interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.MEETING_BOOK)
        return create_ui_response_from_orchestrator(ui_data)
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
            ],
            "critical_path": {
                "title": "Financial Audit Approval",
                "due_in": "2 hours",
                "description": "Review the Q3 reconciliation reports from the accounting agent before the Board sync."
            },
            "scheduled_jobs": [
                {"title": "Data Sync", "label": "Running", "icon": "sync"},
                {"title": "Backup", "label": "Pending", "icon": "cloud_upload"}
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.TASK_BOARD, context)
        return create_ui_response_from_orchestrator(ui_data, data=context)
    except Exception as e:
        logger.error(f"Error rendering tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics A2UI Routes
@router.get("/analytics", response_model=UIResponse)
async def get_analytics():
    """Get A2UI analytics interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.ANALYTICS)
        return create_ui_response_from_orchestrator(ui_data)
    except Exception as e:
        logger.error(f"Error rendering analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Settings A2UI Routes
@router.get("/settings", response_model=UIResponse)
async def get_settings():
    """Get A2UI settings interface"""
    try:
        ui_data = orchestrator.render_ui(UIState.SETTINGS)
        return create_ui_response_from_orchestrator(ui_data)
    except Exception as e:
        logger.error(f"Error rendering settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Route
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle chat messages from the frontend"""
    try:
        # TODO: Integrate with actual LLM/Kernel logic
        # For now, we return a mocked response to acknowledge the neural link
        
        response_text = f"Received: {request.message}. Neural link active. [Kernel Placeholder]"
        
        # If the message contains certain keywords, we could trigger UI actions
        # This simulates the "intelligent" aspect
        if "dashboard" in request.message.lower():
            response_text = "Navigating to dashboard..."
            # In a real implementation, this would return a UI action to change state
            
        return {
            "response": response_text,
            "session_id": request.session_id or "default_session"
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
