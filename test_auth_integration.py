#!/usr/bin/env python3
"""Test authentication integration with A2UI endpoints"""

import requests
import json

def test_auth_integration():
    """Test authentication integration with A2UI endpoints"""
    base_url = "http://localhost:8005"
    
    print("Testing Authentication Integration...")
    print("=" * 50)
    
    # Test 1: Try to access dashboard without authentication
    print("1. Testing dashboard without authentication...")
    try:
        response = requests.get(f"{base_url}/api/a2ui/dashboard")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected unauthenticated request")
        else:
            print(f"   ❌ Unexpected response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Try to access dashboard with invalid token
    print("\n2. Testing dashboard with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{base_url}/api/a2ui/dashboard", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid token")
        else:
            print(f"   ❌ Unexpected response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test process-intent without authentication
    print("\n3. Testing process-intent without authentication...")
    try:
        intent_data = {
            "user_input": "show dashboard",
            "context": {}
        }
        response = requests.post(f"{base_url}/api/a2ui/process-intent", json=intent_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected unauthenticated request")
        else:
            print(f"   ❌ Unexpected response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test stream-intent without authentication
    print("\n4. Testing stream-intent without authentication...")
    try:
        intent_data = {
            "user_input": "show dashboard",
            "context": {}
        }
        response = requests.post(f"{base_url}/api/a2ui/stream-intent", json=intent_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected unauthenticated request")
        else:
            print(f"   ❌ Unexpected response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Authentication integration test completed!")

if __name__ == "__main__":
    test_auth_integration()