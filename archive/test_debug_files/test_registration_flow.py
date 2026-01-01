"""
dhii Mail - A2UI Chat Authentication Test (Registration Focus)
Tests the registration flow specifically.
"""

import requests
import json
import uuid

def test_registration_flow():
    """Test the A2UI chat-based registration flow."""
    base_url = "http://localhost:8000"
    
    print("Testing dhii Mail A2UI Chat Registration Flow...")
    
    # Generate unique test data
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"testuser_{unique_id}@dhii.ai"
    test_username = f"testuser_{unique_id}"
    
    print(f"Using unique test data:")
    print(f"Email: {test_email}")
    print(f"Username: {test_username}")
    
    # Test 1: Start registration
    print("\n1. Starting registration flow...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "register"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        session_id = result['session_id']
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 2: Provide email
    print("\n2. Providing email...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": test_email,
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 3: Provide username
    print("\n3. Providing username...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": test_username,
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 4: Provide first name
    print("\n4. Providing first name...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "Test",
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 5: Provide last name
    print("\n5. Providing last name...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "User",
        "session_id": session_id
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    # Test 6: Provide password and complete registration
    print("\n6. Providing password and completing registration...")
    response = requests.post(f"{base_url}/auth/chat", json={
        "message": "securepassword123",
        "session_id": session_id
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
            if 'error' in result:
                print(f"Error details: {result['error']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return
    
    print("\n✓ Registration flow test completed!")

if __name__ == "__main__":
    test_registration_flow()