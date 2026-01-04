"""
Test suite for lazy loading plugin integration
Verifies resilience and proper error handling
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginConfig, PluginType
from kernel_plugin_integration_refactored import KernelPluginIntegration


class TestLazyLoadingIntegration:
    """Test lazy loading plugin integration"""
    
    @pytest.fixture
    def mock_kernel(self):
        """Create a mock kernel for testing"""
        kernel = Mock(spec=Kernel)
        kernel.shared_services = Mock()
        kernel.register_plugin = Mock(return_value=asyncio.Future())
        kernel.register_plugin.return_value.set_result(None)
        return kernel
    
    @pytest.fixture
    def temp_plugins_dir(self):
        """Create temporary plugins directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugins_dir = Path(temp_dir) / "plugins"
            plugins_dir.mkdir()
            
            # Create test plugin with manifest
            test_plugin_dir = plugins_dir / "test_plugin"
            test_plugin_dir.mkdir()
            
            manifest = {
                "id": "test_plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "description": "A test plugin",
                "type": "general",
                "enabled": True,
                "dependencies": {"os": "*"},  # Built-in module
                "capabilities": [
                    {
                        "id": "test_capability",
                        "domain": "test",
                        "name": "Test Capability",
                        "description": "A test capability",
                        "input_schema": {"type": "object"},
                        "output_schema": {"type": "object"}
                    }
                ],
                "ui_routes": [
                    {
                        "path": "/test",
                        "name": "Test Route",
                        "component": "TestComponent",
                        "description": "A test route"
                    }
                ]
            }
            
            with open(test_plugin_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f)
            
            # Create plugin module
            plugin_py = test_plugin_dir / "test_plugin.py"
            plugin_py.write_text("""
class Plugin:
    def __init__(self):
        self.name = "Test Plugin"
""")
            
            yield plugins_dir
    
    @pytest.mark.asyncio
    async def test_plugin_discovery(self, mock_kernel, temp_plugins_dir):
        """Test plugin discovery from manifest files"""
        with patch('kernel_plugin_integration_refactored.Path') as mock_path:
            mock_path.return_value = temp_plugins_dir
            
            integration = KernelPluginIntegration(mock_kernel)
            discovered = await integration._discover_plugins()
            
            assert len(discovered) == 1
            plugin_path, manifest = list(discovered.items())[0]
            assert manifest['id'] == 'test_plugin'
            assert manifest['name'] == 'Test Plugin'
    
    @pytest.mark.asyncio
    async def test_dependency_check_success(self, mock_kernel):
        """Test successful dependency check"""
        integration = KernelPluginIntegration(mock_kernel)
        
        # Test with built-in module
        await integration._check_dependencies({"os": "*"})
        
        # Should not raise any exception
    
    @pytest.mark.asyncio
    async def test_dependency_check_failure(self, mock_kernel):
        """Test dependency check failure"""
        integration = KernelPluginIntegration(mock_kernel)
        
        # Test with non-existent module
        with pytest.raises(ImportError, match="Required dependency 'nonexistent_module' not found"):
            await integration._check_dependencies({"nonexistent_module": "1.0.0"})
    
    @pytest.mark.asyncio
    async def test_plugin_registration_with_missing_dependency(self, mock_kernel, temp_plugins_dir):
        """Test plugin registration continues even with missing dependencies"""
        # Create plugin with missing dependency
        missing_dep_plugin = temp_plugins_dir / "missing_dep_plugin"
        missing_dep_plugin.mkdir()
        
        manifest = {
            "id": "missing_dep_plugin",
            "name": "Missing Dep Plugin",
            "version": "1.0.0",
            "description": "Plugin with missing dependency",
            "type": "general",
            "enabled": True,
            "dependencies": {"nonexistent_module": "1.0.0"},  # Missing dependency
            "capabilities": []
        }
        
        with open(missing_dep_plugin / "manifest.json", 'w') as f:
            json.dump(manifest, f)
        
        with patch('kernel_plugin_integration_refactored.Path') as mock_path:
            mock_path.return_value = temp_plugins_dir
            
            integration = KernelPluginIntegration(mock_kernel)
            
            # Should not crash, just log error
            await integration.integrate_all_plugins()
            
            # Plugin should not be registered due to missing dependency
            assert len(integration.list_registered_plugins()) == 0
    
    @pytest.mark.asyncio
    async def test_plugin_registration_with_disabled_plugin(self, mock_kernel, temp_plugins_dir):
        """Test disabled plugins are skipped"""
        # Create disabled plugin
        disabled_plugin = temp_plugins_dir / "disabled_plugin"
        disabled_plugin.mkdir()
        
        manifest = {
            "id": "disabled_plugin",
            "name": "Disabled Plugin",
            "version": "1.0.0",
            "description": "A disabled plugin",
            "type": "general",
            "enabled": False,  # Disabled
            "dependencies": {},
            "capabilities": []
        }
        
        with open(disabled_plugin / "manifest.json", 'w') as f:
            json.dump(manifest, f)
        
        with patch('kernel_plugin_integration_refactored.Path') as mock_path:
            mock_path.return_value = temp_plugins_dir
            
            integration = KernelPluginIntegration(mock_kernel)
            await integration.integrate_all_plugins()
            
            # Disabled plugin should not be registered
            assert len(integration.list_registered_plugins()) == 0
    
    @pytest.mark.asyncio
    async def test_malformed_manifest_handling(self, mock_kernel, temp_plugins_dir):
        """Test handling of malformed manifest files"""
        # Create plugin with malformed manifest
        malformed_plugin = temp_plugins_dir / "malformed_plugin"
        malformed_plugin.mkdir()
        
        # Write invalid JSON
        with open(malformed_plugin / "manifest.json", 'w') as f:
            f.write("{ invalid json")
        
        with patch('kernel_plugin_integration_refactored.Path') as mock_path:
            mock_path.return_value = temp_plugins_dir
            
            integration = KernelPluginIntegration(mock_kernel)
            
            # Should not crash, just log error
            await integration.integrate_all_plugins()
            
            # No plugins should be registered
            assert len(integration.list_registered_plugins()) == 0
    
    @pytest.mark.asyncio
    async def test_plugin_instance_initialization_failure(self, mock_kernel, temp_plugins_dir):
        """Test plugin instance initialization failure handling"""
        # Create plugin that fails during initialization
        failing_plugin = temp_plugins_dir / "failing_plugin"
        failing_plugin.mkdir()
        
        manifest = {
            "id": "failing_plugin",
            "name": "Failing Plugin",
            "version": "1.0.0",
            "description": "A plugin that fails during init",
            "type": "general",
            "enabled": True,
            "dependencies": {},
            "capabilities": []
        }
        
        with open(failing_plugin / "manifest.json", 'w') as f:
            json.dump(manifest, f)
        
        # Create plugin module that will fail to import
        plugin_py = failing_plugin / "failing_plugin.py"
        plugin_py.write_text("raise ImportError('Simulated import failure')")
        
        with patch('kernel_plugin_integration_refactored.Path') as mock_path:
            mock_path.return_value = temp_plugins_dir
            
            integration = KernelPluginIntegration(mock_kernel)
            
            # Should not crash, just log error
            await integration.integrate_all_plugins()
            
            # Plugin should be registered with kernel but instance should not be created
            assert mock_kernel.register_plugin.called
            assert len(integration.list_registered_plugins()) == 0  # No instance created
    
    @pytest.mark.asyncio
    async def test_ui_route_registration(self, mock_kernel):
        """Test UI route registration"""
        # Mock app_shell
        mock_kernel.app_shell = Mock()
        mock_kernel.app_shell.register_route = Mock(return_value=asyncio.Future())
        mock_kernel.app_shell.register_route.return_value.set_result(None)
        
        integration = KernelPluginIntegration(mock_kernel)
        
        manifest = {
            "ui_routes": [
                {
                    "path": "/test",
                    "name": "Test Route",
                    "component": "TestComponent",
                    "description": "A test route"
                }
            ]
        }
        
        await integration._register_ui_routes(manifest)
        
        # Verify route was registered
        mock_kernel.app_shell.register_route.assert_called_once_with(
            path="/test",
            name="Test Route",
            component="TestComponent",
            description="A test route"
        )
    
    def test_plugin_config_creation(self, mock_kernel):
        """Test PluginConfig creation from manifest"""
        integration = KernelPluginIntegration(mock_kernel)
        
        manifest = {
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "type": "email",
            "author": "test_author",
            "enabled": True,
            "config": {"setting": "value"},
            "capabilities": [
                {
                    "id": "test_cap",
                    "domain": "test",
                    "name": "Test Capability",
                    "description": "A test capability"
                }
            ]
        }
        
        config = integration._create_plugin_config_from_manifest(manifest)
        
        assert config.id == "test_plugin"
        assert config.name == "Test Plugin"
        assert config.type == PluginType.EMAIL
        assert len(config.capabilities) == 1
        assert config.capabilities[0].id == "test_cap"
    
    @pytest.mark.asyncio
    async def test_resilience_with_multiple_plugins(self, mock_kernel, temp_plugins_dir):
        """Test resilience with multiple plugins, some failing"""
        # Create multiple plugins - some working, some failing
        
        # Working plugin
        working_plugin = temp_plugins_dir / "working_plugin"
        working_plugin.mkdir()
        
        working_manifest = {
            "id": "working_plugin",
            "name": "Working Plugin",
            "version": "1.0.0",
            "description": "A working plugin",
            "type": "general",
            "enabled": True,
            "dependencies": {"os": "*"},
            "capabilities": []
        }
        
        with open(working_plugin / "manifest.json", 'w') as f:
            json.dump(working_manifest, f)
        
        plugin_py = working_plugin / "working_plugin.py"
        plugin_py.write_text("""
class Plugin:
    def __init__(self):
        self.name = "Working Plugin"
""")
        
        # Failing plugin (missing dependency)
        failing_plugin = temp_plugins_dir / "failing_plugin"
        failing_plugin.mkdir()
        
        failing_manifest = {
            "id": "failing_plugin",
            "name": "Failing Plugin",
            "version": "1.0.0",
            "description": "A failing plugin",
            "type": "general",
            "enabled": True,
            "dependencies": {"nonexistent_module": "1.0.0"},
            "capabilities": []
        }
        
        with open(failing_plugin / "manifest.json", 'w') as f:
            json.dump(failing_manifest, f)
        
        with patch('kernel_plugin_integration_refactored.Path') as mock_path:
            mock_path.return_value = temp_plugins_dir
            
            integration = KernelPluginIntegration(mock_kernel)
            await integration.integrate_all_plugins()
            
            # Only working plugin should be registered
            registered_plugins = integration.list_registered_plugins()
            assert len(registered_plugins) == 1
            assert "working_plugin" in registered_plugins
            assert "failing_plugin" not in registered_plugins


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])