#!/usr/bin/env python3
"""
Test script to verify A2UI orchestrator uses unified AppShell response format.
This addresses Issue #2: Standardize A2UI router response to AppShell orchestrator shape.
"""

import sys
import json
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator
from a2ui_integration.a2ui_state_machine import UIState

def test_unified_response_format():
    """Test that all render functions return unified AppShell format"""
    print("Testing A2UI Orchestrator unified response format...")
    
    # Initialize orchestrator
    orchestrator = A2UIOrchestrator()
    
    # Test context
    test_context = {
        'name': 'Test User',
        'unread_count': 5,
        'today_meetings': 3,
        'pending_tasks': 7,
        'emails': [
            {'from': 'test@example.com', 'subject': 'Test Email', 'date': '2024-01-01', 'status': 'unread'}
        ],
        'meetings': [
            {'title': 'Test Meeting', 'date': '2024-01-01', 'time': '10:00', 'participants': ['user1'], 'status': 'scheduled'}
        ],
        'tasks': [
            {'id': 1, 'title': 'Test Task', 'status': 'To Do'}
        ]
    }
    
    # Test all UI states
    test_states = [
        UIState.DASHBOARD,
        UIState.EMAIL_INBOX,
        UIState.EMAIL_COMPOSE,
        UIState.EMAIL_DETAIL,
        UIState.CALENDAR_VIEW,
        UIState.MEETING_LIST,
        UIState.MEETING_DETAIL,
        UIState.MEETING_BOOK,
        UIState.TASK_BOARD,
        UIState.ANALYTICS,
        UIState.SETTINGS,
        UIState.CHAT
    ]
    
    all_passed = True
    
    for state in test_states:
        print(f"\nTesting state: {state.value}")
        try:
            result = orchestrator.render_ui(state, test_context)
            
            # Check unified format
            if 'component' not in result:
                print(f"❌ FAIL: Missing 'component' key in response")
                all_passed = False
                continue
                
            if 'state_info' not in result:
                print(f"❌ FAIL: Missing 'state_info' key in response")
                all_passed = False
                continue
            
            # Check component structure
            component = result['component']
            if 'type' not in component:
                print(f"❌ FAIL: Missing 'type' in component")
                all_passed = False
                continue
                
            if component['type'] != 'appshell':
                print(f"❌ FAIL: Component type is '{component['type']}', expected 'appshell'")
                all_passed = False
                continue
            
            # Check for required AppShell fields
            required_fields = ['layout', 'navigation']
            for field in required_fields:
                if field not in component:
                    print(f"❌ FAIL: Missing '{field}' in component")
                    all_passed = False
                    break
            else:
                print(f"✅ PASS: State {state.value} returns unified AppShell format")
                
        except Exception as e:
            print(f"❌ FAIL: Exception testing state {state.value}: {e}")
            all_passed = False
    
    return all_passed

def test_individual_render_functions():
    """Test individual render functions directly"""
    print("\n\nTesting individual render functions...")
    
    orchestrator = A2UIOrchestrator()
    test_context = {
        'name': 'Test User',
        'unread_count': 5,
        'today_meetings': 3,
        'pending_tasks': 7,
        'emails': [
            {'from': 'test@example.com', 'subject': 'Test Email', 'date': '2024-01-01', 'status': 'unread'}
        ],
        'meetings': [
            {'title': 'Test Meeting', 'date': '2024-01-01', 'time': '10:00', 'participants': ['user1'], 'status': 'scheduled'}
        ],
        'tasks': [
            {'id': 1, 'title': 'Test Task', 'status': 'To Do'}
        ]
    }
    
    orchestrator.user_context = test_context
    
    # Test each render function
    render_functions = [
        ('_render_dashboard', orchestrator._render_dashboard),
        ('_render_email_inbox', orchestrator._render_email_inbox),
        ('_render_email_compose', orchestrator._render_email_compose),
        ('_render_email_detail', orchestrator._render_email_detail),
        ('_render_calendar', orchestrator._render_calendar),
        ('_render_meeting_list', orchestrator._render_meeting_list),
        ('_render_meeting_detail', orchestrator._render_meeting_detail),
        ('_render_meeting_book', orchestrator._render_meeting_book),
        ('_render_task_board', orchestrator._render_task_board),
        ('_render_analytics', orchestrator._render_analytics),
        ('_render_settings', orchestrator._render_settings),
        ('_render_chat', orchestrator._render_chat)
    ]
    
    all_passed = True
    
    for func_name, func in render_functions:
        print(f"\nTesting {func_name}...")
        try:
            result = func()
            
            # Check unified format
            if 'component' not in result:
                print(f"❌ FAIL: Missing 'component' key")
                all_passed = False
                continue
                
            if 'state_info' not in result:
                print(f"❌ FAIL: Missing 'state_info' key")
                all_passed = False
                continue
            
            # Check component structure
            component = result['component']
            if 'type' not in component or component['type'] != 'appshell':
                print(f"❌ FAIL: Component type is not 'appshell'")
                all_passed = False
                continue
            
            print(f"✅ PASS: {func_name} returns unified AppShell format")
            
        except Exception as e:
            print(f"❌ FAIL: Exception in {func_name}: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("A2UI Orchestrator Unified Response Format Test")
    print("=" * 60)
    
    # Test render_ui method
    test1_passed = test_unified_response_format()
    
    # Test individual render functions
    test2_passed = test_individual_render_functions()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ A2UI orchestrator now uses unified AppShell response format")
        print("✅ Issue #2 has been resolved")
    else:
        print("❌ SOME TESTS FAILED!")
        print("❌ Unified response format needs more work")
    
    print("=" * 60)