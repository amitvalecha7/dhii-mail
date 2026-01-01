# FastAPI Integration for A2UI Meeting Assistant
# Extends existing main.py with A2UI endpoints

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
from datetime import datetime

# Import existing modules
from main import app, get_db
from auth import get_auth, get_current_user
from a2ui_integration.agent.agent_updated_v2 import run_meeting_agent_async
from a2ui_integration.agent.prompt_builder import get_meeting_list_ui, get_booking_ui
from a2ui_integration.agent.meeting_tools_updated_v2 import (
    get_upcoming_meetings,
    get_available_time_slots,
    book_meeting,
    get_meeting_details,
    cancel_meeting,
)

logger = logging.getLogger(__name__)

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
@app.post("/api/a2ui/chat", response_model=A2UIResponse)
async def a2ui_chat(request: A2UIRequest, current_user: dict = Depends(get_current_user)):
    """Process A2UI chat request and return A2UI JSON components using existing backend"""
    try:
        # Use existing AI engine or meeting agent
        from a2ui_integration.agent.agent_updated_v2 import run_meeting_agent_async
        
        # Process the meeting request using existing agent
        agent_result = await run_meeting_agent_async(
            user_input=request.message,
            user_email=current_user.email
        )
        
        if agent_result.get("success"):
            # Create A2UI components from agent response
            a2ui_components = create_a2ui_meeting_components(
                agent_result.get("response", ""),
                current_user.email
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

@app.get("/api/a2ui/meetings")
async def get_a2ui_meetings(current_user: dict = Depends(get_current_user)):
    """Get meetings formatted as A2UI JSON"""
    try:
        # Get meetings from our existing system
        meetings = get_upcoming_meetings()
        
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

@app.post("/api/a2ui/book")
async def book_a2ui_meeting(request: MeetingBookingRequest, current_user: dict = Depends(get_current_user)):
    """Book a new meeting via A2UI"""
    try:
        # Book the meeting using our existing system
        meeting_data = book_meeting(
            title=request.title,
            date=request.date,
            time=request.time,
            duration_minutes=request.duration_minutes,
            participants=request.participants,
            description=request.description,
            meeting_type=request.meeting_type
        )
        
        # Generate success A2UI JSON
        success_ui = json.dumps([
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
        ])
        
        return {
            "success": True,
            "meeting_id": meeting_data["id"],
            "a2ui_json": success_ui,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error booking A2UI meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/a2ui/meetings/{meeting_id}")
async def get_a2ui_meeting_details(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed meeting information formatted as A2UI JSON"""
    try:
        # Get meeting details from our existing system
        meeting = get_meeting_details(meeting_id)
        
        if "error" in meeting:
            raise HTTPException(status_code=404, detail=meeting["error"])
        
        # Generate A2UI JSON for meeting details
        # This would be implemented in prompt_builder.py
        details_ui = json.dumps([
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
                        # Meeting details components would go here
                    ]
                }
            },
            {
                "dataModelUpdate": {
                    "surfaceId": "details",
                    "path": "/",
                    "contents": [
                        {"key": "meetingTitle", "valueString": meeting["title"]},
                        {"key": "datetime", "valueString": meeting["datetime"]},
                        {"key": "duration", "valueString": "30 minutes"},
                        {"key": "location", "valueString": "Google Meet"},
                        {"key": "description", "valueString": meeting.get("description", "")},
                        {"key": "meetingId", "valueString": meeting["id"]},
                        {"key": "meetingLink", "valueString": meeting["meetingLink"]}
                    ]
                }
            }
        ])
        
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
@app.websocket("/ws/a2ui/{user_email}")
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
                
                # Process the request
                a2ui_json = await process_meeting_request(message, session_id)
                
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

# Static file serving for A2UI client
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Serve A2UI client files
A2UI_CLIENT_DIR = "/root/dhii-mail/a2ui_integration/client"
if os.path.exists(A2UI_CLIENT_DIR):
    app.mount("/a2ui", StaticFiles(directory=A2UI_CLIENT_DIR, html=True), name="a2ui")

@app.get("/a2ui")
async def serve_a2ui_client():
    """Serve the A2UI client interface"""
    client_path = os.path.join(A2UI_CLIENT_DIR, "index.html")
    if os.path.exists(client_path):
        return FileResponse(client_path)
    else:
        raise HTTPException(status_code=404, detail="A2UI client not found")

# Health check endpoint for A2UI
@app.get("/api/a2ui/health")
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