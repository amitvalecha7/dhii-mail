#!/usr/bin/env python3
"""
Test script for chat API email integration
"""

import requests
import json

def test_chat_email_integration():
    """Test the chat API email integration"""
    base_url = "http://localhost:8006"
    
    print("🧪 Testing Chat API Email Integration")
    print("=" * 50)
    
    # Test 1: Check root endpoint
    print("\n1. Testing chat API root...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print(f"   ✅ Chat API root working")
        else:
            print(f"   ❌ Root check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root check error: {e}")
    
    # Test 2: Test auth status
    print("\n2. Testing auth status...")
    try:
        response = requests.get(f"{base_url}/api/auth/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Auth status endpoint working")
            print(f"   🔐 Authenticated: {data.get('is_authenticated', False)}")
        else:
            print(f"   ⚠️  Auth status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Auth status error: {e}")
    
    # Test 3: Test chat processing with email search
    print("\n3. Testing email search...")
    try:
        response = requests.post(
            f"{base_url}/api/chat/process",
            json={"message": "show me emails from john", "session_id": "test-session"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Email search endpoint working")
            print(f"   💬 Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"   ⚠️  Email search status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Email search error: {e}")
    
    # Test 4: Test email analysis functionality
    print("\n4. Testing email analysis...")
    try:
        response = requests.post(
            f"{base_url}/api/chat/process",
            json={"message": "analyze my emails", "session_id": "test-session"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Email analysis endpoint working")
            print(f"   💬 Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"   ⚠️  Email analysis status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Email analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Chat API email integration test completed!")

if __name__ == "__main__":
    test_chat_email_integration()