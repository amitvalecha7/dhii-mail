# Teams Bridge Plugin
# Simulates connection to Microsoft Teams Graph API

# Mock Data Store
_CHANNELS = [
    {
        "id": "general",
        "name": "General",
        "team": "Engineering",
        "last_activity": "Standup at 10:00",
        "unread": 2
    },
    {
        "id": "random",
        "name": "Random",
        "team": "Engineering",
        "last_activity": "Lunch plans?",
        "unread": 0
    }
]

def register(kernel):
    kernel["log"]("Teams Bridge loading...")

    def get_channels(params):
        """
        Fetches Teams channels.
        Returns an A2UI List Card.
        """
        items = []
        for c in _CHANNELS:
            items.append({
                "id": c["id"],
                "title": f"#{c['name']}",
                "subtitle": f"{c['team']} | {c['last_activity']}",
                "action": {
                    "type": "run_capability",
                    "capability_id": "post_message",
                    "params": {"channel_id": c["id"], "message": ""}
                }
            })
        
        return {
            "type": "card",
            "id": "teams-channels",
            "title": "Microsoft Teams",
            "children": [
                {
                    "type": "list",
                    "items": items
                }
            ]
        }

    def post_message(params):
        """
        Posts a message to a channel.
        """
        channel_id = params.get("channel_id")
        message = params.get("message")
        
        if not channel_id or not message:
             return {
                "type": "card",
                "title": "Error",
                "children": [{"type": "text", "content": "Missing 'channel_id' or 'message'."}]
            }

        # Simulate sending
        kernel["log"](f"Teams: Posting to {channel_id}: {message}")
        
        return {
            "type": "card",
            "title": "Message Posted",
            "children": [
                {
                    "type": "text",
                    "content": f"Posted to #{channel_id}"
                }
            ]
        }

    kernel["register_capability"]("get_channels", get_channels)
    kernel["register_capability"]("post_message", post_message)
