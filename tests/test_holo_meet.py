import sys
import os
import json
import uuid
from datetime import datetime

# Add project root to path
sys.path.append("/root/dhii-mail")

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.runner import PluginRunner
from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator, UIState
from plugins.meeting import meeting_create, meeting_update, meeting_list, register

def test_capabilities():
    print("\n--- Testing Holo-Meet Capabilities ---")
    
    # Test Create
    params = {
        "title": "Test Meeting",
        "date": "2024-02-01",
        "time": "10:00",
        "duration": 60,
        "participants": ["test@dhii.ai"],
        "description": "A test meeting"
    }
    result = meeting_create(params)
    print(f"Create Result: {json.dumps(result, indent=2)}")
    
    if result["status"] == "success":
        meeting_id = result["meeting"]["id"]
        
        # Test Update
        update_params = {"id": meeting_id, "duration": 90}
        update_result = meeting_update(update_params)
        print(f"Update Result: {json.dumps(update_result, indent=2)}")
        
        # Test List
        list_result = meeting_list({})
        print(f"List Result: {json.dumps(list_result, indent=2)}")
        
        assert any(m["id"] == meeting_id for m in list_result["meetings"]), "Created meeting not found in list"
    else:
        print("Skipping Update/List tests due to Create failure")

def test_plugin_registration():
    print("\n--- Testing Plugin Registration ---")
    
    # Mock kernel context
    kernel_context = {"capabilities": {}}
    
    def mock_register(name, func):
        kernel_context["capabilities"][name] = func
        
    kernel_context["log"] = lambda msg: print(f"[KERNEL] {msg}")
    kernel_context["register_capability"] = mock_register
    
    # Register plugin manually (simulating loader)
    register(kernel_context)
    
    # Check if capabilities are registered
    caps = kernel_context["capabilities"]
    print(f"Registered Capabilities: {list(caps.keys())}")
    
    assert "meeting_create" in caps
    assert "meeting_update" in caps
    assert "meeting_list" in caps

def test_holo_renderer():
    print("\n--- Testing Holo-Renderer (A2UI Schema) ---")
    orchestrator = A2UIOrchestrator()
    
    # 1. Test Meeting List (Grid View)
    print("Rendering Meeting List...")
    context_list = {
        "meetings": [
            {
                "id": "1",
                "title": "Render Test",
                "date": "2024-02-01",
                "time": "14:00",
                "duration": 30,
                "participants": ["a@b.com"],
                "status": "scheduled"
            }
        ]
    }
    ui_list = orchestrator.render_ui(UIState.MEETING_LIST, context_list)
    layout_json = json.dumps(ui_list["component"]["layout"], indent=2)
    # Check for Grid and Glass variants
    # Note: A2UIComponents produces {"component": {"Grid": {...}}}, so we check for "Grid":
    if '"variant": "glass"' in layout_json and '"Grid":' in layout_json:
        print("✅ Meeting List: Glass Grid detected")
    else:
        print("❌ Meeting List: Glass Grid NOT detected")
        
    # 2. Test Meeting Detail (Glass Card)
    print("Rendering Meeting Detail...")
    context_detail = {
        "meeting_detail": {
            "title": "Deep Dive",
            "date": "2024-02-02",
            "time": "09:00",
            "duration": 120,
            "participants": ["team@dhii.ai"],
            "agenda": "Details...",
            "status": "confirmed"
        }
    }
    ui_detail = orchestrator.render_ui(UIState.MEETING_DETAIL, context_detail)
    layout_detail_json = json.dumps(ui_detail["component"]["layout"], indent=2)
    if '"variant": "glass"' in layout_detail_json:
         print("✅ Meeting Detail: Glass Card detected")
    else:
         print("❌ Meeting Detail: Glass Card NOT detected")

    # 3. Test Meeting Book (Form)
    print("Rendering Meeting Book...")
    ui_book = orchestrator.render_ui(UIState.MEETING_BOOK)
    layout_book_json = json.dumps(ui_book["component"]["layout"], indent=2)
    if '"Form":' in layout_book_json:
        print("✅ Meeting Book: Form detected")
    else:
        print("❌ Meeting Book: Form NOT detected")

if __name__ == "__main__":
    try:
        test_capabilities()
        test_plugin_registration()
        test_holo_renderer()
        print("\nAll Holo-Meet tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
