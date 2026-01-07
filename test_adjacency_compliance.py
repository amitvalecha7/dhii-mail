#!/usr/bin/env python3
"""
Test script to verify A2UI adjacency list compliance for all UI states.
This validates that the ComponentGraph implementation follows the proper format
as required by Issue #25 and the New Design Spec v1.2.
"""

import json
import sys
from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator
from a2ui_integration.a2ui_state_machine import UIState

def validate_adjacency_list_format(adjacency_list: dict) -> bool:
    """Validate that adjacency list follows the required format"""
    
    # Check top-level structure
    required_keys = ["nodes", "rootId", "operations"]
    for key in required_keys:
        if key not in adjacency_list:
            print(f"❌ Missing required key: {key}")
            return False
    
    # Validate nodes structure
    nodes = adjacency_list.get("nodes", {})
    if not isinstance(nodes, dict):
        print("❌ Nodes must be a dictionary")
        return False
    
    for node_id, node_data in nodes.items():
        # Check node structure
        node_required_keys = ["id", "type", "props", "children"]
        for key in node_required_keys:
            if key not in node_data:
                print(f"❌ Node {node_id} missing required key: {key}")
                return False
        
        # Validate node data types
        if not isinstance(node_data["id"], str):
            print(f"❌ Node {node_id} id must be string")
            return False
        if not isinstance(node_data["type"], str):
            print(f"❌ Node {node_id} type must be string")
            return False
        if not isinstance(node_data["props"], dict):
            print(f"❌ Node {node_id} props must be dictionary")
            return False
        if not isinstance(node_data["children"], list):
            print(f"❌ Node {node_id} children must be list")
            return False
    
    # Validate rootId
    root_id = adjacency_list.get("rootId")
    if root_id not in nodes:
        print(f"❌ Root ID {root_id} not found in nodes")
        return False
    
    # Validate operations
    operations = adjacency_list.get("operations", [])
    if not isinstance(operations, list):
        print("❌ Operations must be a list")
        return False
    
    for op in operations:
        op_required_keys = ["type", "nodeId", "componentType", "props", "parentId", "index"]
        for key in op_required_keys:
            if key not in op:
                print(f"❌ Operation missing required key: {key}")
                return False
    
    return True

def test_ui_state_compliance(state: UIState, orchestrator: A2UIOrchestrator) -> bool:
    """Test a specific UI state for adjacency list compliance"""
    
    print(f"\n🧪 Testing UI State: {state.value}")
    
    # Mock user context for testing
    user_context = {
        "name": "Test User",
        "email": "test@example.com",
        "pendingEmails": 3,
        "overdueTasks": 2,
        "meetingsToday": 1,
        "pendingActions": 4,
        "emails": [
            {"id": "1", "from": "sender@example.com", "subject": "Test Email", "date": "2024-01-01", "status": "unread"}
        ],
        "email_detail": {
            "from": "sender@example.com",
            "to": "user@example.com",
            "subject": "Test Email Subject",
            "date": "2024-01-01",
            "content": "Test email content"
        },
        "calendar_events": [
            {"title": "Test Meeting", "date": "2024-01-01", "time": "10:00", "duration": 60}
        ],
        "meetings": [
            {"title": "Team Meeting", "date": "2024-01-01", "time": "10:00", "duration": 60, "participants": ["User 1", "User 2"]}
        ],
        "meeting_detail": {
            "title": "Team Meeting",
            "date": "2024-01-01",
            "time": "10:00",
            "duration": 60,
            "location": "Conference Room",
            "participants": ["User 1", "User 2"],
            "agenda": "Team sync discussion"
        },
        "tasks": [
            {"title": "Task 1", "status": "todo", "priority": "high"},
            {"title": "Task 2", "status": "in_progress", "priority": "medium"}
        ]
    }
    
    try:
        # Render UI for the state
        result = orchestrator.render_ui(state, user_context)
        
        # Check if result has adjacency list
        if "adjacencyList" not in result:
            print(f"❌ No adjacencyList in result for state {state.value}")
            return False
        
        adjacency_list = result["adjacencyList"]
        
        # Validate format
        is_valid = validate_adjacency_list_format(adjacency_list)
        
        if is_valid:
            print(f"✅ State {state.value} adjacency list format is valid")
            
            # Additional validation: check for required component types
            nodes = adjacency_list.get("nodes", {})
            component_types = set(node_data["type"] for node_data in nodes.values())
            
            print(f"   Component types found: {', '.join(sorted(component_types))}")
            
            # Check for New Design Spec v1.2 components
            if "text_block" in component_types:
                print("   ✅ TextBlock component found (New Design Spec compliant)")
            if "aggregated_card" in component_types:
                print("   ✅ AggregatedCard component found (New Design Spec compliant)")
            
        else:
            print(f"❌ State {state.value} adjacency list format is invalid")
            
        return is_valid
        
    except Exception as e:
        print(f"❌ Error testing state {state.value}: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🔍 A2UI Adjacency List Compliance Test")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = A2UIOrchestrator()
    
    # Test all UI states
    states_to_test = [
        UIState.DASHBOARD,
        UIState.EMAIL_INBOX,
        UIState.EMAIL_DETAIL,
        UIState.CALENDAR_VIEW,
        UIState.MEETING_LIST,
        UIState.MEETING_DETAIL
    ]
    
    passed_tests = 0
    total_tests = len(states_to_test)
    
    for state in states_to_test:
        if test_ui_state_compliance(state, orchestrator):
            passed_tests += 1
    
    print(f"\n📊 Test Results:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All adjacency list compliance tests passed!")
        return 0
    else:
        print("❌ Some adjacency list compliance tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())