import unittest
from unittest.mock import patch, MagicMock
import shutil
import os
from pathlib import Path
import json

from a2ui_integration.core.plugin_installer import PluginInstaller

class TestPluginInstaller(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "test_plugins"
        self.installer = PluginInstaller(registry_url="http://mock-registry", plugins_dir=self.test_dir)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('requests.get')
    def test_install_plugin_success(self, mock_get):
        # Mock Registry Response
        plugin_id = "com.test.plugin"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": plugin_id,
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin"
        }
        mock_get.return_value = mock_response

        # Execute
        result = self.installer.install_plugin(plugin_id)

        # Verify
        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, plugin_id, "manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, plugin_id, "__init__.py")))
        
        # Check manifest content
        with open(os.path.join(self.test_dir, plugin_id, "manifest.json")) as f:
            manifest = json.load(f)
            self.assertEqual(manifest['name'], "Test Plugin")

    @patch('requests.get')
    def test_install_plugin_not_found(self, mock_get):
        # Mock 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Execute
        result = self.installer.install_plugin("non.existent.plugin")

        # Verify
        self.assertFalse(result)

    @patch('requests.get')
    def test_install_plugin_validation_failure(self, mock_get):
        # Mock Invalid Metadata (Missing version)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "com.test.invalid",
            "name": "Invalid Plugin"
            # Missing version
        }
        mock_get.return_value = mock_response

        # Execute
        result = self.installer.install_plugin("com.test.invalid")

        # Verify
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()