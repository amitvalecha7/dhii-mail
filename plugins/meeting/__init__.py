
import json
import uuid
from datetime import datetime

# Simple in-memory storage for MVP
# In a real system, we'd use a database via kernel services
MEETINGS = []

def meeting_create(params):
    """
    Create a new meeting.
    Params: title, date, time, duration, participants, description
    """
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
        
        MEETINGS.append(new_meeting)
        
        return {
            "status": "success",
            "message": "Meeting created successfully",
            "meeting": new_meeting
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def meeting_update(params):
    """
    Update an existing meeting.
    Params: id, ... (fields to update)
    """
    try:
        meeting_id = params.get("id")
        if not meeting_id:
            return {"status": "error", "message": "Meeting ID required"}
            
        for meeting in MEETINGS:
            if meeting["id"] == meeting_id:
                # Update fields
                for key, value in params.items():
                    if key != "id":
                        meeting[key] = value
                
                meeting["updated_at"] = datetime.now().isoformat()
                
                return {
                    "status": "success",
                    "message": "Meeting updated successfully",
                    "meeting": meeting
                }
                
        return {"status": "error", "message": "Meeting not found"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def meeting_list(params):
    """
    List meetings.
    Params: filter (optional)
    """
    try:
        # Simple list for now, filtering can be added later
        return {
            "status": "success",
            "meetings": MEETINGS,
            "count": len(MEETINGS)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def register(kernel):
    """
    Register capabilities with the kernel.
    """
    kernel["log"]("Initializing Holo-Meet Plugin...")
    
    # Register capabilities
    kernel["register_capability"]("meeting_create", meeting_create)
    kernel["register_capability"]("meeting_update", meeting_update)
    kernel["register_capability"]("meeting_list", meeting_list)
    
    # Add some seed data for testing
    if not MEETINGS:
        MEETINGS.append({
            "id": "seed-1",
            "title": "Project Kickoff",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "10:00",
            "duration": 60,
            "participants": ["alice@dhii.ai", "bob@dhii.ai"],
            "description": "Initial kickoff meeting for Holo-Meet",
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    
    kernel["log"](f"Holo-Meet Plugin Registered with {len(MEETINGS)} initial meetings.")
