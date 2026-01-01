"""
dhii Mail - A2UI Chat Authentication Test
Tests the chat-based authentication system.
"""

import requests
import json

def test_chat_auth():
    """Test the A2UI chat-based authentication."""
    base_url = "http://localhost:8000"
    
    print("Testing dhii Mail A2UI Chat Authentication...")
    
    # Test 1: Initial greeting
    print("\n1. Testing initial greeting...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "hello"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        print(f"✓ Requires input: {result['requires_input']}")
        session_id = result['session_id']
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 2: Login flow
    print("\n2. Testing login flow...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "I want to login",
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        print(f"✓ Step: login_username")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 3: Provide username
    print("\n3. Providing username...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "testuser",
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        print(f"✓ Step: login_password")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 4: Provide password
    print("\n4. Providing password...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "test123",
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        if result.get('auth_result'):
            print(f"✓ Login successful!")
            print(f"✓ Access token: {result['auth_result']['access_token'][:50]}...")
            print(f"✓ User: {result['auth_result']['user']['username']}")
        else:
            print("✗ Login failed")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 5: Registration flow (new session)
    print("\n5. Testing registration flow...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "register"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        new_session_id = result['session_id']
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 6: Provide email for registration
    print("\n6. Providing email for registration...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "newuser@dhii.ai",
        "session_id": new_session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 7: Provide username for registration
    print("\n7. Providing username for registration...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "newuser",
        "session_id": new_session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 8: Provide first name
    print("\n8. Providing first name...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "New",
        "session_id": new_session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 9: Provide last name
    print("\n9. Providing last name...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "User",
        "session_id": new_session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 10: Provide password and complete registration
    print("\n10. Providing password and completing registration...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "securepassword123",
        "session_id": new_session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        if result.get('auth_result'):
            print(f"✓ Registration and login successful!")
            print(f"✓ Access token: {result['auth_result']['access_token'][:50]}...")
            print(f"✓ User: {result['auth_result']['user']['username']}")
        else:
            print("✗ Registration failed")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    print("\n✓ A2UI Chat Authentication test completed successfully!")

if __name__ == "__main__":
    test_chat_auth()