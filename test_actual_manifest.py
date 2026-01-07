#!/usr/bin/env python3
"""Test with actual test_plugin manifest"""

import sys
sys.path.insert(0, '/root/dhii-mail')

from a2ui_integration.framework.types import PluginManifest
import json

# Load actual test_plugin manifest
with open('/root/dhii-mail/plugins/test_plugin/manifest.json', 'r') as f:
    manifest_data = json.load(f)

print("Raw manifest data:")
print(f"Capabilities: {manifest_data['capabilities']}")

# Test validation
manifest = PluginManifest(**manifest_data)
print(f"\nValidated manifest:")
print(f"Capabilities: {manifest.capabilities}")
print(f"First capability type: {type(manifest.capabilities[0])}")
print(f"First capability ID: {manifest.capabilities[0].id}")
print(f"First capability name: {manifest.capabilities[0].name}")