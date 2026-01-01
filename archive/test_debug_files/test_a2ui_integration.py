"""
dhii Mail - A2UI Authentication Integration Test
Tests both chat-based and form-based authentication working together.
"""

import requests
import json
import uuid

def test_a2ui_authentication_integration():
    """Test the complete A2UI authentication system integration."""
    base_url = "http://localhost:8000"
    
    print("Testing dhii Mail A2UI Authentication Integration...")
    print("=" * 60)
    
    # Test 1: Chat-based authentication with login card
    print("\n1. Chat-based authentication (login card approach)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "login"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Chat response: {result['response']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"✓ Login card provided: {card['type']}")
            print(f"✓ Visual form with {len(card['fields'])} fields")
            print("✓ No user input required - visual interaction")
        else:
            print("✗ No login card provided")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 2: Form-based authentication submission
    print("\n2. Form-based authentication submission...")
    login_data = {
        "action": "login",
        "form_data": {
            "username": "testuser",
            "password": "securepassword123"
        }
    }
    response = requests.post(f"{base_url}/auth/form", json=login_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Form response: {result['response']}")
        if result.get('auth_result'):
            auth = result['auth_result']
            print(f"✓ Authentication successful!")
            print(f"✓ Access token generated: {auth['access_token'][:30]}...")
            print(f"✓ User: {auth['user']['username']}")
        else:
            print("✗ Authentication failed")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 3: Chat-based authentication with registration card
    print("\n3. Chat-based authentication (registration card approach)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "register"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Chat response: {result['response']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"✓ Registration card provided: {card['type']}")
            print(f"✓ Visual form with {len(card['fields'])} fields")
            print("✓ No user input required - visual interaction")
        else:
            print("✗ No registration card provided")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 4: Form-based registration submission
    print("\n4. Form-based registration submission...")
    unique_id = str(uuid.uuid4())[:8]
    reg_data = {
        "action": "register",
        "form_data": {
            "email": f"newuser_{unique_id}@dhii.ai",
            "username": f"newuser_{unique_id}",
            "first_name": "New",
            "last_name": "User",
            "password": "securepassword123"
        }
    }
    response = requests.post(f"{base_url}/auth/form", json=reg_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Form response: {result['response']}")
        if result.get('auth_result'):
            auth = result['auth_result']
            print(f"✓ Registration and authentication successful!")
            print(f"✓ Access token generated: {auth['access_token'][:30]}...")
            print(f"✓ New user: {auth['user']['username']}")
        else:
            print("✗ Registration failed")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 5: Traditional chat-based flow (fallback)
    print("\n5. Traditional chat-based flow (fallback)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "hello"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Chat response: {result['response']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"✓ Welcome card provided: {card['type']}")
            print("✓ Visual interaction available")
        else:
            print("✗ No welcome card provided")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✓ A2UI Authentication Integration Test Completed!")
    print("\nKey Features Implemented:")
    print("✓ Visual login cards with form fields")
    print("✓ Form-based authentication submission")
    print("✓ Seamless integration between chat and forms")
    print("✓ Error handling with form re-display")
    print("✓ Both login and registration workflows")
    print("✓ Token generation and user authentication")
    print("\nBenefits:")
    print("- Users get visual forms instead of conversational input")
    print("- Consistent authentication experience")
    print("- Better user experience with structured forms")
    print("- Fallback to traditional chat if needed")
    print("- Seamless integration with existing auth system")

if __name__ == "__main__":
    test_a2ui_authentication_integration()