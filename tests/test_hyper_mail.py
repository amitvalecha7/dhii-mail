import unittest
import json
import asyncio
import os
import tempfile
from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginConfig, PluginType, Capability

class TestHyperMail(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create a temporary file for the database
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self):
        # Remove the temporary database file
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_hyper_mail_integration(self):
        # Use temp DB file
        kernel = Kernel(db_path=self.db_path)
        
        # Initialize Shared Services manually since we are not using the full app bootstrap
        # (Kernel.__init__ calls _init_shared_services which calls initialize_shared_services)
        # This should be enough to setup the DB.
        
        # Create Config from manifest
        with open("plugins/hyper_mail/manifest.json") as f:
            manifest = json.load(f)
            
        config = PluginConfig(
            id=manifest["id"],
            name=manifest["name"],
            version=manifest["version"],
            description=manifest["description"],
            type=PluginType(manifest["type"]),
            author=manifest["author"],
            enabled=True, # Enable immediately
            capabilities=[
                Capability(**cap) for cap in manifest["capabilities"]
            ],
            dependencies=manifest["dependencies"],
            config={}
        )
        
        # Register Plugin (Writes to DB)
        success = await kernel.register_plugin(config)
        self.assertTrue(success)
        
        # Enable Plugin (Reads from DB, updates Kernel state)
        success = await kernel.enable_plugin("hyper_mail")
        self.assertTrue(success)
        
        # Manually trigger load because initialize() is usually called at startup
        # and we just added the plugin.
        kernel._load_plugin("hyper_mail")
        
        # Verify Plugin is loaded in memory
        self.assertIn("hyper_mail", kernel._plugins)
        
        # Execute Capability
        result = await kernel.execute_capability("fetch_inbox", {})
        
        # Assertions on A2UI Structure
        self.assertEqual(result["type"], "card")
        self.assertEqual(result["id"], "inbox-card")
        self.assertEqual(result["title"], "Inbox")
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["type"], "list")
        self.assertEqual(len(result["children"][0]["items"]), 3)

if __name__ == "__main__":
    unittest.main()
