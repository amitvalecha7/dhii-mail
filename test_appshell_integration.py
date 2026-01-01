#!/usr/bin/env python3
"""
Test script for A2UI AppShell integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator
from a2ui_integration.a2ui_state_machine import UIState

def test_appshell_integration():
    """Test AppShell integration with orchestrator"""
    print("🚀 Testing AppShell Integration...")
    
    orchestrator = A2UIOrchestrator()
    
    # Test 1: Render dashboard with AppShell
    print("\n1️⃣ Testing dashboard with AppShell...")
    result = orchestrator.render_ui(UIState.DASHBOARD, {"user_id": "test_user"})
    
    if "AppShell" in result.get("component", {}):
        appshell = result["component"]["AppShell"]
        print(f"✅ AppShell rendered successfully")
        print(f"   - Ribbon present: {'ribbon' in appshell}")
        print(f"   - Layout present: {'layout' in appshell}")
        print(f"   - Number of panes: {len(appshell.get('layout', {}).get('panes', []))}")
        
        # Check ribbon
        if "ribbon" in appshell:
            ribbon = appshell["ribbon"]
            print(f"   - Ribbon tabs: {len(ribbon.get('tabs', []))}")
            active_tabs = [tab for tab in ribbon.get('tabs', []) if tab.get('active')]
            print(f"   - Active tabs: {len(active_tabs)}")
            if active_tabs:
                print(f"   - Active tab: {active_tabs[0].get('title')}")
        
        # Check layout
        layout = appshell.get('layout', {})
        print(f"   - Layout type: {layout.get('type')}")
        print(f"   - Pane sizes: {layout.get('sizes', [])}")
    else:
        print("❌ AppShell not found in result")
        return False
    
    # Test 2: Test different states
    print("\n2️⃣ Testing email state with AppShell...")
    result = orchestrator.render_ui(UIState.EMAIL_INBOX, {"user_id": "test_user"})
    
    if "AppShell" in result.get("component", {}):
        appshell = result["component"]["AppShell"]
        ribbon = appshell.get("ribbon", {})
        active_tabs = [tab for tab in ribbon.get('tabs', []) if tab.get('active')]
        
        if active_tabs and active_tabs[0].get('type') == 'email':
            print(f"✅ Email state rendered with correct ribbon tab")
            print(f"   - Active tab: {active_tabs[0].get('title')}")
        else:
            print("❌ Email state not showing correct active tab")
            return False
    else:
        print("❌ AppShell not found in email state")
        return False
    
    # Test 3: Test pane content
    print("\n3️⃣ Testing pane content...")
    result = orchestrator.render_ui(UIState.CALENDAR_VIEW, {"user_id": "test_user"})
    
    if "AppShell" in result.get("component", {}):
        appshell = result["component"]["AppShell"]
        panes = appshell.get('layout', {}).get('panes', [])
        
        if len(panes) >= 3:
            sidebar_pane = panes[0]
            main_pane = panes[1]
            details_pane = panes[2]
            
            print(f"✅ All panes present")
            print(f"   - Sidebar pane: {sidebar_pane.get('title')}")
            print(f"   - Main pane: {main_pane.get('title')}")
            print(f"   - Details pane: {details_pane.get('title')}")
            
            # Check if panes have content
            if sidebar_pane.get('content'):
                print(f"   - Sidebar has content: {type(sidebar_pane['content'])}")
            if main_pane.get('content'):
                print(f"   - Main pane has content: {type(main_pane['content'])}")
            if details_pane.get('content'):
                print(f"   - Details pane has content: {type(details_pane['content'])}")
        else:
            print("❌ Not enough panes found")
            return False
    else:
        print("❌ AppShell not found")
        return False
    
    # Test 4: Test keyboard shortcuts
    print("\n4️⃣ Testing keyboard shortcuts...")
    shortcuts = orchestrator.appshell.get_keyboard_shortcuts()
    print(f"✅ Found {len(shortcuts)} keyboard shortcuts")
    
    for shortcut in shortcuts[:3]:
        print(f"   - {shortcut['key']}: {shortcut['description']} ({shortcut['context']})")
    
    # Test 5: Test AppShell actions
    print("\n5️⃣ Testing AppShell actions...")
    result = orchestrator.handle_action("open_command_palette", {}, "test_user")
    
    if "command_palette" in result:
        print(f"✅ Command palette action works with AppShell")
    else:
        print("❌ Command palette action failed with AppShell")
        return False
    
    print("\n🎉 All AppShell integration tests passed!")
    return True

if __name__ == "__main__":
    success = test_appshell_integration()
    sys.exit(0 if success else 1)