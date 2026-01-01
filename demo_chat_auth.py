"""
dhii Mail - A2UI Chat Authentication Demo
Interactive demo showing chat-based authentication.
"""

import requests
import json

def interactive_chat_auth():
    """Interactive chat-based authentication demo."""
    base_url = "http://localhost:8000"
    session_id = None
    
    print("🤖 Welcome to dhii Mail A2UI Chat Authentication!")
    print("You can chat naturally to login or register.")
    print("Type 'quit' to exit.\n")
    
    while True:
        # Get user input
        if not session_id:
            message = input("💬 You: ").strip()
        else:
            message = input("💬 You: ").strip()
        
        if message.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if not message:
            continue
        
        # Send message to chat auth endpoint
        try:
            payload = {"message": message}
            if session_id:
                payload["session_id"] = session_id
            
            response = requests.post(f"{base_url}/auth/chat", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"🤖 Assistant: {result['response']}")
                
                # Update session ID
                session_id = result.get('session_id')
                
                # Check if authentication was successful
                if result.get('auth_result'):
                    auth_result = result['auth_result']
                    print(f"\n✅ Authentication successful!")
                    print(f"👤 User: {auth_result['user']['username']}")
                    print(f"📧 Email: {auth_result['user']['email']}")
                    print(f"🔑 Access Token: {auth_result['access_token'][:50]}...")
                    print(f"🔄 Refresh Token: {auth_result['refresh_token'][:50]}...")
                    
                    # Reset for next interaction
                    session_id = None
                    print("\n" + "="*50)
                    print("You can start a new authentication session!")
                    print("="*50 + "\n")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the server is running on http://localhost:8000")

if __name__ == "__main__":
    interactive_chat_auth()