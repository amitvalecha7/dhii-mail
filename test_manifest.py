#!/usr/bin/env python3
"""Test manifest validation"""

import sys
sys.path.insert(0, '/root/dhii-mail')

from a2ui_integration.framework.types import PluginManifest
import json

# Test with email plugin manifest
with open('/root/dhii-mail/plugins/email/manifest.json', 'r') as f:
    manifest_data = json.load(f)

print("Raw manifest data:")
print(f"Capabilities: {manifest_data['capabilities']}")
print(f"Type of first capability: {type(manifest_data['capabilities'][0])}")

# Test validation
manifest = PluginManifest(**manifest_data)
print(f"\nValidated manifest:")
print(f"Capabilities: {manifest.capabilities}")
print(f"Type of first capability: {type(manifest.capabilities[0])}")
print(f"First capability ID: {manifest.capabilities[0].id}")
print(f"First capability type: {manifest.capabilities[0].capability_type}")