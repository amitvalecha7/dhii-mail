# Framework 2.0: CLI Module

"""
Developer tools CLI for Plugin Framework 2.0

This module provides command-line tools for:
- Creating new plugins with V2 structure
- Validating plugin manifests and structure
- Listing and managing plugins
- Migrating plugins from V1 to V2
- Bundling plugins for distribution
- Testing plugin capabilities

Usage:
    python -m a2ui_integration.cli [command] [options]
    
Commands:
    create      Create a new plugin
    validate    Validate plugin structure and manifest
    list        List plugins
    migrate     Migrate plugin to V2 format
    bundle      Bundle plugin for distribution
    test        Test plugin capabilities
"""

from .main import main

__all__ = ['main']