"""
Test suite for structured logging system
"""

import json
import logging
import tempfile
import os
import time
from datetime import datetime
import pytest
import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from a2ui_integration.core.logging import (
    setup_structured_logging, 
    get_logger, 
    set_correlation_id, 
    get_correlation_id,
    clear_correlation_id,
    PerformanceTracker
)
from middleware.logging_middleware import LoggingMiddleware, CorrelationIDMiddleware

class TestStructuredLogging:
    """Test structured logging functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create temporary log file
        self.temp_log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
        self.temp_log_file.close()
        
        # Setup structured logging
        setup_structured_logging(
            log_level="INFO",
            log_file=self.temp_log_file.name
        )
        
        self.logger = get_logger("test.logging")
    
    def teardown_method(self):
        """Cleanup test environment"""
        # Remove temp file
        if os.path.exists(self.temp_log_file.name):
            os.unlink(self.temp_log_file.name)
        clear_correlation_id()
    
    def test_basic_structured_logging(self):
        """Test basic structured logging functionality"""
        # Log a simple message
        self.logger.info("Test message", extra_fields={"test_field": "test_value"})
        
        # Read log file
        with open(self.temp_log_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        # Parse JSON log
        log_data = json.loads(log_line)
        
        # Verify structure
        assert log_data['message'] == "Test message"
        assert log_data['level'] == "INFO"
        assert log_data['test_field'] == "test_value"
        assert 'timestamp' in log_data
        assert 'correlation_id' in log_data
        assert 'logger' in log_data
    
    def test_correlation_id_management(self):
        """Test correlation ID functionality"""
        # Test setting and getting correlation ID
        test_id = "test-correlation-123"
        set_correlation_id(test_id)
        
        assert get_correlation_id() == test_id
        
        # Clear previous logs by reopening the file
        self.temp_log_file.close()
        setup_structured_logging(
            log_level="INFO",
            log_file=self.temp_log_file.name
        )
        
        # Log message and verify correlation ID
        self.logger.info("Test with correlation ID")
        
        with open(self.temp_log_file.name, 'r') as f:
            log_lines = f.readlines()
        
        # Should have at least one log line
        assert len(log_lines) >= 1
        
        # Get the last log line (our test message)
        log_data = json.loads(log_lines[-1].strip())
        assert log_data['correlation_id'] == test_id
        
        # Test clearing
        clear_correlation_id()
        assert get_correlation_id() == ""
    
    def test_error_logging_with_exception(self):
        """Test error logging with exception information"""
        # Clear previous logs
        self.temp_log_file.close()
        setup_structured_logging(
            log_level="INFO",
            log_file=self.temp_log_file.name
        )
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            self.logger.error("Test error message", extra_fields={"error_code": "TEST001"})
        
        with open(self.temp_log_file.name, 'r') as f:
            log_lines = f.readlines()
        
        # Find the error log line
        error_logs = [line for line in log_lines if '"ERROR"' in line]
        assert len(error_logs) >= 1
        
        log_data = json.loads(error_logs[0].strip())
        assert log_data['level'] == "ERROR"
        assert log_data['message'] == "Test error message"
        assert log_data['error_code'] == "TEST001"
    
    def test_performance_tracker(self):
        """Test performance tracking functionality"""
        # Clear previous logs
        self.temp_log_file.close()
        setup_structured_logging(
            log_level="INFO",
            log_file=self.temp_log_file.name
        )
        
        with PerformanceTracker("test_operation", self.logger):
            # Simulate some work
            time.sleep(0.1)
        
        with open(self.temp_log_file.name, 'r') as f:
            log_lines = f.readlines()
        
        # Should have logged completion
        assert len(log_lines) >= 1
        
        # Find the performance log
        perf_logs = [line for line in log_lines if '"test_operation completed successfully"' in line]
        assert len(perf_logs) >= 1
        
        log_data = json.loads(perf_logs[0].strip())
        assert "duration_ms" in log_data
        assert log_data["operation"] == "test_operation"
        assert log_data["status"] == "success"
        assert log_data["duration_ms"] >= 100  # Should be at least 100ms
    
    def test_performance_tracker_with_error(self):
        """Test performance tracker with exception"""
        # Clear previous logs
        self.temp_log_file.close()
        setup_structured_logging(
            log_level="INFO",
            log_file=self.temp_log_file.name
        )
        
        try:
            with PerformanceTracker("failing_operation", self.logger):
                raise RuntimeError("Test error")
        except RuntimeError:
            pass  # Expected
        
        with open(self.temp_log_file.name, 'r') as f:
            log_lines = f.readlines()
        
        # Find the error performance log
        perf_error_logs = [line for line in log_lines if '"failing_operation failed"' in line]
        assert len(perf_error_logs) >= 1
        
        log_data = json.loads(perf_error_logs[0].strip())
        assert log_data["operation"] == "failing_operation"
        assert log_data["status"] == "failed"
        assert log_data["error_type"] == "RuntimeError"

class TestLoggingMiddleware:
    """Test logging middleware functionality"""
    
    def setup_method(self):
        """Setup test app and client"""
        self.app = FastAPI()
        
        # Setup structured logging
        setup_structured_logging(log_level="INFO")
        
        # Add middleware
        self.app.add_middleware(CorrelationIDMiddleware)
        self.app.add_middleware(LoggingMiddleware)
        
        # Add test endpoint
        @self.app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        @self.app.get("/error")
        def error_endpoint():
            raise ValueError("Test error")
        
        self.client = TestClient(self.app)
    
    def test_request_response_logging(self):
        """Test that requests and responses are logged"""
        # Create temporary log file
        temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
        temp_log.close()
        
        # Setup logging to file
        setup_structured_logging(log_level="INFO", log_file=temp_log.name)
        
        # Make request
        response = self.client.get("/test")
        
        # Read logs
        with open(temp_log.name, 'r') as f:
            log_lines = f.readlines()
        
        # Should have request and response logs
        assert len(log_lines) >= 2
        
        # Parse logs
        request_log = json.loads(log_lines[0])
        response_log = json.loads(log_lines[1])
        
        # Verify request log
        assert request_log['message'] == "Incoming request"
        assert request_log['request']['method'] == "GET"
        assert request_log['request']['path'] == "/test"
        
        # Verify response log
        assert response_log['message'] == "Request completed successfully"
        assert response_log['response']['status_code'] == 200
        assert 'duration_ms' in response_log['response']
        
        # Cleanup
        os.unlink(temp_log.name)
    
    def test_correlation_id_propagation(self):
        """Test correlation ID propagation through requests"""
        # Test with provided correlation ID
        test_correlation_id = "test-corr-456"
        response = self.client.get("/test", headers={"X-Correlation-ID": test_correlation_id})
        
        # Check response header
        assert response.headers["X-Correlation-ID"] == test_correlation_id
        
        # Test without correlation ID (should generate one)
        response = self.client.get("/test")
        assert "X-Correlation-ID" in response.headers
        assert len(response.headers["X-Correlation-ID"]) > 0
    
    def test_error_logging(self):
        """Test error logging in middleware"""
        temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
        temp_log.close()
        
        setup_structured_logging(log_level="INFO", log_file=temp_log.name)
        
        # Make request that will fail
        with pytest.raises(ValueError):
            self.client.get("/error")
        
        # Read logs
        with open(temp_log.name, 'r') as f:
            log_lines = f.readlines()
        
        # Should have error log
        error_logs = [json.loads(line) for line in log_lines if json.loads(line).get('message') == "Request failed with exception"]
        assert len(error_logs) >= 1
        
        error_log = error_logs[0]
        assert error_log['error']['type'] == "ValueError"
        assert error_log['error']['message'] == "Test error"
        
        # Cleanup
        os.unlink(temp_log.name)

@pytest.mark.asyncio
class TestAsyncLogging:
    """Test async logging functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
        self.temp_log_file.close()
        
        setup_structured_logging(
            log_level="INFO",
            log_file=self.temp_log_file.name
        )
        
        self.logger = get_logger("test.async")
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_log_file.name):
            os.unlink(self.temp_log_file.name)
        clear_correlation_id()
    
    async def test_async_logging(self):
        """Test logging in async context"""
        # Set correlation ID
        test_id = "async-test-789"
        set_correlation_id(test_id)
        
        # Log in async context
        self.logger.info("Async test message", extra_fields={"async": True})
        
        # Read log
        with open(self.temp_log_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        assert log_data['message'] == "Async test message"
        assert log_data['correlation_id'] == test_id
        assert log_data['async'] is True

if __name__ == "__main__":
    # Run basic tests
    test = TestStructuredLogging()
    test.setup_method()
    
    print("Running structured logging tests...")
    
    try:
        test.test_basic_structured_logging()
        print("✅ Basic structured logging test passed")
        
        test.test_correlation_id_management()
        print("✅ Correlation ID management test passed")
        
        test.test_error_logging_with_exception()
        print("✅ Error logging test passed")
        
        test.test_performance_tracker()
        print("✅ Performance tracker test passed")
        
        test.test_performance_tracker_with_error()
        print("✅ Performance tracker error test passed")
        
        print("🎉 All structured logging tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        test.teardown_method()