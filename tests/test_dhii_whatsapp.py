import unittest
import os
import tempfile
from a2ui_integration.core.kernel import Kernel

class TestDhiiWhatsApp(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_whatsapp_integration(self):
        kernel = Kernel(db_path=self.db_path)
        
        # Load plugin
        kernel._load_plugin("dhii_whatsapp")
        self.assertIn("dhii_whatsapp", kernel._plugins)
        
        # 1. Get Threads
        threads_result = await kernel.execute_capability("get_threads", {})
        self.assertEqual(threads_result["title"], "WhatsApp Chats")
        self.assertGreaterEqual(len(threads_result["children"][0]["items"]), 2)
        
        # 2. Send Message
        send_result = await kernel.execute_capability("send_message", {
            "to": "Alice",
            "message": "Yes, 12:30 works."
        })
        
        self.assertEqual(send_result["title"], "Message Sent")
        self.assertIn("Sent to Alice", send_result["children"][0]["content"])
