#!/usr/bin/env python3
"""Test script for A2UI router with specific intents"""

import requests
import json

def test_specific_intents():
    """Test specific intents that should trigger different responses"""
    base_url = "http://localhost:8005/api/a2ui"
    
    print("Testing Specific Intents with Symphony Orchestrator...")
    print("=" * 60)
    
    # Test 1: Simple intent that should work
    try:
        print("Test 1: Simple email intent")
        intent_data = {
            "user_input": "Show me my emails",
            "context": {"user_id": "test_user"}
        }
        
        response = requests.post(f"{base_url}/process-intent", json=intent_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {data.get('type', 'unknown')}")
            print(f"Has UI data: {'ui' in data}")
            print(f"Has skeleton: {'skeleton' in data}")
            print(f"Clarification questions: {len(data.get('clarification_questions', []))}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Complex meeting intent with more context
    try:
        print("Test 2: Complex meeting intent with context")
        intent_data = {
            "user_input": "Schedule a meeting with John tomorrow at 2 PM to discuss the project",
            "context": {
                "user_id": "test_user",
                "contacts": ["John", "Jane", "Bob"],
                "current_project": "Website Redesign"
            }
        }
        
        response = requests.post(f"{base_url}/process-intent", json=intent_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {data.get('type', 'unknown')}")
            print(f"Has UI data: {'ui' in data}")
            print(f"Has skeleton: {'skeleton' in data}")
            print(f"Clarification questions: {len(data.get('clarification_questions', []))}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_specific_intents()