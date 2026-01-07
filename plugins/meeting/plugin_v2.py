"""
Holo-Meet Plugin for dhii Mail - Framework 2.0
Next-gen meeting management with LiquidGlass UI
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from a2ui_integration.core.plugins import BasePlugin
from a2ui_integration.core.types import PluginType, Capability, PluginStatus
from a2ui_integration.core.shared_services import get_shared_services

logger = logging.getLogger(__name__)

class MeetingPlugin(BasePlugin):
    """Holo-Meet Plugin for comprehensive meeting management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            plugin_id="meeting",
            name="Holo-Meet",
            version="2.0.0",
            description="Next-gen meeting management with LiquidGlass UI",
            plugin_type=PluginType.CUSTOM
        )
        self.config = config or {}
        self.meetings = []
        self.shared_services = get_shared_services()
        self._seed_data()
    
    def _seed_data(self):
        """Seed initial meeting data"""
        self.meetings = [
            {
                "id": "meet-001",
                "title": "Quantum Sync",
                "start": (datetime.now() + timedelta(hours=1)).isoformat(),
                "end": (datetime.now() + timedelta(hours=2)).isoformat(),
                "attendees": ["alice@dhii.ai", "bob@dhii.ai"],
                "status": "confirmed",
                "description": "Synchronize quantum systems across neural networks",
                "location": "Virtual - Neural Link",
                "meeting_type": "video",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "meet-002",
                "title": "Deepmind Collaboration",
                "start": (datetime.now() + timedelta(days=1)).isoformat(),
                "end": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
                "attendees": ["charlie@google.com", "diana@dhii.ai"],
                "status": "tentative",
                "description": "Collaborative AI research and development planning",
                "location": "Google Meet",
                "meeting_type": "video",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
    
    def _register_capabilities(self):
        """Register meeting-related capabilities"""
        capabilities = [
            # Meeting management capabilities
            Capability(
                id="meeting.create_meeting",
                domain="meeting",
                name="Create Meeting",
                description="Create a new meeting",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "minLength": 1},
                        "description": {"type": "string"},
                        "start_time": {"type": "string", "format": "date-time"},
                        "end_time": {"type": "string", "format": "date-time"},
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "location": {"type": "string"},
                        "meeting_type": {"type": "string", "enum": ["video", "audio", "in_person"]}
                    },
                    "required": ["title", "start_time", "end_time"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "meeting_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                },
                side_effects=["write"],
                requires_auth=True
            ),
            
            Capability(
                id="meeting.update_meeting",
                domain="meeting",
                name="Update Meeting",
                description="Update an existing meeting",
                input_schema={
                    "type": "object",
                    "properties": {
                        "meeting_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "start_time": {"type": "string", "format": "date-time"},
                        "end_time": {"type": "string", "format": "date-time"},
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "location": {"type": "string"},
                        "meeting_type": {"type": "string", "enum": ["video", "audio", "in_person"]}
                    },
                    "required": ["meeting_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "message": {"type": "string"}
                    }
                },
                side_effects=["write"],
                requires_auth=True
            ),
            
            Capability(
                id="meeting.get_meeting",
                domain="meeting",
                name="Get Meeting",
                description="Get meeting details",
                input_schema={
                    "type": "object",
                    "properties": {
                        "meeting_id": {"type": "string"}
                    },
                    "required": ["meeting_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "meeting": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "start_time": {"type": "string", "format": "date-time"},
                                "end_time": {"type": "string", "format": "date-time"},
                                "attendees": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "location": {"type": "string"},
                                "meeting_type": {"type": "string"},
                                "status": {"type": "string"},
                                "created_at": {"type": "string", "format": "date-time"},
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                },
                side_effects=["read"],
                requires_auth=True
            ),
            
            Capability(
                id="meeting.list_meetings",
                domain="meeting",
                name="List Meetings",
                description="List meetings with filtering options",
                input_schema={
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "format": "date"},
                        "end_date": {"type": "string", "format": "date"},
                        "status": {"type": "string", "enum": ["scheduled", "in_progress", "completed", "cancelled"]},
                        "meeting_type": {"type": "string", "enum": ["video", "audio", "in_person"]},
                        "limit": {"type": "integer", "default": 50},
                        "offset": {"type": "integer", "default": 0}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "meetings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "start_time": {"type": "string", "format": "date-time"},
                                    "end_time": {"type": "string", "format": "date-time"},
                                    "status": {"type": "string"},
                                    "meeting_type": {"type": "string"},
                                    "attendee_count": {"type": "integer"}
                                }
                            }
                        },
                        "total": {"type": "integer"}
                    }
                },
                side_effects=["read"],
                requires_auth=True
            ),
            
            Capability(
                id="meeting.delete_meeting",
                domain="meeting",
                name="Delete Meeting",
                description="Delete a meeting",
                input_schema={
                    "type": "object",
                    "properties": {
                        "meeting_id": {"type": "string"}
                    },
                    "required": ["meeting_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "message": {"type": "string"}
                    }
                },
                side_effects=["delete"],
                requires_auth=True
            ),
            
            # UI capabilities
            Capability(
                id="meeting.render_meeting_list",
                domain="meeting",
                name="Render Meeting List UI",
                description="Render the meeting list UI component",
                input_schema={
                    "type": "object",
                    "properties": {
                        "meetings": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "filters": {"type": "object"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "html": {"type": "string"},
                        "css": {"type": "string"},
                        "javascript": {"type": "string"}
                    }
                },
                side_effects=["read"],
                requires_auth=False,
                timeout_seconds=10
            ),
            
            Capability(
                id="meeting.render_meeting_detail",
                domain="meeting",
                name="Render Meeting Detail UI",
                description="Render the meeting detail UI component",
                input_schema={
                    "type": "object",
                    "properties": {
                        "meeting": {"type": "object"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "html": {"type": "string"},
                        "css": {"type": "string"},
                        "javascript": {"type": "string"}
                    }
                },
                side_effects=["read"],
                requires_auth=False,
                timeout_seconds=10
            ),
            
            Capability(
                id="meeting.render_meeting_book",
                domain="meeting",
                name="Render Meeting Booking UI",
                description="Render the meeting booking UI component",
                input_schema={
                    "type": "object",
                    "properties": {
                        "available_slots": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "html": {"type": "string"},
                        "css": {"type": "string"},
                        "javascript": {"type": "string"}
                    }
                },
                side_effects=["read"],
                requires_auth=False,
                timeout_seconds=10
            )
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    async def _initialize_plugin(self):
        """Initialize the meeting plugin"""
        logger.info("Holo-Meet plugin initialized")
    
    async def _shutdown_plugin(self):
        """Shutdown the meeting plugin"""
        logger.info("Holo-Meet plugin shut down")
    
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific meeting capability"""
        if capability_id.startswith("meeting."):
            return await self._execute_meeting_capability(capability_id, params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _execute_meeting_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute meeting-related capabilities"""
        if capability_id == "meeting.create_meeting":
            return await self._create_meeting(params)
        elif capability_id == "meeting.update_meeting":
            return await self._update_meeting(params)
        elif capability_id == "meeting.get_meeting":
            return await self._get_meeting(params)
        elif capability_id == "meeting.list_meetings":
            return await self._list_meetings(params)
        elif capability_id == "meeting.delete_meeting":
            return await self._delete_meeting(params)
        elif capability_id == "meeting.render_meeting_list":
            return await self._render_meeting_list(params)
        elif capability_id == "meeting.render_meeting_detail":
            return await self._render_meeting_detail(params)
        elif capability_id == "meeting.render_meeting_book":
            return await self._render_meeting_book(params)
        else:
            raise ValueError(f"Unknown meeting capability: {capability_id}")
    
    async def _create_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new meeting"""
        meeting_id = f"meet_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        # Set default values
        params.setdefault("attendees", [])
        params.setdefault("location", "Virtual")
        params.setdefault("meeting_type", "video")
        params.setdefault("status", "scheduled")
        
        new_meeting = {
            "id": meeting_id,
            "title": params["title"],
            "description": params.get("description", ""),
            "start": params["start_time"],
            "end": params["end_time"],
            "attendees": params["attendees"],
            "location": params["location"],
            "meeting_type": params["meeting_type"],
            "status": params["status"],
            "created_at": now,
            "updated_at": now
        }
        
        self.meetings.append(new_meeting)
        
        logger.info(f"Meeting created successfully: {meeting_id}")
        return {"meeting_id": meeting_id, "status": "success"}
    
    async def _update_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing meeting"""
        meeting_id = params["meeting_id"]
        now = datetime.now().isoformat()
        
        for meeting in self.meetings:
            if meeting["id"] == meeting_id:
                # Update fields
                for key, value in params.items():
                    if key != "meeting_id":
                        if key == "start_time":
                            meeting["start"] = value
                        elif key == "end_time":
                            meeting["end"] = value
                        elif key == "attendees":
                            meeting["attendees"] = value
                        else:
                            meeting[key] = value
                
                meeting["updated_at"] = now
                
                logger.info(f"Meeting updated successfully: {meeting_id}")
                return {"success": True, "message": "Meeting updated successfully"}
        
        return {"success": False, "message": "Meeting not found"}
    
    async def _get_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get meeting details"""
        meeting_id = params["meeting_id"]
        
        for meeting in self.meetings:
            if meeting["id"] == meeting_id:
                # Convert to the expected format
                meeting_data = meeting.copy()
                meeting_data["start_time"] = meeting_data["start"]
                meeting_data["end_time"] = meeting_data["end"]
                meeting_data.pop("start", None)
                meeting_data.pop("end", None)
                
                return {"meeting": meeting_data}
        
        return {"meeting": None}
    
    async def _list_meetings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List meetings with filtering"""
        filtered_meetings = self.meetings.copy()
        
        # Apply filters
        if "start_date" in params:
            start_date = datetime.fromisoformat(params["start_date"])
            filtered_meetings = [
                m for m in filtered_meetings 
                if datetime.fromisoformat(m["start"]) >= start_date
            ]
        
        if "end_date" in params:
            end_date = datetime.fromisoformat(params["end_date"]) + timedelta(days=1)
            filtered_meetings = [
                m for m in filtered_meetings 
                if datetime.fromisoformat(m["start"]) <= end_date
            ]
        
        if "status" in params:
            filtered_meetings = [
                m for m in filtered_meetings 
                if m["status"] == params["status"]
            ]
        
        if "meeting_type" in params:
            filtered_meetings = [
                m for m in filtered_meetings 
                if m["meeting_type"] == params["meeting_type"]
            ]
        
        # Format meetings for output
        formatted_meetings = []
        for meeting in filtered_meetings:
            formatted_meeting = {
                "id": meeting["id"],
                "title": meeting["title"],
                "start_time": meeting["start"],
                "end_time": meeting["end"],
                "status": meeting["status"],
                "meeting_type": meeting["meeting_type"],
                "attendee_count": len(meeting.get("attendees", []))
            }
            formatted_meetings.append(formatted_meeting)
        
        # Apply pagination
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        paginated_meetings = formatted_meetings[offset:offset + limit]
        
        return {
            "meetings": paginated_meetings,
            "total": len(formatted_meetings)
        }
    
    async def _delete_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a meeting"""
        meeting_id = params["meeting_id"]
        
        for i, meeting in enumerate(self.meetings):
            if meeting["id"] == meeting_id:
                self.meetings.pop(i)
                logger.info(f"Meeting deleted successfully: {meeting_id}")
                return {"success": True, "message": "Meeting deleted successfully"}
        
        return {"success": False, "message": "Meeting not found"}
    
    async def _render_meeting_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render meeting list UI"""
        meetings = params.get("meetings", self.meetings)
        
        html_content = """
        <div class="meeting-list">
            <h2>Upcoming Meetings</h2>
            <div class="meeting-grid">
        """
        
        for meeting in meetings:
            start_time = datetime.fromisoformat(meeting["start"])
            end_time = datetime.fromisoformat(meeting["end"])
            duration = int((end_time - start_time).total_seconds() / 60)
            
            attendees = meeting.get("attendees", [])
            attendee_text = ", ".join(attendees[:2])
            if len(attendees) > 2:
                attendee_text += f" +{len(attendees)-2} more"
            
            html_content += f"""
                <div class="meeting-card glass" data-meeting-id="{meeting['id']}">
                    <h3>{meeting['title']}</h3>
                    <div class="meeting-info">
                        <p><span class="icon">📅</span> {start_time.strftime('%Y-%m-%d')}</p>
                        <p><span class="icon">🕐</span> {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} ({duration} min)</p>
                        <p><span class="icon">👥</span> {attendee_text}</p>
                        <p><span class="icon">📍</span> {meeting.get('location', 'Virtual')}</p>
                        <p><span class="icon">📊</span> Status: {meeting['status']}</p>
                    </div>
                    <div class="meeting-actions">
                        <button class="btn btn-primary" onclick="viewMeeting('{meeting['id']}')">View Details</button>
                        <button class="btn btn-secondary" onclick="joinMeeting('{meeting['id']}')">Join Meeting</button>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
        </div>
        """
        
        css_content = """
        .meeting-list {
            padding: 20px;
            font-family: 'Inter', sans-serif;
        }
        
        .meeting-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .meeting-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .meeting-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .meeting-card h3 {
            margin-top: 0;
            color: #333;
            font-size: 1.2em;
        }
        
        .meeting-info p {
            margin: 8px 0;
            color: #666;
            font-size: 0.9em;
        }
        
        .meeting-info .icon {
            margin-right: 8px;
        }
        
        .meeting-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s ease;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        """
        
        javascript_content = """
        function viewMeeting(meetingId) {
            console.log('Viewing meeting:', meetingId);
            // Navigate to meeting detail view
            window.location.href = `/meetings/${meetingId}`;
        }
        
        function joinMeeting(meetingId) {
            console.log('Joining meeting:', meetingId);
            // Open meeting in new tab/window
            window.open(`/meetings/${meetingId}/join`, '_blank');
        }
        """
        
        return {
            "html": html_content,
            "css": css_content,
            "javascript": javascript_content
        }
    
    async def _render_meeting_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render meeting detail UI"""
        meeting = params.get("meeting")
        if not meeting:
            return {"html": "<div>Meeting not found</div>", "css": "", "javascript": ""}
        
        start_time = datetime.fromisoformat(meeting["start"])
        end_time = datetime.fromisoformat(meeting["end"])
        duration = int((end_time - start_time).total_seconds() / 60)
        
        attendees = meeting.get("attendees", [])
        attendee_list = ""
        for attendee in attendees:
            attendee_list += f'<li>{attendee}</li>'
        
        html_content = f"""
        <div class="meeting-detail">
            <div class="meeting-header">
                <h1>{meeting['title']}</h1>
                <span class="status-badge status-{meeting['status']}">{meeting['status']}</span>
            </div>
            
            <div class="meeting-info">
                <div class="info-section">
                    <h3>Meeting Details</h3>
                    <p><strong>Date:</strong> {start_time.strftime('%A, %B %d, %Y')}</p>
                    <p><strong>Time:</strong> {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}</p>
                    <p><strong>Duration:</strong> {duration} minutes</p>
                    <p><strong>Location:</strong> {meeting.get('location', 'Virtual')}</p>
                    <p><strong>Type:</strong> {meeting['meeting_type']}</p>
                </div>
                
                <div class="info-section">
                    <h3>Description</h3>
                    <p>{meeting.get('description', 'No description provided.')}</p>
                </div>
                
                <div class="info-section">
                    <h3>Attendees ({len(attendees)})</h3>
                    <ul class="attendee-list">
                        {attendee_list}
                    </ul>
                </div>
            </div>
            
            <div class="meeting-actions">
                <button class="btn btn-primary" onclick="joinMeeting('{meeting['id']}')">Join Meeting</button>
                <button class="btn btn-secondary" onclick="editMeeting('{meeting['id']}')">Edit Meeting</button>
                <button class="btn btn-danger" onclick="cancelMeeting('{meeting['id']}')">Cancel Meeting</button>
            </div>
        </div>
        """
        
        css_content = """
        .meeting-detail {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Inter', sans-serif;
        }
        
        .meeting-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .meeting-header h1 {
            margin: 0;
            color: #333;
            font-size: 2em;
        }
        
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-scheduled {
            background: #28a745;
            color: white;
        }
        
        .status-confirmed {
            background: #007bff;
            color: white;
        }
        
        .status-tentative {
            background: #ffc107;
            color: #333;
        }
        
        .status-cancelled {
            background: #dc3545;
            color: white;
        }
        
        .meeting-info {
            margin-bottom: 30px;
        }
        
        .info-section {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .info-section h3 {
            margin-top: 0;
            margin-bottom: 15px;
            color: #495057;
            font-size: 1.2em;
        }
        
        .info-section p {
            margin: 8px 0;
            color: #666;
            line-height: 1.5;
        }
        
        .attendee-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .attendee-list li {
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
            color: #495057;
        }
        
        .attendee-list li:last-child {
            border-bottom: none;
        }
        
        .meeting-actions {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        """
        
        javascript_content = """
        function joinMeeting(meetingId) {
            console.log('Joining meeting:', meetingId);
            window.open(`/meetings/${meetingId}/join`, '_blank');
        }
        
        function editMeeting(meetingId) {
            console.log('Editing meeting:', meetingId);
            window.location.href = `/meetings/${meetingId}/edit`;
        }
        
        function cancelMeeting(meetingId) {
            if (confirm('Are you sure you want to cancel this meeting?')) {
                console.log('Cancelling meeting:', meetingId);
                // Call API to cancel meeting
                fetch(`/api/meetings/${meetingId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/meetings';
                    } else {
                        alert('Failed to cancel meeting: ' + data.message);
                    }
                });
            }
        }
        """
        
        return {
            "html": html_content,
            "css": css_content,
            "javascript": javascript_content
        }
    
    async def _render_meeting_book(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render meeting booking UI"""
        available_slots = params.get("available_slots", [])
        
        html_content = """
        <div class="meeting-book">
            <h1>Schedule a Meeting</h1>
            <form id="meeting-form">
                <div class="form-group">
                    <label for="title">Meeting Title</label>
                    <input type="text" id="title" name="title" required>
                </div>
                
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" rows="3"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="start_time">Start Time</label>
                    <input type="datetime-local" id="start_time" name="start_time" required>
                </div>
                
                <div class="form-group">
                    <label for="end_time">End Time</label>
                    <input type="datetime-local" id="end_time" name="end_time" required>
                </div>
                
                <div class="form-group">
                    <label for="attendees">Attendees (comma-separated emails)</label>
                    <input type="text" id="attendees" name="attendees" placeholder="alice@example.com, bob@example.com">
                </div>
                
                <div class="form-group">
                    <label for="location">Location</label>
                    <input type="text" id="location" name="location" placeholder="Virtual meeting link or physical location">
                </div>
                
                <div class="form-group">
                    <label for="meeting_type">Meeting Type</label>
                    <select id="meeting_type" name="meeting_type">
                        <option value="video">Video Call</option>
                        <option value="audio">Audio Call</option>
                        <option value="in_person">In Person</option>
                    </select>
                </div>
                
                <button type="submit" class="btn btn-primary">Schedule Meeting</button>
            </form>
        </div>
        """
        
        css_content = """
        .meeting-book {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Inter', sans-serif;
        }
        
        .meeting-book h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        
        #meeting-form {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #495057;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.2s ease;
        }
        
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #007bff;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        """
        
        javascript_content = """
        document.getElementById('meeting-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const meetingData = {};
            
            // Convert form data to object
            for (let [key, value] of formData.entries()) {
                if (key === 'attendees') {
                    // Split attendees by comma and trim whitespace
                    meetingData[key] = value.split(',').map(email => email.trim()).filter(email => email);
                } else {
                    meetingData[key] = value;
                }
            }
            
            console.log('Creating meeting:', meetingData);
            
            // Call API to create meeting
            fetch('/api/meetings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(meetingData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Meeting scheduled successfully!');
                    window.location.href = '/meetings';
                } else {
                    alert('Failed to schedule meeting: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while scheduling the meeting.');
            });
        });
        """
        
        return {
            "html": html_content,
            "css": css_content,
            "javascript": javascript_content
        }

# Framework 2.0 registration function
def register(kernel_api: Dict[str, Any]) -> MeetingPlugin:
    """Register the Holo-Meet plugin with Framework 2.0"""
    plugin = MeetingPlugin()
    plugin.initialize(kernel_api)
    return plugin