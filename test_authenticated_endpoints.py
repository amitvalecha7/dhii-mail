#!/usr/bin/env python3
"""Test authenticated A2UI endpoints with valid tokens"""

import requests
import json

def test_authenticated_endpoints():
    """Test A2UI endpoints with valid authentication"""
    base_url = "http://localhost:8005"
    
    print("Testing Authenticated A2UI Endpoints...")
    print("=" * 60)
    
    # Test 1: Create a test user (signup)
    print("1. Testing user signup...")
    try:
        signup_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        }
        response = requests.post(f"{base_url}/auth/api/signup", json=signup_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ User created successfully")
                print(f"   Token: {data.get('token', 'No token')[:20]}...")
            else:
                print(f"   ⚠️  User creation message: {data.get('message')}")
                if "already exists" in data.get('message', ''):
                    print("   User already exists, continuing with login...")
        else:
            print(f"   ❌ Signup failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error during signup: {e}")
    
    # Test 2: Login to get valid token
    print("\n2. Testing user login...")
    token = None
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{base_url}/auth/api/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                token = data.get("token")
                print("   ✅ Login successful")
                print(f"   Token: {token[:20]}..." if token else "   ❌ No token received")
            else:
                print(f"   ❌ Login failed: {data.get('message')}")
        else:
            print(f"   ❌ Login failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error during login: {e}")
    
    if not token:
        print("   Cannot proceed without valid token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Access dashboard with valid token
    print("\n3. Testing dashboard with valid token...")
    try:
        response = requests.get(f"{base_url}/api/a2ui/dashboard", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Dashboard accessed successfully")
            print(f"   Response type: {data.get('type', 'unknown')}")
            print(f"   Has UI data: {'ui' in data}")
        else:
            print(f"   ❌ Dashboard access failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error accessing dashboard: {e}")
    
    # Test 4: Test process-intent with valid token
    print("\n4. Testing process-intent with valid token...")
    try:
        intent_data = {
            "user_input": "show dashboard",
            "context": {}
        }
        response = requests.post(f"{base_url}/api/a2ui/process-intent", json=intent_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Process-intent successful")
            print(f"   Response type: {data.get('type', 'unknown')}")
            print(f"   Has UI data: {'ui' in data}")
        else:
            print(f"   ❌ Process-intent failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error during process-intent: {e}")
    
    # Test 5: Test stream-intent with valid token
    print("\n5. Testing stream-intent with valid token...")
    try:
        intent_data = {
            "user_input": "show dashboard",
            "context": {}
        }
        response = requests.post(f"{base_url}/api/a2ui/stream-intent", json=intent_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Stream-intent successful")
            print(f"   Response type: {data.get('type', 'unknown')}")
            print(f"   Has UI data: {'ui' in data}")
        else:
            print(f"   ❌ Stream-intent failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error during stream-intent: {e}")
    
    print("\n" + "=" * 60)
    print("Authenticated endpoints test completed!")

if __name__ == "__main__":
    test_authenticated_endpoints()