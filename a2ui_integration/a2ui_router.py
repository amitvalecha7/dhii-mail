# FastAPI Router for A2UI Meeting Assistant
# Standalone router that can be imported into main.py

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
import uuid
from datetime import datetime
import io

# Import from existing modules (avoid circular imports)
from auth import get_current_user
from a2ui_integration.agent.agent_updated_v2 import run_meeting_agent_async
from marketing_manager import CampaignCreate
from a2ui_integration.a2ui_components_extended import A2UIComponents, A2UITemplates
from a2ui_integration.whatsapp_analyzer import WhatsAppAnalyzer
from a2ui_integration.plugin_manager import plugin_manager
from a2ui_integration.skill_store_ui import create_kernel_dashboard_ui, create_plugin_store_ui

logger = logging.getLogger(__name__)

# Create router instead of app
router = APIRouter(prefix="/api/a2ui", tags=["a2ui"])

# Pydantic models for A2UI requests
class A2UIRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class A2UIResponse(BaseModel):
    a2ui_json: str  # JSON string of A2UI components
    session_id: str
    timestamp: datetime

class MeetingBookingRequest(BaseModel):
    title: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM AM/PM format
    duration_minutes: int = 30
    participants: List[str]
    description: Optional[str] = ""
    meeting_type: str = "google_meet"

class MeetingUpdateRequest(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    duration_minutes: Optional[int] = None
    participants: Optional[List[str]] = None
    description: Optional[str] = None

# A2UI WebSocket connection manager
class A2UIConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_email: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_email] = websocket
        logger.info(f"A2UI WebSocket connected for user: {user_email}")

    def disconnect(self, websocket: WebSocket, user_email: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_email in self.user_connections:
            del self.user_connections[user_email]
        logger.info(f"A2UI WebSocket disconnected for user: {user_email}")

    async def send_a2ui_update(self, user_email: str, a2ui_json: str):
        """Send A2UI JSON update to specific user"""
        if user_email in self.user_connections:
            websocket = self.user_connections[user_email]
            try:
                await websocket.send_json({
                    "type": "a2ui_update",
                    "a2ui_json": a2ui_json,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error sending A2UI update to {user_email}: {e}")

    async def broadcast_a2ui_update(self, a2ui_json: str):
        """Broadcast A2UI JSON update to all connected users"""
        for connection in self.active_connections:
            try:
                await connection.send_json({
                    "type": "a2ui_update",
                    "a2ui_json": a2ui_json,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error broadcasting A2UI update: {e}")

# Initialize connection manager
a2ui_manager = A2UIConnectionManager()

# A2UI Endpoints - Integrated with existing dhii-mail backend
@router.post("/chat", response_model=A2UIResponse)
async def a2ui_chat(request: A2UIRequest):
    """Process A2UI chat request and return A2UI JSON components using existing backend"""
    try:
        # Use demo user for A2UI interface (can be enhanced with session-based auth)
        user_email = "demo@example.com"
        
        # Process the meeting request using existing agent
        agent_result = await run_meeting_agent_async(
            user_input=request.message,
            user_email=user_email
        )
        
        if agent_result.get("success"):
            # Create A2UI components from agent response
            a2ui_components = create_a2ui_meeting_components(
                agent_result.get("response", ""),
                user_email
            )
        else:
            # Create error components
            a2ui_components = create_a2ui_error_components(agent_result.get("error", "Unknown error"))
        
        a2ui_json = json.dumps(a2ui_components)
        
        # Generate new session ID if not provided
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        
        return A2UIResponse(
            a2ui_json=a2ui_json,
            session_id=session_id,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error processing A2UI chat request: {e}")
        
        # Return error UI
        error_components = create_a2ui_error_components(str(e))
        error_ui = json.dumps(error_components)
        
        return A2UIResponse(
            a2ui_json=error_ui,
            session_id=request.session_id or f"session_{datetime.now().timestamp()}",
            timestamp=datetime.now()
        )

@router.get("/meetings")
async def get_a2ui_meetings():
    """Get meetings formatted as A2UI JSON"""
    try:
        # Import here to avoid circular imports
        from a2ui_integration.agent.meeting_tools_updated_v2 import get_upcoming_meetings
        from a2ui_integration.agent.prompt_builder import get_meeting_list_ui
        
        # Get meetings from our existing system
        meetings = get_upcoming_meetings(user_email="demo@example.com")
        
        # Generate A2UI JSON for meeting list
        a2ui_json = get_meeting_list_ui(meetings)
        
        return {
            "a2ui_json": a2ui_json,
            "meeting_count": len(meetings),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting A2UI meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book")
async def book_a2ui_meeting(request: MeetingBookingRequest):
    """Book a new meeting via A2UI"""
    try:
        # Import here to avoid circular imports
        from a2ui_integration.agent.meeting_tools_updated_v2 import book_meeting
        
        # Parse date and time to create start_time and end_time
        from datetime import datetime, timedelta
        
        # Parse date (format: "2025-01-01")
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        # Parse time (format: "10:00 AM")
        time_str = request.time.replace(" AM", "").replace(" PM", "")
        hour, minute = map(int, time_str.split(":"))
        if "PM" in request.time and hour != 12:
            hour += 12
        elif "AM" in request.time and hour == 12:
            hour = 0
            
        start_time = date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=request.duration_minutes)
        
        # Book the meeting using our existing system
        meeting_data_dict = {
            "id": f"meeting_{uuid.uuid4().hex[:8]}",
            "title": request.title,
            "description": request.description,
            "start_time": start_time,
            "end_time": end_time,
            "timezone": "UTC",
            "meeting_type": request.meeting_type or "google_meet",
            "meeting_link": f"https://meet.google.com/{uuid.uuid4().hex[:8]}",
            "organizer_email": "demo@example.com",
            "status": "confirmed",
            "participants": request.participants,
            "reminder_enabled": True,
            "reminder_time_before": 15
        }
        meeting_result = book_meeting(meeting_data_dict)
        
        # Check if booking was successful
        if "error" in meeting_result:
            error_ui = create_a2ui_error_components(meeting_result["error"])
            return {
                "success": False,
                "error": meeting_result["error"],
                "a2ui_json": error_ui,
                "timestamp": datetime.now()
            }
        
        # Generate success A2UI JSON
        success_ui = create_booking_success_ui(request, meeting_result)
        
        return {
            "success": True,
            "meeting_id": meeting_result["meeting_id"],
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error booking A2UI meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meetings/{meeting_id}")
async def get_a2ui_meeting_details(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed meeting information formatted as A2UI JSON"""
    try:
        # Import here to avoid circular imports
        from a2ui_integration.agent.meeting_tools_updated_v2 import get_meeting_details
        
        # Get meeting details from our existing system
        meeting = get_meeting_details(meeting_id)
        
        if "error" in meeting:
            raise HTTPException(status_code=404, detail=meeting["error"])
        
        # Generate A2UI JSON for meeting details
        details_ui = create_meeting_details_ui(meeting)
        
        return {
            "a2ui_json": details_ui,
            "meeting": meeting,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A2UI meeting details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# A2UI WebSocket endpoint for real-time updates
@router.websocket("/ws/{user_email}")
async def websocket_a2ui(websocket: WebSocket, user_email: str):
    """WebSocket endpoint for A2UI real-time updates"""
    await a2ui_manager.connect(websocket, user_email)
    try:
        while True:
            # Receive and process messages
            data = await websocket.receive_json()
            
            if data.get("type") == "a2ui_request":
                # Process A2UI request
                message = data.get("message", "")
                session_id = data.get("session_id")
                
                # Process the request using agent
                agent_result = await run_meeting_agent_async(
                    user_input=message,
                    user_email=user_email
                )
                
                if agent_result.get("success"):
                    a2ui_components = create_a2ui_meeting_components(
                        agent_result.get("response", ""),
                        user_email
                    )
                else:
                    a2ui_components = create_a2ui_error_components(
                        agent_result.get("error", "Unknown error")
                    )
                
                a2ui_json = json.dumps(a2ui_components)
                
                # Send response back
                await websocket.send_json({
                    "type": "a2ui_response",
                    "a2ui_json": a2ui_json,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        a2ui_manager.disconnect(websocket, user_email)
    except Exception as e:
        logger.error(f"WebSocket error for {user_email}: {e}")
        a2ui_manager.disconnect(websocket, user_email)

# Health check endpoint for A2UI
@router.get("/health")
async def a2ui_health_check():
    """Health check for A2UI integration"""
    return {
        "status": "healthy",
        "a2ui_enabled": True,
        "timestamp": datetime.now()
    }

# Helper functions for creating A2UI components
def create_a2ui_meeting_components(agent_response: str, user_email: str) -> List[Dict[str, Any]]:
    """Create A2UI components for meeting-related responses"""
    return [
        {
            "beginRendering": {
                "surfaceId": "meeting-response",
                "root": "response-container",
                "styles": {"primaryColor": "#3b82f6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "meeting-response",
                "components": [
                    {
                        "id": "response-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["response-header", "response-content", "action-buttons"]
                                }
                            }
                        }
                    },
                    {
                        "id": "response-header",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Meeting Assistant Response"},
                                "style": {"fontSize": "18px", "fontWeight": "bold", "color": "#1f2937"}
                            }
                        }
                    },
                    {
                        "id": "response-content",
                        "component": {
                            "Text": {
                                "text": {"literalString": agent_response},
                                "style": {"fontSize": "14px", "color": "#4b5563", "marginTop": "8px"}
                            }
                        }
                    },
                    {
                        "id": "action-buttons",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["book-meeting-btn", "view-calendar-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "book-meeting-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Book New Meeting"},
                                "onClick": {"action": "book_meeting"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white"}
                            }
                        }
                    },
                    {
                        "id": "view-calendar-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "View Calendar"},
                                "onClick": {"action": "view_calendar"},
                                "style": {"backgroundColor": "#6b7280", "color": "white"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "meeting-response",
                "path": "/",
                "contents": {
                    "user_email": user_email,
                    "response_text": agent_response
                }
            }
        }
    ]

def create_a2ui_error_components(error_message: str) -> List[Dict[str, Any]]:
    """Create A2UI components for error responses"""
    return [
        {
            "beginRendering": {
                "surfaceId": "error",
                "root": "error-container",
                "styles": {"primaryColor": "#ef4444", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "error",
                "components": [
                    {
                        "id": "error-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["error-icon", "error-title", "error-message"]
                                }
                            }
                        }
                    },
                    {
                        "id": "error-icon",
                        "component": {
                            "Icon": {
                                "name": "error_outline",
                                "style": {"fontSize": "48px", "color": "#ef4444", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "error-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Error"},
                                "style": {"fontSize": "18px", "fontWeight": "bold", "color": "#ef4444"}
                            }
                        }
                    },
                    {
                        "id": "error-message",
                        "component": {
                            "Text": {
                                "text": {"literalString": error_message},
                                "style": {"fontSize": "14px", "color": "#6b7280"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "error",
                "path": "/",
                "contents": {
                    "error": True,
                    "error_message": error_message
                }
            }
        }
    ]

def create_booking_success_ui(request: MeetingBookingRequest, meeting_data: Dict[str, Any]) -> str:
    """Create A2UI JSON for successful booking"""
    success_components = [
        {
            "beginRendering": {
                "surfaceId": "success",
                "root": "success-container",
                "styles": {"primaryColor": "#10b981", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "success",
                "components": [
                    {
                        "id": "success-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["success-icon", "success-title", "success-message", "meeting-details", "action-buttons"]
                                }
                            }
                        }
                    },
                    {
                        "id": "success-icon",
                        "component": {
                            "Icon": {
                                "name": "check_circle",
                                "style": {"fontSize": "48px", "color": "#10b981", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "success-title",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Meeting Booked Successfully!"},
                                "style": {"color": "#10b981", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "success-message",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Your meeting '{request.title}' has been scheduled for {request.date} at {request.time}."},
                                "style": {"fontSize": "14px", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-details",
                        "component": {
                            "Card": {
                                "child": "details-content",
                                "style": {"padding": "16px", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "details-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["meeting-title", "meeting-datetime", "meeting-link"]
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-title",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"literalString": request.title},
                                "style": {"fontWeight": "600", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-datetime",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"{request.date} at {request.time}"},
                                "style": {"color": "#6b7280", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-link",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Meeting Link: {meeting_data.get('meeting_link', 'Link will be provided')}"},
                                "style": {"fontSize": "12px", "color": "#4F46E5"}
                            }
                        }
                    },
                    {
                        "id": "action-buttons",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["view-meetings-btn", "schedule-another-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "view-meetings-btn",
                        "component": {
                            "Button": {
                                "child": "view-text",
                                "primary": True,
                                "action": {"name": "view_upcoming_meetings"}
                            }
                        }
                    },
                    {
                        "id": "view-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "View Meetings"}
                            }
                        }
                    },
                    {
                        "id": "schedule-another-btn",
                        "component": {
                            "Button": {
                                "child": "schedule-text",
                                "variant": "outline",
                                "action": {"name": "schedule_another_meeting"}
                            }
                        }
                    },
                    {
                        "id": "schedule-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Schedule Another"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "success",
                "path": "/",
                "contents": []
            }
        }
    ]

    return json.dumps(success_components)

# WhatsApp Integration Models
class WhatsAppAnalysisRequest(BaseModel):
    chat_content: str
    filename: str = "chat.txt"
    format_type: str = "txt"  # "txt" or "json"

class WhatsAppAnalysisResponse(BaseModel):
    status: str
    analysis: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    a2ui_json: Optional[str] = None

# Initialize WhatsApp analyzer
whatsapp_analyzer = WhatsAppAnalyzer()

# WhatsApp Integration Endpoints
@router.post("/whatsapp/analyze-chat", response_model=WhatsAppAnalysisResponse)
async def analyze_whatsapp_chat(
    chat_content: str = Form(...),
    filename: str = Form("chat.txt"),
    format_type: str = Form("txt")
):
    """Analyze WhatsApp chat export and return A2UI components"""
    try:
        # Determine format from filename if not specified
        if format_type == "txt" and filename.endswith(".json"):
            format_type = "json"
        
        # Parse the chat content
        messages = whatsapp_analyzer.parse_chat_export(chat_content, format_type)
        
        if not messages:
            return WhatsAppAnalysisResponse(
                status="failed",
                error="No messages found in chat export"
            )
        
        # Analyze the chat
        analysis = whatsapp_analyzer.analyze_chat(messages)
        
        # Generate summary
        summary = f"Analyzed {len(messages)} messages from {len(analysis['participant_stats'])} participants"
        
        # Create A2UI components for the analysis
        a2ui_components = create_whatsapp_analysis_ui(analysis, summary)
        a2ui_json = json.dumps(a2ui_components)
        
        # Track plugin usage
        plugin_manager.increment_usage("whatsapp_analyzer")
        
        return WhatsAppAnalysisResponse(
            status="success",
            analysis=analysis,
            summary=summary,
            a2ui_json=a2ui_json
        )
        
    except Exception as e:
        logger.error(f"Error analyzing WhatsApp chat: {e}")
        error_components = create_a2ui_error_components(str(e))
        error_ui = json.dumps(error_components)
        
        # Track plugin error
        plugin_manager.increment_error("whatsapp_analyzer", str(e))
        
        return WhatsAppAnalysisResponse(
            status="failed",
            error=str(e),
            a2ui_json=error_ui
        )

@router.post("/whatsapp/upload-chat")
async def upload_whatsapp_chat(file: UploadFile = File(...)):
    """Upload WhatsApp chat file for analysis"""
    try:
        # Validate file type
        if not file.filename.endswith((".txt", ".json")):
            raise HTTPException(status_code=400, detail="Only .txt and .json files are supported")
        
        # Read file content
        content = await file.read()
        chat_content = content.decode('utf-8')
        
        # Determine format
        format_type = "json" if file.filename.endswith(".json") else "txt"
        
        # Parse and analyze
        messages = whatsapp_analyzer.parse_chat_export(chat_content, format_type)
        analysis = whatsapp_analyzer.analyze_chat(messages)
        
        # Create A2UI components
        summary = f"Analyzed {len(messages)} messages from {file.filename}"
        a2ui_components = create_whatsapp_analysis_ui(analysis, summary)
        a2ui_json = json.dumps(a2ui_components)
        
        # Track plugin usage
        plugin_manager.increment_usage("whatsapp_analyzer")
        
        return {
            "status": "success",
            "filename": file.filename,
            "message_count": len(messages),
            "participant_count": len(analysis["participant_stats"]),
            "analysis": analysis,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error uploading WhatsApp chat: {e}")
        # Track plugin error
        plugin_manager.increment_error("whatsapp_analyzer", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/whatsapp/plugin-info")
async def get_whatsapp_plugin_info():
    """Get WhatsApp plugin information and status"""
    try:
        plugin_info = plugin_manager.get_plugin_info("whatsapp_analyzer")
        if not plugin_info:
            return {
                "status": "not_found",
                "message": "WhatsApp analyzer plugin not found"
            }
        
        return {
            "status": "success",
            "plugin": plugin_info,
            "capabilities": [
                "Chat export parsing (txt/json)",
                "Message analysis and statistics",
                "Participant activity patterns",
                "Sentiment analysis",
                "Media usage statistics",
                "Conversation insights",
                "Privacy-aware processing"
            ],
            "supported_formats": ["txt", "json"],
            "max_file_size": "10MB",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp plugin info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to create WhatsApp analysis UI components
def create_whatsapp_analysis_ui(analysis: Dict[str, Any], summary: str) -> List[Dict[str, Any]]:
    """Create A2UI components for WhatsApp chat analysis"""
    participant_stats = analysis.get("participant_stats", {})
    activity_patterns = analysis.get("activity_patterns", {})
    sentiment_analysis = analysis.get("sentiment_analysis", {})
    
    return [
        {
            "beginRendering": {
                "surfaceId": "whatsapp-analysis",
                "root": "analysis-container",
                "styles": {"primaryColor": "#25D366", "font": "Inter"}  # WhatsApp green
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "whatsapp-analysis",
                "components": [
                    {
                        "id": "analysis-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": [
                                        "header-section",
                                        "overview-section", 
                                        "participants-section",
                                        "activity-section",
                                        "sentiment-section",
                                        "insights-section"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["whatsapp-icon", "analysis-title", "summary-text"]
                                }
                            }
                        }
                    },
                    {
                        "id": "whatsapp-icon",
                        "component": {
                            "Icon": {
                                "name": "chat",
                                "style": {"fontSize": "48px", "color": "#25D366", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "analysis-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": "WhatsApp Chat Analysis"},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#1f2937", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "summary-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": summary},
                                "style": {"fontSize": "16px", "color": "#6b7280", "marginBottom": "24px"}
                            }
                        }
                    },
                    {
                        "id": "overview-section",
                        "component": {
                            "Card": {
                                "title": {"literalString": "Overview"},
                                "content": {
                                    "explicitList": ["total-messages", "date-range", "media-count"]
                                }
                            }
                        }
                    },
                    {
                        "id": "total-messages",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"📊 Total Messages: {analysis.get('overview', {}).get('total_messages', 0)}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "date-range",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"📅 Period: {analysis.get('overview', {}).get('date_range', 'N/A')}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "media-count",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"🎬 Media Files: {analysis.get('media_statistics', {}).get('total_media', 0)}"},
                                "style": {"fontSize": "14px"}
                            }
                        }
                    },
                    {
                        "id": "participants-section",
                        "component": {
                            "Card": {
                                "title": {"literalString": "Participants"},
                                "content": {
                                    "explicitList": ["participant-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "participant-list",
                        "component": {
                            "ListView": {
                                "items": {
                                    "explicitList": [
                                        {
                                            "name": name,
                                            "messages": stats.get("message_count", 0),
                                            "words": stats.get("word_count", 0)
                                        }
                                        for name, stats in participant_stats.items()
                                    ]
                                },
                                "itemBuilder": {
                                    "type": "participant_item",
                                    "template": "{name}: {messages} messages, {words} words"
                                }
                            }
                        }
                    },
                    {
                        "id": "activity-section",
                        "component": {
                            "Card": {
                                "title": {"literalString": "Activity Patterns"},
                                "content": {
                                    "explicitList": ["peak-hours", "daily-activity"]
                                }
                            }
                        }
                    },
                    {
                        "id": "peak-hours",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"⏰ Peak Hours: {activity_patterns.get('peak_hours', 'N/A')}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "daily-activity",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"📈 Most Active Day: {activity_patterns.get('most_active_day', 'N/A')}"},
                                "style": {"fontSize": "14px"}
                            }
                        }
                    },
                    {
                        "id": "sentiment-section",
                        "component": {
                            "Card": {
                                "title": {"literalString": "Sentiment Analysis"},
                                "content": {
                                    "explicitList": ["overall-sentiment", "positive-ratio", "negative-ratio"]
                                }
                            }
                        }
                    },
                    {
                        "id": "overall-sentiment",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"😊 Overall: {sentiment_analysis.get('overall_sentiment', 'Neutral')}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "positive-ratio",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"✅ Positive: {sentiment_analysis.get('positive_ratio', 0):.1%}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "negative-ratio",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"❌ Negative: {sentiment_analysis.get('negative_ratio', 0):.1%}"},
                                "style": {"fontSize": "14px"}
                            }
                        }
                    },
                    {
                        "id": "insights-section",
                        "component": {
                            "Card": {
                                "title": {"literalString": "Key Insights"},
                                "content": {
                                    "explicitList": ["insights-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "insights-list",
                        "component": {
                            "ListView": {
                                "items": {
                                    "explicitList": analysis.get("conversation_insights", {}).get("key_insights", [])
                                },
                                "itemBuilder": {
                                    "type": "insight_item",
                                    "template": "• {insight}"
                                }
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "whatsapp-analysis",
                "path": "/",
                "contents": {
                    "analysis": analysis,
                    "summary": summary,
                    "participant_count": len(participant_stats),
                    "total_messages": analysis.get("overview", {}).get("total_messages", 0)
                }
            }
        }
    ]

def create_meeting_details_ui(meeting: Dict[str, Any]) -> str:
    """Create A2UI JSON for meeting details"""
    details_components = [
        {
            "beginRendering": {
                "surfaceId": "details",
                "root": "details-container",
                "styles": {"primaryColor": "#4F46E5", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "details",
                "components": [
                    {
                        "id": "details-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["details-header", "details-content", "action-buttons"]
                                }
                            }
                        }
                    },
                    {
                        "id": "details-header",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Meeting Details"},
                                "style": {"fontWeight": "bold", "marginBottom": "16px"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "details",
                "path": "/",
                "contents": {
                    "meetingTitle": meeting.get("title", ""),
                    "datetime": meeting.get("datetime", ""),
                    "duration": "30 minutes",
                    "location": "Google Meet",
                    "description": meeting.get("description", ""),
                    "meetingId": meeting.get("id", ""),
                    "meetingLink": meeting.get("meetingLink", "")
                }
            }
        }
    ]
    
    return json.dumps(details_components)

# Video Meeting Endpoints for A2UI
class A2UIVideoMeetingCreate(BaseModel):
    """Video meeting creation request for A2UI"""
    title: str
    description: Optional[str] = None
    start_time: str  # ISO format string
    end_time: Optional[str] = None  # ISO format string
    participants: List[str] = []
    auto_recording: bool = True

@router.post("/video/meetings")
async def create_a2ui_video_meeting(request: A2UIVideoMeetingCreate):
    """Create a new video meeting via A2UI"""
    try:
        # Import video manager and models
        from video_manager import video_manager, VideoMeetingCreate
        from datetime import datetime
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        
        # Convert string dates to datetime objects
        start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
        end_time = None
        if request.end_time:
            end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
        
        # Create proper VideoMeetingCreate object
        meeting_create = VideoMeetingCreate(
            title=request.title,
            description=request.description,
            start_time=start_time,
            end_time=end_time,
            participants=request.participants,
            auto_recording=request.auto_recording
        )
        
        # Create video meeting
        new_meeting = video_manager.create_meeting(meeting_create, user_email)
        
        # Generate A2UI JSON for success
        success_ui = create_video_meeting_success_ui(new_meeting)
        
        return {
            "success": True,
            "meeting_id": new_meeting.id,
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error creating A2UI video meeting: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/video/meetings")
async def get_a2ui_video_meetings():
    """Get all video meetings for A2UI user"""
    try:
        # Import video manager
        from video_manager import video_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        meetings = video_manager.list_user_meetings(user_email)
        
        # Generate A2UI JSON for meeting list
        meeting_list_ui = create_video_meeting_list_ui(meetings)
        
        return {
            "success": True,
            "meetings": meetings,
            "a2ui_json": meeting_list_ui,
            "meeting_count": len(meetings),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting A2UI video meetings: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/video/meetings/{meeting_id}")
async def get_a2ui_video_meeting_details(meeting_id: str):
    """Get detailed video meeting information for A2UI"""
    try:
        # Import video manager
        from video_manager import video_manager
        
        meeting = video_manager.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Generate A2UI JSON for meeting details
        details_ui = create_video_meeting_details_ui(meeting)
        
        return {
            "success": True,
            "meeting": meeting,
            "a2ui_json": details_ui,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A2UI video meeting details: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.post("/video/meetings/{meeting_id}/start")
async def start_a2ui_video_meeting(meeting_id: str):
    """Start a video meeting via A2UI"""
    try:
        # Import video manager
        from video_manager import video_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        
        result = video_manager.start_meeting(meeting_id, user_email)
        
        # Generate A2UI JSON for success
        success_ui = create_video_meeting_action_ui("Meeting started successfully", "start")
        
        return {
            "success": True,
            "result": result,
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error starting A2UI video meeting: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.post("/video/meetings/{meeting_id}/end")
async def end_a2ui_video_meeting(meeting_id: str):
    """End a video meeting via A2UI"""
    try:
        # Import video manager
        from video_manager import video_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        
        result = video_manager.end_meeting(meeting_id, user_email)
        
        # Generate A2UI JSON for success
        success_ui = create_video_meeting_action_ui("Meeting ended successfully", "end")
        
        return {
            "success": True,
            "result": result,
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error ending A2UI video meeting: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

# Helper functions for video meeting A2UI components
def create_video_meeting_success_ui(meeting) -> str:
    """Create A2UI JSON for successful video meeting creation"""
    success_components = [
        {
            "beginRendering": {
                "surfaceId": "video-success",
                "root": "success-container",
                "styles": {"primaryColor": "#10b981", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "video-success",
                "components": [
                    {
                        "id": "success-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["success-icon", "success-title", "meeting-info", "action-buttons"]
                                }
                            }
                        }
                    },
                    {
                        "id": "success-icon",
                        "component": {
                            "Icon": {
                                "name": "videocam",
                                "style": {"fontSize": "48px", "color": "#10b981", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "success-title",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Video Meeting Created!"},
                                "style": {"color": "#10b981", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-info",
                        "component": {
                            "Card": {
                                "child": "info-content",
                                "style": {"marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "info-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["meeting-title", "meeting-url", "meeting-time"]
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Title: {meeting.title}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-url",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Meeting URL: {meeting.meeting_url}"},
                                "style": {"fontSize": "14px", "marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-time",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Time: {meeting.start_time}"},
                                "style": {"fontSize": "14px"}
                            }
                        }
                    },
                    {
                        "id": "action-buttons",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["start-meeting-btn", "copy-url-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "start-meeting-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Start Meeting"},
                                "onClick": {"action": f"start_video_meeting_{meeting.id}"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white", "marginRight": "8px"}
                            }
                        }
                    },
                    {
                        "id": "copy-url-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Copy URL"},
                                "onClick": {"action": f"copy_meeting_url_{meeting.id}"},
                                "style": {"backgroundColor": "#6b7280", "color": "white"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "video-success",
                "path": "/",
                "contents": {
                    "meeting_id": meeting.id,
                    "meeting_url": meeting.meeting_url,
                    "meeting_title": meeting.title
                }
            }
        }
    ]
    
    return json.dumps(success_components)

def create_video_meeting_list_ui(meetings) -> str:
    """Create A2UI JSON for video meeting list"""
    if not meetings:
        no_meetings_components = [
            {
                "beginRendering": {
                    "surfaceId": "video-list",
                    "root": "no-meetings-container",
                    "styles": {"primaryColor": "#6b7280", "font": "Inter"}
                }
            },
            {
                "surfaceUpdate": {
                    "surfaceId": "video-list",
                    "components": [
                        {
                            "id": "no-meetings-container",
                            "component": {
                                "Column": {
                                    "children": {
                                        "explicitList": ["no-meetings-icon", "no-meetings-text"]
                                    }
                                }
                            }
                        },
                        {
                            "id": "no-meetings-icon",
                            "component": {
                                "Icon": {
                                    "name": "videocam_off",
                                    "style": {"fontSize": "48px", "color": "#9ca3af", "marginBottom": "16px"}
                                }
                            }
                        },
                        {
                            "id": "no-meetings-text",
                            "component": {
                                "Text": {
                                    "text": {"literalString": "No video meetings scheduled"},
                                    "style": {"fontSize": "16px", "color": "#6b7280"}
                                }
                            }
                        }
                    ]
                }
            }
        ]
        return json.dumps(no_meetings_components)
    
    meeting_items = []
    for i, meeting in enumerate(meetings):
        meeting_items.append(f"meeting-item-{i}")
    
    list_components = [
        {
            "beginRendering": {
                "surfaceId": "video-list",
                "root": "list-container",
                "styles": {"primaryColor": "#4F46E5", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "video-list",
                "components": [
                    {
                        "id": "list-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["list-header"] + meeting_items
                                }
                            }
                        }
                    },
                    {
                        "id": "list-header",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Your Video Meetings"},
                                "style": {"fontWeight": "bold", "marginBottom": "16px"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    # Add individual meeting items
    for i, meeting in enumerate(meetings):
        meeting_component = {
            "id": f"meeting-item-{i}",
            "component": {
                "Card": {
                    "child": f"meeting-content-{i}",
                    "style": {"marginBottom": "12px", "padding": "16px"}
                }
            }
        }
        
        content_component = {
            "id": f"meeting-content-{i}",
            "component": {
                "Column": {
                    "children": {
                        "explicitList": [f"meeting-title-{i}", f"meeting-time-{i}", f"meeting-actions-{i}"]
                    }
                }
            }
        }
        
        title_component = {
            "id": f"meeting-title-{i}",
            "component": {
                "Text": {
                    "text": {"literalString": meeting.title},
                    "style": {"fontSize": "16px", "fontWeight": "bold", "marginBottom": "4px"}
                }
            }
        }
        
        time_component = {
            "id": f"meeting-time-{i}",
            "component": {
                "Text": {
                    "text": {"literalString": f"Time: {meeting.start_time}"},
                    "style": {"fontSize": "14px", "color": "#6b7280", "marginBottom": "8px"}
                }
            }
        }
        
        actions_component = {
            "id": f"meeting-actions-{i}",
            "component": {
                "Row": {
                    "children": {
                        "explicitList": [f"view-btn-{i}", f"start-btn-{i}"]
                    }
                }
            }
        }
        
        view_btn = {
            "id": f"view-btn-{i}",
            "component": {
                "Button": {
                    "text": {"literalString": "View Details"},
                    "onClick": {"action": f"view_video_meeting_{meeting.id}"},
                    "style": {"backgroundColor": "#6b7280", "color": "white", "marginRight": "8px"}
                }
            }
        }
        
        start_btn = {
            "id": f"start-btn-{i}",
            "component": {
                "Button": {
                    "text": {"literalString": "Start"},
                    "onClick": {"action": f"start_video_meeting_{meeting.id}"},
                    "style": {"backgroundColor": "#10b981", "color": "white"}
                }
            }
        }
        
        list_components.extend([
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [meeting_component]}},
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [content_component]}},
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [title_component]}},
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [time_component]}},
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [actions_component]}},
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [view_btn]}},
            {"surfaceUpdate": {"surfaceId": "video-list", "components": [start_btn]}}
        ])
    
    return json.dumps(list_components)

def create_video_meeting_details_ui(meeting) -> str:
    """Create A2UI JSON for detailed video meeting information"""
    details_components = [
        {
            "beginRendering": {
                "surfaceId": "video-details",
                "root": "details-container",
                "styles": {"primaryColor": "#4F46E5", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "video-details",
                "components": [
                    {
                        "id": "details-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["details-header", "details-content", "action-buttons"]
                                }
                            }
                        }
                    },
                    {
                        "id": "details-header",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Video Meeting Details"},
                                "style": {"fontWeight": "bold", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "details-content",
                        "component": {
                            "Card": {
                                "child": "meeting-info",
                                "style": {"marginBottom": "16px", "padding": "16px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-info",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["meeting-title", "meeting-url", "meeting-time", "meeting-status"]
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Title: {meeting.title}"},
                                "style": {"fontSize": "16px", "fontWeight": "bold", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-url",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Meeting URL: {meeting.meeting_url}"},
                                "style": {"fontSize": "14px", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-time",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Time: {meeting.start_time} - {meeting.end_time}"},
                                "style": {"fontSize": "14px", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-status",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Status: {meeting.status}"},
                                "style": {"fontSize": "14px", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "action-buttons",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["start-btn", "copy-url-btn", "back-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "start-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Start Meeting"},
                                "onClick": {"action": f"start_video_meeting_{meeting.id}"},
                                "style": {"backgroundColor": "#10b981", "color": "white", "marginRight": "8px"}
                            }
                        }
                    },
                    {
                        "id": "copy-url-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Copy URL"},
                                "onClick": {"action": f"copy_meeting_url_{meeting.id}"},
                                "style": {"backgroundColor": "#6b7280", "color": "white", "marginRight": "8px"}
                            }
                        }
                    },
                    {
                        "id": "back-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Back to List"},
                                "onClick": {"action": "view_video_meetings"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "video-details",
                "path": "/",
                "contents": {
                    "meeting_id": meeting.id,
                    "meeting_url": meeting.meeting_url,
                    "meeting_title": meeting.title,
                    "meeting_status": meeting.status
                }
            }
        }
    ]
    
    return json.dumps(details_components)

def create_video_meeting_action_ui(message: str, action: str) -> str:
    """Create A2UI JSON for video meeting action confirmation"""
    action_components = [
        {
            "beginRendering": {
                "surfaceId": "video-action",
                "root": "action-container",
                "styles": {"primaryColor": "#10b981", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "video-action",
                "components": [
                    {
                        "id": "action-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["action-icon", "action-message", "action-button"]
                                }
                            }
                        }
                    },
                    {
                        "id": "action-icon",
                        "component": {
                            "Icon": {
                                "name": "check_circle",
                                "style": {"fontSize": "48px", "color": "#10b981", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "action-message",
                        "component": {
                            "Text": {
                                "text": {"literalString": message},
                                "style": {"fontSize": "16px", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "action-button",
                        "component": {
                            "Button": {
                                "text": {"literalString": "View Meetings"},
                                "onClick": {"action": "view_video_meetings"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    return json.dumps(action_components)

# Marketing Campaign Endpoints for A2UI
@router.post("/marketing/campaigns")
async def create_a2ui_marketing_campaign(request: dict):
    """Create a new marketing campaign via A2UI"""
    try:
        # Import marketing manager
        from marketing_manager import marketing_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        
        # Create campaign
        campaign_data = CampaignCreate(**request)
        new_campaign = marketing_manager.create_campaign(campaign_data, user_email)
        
        # Generate A2UI JSON for success
        success_ui = create_campaign_success_ui(new_campaign)
        
        return {
            "success": True,
            "campaign_id": new_campaign.id,
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error creating A2UI marketing campaign: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/marketing/campaigns")
async def get_a2ui_marketing_campaigns():
    """Get all marketing campaigns for A2UI user"""
    try:
        # Import marketing manager
        from marketing_manager import marketing_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        campaigns = marketing_manager.list_campaigns(user_email)
        
        # Generate A2UI JSON for campaign list
        campaign_list_ui = create_campaign_list_ui(campaigns)
        
        return {
            "success": True,
            "campaigns": campaigns,
            "a2ui_json": campaign_list_ui,
            "campaign_count": len(campaigns),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting A2UI marketing campaigns: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/marketing/campaigns/{campaign_id}")
async def get_a2ui_campaign_details(campaign_id: str):
    """Get detailed campaign information for A2UI"""
    try:
        # Import marketing manager
        from marketing_manager import marketing_manager
        
        campaign = marketing_manager.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate A2UI JSON for campaign details
        details_ui = create_campaign_details_ui(campaign)
        
        return {
            "success": True,
            "campaign": campaign,
            "a2ui_json": details_ui,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A2UI campaign details: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.post("/marketing/campaigns/{campaign_id}/send")
async def send_a2ui_campaign(campaign_id: str):
    """Send a marketing campaign via A2UI"""
    try:
        # Import marketing manager
        from marketing_manager import marketing_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        
        result = marketing_manager.send_campaign(campaign_id, user_email)
        
        # Generate A2UI JSON for success
        success_ui = create_campaign_action_ui("Campaign sent successfully", "send")
        
        return {
            "success": True,
            "result": result,
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error sending A2UI campaign: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/marketing/dashboard")
async def get_a2ui_marketing_dashboard():
    """Get marketing dashboard data for A2UI"""
    try:
        # Import marketing manager
        from marketing_manager import marketing_manager
        
        # Use demo user for A2UI interface
        user_email = "demo@example.com"
        dashboard_data = marketing_manager.get_marketing_dashboard(user_email)
        
        # Generate A2UI JSON for dashboard
        dashboard_ui = create_marketing_dashboard_ui(dashboard_data)
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "a2ui_json": dashboard_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting A2UI marketing dashboard: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

# Helper functions for marketing campaign A2UI components
def create_campaign_success_ui(campaign) -> str:
    """Create A2UI JSON for successful campaign creation"""
    success_components = [
        {
            "beginRendering": {
                "surfaceId": "campaign-success",
                "root": "success-container",
                "styles": {"primaryColor": "#10b981", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "campaign-success",
                "components": [
                    {
                        "id": "success-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["success-icon", "success-title", "campaign-info", "action-buttons"]
                                }
                            }
                        }
                    },
                    {
                        "id": "success-icon",
                        "component": {
                            "Icon": {
                                "name": "campaign",
                                "style": {"fontSize": "48px", "color": "#10b981", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "success-title",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Campaign Created!"},
                                "style": {"color": "#10b981", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "campaign-info",
                        "component": {
                            "Card": {
                                "child": "info-content",
                                "style": {"marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "info-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["campaign-name", "campaign-type", "campaign-status"]
                                }
                            }
                        }
                    },
                    {
                        "id": "campaign-name",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Name: {campaign.name}"},
                                "style": {"marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "campaign-type",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Type: {campaign.campaign_type}"},
                                "style": {"marginBottom": "4px"}
                            }
                        }
                    },
                    {
                        "id": "campaign-status",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Status: {campaign.status}"}
                            }
                        }
                    },
                    {
                        "id": "action-buttons",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["view-campaigns-btn", "send-campaign-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "view-campaigns-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "View Campaigns"},
                                "onClick": {"action": "view_campaigns"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white", "marginRight": "8px"}
                            }
                        }
                    },
                    {
                        "id": "send-campaign-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Send Campaign"},
                                "onClick": {"action": f"send_campaign_{campaign.id}"},
                                "style": {"backgroundColor": "#10b981", "color": "white"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    return json.dumps(success_components)

def create_campaign_list_ui(campaigns) -> str:
    """Create A2UI JSON for campaign list"""
    if not campaigns:
        empty_components = [
            {
                "beginRendering": {
                    "surfaceId": "campaign-list",
                    "root": "empty-container",
                    "styles": {"primaryColor": "#6b7280", "font": "Inter"}
                }
            },
            {
                "surfaceUpdate": {
                    "surfaceId": "campaign-list",
                    "components": [
                        {
                            "id": "empty-container",
                            "component": {
                                "Column": {
                                    "children": {
                                        "explicitList": ["empty-icon", "empty-text"]
                                    }
                                }
                            }
                        },
                        {
                            "id": "empty-icon",
                            "component": {
                                "Icon": {
                                    "name": "campaign",
                                    "style": {"fontSize": "64px", "color": "#d1d5db", "marginBottom": "16px"}
                                }
                            }
                        },
                        {
                            "id": "empty-text",
                            "component": {
                                "Text": {
                                    "text": {"literalString": "No campaigns found"},
                                    "style": {"color": "#6b7280", "fontSize": "18px"}
                                }
                            }
                        }
                    ]
                }
            }
        ]
        return json.dumps(empty_components)
    
    # Create campaign list components
    campaign_items = []
    for i, campaign in enumerate(campaigns):
        campaign_items.append(f"campaign-item-{i}")
    
    list_components = [
        {
            "beginRendering": {
                "surfaceId": "campaign-list",
                "root": "list-container",
                "styles": {"primaryColor": "#3b82f6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "campaign-list",
                "components": [
                    {
                        "id": "list-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["list-header"] + campaign_items
                                }
                            }
                        }
                    },
                    {
                        "id": "list-header",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["header-title", "create-campaign-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-title",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": "Marketing Campaigns"},
                                "style": {"marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "create-campaign-btn",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Create Campaign"},
                                "onClick": {"action": "create_campaign"},
                                "style": {"backgroundColor": "#10b981", "color": "white"}
                            }
                        }
                    }
                ] + create_campaign_item_components(campaigns)
            }
        }
    ]
    
    return json.dumps(list_components)

def create_campaign_item_components(campaigns) -> List[Dict[str, Any]]:
    """Create individual campaign item components"""
    components = []
    
    for i, campaign in enumerate(campaigns):
        status_color = {
            "draft": "#6b7280",
            "scheduled": "#f59e0b",
            "sent": "#10b981",
            "failed": "#ef4444"
        }.get(campaign.status, "#6b7280")
        
        components.extend([
            {
                "id": f"campaign-item-{i}",
                "component": {
                    "Card": {
                        "child": f"item-content-{i}",
                        "style": {"marginBottom": "12px", "padding": "16px"}
                    }
                }
            },
            {
                "id": f"item-content-{i}",
                "component": {
                    "Column": {
                        "children": {
                            "explicitList": [f"item-header-{i}", f"item-details-{i}", f"item-actions-{i}"]
                        }
                    }
                }
            },
            {
                "id": f"item-header-{i}",
                "component": {
                    "Row": {
                        "children": {
                            "explicitList": [f"campaign-name-{i}", f"campaign-status-{i}"]
                        }
                    }
                }
            },
            {
                "id": f"campaign-name-{i}",
                "component": {
                    "Text": {
                        "usageHint": "h3",
                        "text": {"literalString": campaign.name},
                        "style": {"fontWeight": "bold"}
                    }
                }
            },
            {
                "id": f"campaign-status-{i}",
                "component": {
                    "Badge": {
                        "text": {"literalString": campaign.status.upper()},
                        "style": {"backgroundColor": status_color, "color": "white"}
                    }
                }
            },
            {
                "id": f"item-details-{i}",
                "component": {
                    "Column": {
                        "children": {
                            "explicitList": [f"campaign-type-{i}", f"campaign-description-{i}"]
                        }
                    }
                }
            },
            {
                "id": f"campaign-type-{i}",
                "component": {
                    "Text": {
                        "text": {"literalString": f"Type: {campaign.campaign_type}"},
                        "style": {"color": "#6b7280", "fontSize": "14px"}
                    }
                }
            },
            {
                "id": f"campaign-description-{i}",
                "component": {
                    "Text": {
                        "text": {"literalString": campaign.description[:100] + ("..." if len(campaign.description) > 100 else "")},
                        "style": {"color": "#6b7280", "fontSize": "14px"}
                    }
                }
            },
            {
                "id": f"item-actions-{i}",
                "component": {
                    "Row": {
                        "children": {
                            "explicitList": [f"view-campaign-{i}", f"send-campaign-{i}"]
                        }
                    }
                }
            },
            {
                "id": f"view-campaign-{i}",
                "component": {
                    "Button": {
                        "text": {"literalString": "View"},
                        "onClick": {"action": f"view_campaign_{campaign.id}"},
                        "style": {"backgroundColor": "#3b82f6", "color": "white", "marginRight": "8px"}
                    }
                }
            },
            {
                "id": f"send-campaign-{i}",
                "component": {
                    "Button": {
                        "text": {"literalString": "Send"},
                        "onClick": {"action": f"send_campaign_{campaign.id}"},
                        "style": {"backgroundColor": "#10b981", "color": "white"}
                    }
                }
            }
        ])
    
    return components

def create_campaign_details_ui(campaign) -> str:
    """Create A2UI JSON for detailed campaign information"""
    details_components = [
        {
            "beginRendering": {
                "surfaceId": "campaign-details",
                "root": "details-container",
                "styles": {"primaryColor": "#3b82f6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "campaign-details",
                "components": [
                    {
                        "id": "details-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["details-header", "details-content", "details-actions"]
                                }
                            }
                        }
                    },
                    {
                        "id": "details-header",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["campaign-title", "campaign-status"]
                                }
                            }
                        }
                    },
                    {
                        "id": "campaign-title",
                        "component": {
                            "Text": {
                                "usageHint": "h1",
                                "text": {"literalString": campaign.name},
                                "style": {"marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "campaign-status",
                        "component": {
                            "Badge": {
                                "text": {"literalString": campaign.status.upper()},
                                "style": {"backgroundColor": "#10b981", "color": "white"}
                            }
                        }
                    },
                    {
                        "id": "details-content",
                        "component": {
                            "Card": {
                                "child": "content-column",
                                "style": {"marginBottom": "16px", "padding": "24px"}
                            }
                        }
                    },
                    {
                        "id": "content-column",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["description-section", "type-section", "email-section"]
                                }
                            }
                        }
                    },
                    {
                        "id": "description-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["description-label", "description-text"]
                                }
                            }
                        }
                    },
                    {
                        "id": "description-label",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"literalString": "Description"},
                                "style": {"marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "description-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": campaign.description},
                                "style": {"color": "#6b7280", "lineHeight": "1.5"}
                            }
                        }
                    },
                    {
                        "id": "type-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["type-label", "type-text"]
                                }
                            }
                        }
                    },
                    {
                        "id": "type-label",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"literalString": "Campaign Type"},
                                "style": {"marginBottom": "8px", "marginTop": "16px"}
                            }
                        }
                    },
                    {
                        "id": "type-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": campaign.campaign_type},
                                "style": {"color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "email-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["email-label", "email-text"]
                                }
                            }
                        }
                    },
                    {
                        "id": "email-label",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"literalString": "Sender Email"},
                                "style": {"marginBottom": "8px", "marginTop": "16px"}
                            }
                        }
                    },
                    {
                        "id": "email-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": campaign.sender_email},
                                "style": {"color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "details-actions",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["back-button", "send-button"]
                                }
                            }
                        }
                    },
                    {
                        "id": "back-button",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Back to Campaigns"},
                                "onClick": {"action": "view_campaigns"},
                                "style": {"backgroundColor": "#6b7280", "color": "white", "marginRight": "8px"}
                            }
                        }
                    },
                    {
                        "id": "send-button",
                        "component": {
                            "Button": {
                                "text": {"literalString": "Send Campaign"},
                                "onClick": {"action": f"send_campaign_{campaign.id}"},
                                "style": {"backgroundColor": "#10b981", "color": "white"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    return json.dumps(details_components)

def create_campaign_action_ui(message: str, action: str) -> str:
    """Create A2UI JSON for campaign action confirmation"""
    action_components = [
        {
            "beginRendering": {
                "surfaceId": "campaign-action",
                "root": "action-container",
                "styles": {"primaryColor": "#10b981", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "campaign-action",
                "components": [
                    {
                        "id": "action-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["action-icon", "action-message", "action-button"]
                                }
                            }
                        }
                    },
                    {
                        "id": "action-icon",
                        "component": {
                            "Icon": {
                                "name": "check_circle",
                                "style": {"fontSize": "48px", "color": "#10b981", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "action-message",
                        "component": {
                            "Text": {
                                "text": {"literalString": message},
                                "style": {"fontSize": "16px", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "action-button",
                        "component": {
                            "Button": {
                                "text": {"literalString": "View Campaigns"},
                                "onClick": {"action": "view_campaigns"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    return json.dumps(action_components)

def create_marketing_dashboard_ui(dashboard_data) -> str:
    """Create A2UI JSON for marketing dashboard"""
    dashboard_components = [
        {
            "beginRendering": {
                "surfaceId": "marketing-dashboard",
                "root": "dashboard-container",
                "styles": {"primaryColor": "#3b82f6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "marketing-dashboard",
                "components": [
                    {
                        "id": "dashboard-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["dashboard-header", "stats-row", "recent-campaigns"]
                                }
                            }
                        }
                    },
                    {
                        "id": "dashboard-header",
                        "component": {
                            "Text": {
                                "usageHint": "h1",
                                "text": {"literalString": "Marketing Dashboard"},
                                "style": {"marginBottom": "24px"}
                            }
                        }
                    },
                    {
                        "id": "stats-row",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["total-campaigns-card", "sent-campaigns-card", "draft-campaigns-card"]
                                }
                            }
                        }
                    },
                    {
                        "id": "total-campaigns-card",
                        "component": {
                            "Card": {
                                "child": "total-content",
                                "style": {"marginRight": "16px", "padding": "16px", "backgroundColor": "#3b82f6", "color": "white"}
                            }
                        }
                    },
                    {
                        "id": "total-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["total-number", "total-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "total-number",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": str(dashboard_data.get("total_campaigns", 0))},
                                "style": {"fontSize": "32px", "fontWeight": "bold"}
                            }
                        }
                    },
                    {
                        "id": "total-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Total Campaigns"},
                                "style": {"fontSize": "14px", "opacity": "0.9"}
                            }
                        }
                    },
                    {
                        "id": "sent-campaigns-card",
                        "component": {
                            "Card": {
                                "child": "sent-content",
                                "style": {"marginRight": "16px", "padding": "16px", "backgroundColor": "#10b981", "color": "white"}
                            }
                        }
                    },
                    {
                        "id": "sent-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["sent-number", "sent-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "sent-number",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": str(dashboard_data.get("sent_campaigns", 0))},
                                "style": {"fontSize": "32px", "fontWeight": "bold"}
                            }
                        }
                    },
                    {
                        "id": "sent-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Sent Campaigns"},
                                "style": {"fontSize": "14px", "opacity": "0.9"}
                            }
                        }
                    },
                    {
                        "id": "draft-campaigns-card",
                        "component": {
                            "Card": {
                                "child": "draft-content",
                                "style": {"padding": "16px", "backgroundColor": "#f59e0b", "color": "white"}
                            }
                        }
                    },
                    {
                        "id": "draft-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["draft-number", "draft-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "draft-number",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"literalString": str(dashboard_data.get("draft_campaigns", 0))},
                                "style": {"fontSize": "32px", "fontWeight": "bold"}
                            }
                        }
                    },
                    {
                        "id": "draft-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Draft Campaigns"},
                                "style": {"fontSize": "14px", "opacity": "0.9"}
                            }
                        }
                    },
                    {
                        "id": "recent-campaigns",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["recent-header", "recent-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "recent-header",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"literalString": "Recent Campaigns"},
                                "style": {"marginTop": "24px", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "recent-list",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["view-all-campaigns"]
                                }
                            }
                        }
                    },
                    {
                        "id": "view-all-campaigns",
                        "component": {
                            "Button": {
                                "text": {"literalString": "View All Campaigns"},
                                "onClick": {"action": "view_campaigns"},
                                "style": {"backgroundColor": "#3b82f6", "color": "white", "marginTop": "16px"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    return json.dumps(dashboard_components)

# WhatsApp Chat Analysis Endpoints for A2UI
@router.post("/whatsapp/analyze")
async def analyze_whatsapp_chat_a2ui(request: dict):
    """Analyze WhatsApp chat content and return A2UI JSON"""
    try:
        # Import WhatsApp analyzer
        from a2ui_integration.whatsapp_analyzer import whatsapp_analyzer
        
        # Get chat content from request
        chat_content = request.get("chat_content", "")
        filename = request.get("filename", "chat.txt")
        
        if not chat_content:
            error_ui = create_a2ui_error_components("No chat content provided")
            return {
                "success": False,
                "error": "No chat content provided",
                "a2ui_json": error_ui,
                "timestamp": datetime.now()
            }
        
        # Process the chat
        result = whatsapp_analyzer.process_chat_file(chat_content, filename)
        
        if result["status"] == "failed":
            error_ui = create_a2ui_error_components(result.get("error", "Analysis failed"))
            return {
                "success": False,
                "error": result.get("error", "Analysis failed"),
                "a2ui_json": error_ui,
                "timestamp": datetime.now()
            }
        
        # Generate A2UI JSON for WhatsApp analysis
        analysis_ui = create_whatsapp_analysis_ui(result.get("analysis", {}), result.get("summary", {}))
        
        return {
            "success": True,
            "analysis": result.get("analysis"),
            "summary": result.get("summary"),
            "a2ui_json": analysis_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing WhatsApp chat via A2UI: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/whatsapp/sample")
async def get_whatsapp_sample_analysis_a2ui():
    """Get sample WhatsApp analysis for A2UI demonstration"""
    try:
        # Import WhatsApp analyzer for sample data
        from a2ui_integration.whatsapp_analyzer import whatsapp_analyzer
        
        # Get sample analysis
        sample_data = whatsapp_analyzer.get_sample_analysis()
        
        # Generate A2UI JSON for sample analysis
        analysis_ui = create_whatsapp_analysis_ui(sample_data.get("analysis", {}), sample_data.get("summary", {}))
        
        return {
            "success": True,
            "analysis": sample_data.get("analysis"),
            "summary": sample_data.get("summary"),
            "a2ui_json": analysis_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting sample WhatsApp analysis via A2UI: {e}")
        error_ui = create_a2ui_error_components(str(e))
        return {
            "success": False,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

# Helper function for WhatsApp analysis A2UI components
def create_whatsapp_analysis_ui(analysis_data: dict, summary_data: dict) -> str:
    """Create A2UI JSON for WhatsApp chat analysis"""
    components = [
        {
            "beginRendering": {
                "surfaceId": "whatsapp-analysis",
                "root": "analysis-container",
                "styles": {"primaryColor": "#25D366", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "whatsapp-analysis",
                "components": [
                    {
                        "id": "analysis-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["analysis-header", "overview-card", "sentiment-card", "activity-card", "participants-card", "insights-card"]
                                }
                            }
                        }
                    },
                    {
                        "id": "analysis-header",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["header-icon", "header-title"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-icon",
                        "component": {
                            "Icon": {
                                "name": "chat_bubble",
                                "style": {"fontSize": "32px", "color": "#25D366", "marginRight": "12px"}
                            }
                        }
                    },
                    {
                        "id": "header-title",
                        "component": {
                            "Text": {
                                "usageHint": "h1",
                                "text": {"literalString": "WhatsApp Chat Analysis"},
                                "style": {"color": "#25D366"}
                            }
                        }
                    },
                    {
                        "id": "overview-card",
                        "component": {
                            "Card": {
                                "child": "overview-content",
                                "style": {"marginBottom": "16px", "padding": "16px", "backgroundColor": "#f0fdf4"}
                            }
                        }
                    },
                    {
                        "id": "overview-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["overview-title", "overview-stats"]
                                }
                            }
                        }
                    },
                    {
                        "id": "overview-title",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"literalString": "Chat Overview"},
                                "style": {"color": "#166534", "marginBottom": "12px"}
                            }
                        }
                    },
                    {
                        "id": "overview-stats",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["total-messages", "total-participants", "avg-messages"]
                                }
                            }
                        }
                    },
                    {
                        "id": "total-messages",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["messages-number", "messages-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "messages-number",
                        "component": {
                            "Text": {
                                "text": {"literalString": str(analysis_data.get("overview", {}).get("total_messages", 0))},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#166534"}
                            }
                        }
                    },
                    {
                        "id": "messages-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Total Messages"},
                                "style": {"fontSize": "12px", "color": "#166534"}
                            }
                        }
                    },
                    {
                        "id": "total-participants",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["participants-number", "participants-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "participants-number",
                        "component": {
                            "Text": {
                                "text": {"literalString": str(analysis_data.get("overview", {}).get("total_participants", 0))},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#166534"}
                            }
                        }
                    },
                    {
                        "id": "participants-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Participants"},
                                "style": {"fontSize": "12px", "color": "#166534"}
                            }
                        }
                    },
                    {
                        "id": "avg-messages",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["avg-number", "avg-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "avg-number",
                        "component": {
                            "Text": {
                                "text": {"literalString": str(analysis_data.get("overview", {}).get("avg_messages_per_day", 0))},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#166534"}
                            }
                        }
                    },
                    {
                        "id": "avg-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Avg/Day"},
                                "style": {"fontSize": "12px", "color": "#166534"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    return json.dumps(components)

# Kernel-based Plugin Management Endpoints
@router.post("/kernel/register-plugin")
async def register_kernel_plugin(plugin_data: dict):
    """Register a new plugin with the kernel"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        # Extract plugin information
        plugin_id = plugin_data.get("plugin_id")
        plugin_class = plugin_data.get("plugin_class")
        plugin_type = plugin_data.get("plugin_type", "external")
        
        if not plugin_id or not plugin_class:
            raise HTTPException(status_code=400, detail="plugin_id and plugin_class are required")
        
        # Register the plugin
        success = kernel.register_plugin(plugin_id, plugin_class, plugin_type)
        
        if success:
            return {
                "status": "success",
                "plugin_id": plugin_id,
                "message": f"Plugin {plugin_id} registered successfully",
                "timestamp": datetime.now()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to register plugin")
            
    except Exception as e:
        logger.error(f"Error registering kernel plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kernel/enable-plugin/{plugin_id}")
async def enable_kernel_plugin(plugin_id: str):
    """Enable a registered plugin"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        success = kernel.enable_plugin(plugin_id)
        
        if success:
            return {
                "status": "success",
                "plugin_id": plugin_id,
                "message": f"Plugin {plugin_id} enabled successfully",
                "timestamp": datetime.now()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found")
            
    except Exception as e:
        logger.error(f"Error enabling kernel plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kernel/disable-plugin/{plugin_id}")
async def disable_kernel_plugin(plugin_id: str):
    """Disable a plugin"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        success = kernel.disable_plugin(plugin_id)
        
        if success:
            return {
                "status": "success",
                "plugin_id": plugin_id,
                "message": f"Plugin {plugin_id} disabled successfully",
                "timestamp": datetime.now()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found")
            
    except Exception as e:
        logger.error(f"Error disabling kernel plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kernel/execute-capability")
async def execute_kernel_capability(request: dict):
    """Execute a plugin capability"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        capability_id = request.get("capability_id")
        params = request.get("params", {})
        
        if not capability_id:
            raise HTTPException(status_code=400, detail="capability_id is required")
        
        # Execute the capability
        result = await kernel.execute_capability(capability_id, params)
        
        return {
            "status": "success",
            "capability_id": capability_id,
            "result": result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error executing kernel capability: {e}")
        error_components = create_a2ui_error_components(str(e))
        error_ui = json.dumps(error_components)
        
        return {
            "status": "failed",
            "capability_id": capability_id,
            "error": str(e),
            "a2ui_json": error_ui,
            "timestamp": datetime.now()
        }

@router.get("/kernel/plugins")
async def get_kernel_plugins():
    """Get all registered plugins"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        plugins = kernel.get_all_plugins()
        
        return {
            "status": "success",
            "plugins": plugins,
            "count": len(plugins),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting kernel plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kernel/capabilities")
async def get_kernel_capabilities():
    """Get all available capabilities"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        capabilities = kernel.get_all_capabilities()
        
        return {
            "status": "success",
            "capabilities": capabilities,
            "count": len(capabilities),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting kernel capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kernel/search")
async def search_kernel_plugins(query: str):
    """Search for plugins and capabilities"""
    try:
        from a2ui_integration.core.kernel import Kernel
        kernel = Kernel()
        
        results = kernel.search(query)
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error searching kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kernel/dashboard")
async def get_kernel_dashboard():
    """Get kernel dashboard data with adjacency list operations"""
    try:
        from a2ui_integration.core.kernel import Kernel
        from a2ui_integration.core.types import PluginType
        
        kernel = Kernel()
        
        # Get all plugins
        all_plugins = await kernel.list_plugins()
        
        # Get dashboard data
        dashboard_data = {
            "plugins": [
                {
                    "id": plugin.id,
                    "name": plugin.name,
                    "description": plugin.description,
                    "type": plugin.type.value,
                    "version": plugin.version,
                    "author": plugin.author,
                    "enabled": plugin.enabled,
                    "capabilities": len(plugin.capabilities)
                }
                for plugin in all_plugins
            ],
            "stats": {
                "total_plugins": len(all_plugins),
                "enabled_plugins": len([p for p in all_plugins if p.enabled]),
                "by_type": {
                    plugin_type.value: len([p for p in all_plugins if p.type == plugin_type])
                    for plugin_type in PluginType
                }
            }
        }
        
        # Generate A2UI components for dashboard
        a2ui_components = create_kernel_dashboard_ui(dashboard_data)
        a2ui_json = json.dumps(a2ui_components)
        
        return {
            "status": "success",
            "dashboard": dashboard_data,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting kernel dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kernel/plugin-store")
async def get_kernel_plugin_store():
    """Get plugin store interface with adjacency list operations"""
    try:
        from a2ui_integration.core.kernel import Kernel
        
        kernel = Kernel()
        
        # Get all plugins (available for installation/enabling)
        all_plugins = await kernel.list_plugins()
        
        # Format plugins for store display
        store_plugins = [
            {
                "id": plugin.id,
                "name": plugin.name,
                "description": plugin.description,
                "type": plugin.type.value,
                "version": plugin.version,
                "author": plugin.author,
                "enabled": plugin.enabled,
                "capabilities": [
                    {
                        "id": cap.id,
                        "name": cap.name,
                        "description": cap.description,
                        "domain": cap.domain
                    }
                    for cap in plugin.capabilities
                ]
            }
            for plugin in all_plugins
        ]
        
        # Generate A2UI components for plugin store
        a2ui_components = create_plugin_store_ui(store_plugins)
        a2ui_json = json.dumps(a2ui_components)
        
        return {
            "status": "success",
            "plugins": store_plugins,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting kernel plugin store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Skill Store Interface Endpoints
@router.get("/skill-store/plugins")
async def get_skill_store_plugins():
    """Get all available plugins in the skill store"""
    try:
        from a2ui_integration.core.kernel import Kernel
        
        kernel = Kernel()
        
        # Get all plugins
        all_plugins = await kernel.list_plugins()
        
        # Format for skill store display
        skill_store_plugins = [
            {
                "plugin_id": plugin.id,
                "name": plugin.name,
                "description": plugin.description,
                "type": plugin.type.value,
                "version": plugin.version,
                "author": plugin.author,
                "enabled": plugin.enabled,
                "capabilities": [
                    {
                        "id": cap.id,
                        "name": cap.name,
                        "description": cap.description,
                        "domain": cap.domain
                    }
                    for cap in plugin.capabilities
                ],
                "requires_auth": plugin.requires_auth if hasattr(plugin, 'requires_auth') else False,
                "icon": plugin.icon if hasattr(plugin, 'icon') else "🔧",
                "documentation_url": plugin.documentation_url if hasattr(plugin, 'documentation_url') else None,
                "support_url": plugin.support_url if hasattr(plugin, 'support_url') else None
            }
            for plugin in all_plugins
        ]
        
        # Create A2UI components
        a2ui_components = create_skill_store_plugins_ui(skill_store_plugins)
        a2ui_json = json.dumps(a2ui_components)
        
        return {
            "status": "success",
            "plugins": skill_store_plugins,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting skill store plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skill-store/plugins/{plugin_id}")
async def get_skill_store_plugin_details(plugin_id: str):
    """Get detailed information about a specific plugin"""
    try:
        from a2ui_integration.core.kernel import Kernel
        
        kernel = Kernel()
        
        # Get all plugins and find the requested one
        all_plugins = await kernel.list_plugins()
        plugin = next((p for p in all_plugins if p.id == plugin_id), None)
        
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        # Format detailed plugin information
        plugin_details = {
            "plugin_id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
            "type": plugin.type.value,
            "version": plugin.version,
            "author": plugin.author,
            "enabled": plugin.enabled,
            "capabilities": [
                {
                    "id": cap.id,
                    "name": cap.name,
                    "description": cap.description,
                    "domain": cap.domain,
                    "side_effects": cap.side_effects
                }
                for cap in plugin.capabilities
            ],
            "requires_auth": plugin.requires_auth if hasattr(plugin, 'requires_auth') else False,
            "icon": plugin.icon if hasattr(plugin, 'icon') else "🔧",
            "documentation_url": plugin.documentation_url if hasattr(plugin, 'documentation_url') else None,
            "support_url": plugin.support_url if hasattr(plugin, 'support_url') else None,
            "privacy_policy_url": plugin.privacy_policy_url if hasattr(plugin, 'privacy_policy_url') else None,
            "settings": plugin.settings if hasattr(plugin, 'settings') else {},
            "last_updated": plugin.last_updated if hasattr(plugin, 'last_updated') else None
        }
        
        # Create A2UI components
        a2ui_components = create_plugin_details_ui(plugin_details)
        a2ui_json = json.dumps(a2ui_components)
        
        return {
            "status": "success",
            "plugin": plugin_details,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skill-store/plugins/{plugin_id}/enable")
async def enable_skill_store_plugin(plugin_id: str):
    """Enable a plugin"""
    try:
        from a2ui_integration.core.kernel import Kernel
        
        kernel = Kernel()
        
        success = await kernel.enable_plugin(plugin_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to enable plugin")
        
        return {
            "status": "success",
            "message": f"Plugin {plugin_id} enabled successfully",
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skill-store/plugins/{plugin_id}/disable")
async def disable_skill_store_plugin(plugin_id: str):
    """Disable a plugin"""
    try:
        from a2ui_integration.core.kernel import Kernel
        
        kernel = Kernel()
        
        success = await kernel.disable_plugin(plugin_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to disable plugin")
        
        return {
            "status": "success",
            "message": f"Plugin {plugin_id} disabled successfully",
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skill-store/search")
async def search_skill_store(query: str, domains: Optional[str] = None):
    """Search plugins and capabilities in the skill store"""
    try:
        from a2ui_integration.core.kernel import Kernel
        
        kernel = Kernel()
        
        # Parse domains if provided
        domain_list = domains.split(",") if domains else None
        
        # Search using kernel's search method
        search_results = await kernel.search(query, domain_list)
        
        # Create A2UI components for search results
        a2ui_components = create_search_results_ui(search_results, query)
        a2ui_json = json.dumps(a2ui_components)
        
        return {
            "status": "success",
            "query": query,
            "domains": domain_list,
            "results": search_results,
            "a2ui_json": a2ui_json,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error searching skill store: {e}")
        raise HTTPException(status_code=500, detail=str(e))