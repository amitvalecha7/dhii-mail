#!/usr/bin/env python3
"""
Framework 2.0: Plugin Development CLI
Standardized CLI for plugin development, validation, and deployment
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import logging

from a2ui_integration.core.plugin_template import PluginTemplateGenerator
from a2ui_integration.core.plugin_manager import PluginManager, PluginValidationError, PluginLoadError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_plugin(args):
    """Create a new plugin with standardized structure"""
    plugin_id = args.plugin_id
    plugin_type = args.type
    name = args.name or plugin_id.replace("_", " ").title()
    description = args.description or f"{name} plugin"
    
    logger.info(f"Creating {plugin_type} plugin: {plugin_id}")
    
    try:
        # Generate template
        template_data = PluginTemplateGenerator.generate_plugin(
            plugin_id=plugin_id,
            plugin_type=plugin_type,
            name=name,
            description=description,
            author=args.author
        )
        
        # Create plugin directory
        plugin_dir = PluginTemplateGenerator.create_plugin_directory(
            plugin_id, template_data, Path(args.output_dir)
        )
        
        logger.info(f"✅ Plugin created successfully at: {plugin_dir}")
        logger.info(f"Files created:")
        for filename in template_data["files"].keys():
            logger.info(f"  - {plugin_dir / filename}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to create plugin: {e}")
        return 1

def validate_plugin(args):
    """Validate plugin structure and manifest"""
    plugin_path = Path(args.plugin_path)
    
    logger.info(f"Validating plugin: {plugin_path}")
    
    # Validate structure
    errors = PluginTemplateGenerator.validate_plugin_structure(plugin_path)
    
    if errors:
        logger.error("❌ Plugin validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1
    
    # Try to load manifest
    try:
        manager = PluginManager()
        manifest = manager.load_manifest(plugin_path.name)
        logger.info(f"✅ Manifest validated successfully")
        logger.info(f"Plugin: {manifest.name} ({manifest.version})")
        logger.info(f"Type: {manifest.plugin_type.value}")
        logger.info(f"Capabilities: {len(manifest.capabilities)}")
        for cap in manifest.capabilities:
            logger.info(f"  - {cap.id}: {cap.name}")
        
    except PluginValidationError as e:
        logger.error(f"❌ Manifest validation failed: {e}")
        return 1
    
    # Try to load plugin
    if args.load_test:
        try:
            manager = PluginManager(plugin_path.parent)
            plugin = manager.load_plugin(plugin_path.name)
            logger.info(f"✅ Plugin loaded successfully")
            
        except PluginLoadError as e:
            logger.error(f"❌ Plugin loading failed: {e}")
            return 1
    
    logger.info("✅ Plugin validation passed")
    return 0

def list_plugins(args):
    """List available plugins"""
    plugins_dir = Path(args.plugins_dir)
    
    if not plugins_dir.exists():
        logger.error(f"Plugins directory {plugins_dir} does not exist")
        return 1
    
    manager = PluginManager(str(plugins_dir))
    plugins = manager.discover_plugins()
    
    if not plugins:
        logger.info("No plugins found")
        return 0
    
    logger.info(f"Found {len(plugins)} plugins:")
    
    for plugin_id in plugins:
        try:
            manifest = manager.load_manifest(plugin_id)
            logger.info(f"  - {plugin_id}: {manifest.name} ({manifest.version}) - {manifest.plugin_type.value}")
            if args.verbose:
                logger.info(f"    {manifest.description}")
                logger.info(f"    Capabilities: {len(manifest.capabilities)}")
        except Exception as e:
            logger.warning(f"  - {plugin_id}: Failed to load manifest - {e}")
    
    return 0

def migrate_plugin(args):
    """Migrate legacy plugin to Framework 2.0"""
    plugin_path = Path(args.plugin_path)
    
    logger.info(f"Migrating plugin: {plugin_path}")
    
    # Check if it's a legacy plugin
    plugin_file = plugin_path / f"{plugin_path.name}_plugin.py"
    if not plugin_file.exists():
        logger.error(f"Plugin file not found: {plugin_file}")
        return 1
    
    # Read existing plugin
    content = plugin_file.read_text()
    
    # Check if it has register function
    if "def register(" not in content:
        logger.error("Legacy plugin missing register function")
        return 1
    
    # Create manifest.json
    manifest = {
        "id": plugin_path.name,
        "name": plugin_path.name.replace("_", " ").title(),
        "version": "1.0.0",
        "plugin_type": "integration",  # Default type
        "author": "dhii-team",
        "description": f"{plugin_path.name} plugin (migrated)",
        "capabilities": [],  # Will be populated manually
        "dependencies": [],
        "sandbox_config": {
            "allowed_modules": ["logging", "typing"],
            "max_memory_mb": 100,
            "timeout_seconds": 30
        }
    }
    
    manifest_file = plugin_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    
    logger.info(f"✅ Created manifest.json at: {manifest_file}")
    logger.info("⚠️  Note: You may need to:")
    logger.info("  1. Update the plugin_type in manifest.json")
    logger.info("  2. Add capabilities to manifest.json")
    logger.info("  3. Update the register function signature to register_plugin")
    logger.info("  4. Implement PluginInterface")
    
    return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Framework 2.0 Plugin Development CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new integration plugin
  python -m a2ui_integration.cli create-plugin --id email --type integration
  
  # Validate a plugin
  python -m a2ui_integration.cli validate --path ./plugins/email
  
  # List all plugins
  python -m a2ui_integration.cli list
  
  # Migrate legacy plugin
  python -m a2ui_integration.cli migrate --path ./plugins/email
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create plugin command
    create_parser = subparsers.add_parser("create-plugin", help="Create new plugin")
    create_parser.add_argument("--id", "--plugin-id", dest="plugin_id", required=True,
                              help="Plugin ID (alphanumeric with underscores/dashes)")
    create_parser.add_argument("--type", required=True, 
                              choices=["integration", "transport", "intelligence", "ui", "persistence", "utility"],
                              help="Plugin type")
    create_parser.add_argument("--name", help="Plugin name (default: ID formatted)")
    create_parser.add_argument("--description", help="Plugin description")
    create_parser.add_argument("--author", default="dhii-team", help="Plugin author")
    create_parser.add_argument("--output-dir", default="plugins", help="Output directory")
    create_parser.set_defaults(func=create_plugin)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate plugin")
    validate_parser.add_argument("--path", "--plugin-path", dest="plugin_path", required=True,
                                  help="Path to plugin directory")
    validate_parser.add_argument("--load-test", action="store_true",
                                help="Test loading the plugin")
    validate_parser.set_defaults(func=validate_plugin)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List plugins")
    list_parser.add_argument("--plugins-dir", default="plugins", help="Plugins directory")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    list_parser.set_defaults(func=list_plugins)
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Migrate legacy plugin")
    migrate_parser.add_argument("--path", "--plugin-path", dest="plugin_path", required=True,
                               help="Path to legacy plugin directory")
    migrate_parser.set_defaults(func=migrate_plugin)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())