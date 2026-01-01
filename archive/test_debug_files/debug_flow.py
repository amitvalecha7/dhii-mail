"""
Debug the current A2UI authentication flow to understand the issue.
"""

import requests
import json

def debug_current_flow():
    """Debug the current authentication flow step by step."""
    base_url = "http://localhost:8000"
    
    print("=== DEBUGGING CURRENT A2UI AUTHENTICATION FLOW ===")
    
    # Step 1: User initiates authentication
    print("\n1. User says 'hello' (initial greeting)...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "hello"})
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {result['response']}")
        print(f"   Requires input: {result['requires_input']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"   Card type: {card['type']}")
            print(f"   Available actions: {[action['action'] for action in card['actions']]}")
    
    # Step 2: User says "login"
    print("\n2. User says 'login'...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "login"})
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {result['response']}")
        print(f"   Requires input: {result['requires_input']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"   Card type: {card['type']}")
            print(f"   Title: {card['title']}")
            if 'fields' in card:
                print(f"   Fields: {[field['name'] for field in card['fields']]}")
            print(f"   Available actions: {[action['action'] for action in card['actions']]}")
        else:
            print("   No login card provided")
            print(f"   Session step would be: {result.get('session_id', 'N/A')}")
    
    # Step 3: User says "register"
    print("\n3. User says 'register'...")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "register"})
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {result['response']}")
        print(f"   Requires input: {result['requires_input']}")
        if result.get('login_card'):
            card = result['login_card']
            print(f"   Card type: {card['type']}")
            print(f"   Title: {card['title']}")
            if 'fields' in card:
                print(f"   Fields: {[field['name'] for field in card['fields']]}")
            print(f"   Available actions: {[action['action'] for action in card['actions']]}")
        else:
            print("   No login card provided")
    
    # Step 4: Test form submission
    print("\n4. Testing form submission...")
    form_data = {
        "action": "login",
        "form_data": {
            "username": "testuser",
            "password": "securepassword123"
        }
    }
    response = requests.post(f"{base_url}/auth/form", json=form_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {result['response']}")
        print(f"   Success: {'auth_result' in result}")
        if not result.get('auth_result') and result.get('login_card'):
            print("   Error form provided for retry")

if __name__ == "__main__":
    debug_current_flow()