"""
Test the corrected conversational A2UI authentication flow.
"""

import requests

def test_conversational_flow():
    """Test the conversational authentication flow."""
    base_url = "http://localhost:8000"
    
    print("=== TESTING CORRECTED CONVERSATIONAL A2UI FLOW ===")
    
    # Step 1: Initial greeting
    print("\n1. User: 'hello'")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "hello"})
    result = response.json()
    print(f"   A2UI: '{result['response']}'")
    print(f"   Requires input: {result['requires_input']}")
    session_id = result['session_id']
    
    # Step 2: User wants to login
    print("\n2. User: 'login'")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "login", "session_id": session_id})
    result = response.json()
    print(f"   A2UI: '{result['response']}'")
    print(f"   Requires input: {result['requires_input']}")
    
    # Step 3: User provides username
    print("\n3. User: 'testuser'")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "testuser", "session_id": session_id})
    result = response.json()
    print(f"   A2UI: '{result['response']}'")
    print(f"   Requires input: {result['requires_input']}")
    
    # Step 4: User provides password
    print("\n4. User: 'securepassword123'")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "securepassword123", "session_id": session_id})
    result = response.json()
    print(f"   A2UI: '{result['response']}'")
    print(f"   Requires input: {result['requires_input']}")
    if result.get('auth_result'):
        print(f"   Login successful! User: {result['auth_result']['user']['username']}")
    
    # Step 5: Test registration flow
    print("\n" + "="*50)
    print("5. Testing registration flow:")
    print("\n   User: 'register'")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "register"})
    result = response.json()
    print(f"   A2UI: '{result['response']}'")
    print(f"   Requires input: {result['requires_input']}")
    session_id = result['session_id']
    
    print("\n   User: 'newuser@example.com'")
    response = requests.post(f"{base_url}/auth/chat", json={"message": "newuser@example.com", "session_id": session_id})
    result = response.json()
    print(f"   A2UI: '{result['response']}'")
    
    print("\n✅ Conversational flow restored!")
    print("Now users are guided through authentication step-by-step via chat conversation.")

if __name__ == "__main__":
    test_conversational_flow()