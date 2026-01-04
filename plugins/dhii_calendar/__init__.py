import json
import datetime
import uuid

# Simple in-memory store for MVP (since we don't have a DB layer for plugins yet)
# In a real implementation, this would connect to a Google Calendar/Outlook API or local DB
_events_store = []

def register(kernel):
    kernel["log"]("Dhii-Calendar plugin loading...")

    async def fetch_events(params):
        kernel["log"]("Dhii-Calendar: Fetching events...")
        
        # Default to today if not provided
        today = datetime.date.today().isoformat()
        start_date = params.get("start_date", today)
        # Default to 7 days from now
        next_week = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        end_date = params.get("end_date", next_week)
        
        # Filter events (simple string comparison for MVP ISO dates)
        filtered_events = [
            e for e in _events_store 
            if e["start_time"] >= start_date and e["end_time"] <= end_date
        ]
        
        # Sort by start time
        filtered_events.sort(key=lambda x: x["start_time"])
        
        items = []
        for event in filtered_events:
            items.append({
                "id": event["id"],
                "title": event["title"],
                "subtitle": f"{event['start_time']} - {event['end_time']}",
                "action": {
                    "type": "view_details", # Placeholder for detail view
                    "params": {"event_id": event["id"]}
                }
            })
            
        if not items:
             items.append({"type": "text", "content": "No upcoming events."})
        
        return {
            "type": "card",
            "id": "calendar-view",
            "title": "Upcoming Schedule",
            "children": [
                {
                    "type": "list",
                    "items": items
                },
                {
                    "type": "button",
                    "label": "New Event",
                    "action": {
                        "type": "form",
                        "form_id": "create_event_form"
                    }
                }
            ]
        }

    async def create_event(params):
        kernel["log"](f"Dhii-Calendar: Creating event '{params.get('title')}'...")
        
        title = params.get("title")
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        description = params.get("description", "")
        
        if not title or not start_time or not end_time:
             return {"type": "card", "title": "Error", "children": [{"type": "text", "content": "Missing required fields."}]}
             
        new_event = {
            "id": str(uuid.uuid4()),
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description
        }
        
        _events_store.append(new_event)
        
        return {
            "type": "card",
            "title": "Event Created",
            "children": [
                {"type": "text", "content": f"Successfully scheduled: {title}"},
                {"type": "text", "content": f"Time: {start_time} to {end_time}"}
            ]
        }

    kernel["register_capability"]("fetch_events", fetch_events)
    kernel["register_capability"]("create_event", create_event)
    kernel["log"]("Dhii-Calendar: Capabilities registered.")
