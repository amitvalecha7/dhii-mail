import unittest
import os
import tempfile
from a2ui_integration.core.kernel import Kernel

class TestDhiiContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_contacts_integration(self):
        kernel = Kernel(db_path=self.db_path)
        
        # Load plugin
        # Note: uuid is whitelisted in sandbox.
        kernel._load_plugin("dhii_contacts")
        self.assertIn("dhii_contacts", kernel._plugins)
        
        # 1. Fetch Initial Contacts
        initial_result = await kernel.execute_capability("fetch_contacts", {})
        self.assertEqual(initial_result["title"], "Contacts")
        # Should have at least the 2 hardcoded ones
        self.assertGreaterEqual(len(initial_result["children"][0]["items"]), 2)
        
        # 2. Add Contact
        add_result = await kernel.execute_capability("add_contact", {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "phone": "555-0103"
        })
        
        self.assertEqual(add_result["title"], "Contact Added")
        self.assertIn("Charlie Brown", add_result["children"][0]["content"])
        
        # 3. Fetch Updated Contacts (Verify Search)
        search_result = await kernel.execute_capability("fetch_contacts", {
            "query": "Charlie"
        })
        
        items = search_result["children"][0]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Charlie Brown")
        self.assertIn("charlie@example.com", items[0]["subtitle"])
