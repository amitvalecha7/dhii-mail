#!/usr/bin/env python3
"""Check Pydantic version and test validator"""

import pydantic
print(f"Pydantic version: {pydantic.VERSION}")

from a2ui_integration.framework.types import PluginManifest

# Test with simple data
test_data = {
    "id": "test",
    "name": "Test Plugin",
    "version": "1.0.0",
    "plugin_type": "integration",
    "author": "Test",
    "description": "Test plugin",
    "capabilities": [
        {
            "id": "test.capability",
            "name": "Test Capability",
            "description": "Test capability",
            "capability_type": "action"
        }
    ]
}

try:
    manifest = PluginManifest(**test_data)
    print(f"✅ Manifest created successfully")
    print(f"Capabilities: {manifest.capabilities}")
    print(f"First capability type: {type(manifest.capabilities[0])}")
    print(f"First capability ID: {manifest.capabilities[0].id}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()