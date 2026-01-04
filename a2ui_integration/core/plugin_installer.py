import os
import json
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any

from .logging import get_logger

logger = get_logger(__name__)

class PluginInstaller:
    """
    Handles the fetching, validation, and installation of plugins from the Registry.
    """
    
    def __init__(self, registry_url: str, plugins_dir: str):
        self.registry_url = registry_url.rstrip('/')
        self.plugins_dir = Path(plugins_dir)
        self._ensure_plugins_dir()

    def _ensure_plugins_dir(self):
        """Ensure the plugins directory exists."""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created plugins directory at {self.plugins_dir}")

    def install_plugin(self, plugin_id: str) -> bool:
        """
        Fetch a plugin from the registry and install it.
        
        Args:
            plugin_id: The ID of the plugin to install (e.g., 'com.dhiimail.marketing')
            
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        logger.info(f"Attempting to install plugin: {plugin_id}")
        
        # 1. Fetch Metadata
        plugin_info = self._fetch_plugin_metadata(plugin_id)
        if not plugin_info:
            return False
            
        # 2. Validate (Governance Check)
        if not self._validate_plugin(plugin_info):
            logger.error(f"Plugin {plugin_id} failed validation check")
            return False
            
        # 3. Install (Simulate download and extraction)
        return self._install_plugin_files(plugin_id, plugin_info)

    def _fetch_plugin_metadata(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Query the registry API for plugin details."""
        try:
            url = f"{self.registry_url}/api/v1/plugins/{plugin_id}"
            logger.debug(f"Fetching metadata from {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.error(f"Plugin {plugin_id} not found in registry")
            else:
                logger.error(f"Registry returned error {response.status_code}: {response.text}")
                
            return None
        except requests.RequestException as e:
            logger.error(f"Network error contacting registry: {e}")
            return None

    def _validate_plugin(self, plugin_info: Dict[str, Any]) -> bool:
        """
        Validate plugin metadata against governance rules.
        In a real scenario, this would check signatures and permissions.
        """
        required_fields = ['id', 'name', 'version']
        missing = [field for field in required_fields if field not in plugin_info]
        
        if missing:
            logger.error(f"Plugin metadata missing required fields: {missing}")
            return False
            
        # Example Governance Rule: No 'root' in ID
        if 'root' in plugin_info['id']:
            logger.error("Plugin ID cannot contain 'root'")
            return False
            
        return True

    def _install_plugin_files(self, plugin_id: str, plugin_info: Dict[str, Any]) -> bool:
        """
        Write plugin files to disk.
        Since we don't have real zip artifacts yet, we generate a scaffold.
        """
        try:
            install_path = self.plugins_dir / plugin_id
            
            # If it exists, we overwrite (simple update logic)
            if install_path.exists():
                logger.warning(f"Plugin directory {install_path} exists. Overwriting.")
            
            install_path.mkdir(exist_ok=True)
            
            # Write manifest.json
            manifest_path = install_path / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(plugin_info, f, indent=2)
            
            # Write __init__.py (Scaffold)
            init_path = install_path / "__init__.py"
            with open(init_path, "w") as f:
                f.write(f'"""\nPlugin: {plugin_info["name"]}\nVersion: {plugin_info["version"]}\n"""\n\n')
                f.write("def register(kernel):\n")
                f.write(f"    # Auto-generated entry point for {plugin_id}\n")
                f.write(f"    print('Plugin {plugin_id} registered!')\n")
                
            logger.info(f"Plugin {plugin_id} installed successfully at {install_path}")
            return True
            
        except OSError as e:
            logger.error(f"File system error during installation: {e}")
            return False
