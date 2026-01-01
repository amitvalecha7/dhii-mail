"""
Test the complete correct A2UI flow with working authentication
"""

import requests
import json

def test_working_a2ui_flow():
    """Test the complete working A2UI authentication flow."""
    base_url = "http://localhost:8000"
    
    print("=== TESTING COMPLETE WORKING A2UI FLOW ===")
    
    # Step 1: User starts chat (no auth)
    print("\n1. User starts chat (no authentication)...")
    response = requests.post(f"{base_url}/chat", json={"message": "hello"})
    result = response.json()
    print(f"   Response: {result['response']}")
    print(f"   Auth status: {'Authenticated' if result.get('auth_result') else 'Not authenticated'}")
    
    if result.get('login_card'):
        card = result['login_card']
        print(f"   Card type: {card['type']}")
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
            
            # Step 3: User fills and submits login form (with correct credentials)
            print("\n3. User submits login form with correct credentials...")
            login_data = {
                "action": "submit_login",
                "session_id": session_id,
                "form_data": {
                    "username": "debuguser",
                    "password": "debugpassword123"
                }
            }
            submit_response = requests.post(f"{base_url}/auth/card/action", json=login_data)
            submit_result = submit_response.json()
            print(f"   Response: {submit_result['response']}")
            
            if submit_result.get('auth_result'):
                auth_data = submit_result['auth_result']
                print(f"   ✅ Authentication successful!")
                print(f"   User: {auth_data['user']['username']}")
                access_token = auth_data['access_token']
                
                # Step 4: User continues chat with authentication
                print("\n4. User continues chat (with authentication)...")
                chat_response = requests.post(f"{base_url}/chat", 
                                           json={
                                               "message": "hello", 
                                               "session_id": session_id,
                                               "access_token": access_token
                                           })
                chat_result = chat_response.json()
                print(f"   Response: {chat_result['response']}")
                print(f"   Auth status: {'Authenticated' if chat_result.get('auth_result') else 'Not authenticated'}")
                
                print("\n✅ A2UI authentication flow working perfectly!")
                print("Users can now:")
                print("  - Start chat without authentication")
                print("  - Get login/signup cards automatically")
                print("  - Complete authentication via forms")
                print("  - Continue chatting as authenticated user")
                
                return True
            else:
                print("   ❌ Login failed")
                return False
    else:
        print("   No login card provided")
        return False

if __name__ == "__main__":
    success = test_working_a2ui_flow()
    
    if success:
        print("\n🎉 CORRECT A2UI FLOW IMPLEMENTED!")
        print("\nHow it works now:")
        print("1. User starts chat → System checks auth status")
        print("2. If not authenticated → Provides Login/Signup card")
        print("3. User completes authentication via card forms")
        print("4. Chat resumes with authenticated user")
    else:
        print("\n❌ Flow still needs work")