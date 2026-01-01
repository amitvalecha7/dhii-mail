#!/usr/bin/env python3
"""
Test script for A2UI API endpoints with State Machine integration
"""

import requests
import json

def test_api_endpoints():
    """Test the A2UI API endpoints"""
    base_url = "http://localhost:8005"
    
    print("🧪 Testing A2UI API Endpoints with State Machine...")
    
    # Test dashboard endpoint
    print("\n--- Testing Dashboard Endpoint ---")
    try:
        response = requests.get(f"{base_url}/api/a2ui/dashboard")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"UI Type: {data.get('ui_type')}")
            print(f"State Info: {data.get('state_info', {}).get('current_state')}")
            print(f"Available transitions: {len(data.get('state_info', {}).get('available_transitions', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test email inbox endpoint
    print("\n--- Testing Email Inbox Endpoint ---")
    try:
        response = requests.get(f"{base_url}/api/a2ui/email/inbox")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"UI Type: {data.get('ui_type')}")
            print(f"State Info: {data.get('state_info', {}).get('current_state')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test UI action endpoint
    print("\n--- Testing UI Action Endpoint ---")
    try:
        action_data = {
            "action": "navigate_calendar",
            "data": {}
        }
        response = requests.post(f"{base_url}/ui/action", json=action_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Action result: {data.get('status')}")
            print(f"New state: {data.get('state_info', {}).get('current_state')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    print("\n✅ API endpoint tests completed!")

if __name__ == "__main__":
    test_api_endpoints()