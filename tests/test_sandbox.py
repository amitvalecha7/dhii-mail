import unittest
from a2ui_integration.core.sandbox import PluginSandbox, SecurityViolation

class MockKernelAPI:
    def log(self, msg):
        print(f"KERNEL LOG: {msg}")

class TestPluginSandbox(unittest.TestCase):
    
    def setUp(self):
        self.api = MockKernelAPI()
        self.sandbox = PluginSandbox("test.plugin", self.api)
        
    def test_safe_execution(self):
        """Verify standard python logic works."""
        code = """
def register(kernel):
    x = 1 + 1
    kernel.log(f"Math result: {x}")
"""
        register_func = self.sandbox.execute_code(code)
        self.assertIsNotNone(register_func)
        # Should NOT raise exception
        register_func(self.api)

    def test_import_os_blocked(self):
        """Verify importing 'os' is blocked."""
        code = """
import os
def register(kernel):
    pass
"""
        with self.assertRaises(SecurityViolation):
            self.sandbox.execute_code(code)

    def test_import_allowed_module(self):
        """Verify importing 'json' is allowed."""
        code = """
import json
def register(kernel):
    data = json.dumps({"foo": "bar"})
    kernel.log(data)
"""
        register_func = self.sandbox.execute_code(code)
        register_func(self.api)

if __name__ == '__main__':
    unittest.main()
