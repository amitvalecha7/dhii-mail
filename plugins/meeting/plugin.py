from datetime import datetime, timedelta
from typing import List, Dict, Any
from a2ui_integration.core.plugin import PluginBase
from a2ui_integration.core.types import A2UIComponent, A2UIOperation

class MeetingPlugin(PluginBase):
    def __init__(self, context):
        super().__init__(context)
        self.meetings = [
            {
                "id": "meet-001",
                "title": "Quantum Sync",
                "start": (datetime.now() + timedelta(hours=1)).isoformat(),
                "end": (datetime.now() + timedelta(hours=2)).isoformat(),
                "attendees": ["alice@dhii.ai", "bob@dhii.ai"],
                "status": "confirmed"
            },
            {
                "id": "meet-002",
                "title": "Deepmind Collaboration",
                "start": (datetime.now() + timedelta(days=1)).isoformat(),
                "end": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
                "attendees": ["charlie@google.com"],
                "status": "tentative"
            }
        ]

    def get_capabilities(self) -> List[str]:
        return ["meetings"]

    def render(self, view_id: str, context: Dict[str, Any] = None) -> List[A2UIOperation]:
        if view_id == "dashboard":
            return self._render_dashboard_widget()
        elif view_id == "meeting_list":
            return self._render_list_view()
        return []

    def _render_dashboard_widget(self) -> List[A2UIOperation]:
        next_meet = self.meetings[0]
        card = A2UIComponent(
            id="meeting-widget",
            type="Card",
            props={
                "variant": "glass",
                "title": "Next Neural Link",
                "subtitle": next_meet["title"],
                "accent": "blue"
            },
            children=[
                A2UIComponent(id="meet-time", type="Text", props={"content": f"Starts at {next_meet['start']}"}),
                A2UIComponent(id="join-btn", type="Button", props={"label": "Enter Huddle", "action": "join_meeting", "payload": {"id": next_meet["id"]}})
            ]
        )
        return [A2UIOperation(type="insert", parent_id="dashboard-grid", node=card)]

    def _render_list_view(self) -> List[A2UIOperation]:
        # Implementation of Grid View for full meeting list
        grid_items = []
        for meet in self.meetings:
            item = A2UIComponent(
                id=f"card-{meet['id']}",
                type="Card",
                props={"title": meet["title"], "variant": "glass-outlined"},
                children=[
                     A2UIComponent(id=f"desc-{meet['id']}", type="Text", props={"content": f"{meet['start']} | {len(meet['attendees'])} Attendees"})
                ]
            )
            grid_items.append(item)
            
        return [
            A2UIOperation(
                type="insert", 
                parent_id="main-content", 
                node=A2UIComponent(id="meeting-grid", type="Grid", props={"columns": 3}, children=grid_items)
            )
        ]
