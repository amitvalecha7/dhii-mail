"""
Framework 2.0 Migration Tool
Automated migration from DomainModule to PluginInterface
"""

import ast
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class FrameworkMigrationTool:
    """Tool to migrate Framework 1.0 plugins to Framework 2.0"""
    
    def __init__(self):
        self.migration_rules = {
            # Import changes
            "from a2ui_integration.core.types import DomainModule, Capability": 
                "from a2ui_integration.framework.contract import PluginInterface, PluginManifest, PluginCapability, PluginType, CapabilityType",
            
            # Class inheritance changes
            "class (\w+)Plugin\(DomainModule\)": 
                r"class \1PluginV2(PluginInterface)",
            
            # Property changes
            "@property\ndef domain\(self\) -> str:":
                "@property\ndef manifest(self) -> PluginManifest:",
            
            # Capability changes
            "@property\ndef capabilities\(self\) -> List\[Capability\]:":
                "# Capabilities are defined in manifest property",
            
            # Method changes
            "async def initialize\(self\) -> bool:":
                "def initialize(self, kernel_api: Dict[str, Any]) -> None:",
            
            "async def shutdown\(self\) -> bool:":
                "def shutdown(self) -> None:",
            
            "async def execute_capability\(self, capability_id: str, params: Dict\[str, Any\]\) -> Dict\[str, Any\]:":
                "def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:",
        }
    
    def migrate_plugin_file(self, file_path: str) -> str:
        """Migrate a single plugin file from Framework 1.0 to 2.0"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Apply migration rules
        migrated_content = content
        for old_pattern, new_pattern in self.migration_rules.items():
            migrated_content = re.sub(old_pattern, new_pattern, migrated_content, flags=re.MULTILINE)
        
        # Add Framework 2.0 specific imports if not present
        if "from a2ui_integration.framework.contract import" not in migrated_content:
            migrated_content = self._add_imports(migrated_content)
        
        # Add health status tracking
        migrated_content = self._add_health_status(migrated_content)
        
        # Add Framework 2.0 registration function
        migrated_content = self._add_registration_function(migrated_content)
        
        return migrated_content
    
    def _add_imports(self, content: str) -> str:
        """Add Framework 2.0 imports"""
        framework_imports = """from a2ui_integration.framework.contract import PluginInterface, PluginManifest, PluginCapability, PluginType, CapabilityType, ExecutionContext
from a2ui_integration.framework.types import PluginHealth, HealthStatus, CapabilityExecutionResult
"""
        
        # Find the first import and add after it
        lines = content.split('\n')
        import_lines = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                import_lines.append(line)
            else:
                other_lines.append(line)
                break
        
        # Add framework imports
        import_lines.extend(framework_imports.strip().split('\n'))
        
        return '\n'.join(import_lines + other_lines)
    
    def _add_health_status(self, content: str) -> str:
        """Add health status tracking to plugin class"""
        health_init = """        self._health_status = HealthStatus.HEALTHY
        self._kernel_api: Optional[Dict[str, Any]] = None"""
        
        # Find __init__ method and add health tracking
        if "def __init__(self" in content:
            # Add health status initialization
            content = re.sub(
                r"(def __init__\(self.*?\):.*?)(self\.\w+ = )",
                r"\1\2" + health_init + "\n        ",
                content,
                flags=re.DOTALL
            )
        
        # Add get_health_status method
        health_method = """
    def get_health_status(self) -> PluginHealth:
        \"\"\"Get plugin health status (Framework 2.0)\"\"\"
        return PluginHealth(
            plugin_id="email",
            status=self._health_status,
            message="Email plugin operational",
            capabilities={
                "email.send": HealthStatus.HEALTHY,
                "email.receive": HealthStatus.HEALTHY,
                "email.search": HealthStatus.HEALTHY
            }
        )
"""
        
        # Add before the last method or at the end of class
        content = re.sub(
            r"(def \w+\(self.*?\):.*?)(?=\nclass|\n\nclass|\Z)",
            r"\1" + health_method + "\n",
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _add_registration_function(self, content: str) -> str:
        """Add Framework 2.0 registration function"""
        registration_function = """

def register(kernel_api: Dict[str, Any]) -> PluginInterface:
    \"\"\"Register the EmailPluginV2 with Framework 2.0\"\"\"
    plugin = EmailPluginV2()
    plugin.initialize(kernel_api)
    return plugin
"""
        
        # Add at the end of file
        return content + registration_function
    
    def generate_capability_migration(self, old_capabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Framework 1.0 capabilities to Framework 2.0 format"""
        new_capabilities = []
        
        for old_cap in old_capabilities:
            new_cap = {
                "id": old_cap.get("id", ""),
                "name": old_cap.get("name", ""),
                "description": old_cap.get("description", ""),
                "capability_type": self._map_capability_type(old_cap.get("domain", "")),
                "input_schema": old_cap.get("input_schema", {}),
                "output_schema": old_cap.get("output_schema", {}),
                "requires_auth": old_cap.get("requires_auth", False),
                "timeout_seconds": 30  # Default timeout
            }
            new_capabilities.append(new_cap)
        
        return new_capabilities
    
    def _map_capability_type(self, domain: str) -> str:
        """Map old domain-based capability types to new types"""
        capability_type_map = {
            "email": "action",
            "calendar": "action", 
            "task": "action",
            "search": "query",
            "fetch": "query",
            "send": "action",
            "receive": "query",
            "create": "action",
            "update": "action",
            "delete": "action",
            "list": "query",
            "get": "query"
        }
        
        # Try to infer from domain or capability name
        for key, value in capability_type_map.items():
            if key in domain.lower():
                return value
        
        return "action"  # Default
    
    def generate_manifest_migration(self, old_plugin_info: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Framework 1.0 plugin info to Framework 2.0 manifest"""
        return {
            "id": old_plugin_info.get("id", ""),
            "name": old_plugin_info.get("name", ""),
            "version": old_plugin_info.get("version", "1.0.0"),
            "plugin_type": self._map_plugin_type(old_plugin_info.get("type", "")),
            "author": old_plugin_info.get("author", "Unknown"),
            "description": old_plugin_info.get("description", ""),
            "capabilities": self.generate_capability_migration(old_plugin_info.get("capabilities", [])),
            "dependencies": old_plugin_info.get("dependencies", []),
            "sandbox_config": {
                "network_access": True,
                "file_system_access": True,
                "database_access": True
            }
        }
    
    def _map_plugin_type(self, old_type: str) -> str:
        """Map old plugin types to new Framework 2.0 types"""
        type_map = {
            "email": "integration",
            "calendar": "integration",
            "task": "utility",
            "crm": "integration",
            "analytics": "intelligence",
            "ui": "ui",
            "persistence": "persistence",
            "transport": "transport"
        }
        
        return type_map.get(old_type.lower(), "utility")
    
    def create_migration_report(self, original_file: str, migrated_file: str) -> Dict[str, Any]:
        """Create a detailed migration report"""
        return {
            "original_file": original_file,
            "migrated_file": migrated_file,
            "changes_made": [
                "Converted from DomainModule to PluginInterface",
                "Added Framework 2.0 imports",
                "Updated class inheritance",
                "Added health status tracking",
                "Added registration function",
                "Converted capabilities to new format"
            ],
            "manual_review_required": [
                "Verify capability type mappings",
                "Test plugin initialization",
                "Update capability implementations",
                "Review sandbox configuration",
                "Test with Framework 2.0 PluginManager"
            ],
            "next_steps": [
                "Test the migrated plugin",
                "Update plugin manifest.json if needed",
                "Register with Framework 2.0 PluginManager",
                "Update any dependent code"
            ]
        }


def migrate_plugin_directory(source_dir: str, target_dir: str) -> Dict[str, Any]:
    """Migrate an entire plugin directory from Framework 1.0 to 2.0"""
    tool = FrameworkMigrationTool()
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    
    migration_results = {}
    
    # Migrate all Python files
    for py_file in source_path.glob("*.py"):
        if py_file.name.endswith("_v2.py"):  # Skip already migrated files
            continue
            
        try:
            migrated_content = tool.migrate_plugin_file(str(py_file))
            
            # Save migrated file with _v2 suffix
            target_file = target_path / f"{py_file.stem}_v2.py"
            with open(target_file, 'w') as f:
                f.write(migrated_content)
            
            migration_results[str(py_file)] = tool.create_migration_report(
                str(py_file), str(target_file)
            )
            
        except Exception as e:
            migration_results[str(py_file)] = {
                "error": str(e),
                "status": "failed"
            }
    
    return migration_results


if __name__ == "__main__":
    # Example usage
    print("Framework 2.0 Migration Tool")
    print("=" * 50)
    
    # Migrate email plugin
    results = migrate_plugin_directory(
        "/root/dhii-mail/plugins/email",
        "/root/dhii-mail/plugins/email/migrated"
    )
    
    for file_path, result in results.items():
        print(f"\nMigrated: {file_path}")
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Status: Success")
            print(f"  Changes: {len(result['changes_made'])}")
            print(f"  Manual review items: {len(result['manual_review_required'])}")