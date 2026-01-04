import unittest
import os
import tempfile
from a2ui_integration.core.kernel import Kernel

class TestDhiiTeams(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_teams_integration(self):
        kernel = Kernel(db_path=self.db_path)
        
        # Load plugin
        kernel._load_plugin("dhii_teams")
        self.assertIn("dhii_teams", kernel._plugins)
        
        # 1. Get Channels
        channels_result = await kernel.execute_capability("get_channels", {})
        self.assertEqual(channels_result["title"], "Microsoft Teams")
        self.assertGreaterEqual(len(channels_result["children"][0]["items"]), 2)
        
        # 2. Post Message
        post_result = await kernel.execute_capability("post_message", {
            "channel_id": "general",
            "message": "Hello Team!"
        })
        
        self.assertEqual(post_result["title"], "Message Posted")
        self.assertIn("Posted to #general", post_result["children"][0]["content"])
