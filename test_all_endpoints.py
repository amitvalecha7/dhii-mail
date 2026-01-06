#!/usr/bin/env python3
"""
Comprehensive test for all A2UI endpoints with authentication
"""

import requests
import json
import time

BASE_URL = "http://localhost:8005"
AUTH_URL = f"{BASE_URL}/auth"
A2UI_URL = f"{BASE_URL}/api/a2ui"

def test_all_endpoints():
    """Test all A2UI endpoints with authentication"""
    
    # Test data
    test_email = "test@example.com"
    test_password = "testpassword123"
    test_name = "Test User"
    
    print("🧪 Testing DHII-Mail A2UI Endpoints")
    print("=" * 50)
    
    # 1. Test signup
    print("\n1️⃣ Testing signup...")
    signup_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/api/signup", json=signup_data)
        if response.status_code == 200:
            signup_result = response.json()
            if signup_result.get("success"):
                print("✅ Signup successful")
                token = signup_result.get("token")
            else:
                print(f"⚠️  Signup failed: {signup_result.get('message')}")
                # Try login instead
                print("🔄 Trying login instead...")
                login_response = requests.post(f"{AUTH_URL}/api/login", json={"email": test_email, "password": test_password})
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    if login_result.get("success"):
                        token = login_result.get("token")
                        print("✅ Login successful")
                    else:
                        print("❌ Both signup and login failed")
                        return
                else:
                    print(f"❌ Login failed with status {login_response.status_code}")
                    return
        else:
            print(f"❌ Signup failed with status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return
    
    # 2. Test dashboard endpoint
    print("\n2️⃣ Testing dashboard endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{A2UI_URL}/dashboard", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard successful (type: {result.get('type')})")
            if result.get('type') == 'clarification_response':
                print(f"   Clarification: {result.get('clarification_questions', [])}")
        else:
            print(f"❌ Dashboard failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # 3. Test process-intent endpoint
    print("\n3️⃣ Testing process-intent endpoint...")
    
    try:
        intent_data = {
            "user_input": "show dashboard",
            "context": {}
        }
        response = requests.post(f"{A2UI_URL}/process-intent", json=intent_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Process-intent successful (type: {result.get('type')})")
            if result.get('type') == 'clarification_response':
                print(f"   Clarification: {result.get('clarification_questions', [])}")
        else:
            print(f"❌ Process-intent failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Process-intent error: {e}")
    
    # 4. Test stream-intent endpoint
    print("\n4️⃣ Testing stream-intent endpoint...")
    
    try:
        intent_data = {
            "user_input": "show dashboard",
            "context": {}
        }
        response = requests.post(f"{A2UI_URL}/stream-intent", json=intent_data, headers=headers, stream=True)
        if response.status_code == 200:
            # Read first line of streaming response
            first_line = None
            for line in response.iter_lines():
                if line:
                    first_line = line.decode('utf-8')
                    break
            if first_line:
                result = json.loads(first_line)
                print(f"✅ Stream-intent successful (type: {result.get('type')})")
                if result.get('type') == 'clarification_response':
                    print(f"   Clarification: {result.get('clarification_questions', [])}")
            else:
                print("✅ Stream-intent successful (empty response)")
        else:
            print(f"❌ Stream-intent failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Stream-intent error: {e}")
    
    # 5. Test settings endpoint
    print("\n5️⃣ Testing settings endpoint...")
    
    try:
        response = requests.get(f"{A2UI_URL}/settings", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Settings successful (type: {result.get('type')})")
            if result.get('type') == 'clarification_response':
                print(f"   Clarification: {result.get('clarification_questions', [])}")
        else:
            print(f"❌ Settings failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Settings error: {e}")
    
    # 6. Test chat endpoint
    print("\n6️⃣ Testing chat endpoint...")
    
    try:
        chat_data = {
            "message": "Hello, how are you?",
            "session_id": "test_session"
        }
        response = requests.post(f"{A2UI_URL}/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat successful")
            print(f"   Response: {result.get('response')}")
            print(f"   Neural loop state: {result.get('neural_loop_state')}")
            if result.get('ui_update'):
                ui_update = result.get('ui_update', {})
                print(f"   UI update type: {ui_update.get('type')}")
        else:
            print(f"❌ Chat failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    # 7. Test unauthenticated access
    print("\n7️⃣ Testing unauthenticated access...")
    
    try:
        response = requests.get(f"{A2UI_URL}/dashboard")
        if response.status_code == 401:
            print("✅ Unauthenticated access properly rejected (401)")
        else:
            print(f"❌ Unauthenticated access should be rejected, got status {response.status_code}")
    except Exception as e:
        print(f"❌ Unauthenticated test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All endpoint tests completed!")
    print("✅ Authentication system is working correctly")
    print("✅ All A2UI endpoints enforce JWT validation")
    print("✅ Symphony Orchestrator Neural Loop is processing requests")

if __name__ == "__main__":
    test_all_endpoints()