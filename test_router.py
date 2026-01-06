#!/usr/bin/env python3
"""Test script for A2UI router with Symphony Orchestrator"""

import requests
import json

def test_router():
    """Test the A2UI router endpoints"""
    base_url = "http://localhost:8005/api/a2ui"
    
    print("Testing A2UI Router with Symphony Orchestrator...")
    print("=" * 50)
    
    # Test dashboard endpoint
    try:
        print("Testing /dashboard endpoint...")
        response = requests.get(f"{base_url}/dashboard")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {data.get('type', 'unknown')}")
            print(f"Has UI data: {'ui' in data}")
            print(f"Has skeleton: {'skeleton' in data}")
            print(f"Execution ID: {data.get('execution_id', 'none')}")
            
            # Pretty print the response
            print("\nResponse structure:")
            print(json.dumps(data, indent=2, default=str)[:500] + "..." if len(json.dumps(data, indent=2, default=str)) > 500 else json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing dashboard: {e}")
    
    print("\n" + "=" * 50)
    
    # Test intent processing
    try:
        print("Testing /process-intent endpoint...")
        intent_data = {
            "user_input": "Schedule a meeting with John tomorrow at 2 PM",
            "context": {"user_id": "test_user"}
        }
        
        response = requests.post(f"{base_url}/process-intent", json=intent_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {data.get('type', 'unknown')}")
            print(f"Has UI data: {'ui' in data}")
            print(f"Has skeleton: {'skeleton' in data}")
            
            # Pretty print the response
            print("\nResponse structure:")
            print(json.dumps(data, indent=2, default=str)[:500] + "..." if len(json.dumps(data, indent=2, default=str)) > 500 else json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing intent processing: {e}")

if __name__ == "__main__":
    test_router()