#!/usr/bin/env python3
"""
Debug test script to check search results format
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginConfig, PluginType, Capability

async def debug_search():
    """Debug search functionality"""
    print("🔍 Debugging Search Functionality...")
    
    kernel = Kernel()
    
    # Register email plugin
    email_capabilities = [
        Capability(
            id="email.send",
            domain="communication",
            name="Send Email",
            description="Send an email message",
            input_schema={"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "message_id": {"type": "string"}}},
            side_effects=["email_sent"],
            requires_auth=False
        )
    ]
    
    email_config = PluginConfig(
        id="email",
        name="Email Plugin",
        version="1.0.0",
        description="Email communication plugin",
        type=PluginType.EMAIL,
        author="System",
        enabled=False,
        capabilities=email_capabilities,
        dependencies=[]
    )
    
    await kernel.register_plugin(email_config)
    await kernel.enable_plugin("email")
    
    # Test search
    search_results = await kernel.search("email")
    print(f"Search results type: {type(search_results)}")
    print(f"Search results length: {len(search_results)}")
    
    for i, result in enumerate(search_results):
        print(f"Result {i}: type={type(result)}, value={result}")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(debug_search())