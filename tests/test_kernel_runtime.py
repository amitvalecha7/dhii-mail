import unittest
import shutil
import os
import asyncio
from pathlib import Path
from a2ui_integration.core.kernel import Kernel

class TestKernelRuntimeIntegration(unittest.TestCase):
    def setUp(self):
        # Create a dummy plugin
        self.plugin_id = "test_runtime_plugin"
        self.plugin_dir = Path("plugins") / self.plugin_id
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.plugin_dir / "__init__.py", "w") as f:
            f.write("""
def register(kernel):
    kernel['log']('Hello from Sandbox!')
""")
        self.kernel = Kernel(db_path=":memory:")

    def tearDown(self):
        if self.plugin_dir.exists():
            shutil.rmtree(self.plugin_dir)

    def test_load_plugin_via_kernel(self):
        # We manually trigger the internal loading method to test integration
        self.kernel._load_plugin(self.plugin_id)
        
        # Verify it's in the _plugins dict
        self.assertIn(self.plugin_id, self.kernel._plugins)
        runner = self.kernel._plugins[self.plugin_id]
        self.assertTrue(runner.is_active)

if __name__ == '__main__':
    unittest.main()
