#!/usr/bin/env python3
"""
Test script for A2UI Orchestrator with State Machine integration - Updated
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator

def test_orchestrator_integration():
    """Test the orchestrator with state machine integration"""
    print("🧪 Testing A2UI Orchestrator with State Machine...")
    
    # Initialize orchestrator
    orchestrator = A2UIOrchestrator()
    
    print("=== Testing State Transitions ===")
    
    # Test initial state
    print(f"Initial state: {orchestrator.state_machine.get_current_state().value}")
    
    # Test rendering dashboard
    print("\n--- Rendering Dashboard ---")
    dashboard_ui = orchestrator.render_ui(orchestrator.state_machine.get_current_state())
    print(f"Dashboard UI keys: {list(dashboard_ui.keys())}")
    print(f"State info included: {'state_info' in dashboard_ui}")
    
    # Test navigation actions
    print("\n--- Testing Navigation Actions ---")
    
    # Navigate to email inbox
    result = orchestrator.handle_action("navigate_email_inbox")
    success = 'ui_type' in result and result.get('ui_type') == 'email_inbox'
    print(f"Email inbox navigation: {'✅ Success' if success else '❌ Failed'}")
    print(f"New state: {orchestrator.state_machine.get_current_state().value}")
    
    # Navigate to calendar
    result = orchestrator.handle_action("navigate_calendar")
    success = 'ui_type' in result and result.get('ui_type') == 'calendar'
    print(f"Calendar navigation: {'✅ Success' if success else '❌ Failed'}")
    print(f"New state: {orchestrator.state_machine.get_current_state().value}")
    
    # Test invalid navigation
    print("\n--- Testing Invalid Navigation ---")
    result = orchestrator.handle_action("navigate_analytics")  # Should fail from calendar
    has_transition_error = 'transition_error' in result
    print(f"Analytics navigation from calendar: {'✅ Failed as expected' if has_transition_error else '❌ Unexpected success'}")
    print(f"State remained: {orchestrator.state_machine.get_current_state().value}")
    
    # Test rollback
    print("\n--- Testing Rollback ---")
    rollback_result = orchestrator.rollback_state()
    print(f"Rollback: {'✅ Success' if rollback_result['status'] == 'rollback_success' else '❌ Failed'}")
    print(f"State after rollback: {rollback_result['new_state']}")
    
    # Test available actions
    print("\n--- Testing Available Actions ---")
    available_actions = orchestrator.get_available_actions()
    print(f"Available actions: {available_actions}")
    
    # Test state machine info
    print("\n--- Testing State Machine Info ---")
    state_info = orchestrator.get_state_machine_info()
    print(f"Current state: {state_info['current_state']}")
    print(f"Available transitions: {state_info['available_transitions']}")
    print(f"History size: {state_info['history_size']}")
    
    print("\n✅ Orchestrator integration tests completed!")

if __name__ == "__main__":
    test_orchestrator_integration()