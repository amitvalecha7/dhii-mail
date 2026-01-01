#!/usr/bin/env python3
"""
Test script for A2UI Command Palette integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator
from a2ui_integration.a2ui_state_machine import UIState

def test_command_palette_integration():
    """Test command palette integration with orchestrator"""
    print("🚀 Testing Command Palette Integration...")
    
    orchestrator = A2UIOrchestrator()
    
    # Test 1: Open command palette
    print("\n1️⃣ Testing open_command_palette action...")
    result = orchestrator.handle_action("open_command_palette", {}, "test_user")
    
    if "command_palette" in result:
        palette = result["command_palette"]
        print(f"✅ Command palette opened successfully")
        print(f"   - Query: '{palette['component']['CommandPalette']['query']}'")
        print(f"   - Items: {len(palette['component']['CommandPalette']['items'])} commands")
        print(f"   - Categories: {len(palette['component']['CommandPalette']['categories'])} categories")
        
        # Show first few commands
        items = palette['component']['CommandPalette']['items'][:3]
        for item in items:
            print(f"   - Command: {item['title']} ({item['category']})")
    else:
        print("❌ Command palette not found in result")
        return False
    
    # Test 2: Search commands
    print("\n2️⃣ Testing search_commands action...")
    search_data = {"query": "email"}
    result = orchestrator.handle_action("search_commands", search_data, "test_user")
    
    if "command_palette" in result:
        palette = result["command_palette"]
        items = palette['component']['CommandPalette']['items']
        print(f"✅ Search completed successfully")
        print(f"   - Query: '{palette['component']['CommandPalette']['query']}'")
        print(f"   - Results: {len(items)} commands found")
        
        # Show email-related commands
        email_commands = [item for item in items if 'email' in item['title'].lower()]
        for cmd in email_commands[:3]:
            print(f"   - Found: {cmd['title']} ({cmd['category']})")
    else:
        print("❌ Search failed")
        return False
    
    # Test 3: Execute command
    print("\n3️⃣ Testing execute_command action...")
    
    # First, get a command ID from search
    search_data = {"query": "compose"}
    result = orchestrator.handle_action("search_commands", search_data, "test_user")
    
    if "command_palette" in result and result["command_palette"]['component']['CommandPalette']['items']:
        first_command = result["command_palette"]['component']['CommandPalette']['items'][0]
        command_id = first_command['id']
        print(f"   - Will execute command: {first_command['title']} (ID: {command_id})")
        
        # Execute the command
        execute_data = {"command_id": command_id}
        result = orchestrator.handle_action("execute_command", execute_data, "test_user")
        
        # Check if we got a UI result (command executed successfully)
        if "ui_type" in result:
            print(f"✅ Command executed successfully")
            print(f"   - Transitioned to: {result.get('ui_type', 'unknown')}")
            print(f"   - Current state: {result.get('state_info', {}).get('current_state', 'unknown')}")
        elif "command_result" in result:
            command_result = result["command_result"]
            print(f"✅ Command executed with result")
            print(f"   - Success: {command_result.get('success')}")
            print(f"   - Action: {command_result.get('action')}")
            print(f"   - Message: {command_result.get('message')}")
        else:
            print("❌ Command execution failed")
            return False
    else:
        print("❌ No commands found to execute")
        return False
    
    # Test 4: Command palette with different context
    print("\n4️⃣ Testing command palette with email context...")
    
    # Navigate to email state first
    orchestrator.render_ui(UIState.EMAIL_INBOX, {"user_id": "test_user"})
    
    # Open command palette in email context
    result = orchestrator.handle_action("open_command_palette", {}, "test_user")
    
    if "command_palette" in result:
        palette = result["command_palette"]
        items = palette['component']['CommandPalette']['items']
        
        # Check for email-specific commands
        email_commands = [item for item in items if item['category'] == 'email']
        print(f"✅ Command palette in email context")
        print(f"   - Email commands available: {len(email_commands)}")
        
        for cmd in email_commands[:3]:
            print(f"   - Email command: {cmd['title']}")
    else:
        print("❌ Command palette not available in email context")
        return False
    
    print("\n🎉 All command palette integration tests passed!")
    return True

if __name__ == "__main__":
    success = test_command_palette_integration()
    sys.exit(0 if success else 1)