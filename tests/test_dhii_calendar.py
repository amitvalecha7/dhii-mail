import unittest
from unittest.mock import MagicMock, patch
import json
import asyncio
import os
import tempfile
import sys
import datetime
from a2ui_integration.core.kernel import Kernel

class TestDhiiCalendar(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_calendar_integration(self):
        kernel = Kernel(db_path=self.db_path)
        
        # Load plugin
        # Note: We don't need to patch imports here because the plugin uses standard libs (datetime, json, uuid)
        # However, we must ensure these are whitelisted in sandbox.py if not already.
        # datetime, json, uuid are whitelisted.
        
        kernel._load_plugin("dhii_calendar")
        self.assertIn("dhii_calendar", kernel._plugins)
        
        # 1. Create Event
        start_time = "2024-01-01T10:00:00"
        end_time = "2024-01-01T11:00:00"
        create_result = await kernel.execute_capability("create_event", {
            "title": "Team Meeting",
            "start_time": start_time,
            "end_time": end_time,
            "description": "Weekly sync"
        })
        
        self.assertEqual(create_result["title"], "Event Created")
        self.assertIn("Team Meeting", create_result["children"][0]["content"])
        
        # 2. Fetch Events
        fetch_result = await kernel.execute_capability("fetch_events", {
            "start_date": "2024-01-01",
            "end_date": "2024-01-02"
        })
        
        self.assertEqual(fetch_result["title"], "Upcoming Schedule")
        items = fetch_result["children"][0]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Team Meeting")
        self.assertIn(start_time, items[0]["subtitle"])
