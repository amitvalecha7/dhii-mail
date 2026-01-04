import unittest
import os
import tempfile
from a2ui_integration.core.kernel import Kernel

class TestDhiiCRM(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_crm_integration(self):
        kernel = Kernel(db_path=self.db_path)
        
        # Load plugin
        kernel._load_plugin("dhii_crm")
        self.assertIn("dhii_crm", kernel._plugins)
        
        # 1. Get Pipeline
        pipeline_result = await kernel.execute_capability("get_pipeline", {})
        self.assertEqual(pipeline_result["title"], "Sales Pipeline")
        self.assertGreaterEqual(len(pipeline_result["children"][0]["items"]), 2)
        
        # 2. Add Deal
        add_result = await kernel.execute_capability("add_deal", {
            "title": "Big Enterprise Deal",
            "value": 100000,
            "stage": "Lead"
        })
        self.assertEqual(add_result["title"], "Deal Added")
        self.assertIn("Big Enterprise Deal", add_result["children"][0]["content"])
        
        # 3. Update Stage (using the ID from the mock data, which we know is "1")
        update_result = await kernel.execute_capability("update_stage", {
            "deal_id": "1",
            "new_stage": "Closed Won"
        })
        self.assertEqual(update_result["title"], "Deal Updated")
        self.assertIn("Moved Acme Corp Contract", update_result["children"][0]["content"])
