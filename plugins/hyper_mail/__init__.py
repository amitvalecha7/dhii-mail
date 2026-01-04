def register(kernel):
    kernel["log"]("Hyper-Mail plugin loading...")
    
    # Define the capability handler
    async def fetch_inbox(params):
        kernel["log"]("Hyper-Mail: Fetching inbox...")
        # Return a mock A2UI structure
        return {
            "type": "card",
            "id": "inbox-card",
            "title": "Inbox",
            "children": [
                {
                    "type": "list",
                    "items": [
                        {"id": "1", "title": "Welcome to Dhii Mail", "subtitle": "Get started..."},
                        {"id": "2", "title": "Meeting Reminder", "subtitle": "10:00 AM..."},
                        {"id": "3", "title": "Project Update", "subtitle": "Phase 1 complete..."}
                    ]
                }
            ]
        }

    # Register the capability
    kernel["register_capability"]("fetch_inbox", fetch_inbox)
    kernel["log"]("Hyper-Mail: fetch_inbox capability registered.")
