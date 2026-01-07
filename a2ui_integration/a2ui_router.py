"""
A2UI Router - Updated for Unified Orchestrator Integration
Handles all A2UI endpoints with Neural Loop processing and Intent Engine
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, AsyncGenerator
import json
import logging
from datetime import datetime
import asyncio

from a2ui_orchestrator import A2UIOrchestrator, UIState, OrchestratorState
from a2ui_components_extended import A2UIComponents, A2UITemplates
from liquid_glass_host import LiquidGlassHost, ComponentType
from tenant_manager import (
    get_tenant_context, 
    get_mock_tenant_context, 
    TenantContext,
    tenant_manager,
    RequirePermission,
    RequireFeature
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Multi-tenant aware authentication - provides tenant context
async def get_current_user_tenant(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> TenantContext:
    """Get current user with full tenant context for production"""
    if not credentials:
        # Fallback to mock context for testing
        return await get_mock_tenant_context()
    
    try:
        # Use tenant manager to get full tenant context
        return await get_tenant_context(credentials)
    except Exception as e:
        logger.warning(f"Failed to get tenant context: {e}, falling back to mock")
        return await get_mock_tenant_context()

# Legacy mock for backward compatibility
async def get_current_user_mock(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Dict[str, Any]:
    """Mock authentication that always provides a test user for testing purposes."""
    context = await get_current_user_tenant(credentials)
    return {
        "id": context.user.id,
        "name": context.user.name,
        "email": context.user.email,
        "username": context.user.username,
        "tenant_id": context.tenant.id,
        "tenant_name": context.tenant.name,
        "roles": context.user.roles,
        "permissions": context.user.permissions
    }

router = APIRouter(prefix="/api/a2ui", tags=["a2ui"])

# Global orchestrator instances
orchestrator = A2UIOrchestrator()
liquid_glass_host = LiquidGlassHost()

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
    type: Optional[str] = "final_response"  # Unified orchestrator response type
    skeleton: Optional[Dict[str, Any]] = None  # For optimistic execution
    execution_id: Optional[str] = None  # For tracking optimistic execution
    requires_user_input: Optional[bool] = False  # For clarification responses
    clarification_questions: Optional[List[str]] = None  # For ambiguity resolution
    error: Optional[str] = None  # For error responses
    recovery_options: Optional[List[str]] = None  # For error recovery

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ProcessIntentRequest(BaseModel):
    user_input: str
    context: Optional[Dict[str, Any]] = None

def create_ui_response_from_orchestrator(ui_data: Dict[str, Any], data: Dict[str, Any] = None) -> UIResponse:
    """Convert orchestrator output to UIResponse format"""
    # Handle unified orchestrator response format
    if ui_data.get("type") == "optimistic_response":
        return UIResponse(
            component=ui_data.get("skeleton", {}),
            state_info={"type": "optimistic", "execution_id": ui_data.get("execution_id")},
            timestamp=ui_data.get("timestamp", datetime.now().isoformat()),
            data=data or {},
            type=ui_data.get("type", "optimistic_response"),
            skeleton=ui_data.get("skeleton"),
            execution_id=ui_data.get("execution_id")
        )
    elif ui_data.get("type") == "clarification_response":
        return UIResponse(
            component=ui_data.get("ui", {}),
            state_info={"type": "clarification"},
            timestamp=ui_data.get("timestamp", datetime.now().isoformat()),
            data=data or {},
            type=ui_data.get("type", "clarification_response"),
            requires_user_input=True,
            clarification_questions=ui_data.get("clarification_questions", [])
        )
    elif ui_data.get("type") == "error_response":
        return UIResponse(
            component=ui_data.get("ui", {}),
            state_info={"type": "error"},
            timestamp=ui_data.get("timestamp", datetime.now().isoformat()),
            data=data or {},
            type=ui_data.get("type", "error_response"),
            error=ui_data.get("error"),
            recovery_options=ui_data.get("recovery_options", [])
        )
    elif ui_data.get("adjacencyList"):
        # A2UI adjacency list format
        return UIResponse(
            component=ui_data.get("adjacencyList", {}),
            state_info=ui_data.get("state_info", {}),
            timestamp=ui_data.get("timestamp", datetime.now().isoformat()),
            data=data or {},
            type="adjacency_list"
        )
    else:
        # Default final response or legacy format
        return UIResponse(
            component=ui_data.get("ui", ui_data.get("component", {})),
            state_info=ui_data.get("state_info", {}),
            timestamp=ui_data.get("timestamp", datetime.now().isoformat()),
            data=data or {},
            type=ui_data.get("type", "final_response")
        )

# All-A2UI Dashboard Routes
@router.get("/dashboard", response_model=UIResponse)
async def get_dashboard(tenant_context: TenantContext = Depends(get_current_user_tenant)):
    """Get complete A2UI dashboard using unified orchestrator Neural Loop with tenant isolation"""
    try:
        # Set tenant context in orchestrator for multi-tenant isolation
        orchestrator.set_tenant_context({
            "tenant_id": tenant_context.tenant.id,
            "tenant_name": tenant_context.tenant.name,
            "user_roles": tenant_context.user.roles,
            "user_permissions": tenant_context.user.permissions,
            "tenant_features": tenant_context.tenant.features
        })
        
        # Use unified orchestrator for Neural Loop processing
        user_intent = "show dashboard"
        
        # Get tenant-scoped data
        tenant_data = tenant_manager.get_tenant_scoped_data(
            tenant_context.tenant.id, 
            "dashboard"
        )
        
        context = {
            "name": tenant_context.user.name,
            "user_id": tenant_context.user.id,
            "tenant_id": tenant_context.tenant.id,
            "tenant_name": tenant_context.tenant.name,
            "user_roles": tenant_context.user.roles,
            "user_permissions": tenant_context.user.permissions,
            "tenant_features": tenant_context.tenant.features,
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
            ],
            "tenant_data": tenant_data
        }
        
        # Use unified orchestrator dashboard-specific handler to bypass Neural Loop ambiguity
        ui_data = await orchestrator.process_dashboard_request(context)
        return create_ui_response_from_orchestrator(ui_data, data=context)
    except Exception as e:
        logger.error(f"Error rendering dashboard with unified orchestrator: {e}")
        # Fallback to standard UI rendering
        try:
            ui_data = orchestrator.render_ui(UIState.DASHBOARD, context)
            return create_ui_response_from_orchestrator(ui_data, data=context)
        except Exception as fallback_error:
            logger.error(f"Standard UI rendering also failed: {fallback_error}")
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
            "active_session": {
                "title": "Board Review",
                "time_range": "14:00 - 15:00",
                "participants_count": 5
            },
            "timeline": [
                {"time": "14:00", "title": "Project Review", "tag": "Internal", "desc": "Weekly sync with engineering team"},
                {"time": "15:30", "title": "Client Call", "tag": "External", "desc": "Discuss Q1 roadmap"}
            ],
            "meetings": [
                {
                    "id": "1",
                    "title": "Project Review",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "14:00",
                    "duration": 60,
                    "participants": ["alice@dhii.ai", "bob@dhii.ai"],
                    "status": "scheduled"
                },
                {
                    "id": "2",
                    "title": "Client Call",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "15:30",
                    "duration": 30,
                    "participants": ["client@example.com", "sales@dhii.ai"],
                    "status": "confirmed"
                },
                {
                    "id": "3",
                    "title": "Board Review",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "16:30",
                    "duration": 90,
                    "participants": ["board@dhii.ai", "ceo@dhii.ai"],
                    "status": "scheduled"
                }
            ]
        }
        
        ui_data = orchestrator.render_ui(UIState.MEETING_LIST, context)
        return create_ui_response_from_orchestrator(ui_data, data=context)
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
async def get_settings(current_user: dict = Depends(get_current_user_mock)):
    """Get A2UI settings interface"""
    try:
        # Use unified orchestrator for settings
        context = {
            "user_id": current_user.get("id"),
            "user_name": current_user.get("name"),
            "user_email": current_user.get("email"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Process settings request through unified orchestrator
        result = await orchestrator.process_user_intent("show settings", context)
        
        # Convert to UI response format
        return create_ui_response_from_orchestrator(result)
    except Exception as e:
        logger.error(f"Error rendering settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Route - Updated for unified orchestrator Neural Loop
@router.post("/chat")
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user_mock)):
    """Handle chat messages using unified orchestrator Neural Loop processing"""
    try:
        # Process user message through Neural Loop
        context = {
            "session_id": request.session_id or "default_session",
            "user_id": current_user.get("id"),
            "user_name": current_user.get("name"),
            "user_email": current_user.get("email"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Use unified orchestrator for Neural Loop processing
        result = await orchestrator.process_user_intent(request.message, context)
        
        # Handle None result
        if result is None:
            result = {
                "type": "error_response",
                "response": "Sorry, I couldn't process your request.",
                "ui": {"component": {"Card": {"title": {"literalString": "❌ Error"}, "content": {"literalString": "Unable to process your message"}, "actions": [], "variant": "error"}}}
            }
        
        # Convert to UI response format
        ui_response = create_ui_response_from_orchestrator(result)
        
        # Return both chat response and UI update if needed
        return {
            "response": result.get("response", "Processing your request..."),
            "session_id": request.session_id or "default_session",
            "ui_update": ui_response.dict() if hasattr(ui_response, 'dict') else ui_response,
            "neural_loop_state": result.get("type", "final_response")
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint with unified orchestrator: {e}")
        # Fallback to basic response
        return {
            "response": f"I encountered an error processing your request: {str(e)}",
            "session_id": request.session_id or "default_session",
            "error": True
        }

@router.post("/process-intent")
async def process_intent_endpoint(request: ProcessIntentRequest, current_user: dict = Depends(get_current_user_mock)):
    """Process user intent through unified orchestrator Neural Loop"""
    try:
        # Add user context to the request
        user_context = request.context or {}
        user_context["user_id"] = current_user.get("id")
        user_context["user_name"] = current_user.get("name")
        user_context["user_email"] = current_user.get("email")
        
        # Use unified orchestrator for Neural Loop processing
        result = await orchestrator.process_user_intent(request.user_input, user_context)
        
        # Convert to UI response format
        ui_response = create_ui_response_from_orchestrator(result)
        
        return ui_response
        
    except Exception as e:
        logger.error(f"Error in process-intent endpoint with unified orchestrator: {e}")
        # Return error response
        return UIResponse(
            component={"error": str(e)},
            state_info={"type": "error"},
            timestamp=datetime.now().isoformat(),
            type="error_response",
            error=str(e)
        )

# SSE Streaming Support
async def sse_event_generator(session_id: str, user_id: str) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events for real-time UI updates"""
    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Create streaming session with Liquid Glass Host
        stream = await liquid_glass_host.create_stream(session_id)
        
        # Stream events from the orchestrator
        async for event in stream:
            if event.get("type") == "heartbeat":
                yield f"data: {json.dumps(event)}\n\n"
            else:
                # Process UI updates through orchestrator
                if event.get("type") in ["skeleton", "composition", "update"]:
                    ui_data = await orchestrator.process_streaming_event(event, {"user_id": user_id})
                    yield f"data: {json.dumps(ui_data)}\n\n"
                else:
                    yield f"data: {json.dumps(event)}\n\n"
                    
    except asyncio.CancelledError:
        logger.info(f"SSE stream {session_id} cancelled")
        yield f"data: {json.dumps({'type': 'disconnected', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
    except Exception as e:
        logger.error(f"SSE stream error for {session_id}: {e}")
        yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})}\n\n"
    finally:
        logger.info(f"SSE stream {session_id} closed")

@router.get("/stream/{session_id}")
async def stream_ui_updates(session_id: str, current_user: dict = Depends(get_current_user_mock)):
    """Server-Sent Events endpoint for real-time UI updates"""
    try:
        user_id = current_user.get("id", "anonymous")
        logger.info(f"Starting SSE stream for session {session_id}, user {user_id}")
        
        return StreamingResponse(
            sse_event_generator(session_id, user_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable Nginx buffering
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            }
        )
    except Exception as e:
        logger.error(f"Failed to create SSE stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create stream: {str(e)}")

@router.post("/stream/{session_id}/event")
async def send_stream_event(session_id: str, event: Dict[str, Any], current_user: dict = Depends(get_current_user_mock)):
    """Send a custom event to a streaming session"""
    try:
        user_id = current_user.get("id", "anonymous")
        logger.info(f"Sending event to stream {session_id}, user {user_id}: {event.get('type')}")
        
        # Add metadata to event
        event["session_id"] = session_id
        event["user_id"] = user_id
        event["timestamp"] = datetime.now().isoformat()
        
        # Stream the event
        await liquid_glass_host._stream_event(session_id, event)
        
        return {"status": "success", "session_id": session_id, "event_type": event.get("type")}
    except Exception as e:
        logger.error(f"Failed to send stream event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send event: {str(e)}")

@router.delete("/stream/{session_id}")
async def close_stream(session_id: str, current_user: dict = Depends(get_current_user_mock)):
    """Close a streaming session"""
    try:
        user_id = current_user.get("id", "anonymous")
        logger.info(f"Closing stream {session_id} for user {user_id}")
        
        # Send close event to stream
        await liquid_glass_host._stream_event(session_id, {
            "type": "stream_closed",
            "reason": "user_request",
            "timestamp": datetime.now().isoformat()
        })
        
        # Remove stream from active streams
        if session_id in liquid_glass_host.active_streams:
            del liquid_glass_host.active_streams[session_id]
        
        return {"status": "success", "session_id": session_id, "message": "Stream closed"}
    except Exception as e:
        logger.error(f"Failed to close stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to close stream: {str(e)}")

@router.post("/stream-intent")
async def stream_intent_endpoint(request: ProcessIntentRequest, current_user: dict = Depends(get_current_user_mock)):
    """Stream user intent processing through unified orchestrator and Liquid Glass Host"""
    try:
        # Add user context to the request
        user_context = request.context or {}
        user_context["user_id"] = current_user.get("id")
        user_context["user_name"] = current_user.get("name")
        user_context["user_email"] = current_user.get("email")
        
        # First, get the unified orchestrator response
        result = await orchestrator.process_user_intent(request.user_input, user_context)
        
        # Then, process through Liquid Glass Host for dynamic composition
        if result.get("type") == "optimistic_response":
            # Use Liquid Glass to enhance the optimistic skeleton
            enhanced_ui = await liquid_glass_host.compose_ui(
                {"skeleton": result["skeleton"]},
                "optimistic"
            )
            
            return create_ui_response_from_orchestrator({
                "type": "streaming_response",
                "ui": enhanced_ui,
                "timestamp": datetime.now().isoformat()
            })
        
        elif result.get("type") == "clarification_response":
            # Process clarification through Liquid Glass for better UI
            enhanced_ui = await liquid_glass_host.compose_ui(
                {"clarification": result["ui"]},
                "clarification"
            )
            
            return create_ui_response_from_orchestrator({
                "type": "clarification_response",
                "ui": enhanced_ui,
                "clarification_questions": result.get("clarification_questions", []),
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            # Process final response through Liquid Glass
            enhanced_ui = await liquid_glass_host.compose_ui(
                {"final": result.get("ui", {})},
                "final"
            )
            
            return create_ui_response_from_orchestrator({
                "type": "final_response",
                "ui": enhanced_ui,
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in stream-intent endpoint: {e}")
        return UIResponse(
            component={"error": str(e)},
            state_info={"type": "error"},
            timestamp=datetime.now().isoformat(),
            type="error_response",
            error=str(e)
        )

# Create FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="A2UI Router", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)
