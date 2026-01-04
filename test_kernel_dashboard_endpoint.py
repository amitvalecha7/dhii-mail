#!/usr/bin/env python3
"""
Test the actual /api/a2ui/kernel/dashboard endpoint
"""

import asyncio
import json
from datetime import datetime

async def test_kernel_dashboard_endpoint():
    """Test the kernel dashboard endpoint directly"""
    print("=== Testing Kernel Dashboard Endpoint ===")
    
    try:
        # Import the router function directly
        from a2ui_integration.a2ui_router import get_kernel_dashboard
        
        # Call the endpoint function
        result = await get_kernel_dashboard()
        
        print("✅ Kernel Dashboard endpoint test passed")
        print(f"Status: {result['status']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Dashboard data keys: {list(result['dashboard'].keys())}")
        print(f"A2UI JSON length: {len(result['a2ui_json'])} characters")
        
        # Parse and validate A2UI JSON
        a2ui_components = json.loads(result['a2ui_json'])
        print(f"A2UI components: {len(a2ui_components)}")
        
        # Verify adjacency list operations
        operations = [list(comp.keys())[0] for comp in a2ui_components]
        print(f"Operations: {operations}")
        
        # Check for required operations
        required_ops = ['beginRendering', 'surfaceUpdate', 'dataModelUpdate']
        missing_ops = [op for op in required_ops if op not in operations]
        
        if not missing_ops:
            print("✅ All required adjacency list operations present")
        else:
            print(f"⚠️  Missing operations: {missing_ops}")
        
        return {
            "status": "success",
            "components_count": len(a2ui_components),
            "json_length": len(result['a2ui_json']),
            "operations": operations,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        print(f"❌ Kernel Dashboard endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 Testing Kernel Dashboard Endpoint")
    result = asyncio.run(test_kernel_dashboard_endpoint())
    print(f"\n=== Endpoint Test Summary ===")
    print(f"Status: {result['status']}")
    print(f"Components: {result['components_count']}")
    print(f"JSON Length: {result['json_length']} characters")
    print(f"Operations: {result['operations']}")