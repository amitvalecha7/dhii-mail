"""
Framework 2.0: CLI Main Entry Point
Developer tools for plugin development and management
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import a2ui_integration
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .commands import (
        create_plugin_command,
        validate_plugin_command,
        list_plugins_command,
        migrate_plugin_command,
        bundle_plugin_command,
        test_plugin_command
    )
except ImportError:
    # Fallback for when running as module
    from commands import (
        create_plugin_command,
        validate_plugin_command,
        list_plugins_command,
        migrate_plugin_command,
        bundle_plugin_command,
        test_plugin_command
    )

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Plugin Framework 2.0 CLI - Developer tools for plugin management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m a2ui_integration.cli create --name my_plugin --type integration
  python -m a2ui_integration.cli validate --path ./plugins/my_plugin
  python -m a2ui_integration.cli list --all
  python -m a2ui_integration.cli migrate --plugin email --target-version 2.0
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create plugin command
    create_parser = subparsers.add_parser('create', help='Create a new plugin')
    create_parser.add_argument('--name', required=True, help='Plugin name (directory name)')
    create_parser.add_argument('--type', choices=['integration', 'transport', 'intelligence', 'ui', 'persistence', 'utility'], 
                              required=True, help='Plugin type')
    create_parser.add_argument('--author', default='Unknown', help='Plugin author')
    create_parser.add_argument('--description', default='', help='Plugin description')
    create_parser.add_argument('--path', default='./plugins', help='Plugins directory path')
    
    # Validate plugin command
    validate_parser = subparsers.add_parser('validate', help='Validate plugin structure and manifest')
    validate_parser.add_argument('--path', required=True, help='Path to plugin directory')
    validate_parser.add_argument('--strict', action='store_true', help='Enable strict validation')
    
    # List plugins command
    list_parser = subparsers.add_parser('list', help='List plugins')
    list_parser.add_argument('--all', action='store_true', help='List all plugins including unloaded')
    list_parser.add_argument('--loaded', action='store_true', help='List only loaded plugins')
    list_parser.add_argument('--plugins-dir', default='./plugins', help='Plugins directory path')
    
    # Migrate plugin command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate plugin to V2 format')
    migrate_parser.add_argument('--plugin', required=True, help='Plugin ID to migrate')
    migrate_parser.add_argument('--target-version', default='2.0', help='Target framework version')
    migrate_parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    
    # Bundle plugin command
    bundle_parser = subparsers.add_parser('bundle', help='Bundle plugin for distribution')
    bundle_parser.add_argument('--plugin', required=True, help='Plugin ID to bundle')
    bundle_parser.add_argument('--output', default='./dist', help='Output directory')
    bundle_parser.add_argument('--compress', action='store_true', help='Create compressed archive')
    
    # Test plugin command
    test_parser = subparsers.add_parser('test', help='Test plugin capabilities')
    test_parser.add_argument('--plugin', required=True, help='Plugin ID to test')
    test_parser.add_argument('--capability', help='Specific capability to test')
    test_parser.add_argument('--params', default='{}', help='JSON parameters for capability')
    test_parser.add_argument('--plugins-dir', default='./plugins', help='Plugins directory path')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute the appropriate command
        if args.command == 'create':
            return create_plugin_command(args)
        elif args.command == 'validate':
            return validate_plugin_command(args)
        elif args.command == 'list':
            return list_plugins_command(args)
        elif args.command == 'migrate':
            return migrate_plugin_command(args)
        elif args.command == 'bundle':
            return bundle_plugin_command(args)
        elif args.command == 'test':
            return test_plugin_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())