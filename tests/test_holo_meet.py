import pytest
from plugins.meeting.plugin import MeetingPlugin
from a2ui_integration.core.types import A2UIOperation

class MockContext:
    pass

def test_capabilities():
    plugin = MeetingPlugin(MockContext())
    assert "meetings" in plugin.get_capabilities()

def test_render_dashboard():
    plugin = MeetingPlugin(MockContext())
    ops = plugin.render("dashboard")
    assert len(ops) == 1
    assert ops[0].type == "insert"
    assert ops[0].node.id == "meeting-widget"
    assert ops[0].node.children[1].props["action"] == "join_meeting"

def test_render_list():
    plugin = MeetingPlugin(MockContext())
    ops = plugin.render("meeting_list")
    assert len(ops) == 1
    grid = ops[0].node
    assert grid.type == "Grid"
    assert len(grid.children) == 2
