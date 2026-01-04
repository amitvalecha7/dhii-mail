# WhatsApp Bridge Plugin
# Simulates connection to WhatsApp API

# Mock Data Store
_THREADS = [
    {
        "id": "1",
        "name": "Alice",
        "last_message": "Hey, are we still on for lunch?",
        "timestamp": "10:30 AM",
        "unread": 1
    },
    {
        "id": "2",
        "name": "Bob",
        "last_message": "Project update attached.",
        "timestamp": "Yesterday",
        "unread": 0
    }
]

def register(kernel):
    kernel["log"]("WhatsApp Bridge loading...")

    def get_threads(params):
        """
        Fetches recent chat threads.
        Returns an A2UI List Card.
        """
        items = []
        for t in _THREADS:
            items.append({
                "id": t["id"],
                "title": t["name"],
                "subtitle": f"{t['last_message']} | {t['timestamp']}",
                "action": {
                    "type": "run_capability",
                    "capability_id": "send_message", # For now, clicking just prepares to reply
                    "params": {"to": t["name"], "message": ""}
                }
            })
        
        return {
            "type": "card",
            "id": "whatsapp-threads",
            "title": "WhatsApp Chats",
            "children": [
                {
                    "type": "list",
                    "items": items
                }
            ]
        }

    def send_message(params):
        """
        Sends a message.
        """
        to = params.get("to")
        message = params.get("message")
        
        if not to or not message:
             return {
                "type": "card",
                "title": "Error",
                "children": [{"type": "text", "content": "Missing 'to' or 'message'."}]
            }

        # Simulate sending
        # In a real app, this would call the WhatsApp API
        kernel["log"](f"WhatsApp: Sending message to {to}")
        
        return {
            "type": "card",
            "title": "Message Sent",
            "children": [
                {
                    "type": "text",
                    "content": f"Sent to {to}: {message}"
                }
            ]
        }

    kernel["register_capability"]("get_threads", get_threads)
    kernel["register_capability"]("send_message", send_message)
