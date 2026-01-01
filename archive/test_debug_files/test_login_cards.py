"""
dhii Mail - A2UI Login Card Test
Tests the new login card functionality that provides visual authentication forms.
"""

import requests
import json

def test_login_cards():
    """Test the A2UI login card functionality."""
    base_url = "http://localhost:8000"
    
    print("Testing dhii Mail A2UI Login Card Functionality...")
    
    # Test 1: Initial greeting should show welcome card
    print("\n1. Testing initial greeting (should show welcome card)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "hello"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"✓ Login card type: {card['type']}")
            print(f"✓ Title: {card['title']}")
            print(f"✓ Message: {card['message']}")
            print(f"✓ Actions: {len(card['actions'])} available")
            for action in card['actions']:
                print(f"  - {action['label']} ({action['action']})")
        else:
            print("✗ No login card provided")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 2: Request login should show login form
    print("\n2. Testing login request (should show login form)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "login"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"✓ Login card type: {card['type']}")
            print(f"✓ Title: {card['title']}")
            print(f"✓ Fields: {len(card['fields'])} fields")
            for field in card['fields']:
                print(f"  - {field['name']}: {field['type']} ({field['placeholder']})")
            print(f"✓ Actions: {len(card['actions'])} available")
            for action in card['actions']:
                print(f"  - {action['label']} ({action['action']})")
        else:
            print("✗ No login card provided")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 3: Request registration should show registration form
    print("\n3. Testing registration request (should show registration form)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "register"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"✓ Login card type: {card['type']}")
            print(f"✓ Title: {card['title']}")
            print(f"✓ Fields: {len(card['fields'])} fields")
            for field in card['fields']:
                print(f"  - {field['name']}: {field['type']} ({field['placeholder']})")
            print(f"✓ Actions: {len(card['actions'])} available")
            for action in card['actions']:
                print(f"  - {action['label']} ({action['action']})")
        else:
            print("✗ No login card provided")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 4: Test form submission for login
    print("\n4. Testing form submission for login...")
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
        print(f"✓ Response: {result['response']}")
        if result.get('auth_result'):
            auth = result['auth_result']
            print(f"✓ Login successful!")
            print(f"✓ Access token: {auth['access_token'][:50]}...")
            print(f"✓ User: {auth['user']['username']}")
        elif result.get('login_card'):
            print("✗ Login failed, showing error form")
        else:
            print("✗ Unexpected response format")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    # Test 5: Test form submission for registration
    print("\n5. Testing form submission for registration...")
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    reg_data = {
        "action": "register",
        "form_data": {
            "email": f"testuser_{unique_id}@dhii.ai",
            "username": f"testuser_{unique_id}",
            "first_name": "Test",
            "last_name": "User",
            "password": "securepassword123"
        }
    }
    response = requests.post(f"{base_url}/auth/form", json=reg_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Response: {result['response']}")
        if result.get('auth_result'):
            auth = result['auth_result']
            print(f"✓ Registration and login successful!")
            print(f"✓ Access token: {auth['access_token'][:50]}...")
            print(f"✓ User: {auth['user']['username']}")
        elif result.get('login_card'):
            print("✗ Registration failed, showing error form")
        else:
            print("✗ Unexpected response format")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    print("\n✓ A2UI Login Card functionality test completed!")
    print("\nKey Features:")
    print("- Visual login forms instead of conversational input")
    print("- Structured form fields with validation")
    print("- Error handling with form re-display")
    print("- Seamless integration with existing auth system")

if __name__ == "__main__":
    test_login_cards()