#!/usr/bin/env python3
"""
A2UI Meeting Assistant Demo Script

This script demonstrates the capabilities of the A2UI meeting assistant.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from a2ui_integration.agent.agent_updated_v2 import run_meeting_agent

def run_demo():
    """Run the A2UI meeting assistant demo"""
    
    print("🤖 A2UI Meeting Assistant Demo")
    print("=" * 40)
    
    # Demo scenarios
    demo_scenarios = [
        {
            "description": "Show upcoming meetings",
            "input": "Show me my upcoming meetings",
            "user_email": "demo@example.com"
        },
        {
            "description": "Get available time slots",
            "input": "What time slots are available tomorrow?",
            "user_email": "demo@example.com"
        },
        {
            "description": "Book a meeting",
            "input": "Book a meeting with John tomorrow at 2 PM for 30 minutes",
            "user_email": "demo@example.com"
        },
        {
            "description": "Get meeting details",
            "input": "Tell me about meeting demo_001",
            "user_email": "demo@example.com"
        },
        {
            "description": "Cancel a meeting",
            "input": "Cancel my meeting demo_002",
            "user_email": "demo@example.com"
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{i}. {scenario['description']}")
        print(f"   User: {scenario['input']}")
        
        try:
            result = run_meeting_agent(scenario['input'], scenario['user_email'])
            
            if result.get('success'):
                print(f"   Agent: ✅ Response received")
                print(f"   Details: {result.get('response', 'No response text')}")
            else:
                print(f"   Agent: ❌ Error - {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Agent: ❌ Exception - {str(e)}")
        
        print("-" * 40)
    
    print("\n🎉 Demo completed!")
    print("\nTo test with voice commands, run the A2UI client:")
    print("1. Start the backend: ./start_a2ui.sh")
    print("2. Open: http://localhost:3001")
    print("3. Use voice commands or text chat")

if __name__ == "__main__":
    run_demo()
