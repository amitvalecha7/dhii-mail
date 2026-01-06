#!/usr/bin/env python3
"""
Test Tool Registry Pattern Implementation
Verifies that plugin registry endpoints work correctly
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any

async def test_plugin_registry():
    """Test plugin registry endpoints"""
    print("🧪 Testing Tool Registry Pattern Implementation...")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Test 1: List all plugins
        print("\n1. Testing /api/v1/plugins endpoint...")
        try:
            response = await client.get(f"{base_url}/api/v1/plugins")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: Found {len(data.get('plugins', []))} plugins")
                for plugin in data.get('plugins', []):
                    print(f"      - {plugin['name']} ({plugin['id']})")
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test 2: Get specific plugin
        print("\n2. Testing /api/v1/plugins/{plugin_id} endpoint...")
        try:
            response = await client.get(f"{base_url}/api/v1/plugins/com.dhiimail.marketing")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                plugin = response.json()
                print(f"   ✅ Success: Found plugin '{plugin['name']}'")
                print(f"      Description: {plugin['description']}")
                print(f"      Version: {plugin['version']}")
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test 3: Get non-existent plugin
        print("\n3. Testing 404 handling for non-existent plugin...")
        try:
            response = await client.get(f"{base_url}/api/v1/plugins/non.existent.plugin")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ✅ Success: Correctly returned 404")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test 4: Direct plugin registry service access (if available)
        print("\n4. Testing direct plugin registry service...")
        try:
            response = await client.get("http://plugin-registry:5000/api/v1/plugins", timeout=5.0)
            print(f"   Direct Service Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Direct service is accessible")
            else:
                print(f"   ⚠️  Direct service returned: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Direct service not accessible: {e}")
            print(f"   ℹ️  Using fallback data (this is expected in development)")
        
        print("\n🎉 All Tool Registry tests passed!")
        return True

def main():
    """Main test runner"""
    try:
        success = asyncio.run(test_plugin_registry())
        if success:
            print("\n✅ Tool Registry Pattern Implementation is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Tool Registry Pattern Implementation has issues!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()