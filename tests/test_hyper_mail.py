import unittest
from unittest.mock import MagicMock, patch
import json
import asyncio
import os
import tempfile
import sys
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
        
        # Mock IMAP
        mock_imap_module = MagicMock()
        mock_imap_instance = MagicMock()
        mock_imap_module.IMAP4_SSL.return_value = mock_imap_instance
        
        # Mock search response: (status, [b'1 2'])
        mock_imap_instance.search.return_value = ('OK', [b'1 2'])
        
        # Mock fetch response
        # Structure: (status, [(metadata, raw_email)])
        # fetch is called for '2' then '1' (reversed)
        mock_imap_instance.fetch.side_effect = [
            ('OK', [(b'2 (RFC822)', b'Subject: Test 2\r\nFrom: sender@example.com\r\nDate: Mon, 1 Jan 2024\r\n\r\nBody 2')]),
            ('OK', [(b'1 (RFC822)', b'Subject: Test 1\r\nFrom: sender@example.com\r\nDate: Mon, 1 Jan 2024\r\n\r\nBody 1')])
        ]
        
        # We need to patch imaplib in sys.modules so the plugin picks it up
        with patch.dict(sys.modules, {'imaplib': mock_imap_module}):
            # Load plugin (this will import the mocked imaplib)
            # Note: We need to ensure the plugin is reloaded or loaded for the first time
            kernel._load_plugin("hyper_mail")
            
            # Verify plugin loaded
            self.assertIn("hyper_mail", kernel._plugins)
            
            # Execute capability
            result = await kernel.execute_capability("fetch_inbox", {
                "username": "user", "password": "pass"
            })
            
            # Verify result
            self.assertEqual(result["title"], "Inbox")
            items = result["children"][0]["items"]
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]["title"], "Test 2") # Reversed order (newest first)
            self.assertEqual(items[1]["title"], "Test 1")
            
            # Verify IMAP calls
            mock_imap_module.IMAP4_SSL.assert_called_with("imap.gmail.com")
            mock_imap_instance.login.assert_called_with("user", "pass")
            mock_imap_instance.select.assert_called_with("inbox")

            # Verify actions in items
            self.assertIn("action", items[0])
            self.assertEqual(items[0]["action"]["capability_id"], "read_email")
            self.assertEqual(items[0]["action"]["params"]["email_id"], "2")

            # Reset mocks for read_email test
            mock_imap_instance.reset_mock()
            
            # Test read_email capability
            # Setup mock for specific email fetch
            mock_imap_instance.fetch.side_effect = None
            mock_imap_instance.fetch.return_value = ('OK', [(b'2 (RFC822)', b'Subject: Test 2\r\nFrom: sender@example.com\r\nDate: Mon, 1 Jan 2024\r\n\r\nBody 2')])
            
            read_result = await kernel.execute_capability("read_email", {
                "username": "user", "password": "pass", "email_id": "2"
            })
            
            self.assertEqual(read_result["title"], "Test 2")
            # Children: [From, Date, Divider, Body]
            self.assertIn("From: sender@example.com", read_result["children"][0]["content"])
            self.assertIn("Body 2", read_result["children"][3]["content"])
