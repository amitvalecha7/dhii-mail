
import json
import uuid
from datetime import datetime

class MeetingPlugin:
    """
    Holo-Meet Plugin Implementation.
    Manages meeting data and provides LiquidGlass UI schemas.
    """
    
    def __init__(self):
        self.meetings = []
        self._seed_data()

    def _seed_data(self):
        self.meetings.append({
            "id": "seed-1",
            "title": "Quarterly Review",
            "date": "2024-02-15",
            "time": "14:00",
            "duration": 90,
            "participants": ["ceo@dhii.ai", "cto@dhii.ai"],
            "description": "Review Q1 performance and set Q2 goals.",
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })

    def create(self, params):
        """Create a new meeting."""
        try:
            meeting_id = str(uuid.uuid4())
            new_meeting = {
                "id": meeting_id,
                "title": params.get("title", "Untitled Meeting"),
                "date": params.get("date"),
                "time": params.get("time"),
                "duration": params.get("duration", 60),
                "participants": params.get("participants", []),
                "description": params.get("description", ""),
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.meetings.append(new_meeting)
            return {"status": "success", "message": "Meeting created successfully", "meeting": new_meeting}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update(self, params):
        """Update an existing meeting."""
        try:
            meeting_id = params.get("id")
            if not meeting_id:
                return {"status": "error", "message": "Meeting ID required"}
            
            for meeting in self.meetings:
                if meeting["id"] == meeting_id:
                    for key, value in params.items():
                        if key != "id":
                            meeting[key] = value
                    meeting["updated_at"] = datetime.now().isoformat()
                    return {"status": "success", "message": "Meeting updated successfully", "meeting": meeting}
            return {"status": "error", "message": "Meeting not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_meetings(self, params):
        """List meetings with optional filtering."""
        try:
            # TODO: Implement filtering logic based on params
            return {"status": "success", "meetings": self.meetings, "count": len(self.meetings)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # --- LiquidGlass UI Renderers ---

    def render_list_view(self, params=None):
        """Generate LiquidGlass Grid View for Meeting List."""
        # This returns the pure data/schema for the grid
        # The orchestrator wraps this in the AppShell/Layout
        
        cards = []
        for meeting in self.meetings:
            participants = meeting.get("participants", [])
            participant_text = ", ".join(participants[:2])
            if len(participants) > 2:
                participant_text += f" +{len(participants)-2} more"
            
            card_content = (
                f"📅 {meeting.get('date', '')} at {meeting.get('time', '')}\n"
                f"⏱️ {meeting.get('duration', '')} mins\n"
                f"👥 {participant_text}"
            )
            
            cards.append({
                "component": {
                    "Card": {
                        "title": {"literalString": meeting.get("title", "Untitled")},
                        "content": {"literalString": card_content},
                        "variant": "glass",
                        "status": meeting.get("status", "scheduled"),
                        "actions": [
                            {"label": "Details", "action": "view_meeting", "params": {"id": meeting.get("id")}},
                            {"label": "Join", "action": "join_meeting", "params": {"id": meeting.get("id")}}
                        ]
                    }
                }
            })
            
        return {
            "type": "Grid",
            "columns": 3,
            "gap": "medium",
            "title": "Upcoming Meetings",
            "components": cards
        }

    def render_detail_view(self, params):
        """Generate LiquidGlass Card for Meeting Detail."""
        meeting_id = params.get("id")
        meeting = next((m for m in self.meetings if m["id"] == meeting_id), None)
        
        if not meeting:
            return {"error": "Meeting not found"}
            
        return {
            "type": "Card",
            "title": meeting.get("title"),
            "content": meeting.get("description"),
            "variant": "glass",
            "status": meeting.get("status"),
            "expanded": True, # Detail view is expanded
            "actions": [
                {"label": "Edit", "action": "edit_meeting", "params": {"id": meeting_id}},
                {"label": "Cancel", "action": "cancel_meeting", "params": {"id": meeting_id}}
            ]
        }

# Singleton Instance
plugin_instance = MeetingPlugin()

def register(kernel):
    """
    Register capabilities with the kernel.
    """
    kernel["log"]("Initializing Holo-Meet Plugin (Class-based)...")
    
    # Core Data Capabilities
    kernel["register_capability"]("meeting_create", plugin_instance.create)
    kernel["register_capability"]("meeting_update", plugin_instance.update)
    kernel["register_capability"]("meeting_list", plugin_instance.list_meetings)
    
    # UI Capabilities (LiquidGlass)
    kernel["register_capability"]("render_meeting_list", plugin_instance.render_list_view)
    kernel["register_capability"]("render_meeting_detail", plugin_instance.render_detail_view)
