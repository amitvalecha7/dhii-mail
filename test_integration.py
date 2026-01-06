#!/usr/bin/env python3
"""Test script for Symphony Orchestrator and Liquid Glass Host integration"""

import requests
import json

def test_integration():
    """Test the integration between Symphony Orchestrator and Liquid Glass Host"""
    base_url = "http://localhost:8005/api/a2ui"
    
    print("Testing Symphony Orchestrator + Liquid Glass Host Integration...")
    print("=" * 70)
    
    # Test streaming intent endpoint
    try:
        print("Testing /stream-intent endpoint...")
        intent_data = {
            "user_input": "Schedule a meeting with John tomorrow at 2 PM",
            "context": {
                "user_id": "test_user",
                "contacts": ["John", "Jane", "Bob"],
                "current_project": "Website Redesign"
            }
        }
        
        response = requests.post(f"{base_url}/stream-intent", json=intent_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {data.get('type', 'unknown')}")
            print(f"Has UI data: {'ui' in data}")
            print(f"Has skeleton: {'skeleton' in data}")
            print(f"Component type: {data.get('component', {}).get('component', {}).keys()}")
            
            # Show a sample of the response
            print("\nResponse preview:")
            response_preview = json.dumps(data, indent=2, default=str)
            if len(response_preview) > 300:
                print(response_preview[:300] + "...")
            else:
                print(response_preview)
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing integration: {e}")

if __name__ == "__main__":
    test_integration()