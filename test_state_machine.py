#!/usr/bin/env python3
"""
Test script for A2UI State Machine implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2ui_integration.a2ui_state_machine import A2UIStateMachine, UIState

def test_state_machine():
    """Test the state machine functionality"""
    print("🧪 Testing A2UI State Machine...")
    
    # Initialize state machine
    sm = A2UIStateMachine()
    
    print(f"Initial state: {sm.get_current_state().value}")
    print(f"Available transitions: {[s.value for s in sm.get_available_transitions()]}")
    
    # Test valid transition
    print("\n--- Testing valid transition ---")
    success = sm.transition_to(UIState.EMAIL_INBOX, "user_action", {"test": "context"})
    print(f"Transition to EMAIL_INBOX: {'✅ Success' if success else '❌ Failed'}")
    print(f"Current state: {sm.get_current_state().value}")
    
    # Test invalid transition
    print("\n--- Testing invalid transition ---")
    success = sm.transition_to(UIState.ANALYTICS, "invalid_action")
    print(f"Transition from EMAIL_INBOX to ANALYTICS: {'✅ Success' if success else '❌ Failed (expected)'}")
    
    # Test valid sequence
    print("\n--- Testing valid sequence ---")
    transitions = [
        (UIState.DASHBOARD, "return_home"),
        (UIState.CALENDAR_VIEW, "open_calendar"),
        (UIState.MEETING_LIST, "view_meetings"),
        (UIState.MEETING_DETAIL, "view_meeting_detail"),
    ]
    
    for target_state, action in transitions:
        success = sm.transition_to(target_state, action)
        print(f"  {action} -> {target_state.value}: {'✅' if success else '❌'}")
    
    print(f"Final state: {sm.get_current_state().value}")
    
    # Test rollback
    print("\n--- Testing rollback ---")
    success = sm.rollback_to_previous()
    print(f"Rollback: {'✅ Success' if success else '❌ Failed'}")
    print(f"State after rollback: {sm.get_current_state().value}")
    
    # Test state info
    print("\n--- Testing state info ---")
    info = sm.get_state_info()
    print(f"History size: {info['history_size']}")
    print(f"Recent transitions: {len(info['recent_transitions'])}")
    
    # Test context management
    print("\n--- Testing context management ---")
    sm.state_context[UIState.DASHBOARD]["test_key"] = "test_value"
    context = sm.get_state_context(UIState.DASHBOARD)
    print(f"Context for DASHBOARD: {context}")
    
    print("\n✅ State machine tests completed!")

if __name__ == "__main__":
    test_state_machine()