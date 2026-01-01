"""
Test the correct A2UI authentication flow:
1. User starts chat
2. System checks authentication status
3. If not authenticated → provides Login/Signup card
4. User completes authentication via card
5. Chat resumes with authenticated user
"""

import requests
import json

def test_correct_a2ui_flow():
    """Test the complete A2UI authentication flow."""
    base_url = "http://localhost:8000"
    
    print("=== TESTING CORRECT A2UI AUTHENTICATION FLOW ===")
    
    # Step 1: User starts chat (no auth token)
    print("\n1. User starts chat (no authentication)...")
    response = requests.post(f"{base_url}/chat", json={"message": "hello"})
    result = response.json()
    print(f"   Response: {result['response']}")
    print(f"   Auth status: {'Authenticated' if result.get('auth_result') else 'Not authenticated'}")
    
    if result.get('login_card'):
        card = result['login_card']
        print(f"   Card type: {card['type']}")
        print(f"   Title: {card['title']}")
        print(f"   Available actions: {[action['action'] for action in card['actions']]}")
        session_id = result['session_id']
        
        # Step 2: User chooses to login
        print("\n2. User clicks 'Sign In' button...")
        action_response = requests.post(f"{base_url}/auth/card/action", 
                                    json={"action": "show_login", "session_id": session_id})
        action_result = action_response.json()
        print(f"   Response: {action_result['response']}")
        
        if action_result.get('login_card'):
            login_card = action_result['login_card']
            print(f"   Login form provided with fields: {[field['name'] for field in login_card['fields']]}")
            
            # Step 3: User fills and submits login form
            print("\n3. User submits login form...")
            login_data = {
                "action": "submit_login",
                "session_id": session_id,
                "form_data": {
                    "username": "testuser",
                    "password": "securepassword123"
                }
            }
            submit_response = requests.post(f"{base_url}/auth/card/action", json=login_data)
            submit_result = submit_response.json()
            print(f"   Response: {submit_result['response']}")
            
            if submit_result.get('auth_result'):
                auth_data = submit_result['auth_result']
                print(f"   ✅ Authentication successful!")
                print(f"   User: {auth_data['user']['username']}")
                print(f"   Access token received: {auth_data['access_token'][:20]}...")
                
                # Step 4: User continues chat with authentication
                print("\n4. User continues chat (with authentication)...")
                chat_response = requests.post(f"{base_url}/chat", 
                                           json={
                                               "message": "hello", 
                                               "session_id": session_id,
                                               "access_token": auth_data['access_token']
                                           })
                chat_result = chat_response.json()
                print(f"   Response: {chat_result['response']}")
                print(f"   Auth status: {'Authenticated' if chat_result.get('auth_result') else 'Not authenticated'}")
                
                return auth_data['access_token']
            else:
                print("   ❌ Login failed - invalid credentials")
                return None
    else:
        print("   No login card provided")
        return None

def test_registration_flow():
    """Test the registration flow."""
    base_url = "http://localhost:8000"
    
    print("\n" + "="*60)
    print("=== TESTING REGISTRATION FLOW ===")
    
    # Start chat without authentication
    response = requests.post(f"{base_url}/chat", json={"message": "hello"})
    result = response.json()
    session_id = result['session_id']
    
    # Choose registration
    print("\n1. User clicks 'Create Account'...")
    action_response = requests.post(f"{base_url}/auth/card/action", 
                                  json={"action": "show_register", "session_id": session_id})
    action_result = action_response.json()
    print(f"   Response: {action_result['response']}")
    
    if action_result.get('login_card'):
        reg_card = action_result['login_card']
        print(f"   Registration form provided with fields: {[field['name'] for field in reg_card['fields']]}")
        
        # Submit registration form
        print("\n2. User submits registration form...")
        reg_data = {
            "action": "submit_register",
            "session_id": session_id,
            "form_data": {
                "email": "newuser@example.com",
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password": "newpassword123"
            }
        }
        submit_response = requests.post(f"{base_url}/auth/card/action", json=reg_data)
        submit_result = submit_response.json()
        print(f"   Response: {submit_result['response']}")
        
        if submit_result.get('auth_result'):
            auth_data = submit_result['auth_result']
            print(f"   ✅ Registration successful!")
            print(f"   User: {auth_data['user']['username']}")
            return auth_data['access_token']
        else:
            print("   ❌ Registration failed")
            return None

if __name__ == "__main__":
    # Test login flow
    login_token = test_correct_a2ui_flow()
    
    # Test registration flow
    reg_token = test_registration_flow()
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"Login token: {'✅ Received' if login_token else '❌ Failed'}")
    print(f"Registration token: {'✅ Received' if reg_token else '❌ Failed'}")
    
    if login_token or reg_token:
        print("\n✅ A2UI authentication flow working correctly!")
        print("Users can now authenticate via login cards and continue chatting.")
    else:
        print("\n❌ Flow needs debugging")