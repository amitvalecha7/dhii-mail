"""
Debug the registration issue - user created but response says failure
"""

import requests
import json

def debug_registration_response():
    """Debug why registration creates user but returns failure."""
    base_url = "http://localhost:8000"
    
    print("=== DEBUGGING REGISTRATION RESPONSE LOGIC ===")
    
    # Test registration with debug
    session_id = "test-session"
    reg_data = {
        "action": "submit_register",
        "session_id": session_id,
        "form_data": {
            "email": "debuguser@example.com",
            "username": "debuguser",
            "first_name": "Debug",
            "last_name": "User",
            "password": "debugpassword123"
        }
    }
    
    print(f"Submitting registration: {json.dumps(reg_data, indent=2)}")
    
    response = requests.post(f"{base_url}/auth/card/action", json=reg_data)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    try:
        result = response.json()
        print(f"Response body: {json.dumps(result, indent=2)}")
        
        if result.get('auth_result'):
            print("✅ Registration successful!")
            print(f"User: {result['auth_result']['user']}")
        else:
            print("❌ Registration failed")
            print(f"Response message: {result['response']}")
            
            # Check if user was actually created
            print("\nChecking if user was created despite failure response...")
            login_data = {
                "action": "submit_login",
                "session_id": session_id,
                "form_data": {
                    "username": "debuguser",
                    "password": "debugpassword123"
                }
            }
            login_response = requests.post(f"{base_url}/auth/card/action", json=login_data)
            login_result = login_response.json()
            
            if login_result.get('auth_result'):
                print("✅ User was actually created! Login successful.")
            else:
                print("❌ User was not created.")
                
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    debug_registration_response()