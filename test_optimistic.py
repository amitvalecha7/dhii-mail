#!/usr/bin/env python3
"""Test script for optimistic execution with Symphony Orchestrator and Liquid Glass Host"""

import requests
import json

def test_optimistic_execution():
    """Test optimistic execution with specific, actionable intents"""
    base_url = "http://localhost:8005/api/a2ui"
    
    print("Testing Optimistic Execution with Symphony + Liquid Glass...")
    print("=" * 70)
    
    # Test with a very specific intent that should trigger optimistic execution
    try:
        print("Testing specific email action...")
        intent_data = {
            "user_input": "Send email to john@example.com with subject 'Project Update' and body 'The project is on track'",
            "context": {
                "user_id": "test_user",
                "email_provider": "gmail",
                "contacts": ["john@example.com"]
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
            if len(response_preview) > 400:
                print(response_preview[:400] + "...")
            else:
                print(response_preview)
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing optimistic execution: {e}")

if __name__ == "__main__":
    test_optimistic_execution()