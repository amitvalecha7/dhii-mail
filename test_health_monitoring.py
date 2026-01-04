"""
Test suite for health monitoring system
"""

import json
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from a2ui_integration.core.health_monitoring import (
    HealthMonitor,
    HealthCheck,
    HealthCheckResult,
    HealthStatus,
    DatabaseHealthCheck,
    ExternalServiceHealthCheck,
    SystemResourceHealthCheck,
    get_health_monitor,
    setup_default_health_checks
)

class HelperHealthCheck(HealthCheck):
    """Test health check that can be configured to pass or fail"""
    
    def __init__(self, name: str, should_pass: bool = True, result_data: dict = None):
        super().__init__(name)
        self.should_pass = should_pass
        self.result_data = result_data or {"test": "data"}
    
    async def _perform_check(self) -> dict:
        if not self.should_pass:
            raise Exception("Test check failed")
        return self.result_data

class TestHealthMonitoring:
    """Test health monitoring functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.monitor = HealthMonitor()
    
    @pytest.mark.anyio
    async def test_basic_health_check(self):
        """Test basic health check functionality"""
        check = HelperHealthCheck("test_check", should_pass=True)
        result = await check.check()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Check passed"
        assert result.details == {"test": "data"}
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_failing_health_check(self):
        """Test failing health check"""
        check = HelperHealthCheck("failing_check", should_pass=False)
        result = await check.check()
        
        assert result.name == "failing_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Check failed"
        assert result.error == "Test check failed"
        assert result.details is None
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check timeout"""
        class SlowHealthCheck(HealthCheck):
            def __init__(self):
                super().__init__("slow_check", timeout_ms=100)
            
            async def _perform_check(self):
                await asyncio.sleep(0.5)  # Longer than timeout
                return {"slow": "data"}
        
        check = SlowHealthCheck()
        result = await check.check()
        
        assert result.name == "slow_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Check timed out"
        assert "Timeout after 100ms" in result.error
    
    @pytest.mark.asyncio
    async def test_health_monitor_with_multiple_checks(self):
        """Test health monitor with multiple checks"""
        self.monitor.add_check(HelperHealthCheck("check1", should_pass=True))
        self.monitor.add_check(HelperHealthCheck("check2", should_pass=True))
        self.monitor.add_check(HelperHealthCheck("check3", should_pass=False))
        
        report = await self.monitor.perform_health_check()
        
        assert report["status"] == "unhealthy"
        assert report["summary"]["total_checks"] == 3
        assert report["summary"]["healthy_checks"] == 2
        assert report["summary"]["unhealthy_checks"] == 1
        assert len(report["checks"]) == 3
        
        assert report["checks"]["check1"]["status"] == "healthy"
        assert report["checks"]["check2"]["status"] == "healthy"
        assert report["checks"]["check3"]["status"] == "unhealthy"
    
    def test_health_monitor_overall_status_healthy(self):
        """Test overall status calculation - healthy"""
        fresh_monitor = HealthMonitor()
        fresh_monitor.add_check(HelperHealthCheck("check1", should_pass=True))
        fresh_monitor.add_check(HelperHealthCheck("check2", should_pass=True))
        
        report = asyncio.run(fresh_monitor.perform_health_check())
        
        assert report["status"] == "healthy"
    
    def test_health_monitor_overall_status_degraded(self):
        """Test overall status calculation - degraded"""
        class DegradedHealthCheck(HealthCheck):
            def __init__(self):
                super().__init__("degraded_check")
            
            async def check(self):
                return HealthCheckResult(
                    name="degraded_check",
                    status=HealthStatus.DEGRADED,
                    message="Check degraded",
                    duration_ms=100,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
        
        fresh_monitor = HealthMonitor()
        fresh_monitor.add_check(HelperHealthCheck("check1", should_pass=True))
        fresh_monitor.add_check(DegradedHealthCheck())
        
        report = asyncio.run(fresh_monitor.perform_health_check())
        
        assert report["status"] == "degraded"
    
    @pytest.mark.asyncio
    async def test_health_monitor_overall_status_unhealthy(self):
        """Test overall status calculation - unhealthy"""
        self.monitor.add_check(HelperHealthCheck("check1", should_pass=True))
        self.monitor.add_check(HelperHealthCheck("check2", should_pass=False))
        
        report = await self.monitor.perform_health_check()
        
        assert report["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_custom_health_check_function(self):
        """Test custom health check function"""
        fresh_monitor = HealthMonitor()
        
        async def custom_check():
            return {"custom": "result"}
        
        fresh_monitor.add_custom_check("custom_check", custom_check)
        
        report = await fresh_monitor.perform_health_check()
        
        assert report["status"] == "healthy"
        assert "custom_check" in report["checks"]
        assert report["checks"]["custom_check"]["status"] == "healthy"
        assert report["checks"]["custom_check"]["details"] == {"custom": "result"}
    
    @pytest.mark.asyncio
    async def test_custom_health_check_function_with_exception(self):
        """Test custom health check function that raises exception"""
        async def failing_custom_check():
            raise Exception("Custom check failed")
        
        self.monitor.add_custom_check("failing_custom_check", failing_custom_check)
        
        report = await self.monitor.perform_health_check()
        
        assert report["status"] == "unhealthy"
        assert "failing_custom_check" in report["checks"]
        assert report["checks"]["failing_custom_check"]["status"] == "unhealthy"
        assert "Custom check failed" in report["checks"]["failing_custom_check"]["error"]
    
    def test_get_health_monitor_singleton(self):
        """Test that get_health_monitor returns singleton"""
        monitor1 = get_health_monitor()
        monitor2 = get_health_monitor()
        
        assert monitor1 is monitor2
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check"""
        # Mock the _perform_check method
        check = DatabaseHealthCheck("test://connection/string")
        
        # We need to mock _perform_check on the instance
        check._perform_check = AsyncMock(return_value={
            "connection_status": "connected", 
            "response_time_ms": 25
        })
        
        result = await check.check()
        
        assert result.name == "database"
        assert result.status == HealthStatus.HEALTHY
        assert result.details["connection_status"] == "connected"
    
    @pytest.mark.asyncio
    async def test_external_service_health_check(self):
        """Test external service health check"""
        # Mock aiohttp client
        with patch('aiohttp.ClientSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 200
            
            mock_get_ctx = AsyncMock()
            mock_get_ctx.__aenter__.return_value = mock_response
            
            # session.get is not async, it returns a context manager
            mock_session.get = Mock(return_value=mock_get_ctx)
            
            check = ExternalServiceHealthCheck("test_service", "http://test-service.com")
            result = await check.check()
            
            assert result.name == "external_service_test_service"
            assert result.status == HealthStatus.HEALTHY
            assert result.details["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_system_resource_health_check(self):
        """Test system resource health check"""
        # Mock psutil functions
        with patch('psutil.cpu_percent', return_value=50.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 60.0
            mock_memory.return_value.available = 4 * (1024**3)  # 4GB
            
            mock_disk.return_value.used = 50 * (1024**3)  # 50GB used
            mock_disk.return_value.total = 100 * (1024**3)  # 100GB total
            mock_disk.return_value.free = 50 * (1024**3)  # 50GB free
            
            check = SystemResourceHealthCheck()
            result = await check.check()
            
            assert result.name == "system_resources"
            assert result.status == HealthStatus.HEALTHY
            assert result.details["cpu_usage_percent"] == 50.0
            assert result.details["memory_usage_percent"] == 60.0
            assert result.details["disk_usage_percent"] == 50.0
    
    @pytest.mark.asyncio
    async def test_system_resource_health_check_threshold_exceeded(self):
        """Test system resource health check when thresholds exceeded"""
        # Mock psutil functions with high usage
        with patch('psutil.cpu_percent', return_value=90.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 95.0
            mock_memory.return_value.available = 1 * (1024**3)  # 1GB
            
            mock_disk.return_value.used = 95 * (1024**3)  # 95GB used
            mock_disk.return_value.total = 100 * (1024**3)  # 100GB total
            mock_disk.return_value.free = 5 * (1024**3)  # 5GB free
            
            check = SystemResourceHealthCheck()
            result = await check.check()
            
            assert result.name == "system_resources"
            assert result.status == HealthStatus.UNHEALTHY
            assert "System resources above threshold" in result.error
    
    @pytest.mark.asyncio
    async def test_setup_default_health_checks(self):
        """Test setup of default health checks"""
        external_services = [
            {"name": "service1", "url": "http://service1.com"},
            {"name": "service2", "url": "http://service2.com"}
        ]
        
        system_thresholds = {
            "cpu": 70.0,
            "memory": 80.0,
            "disk": 85.0
        }
        
        setup_default_health_checks(
            database_connection_string="test://db",
            external_services=external_services,
            system_thresholds=system_thresholds
        )
        
        monitor = get_health_monitor()
        
        # Should have added database, external services, and system checks
        assert len(monitor.checks) == 4  # database + 2 services + system
        
        # Verify the checks were added correctly
        check_names = [check.name for check in monitor.checks]
        assert "database" in check_names
        assert "external_service_service1" in check_names
        assert "external_service_service2" in check_names
        assert "system_resources" in check_names

if __name__ == "__main__":
    # Run the tests
    test = TestHealthMonitoring()
    
    print("Running health monitoring tests...")
    
    # Run basic tests
    test.setup_method()
    asyncio.run(test.test_basic_health_check())
    print("✅ Basic health check test passed")
    
    asyncio.run(test.test_failing_health_check())
    print("✅ Failing health check test passed")
    
    asyncio.run(test.test_health_monitor_with_multiple_checks())
    print("✅ Multiple checks test passed")
    
    test.test_health_monitor_overall_status_healthy()
    print("✅ Overall status healthy test passed")
    
    test.test_health_monitor_overall_status_degraded()
    print("✅ Overall status degraded test passed")
    
    asyncio.run(test.test_custom_health_check_function())
    print("✅ Custom health check test passed")
    
    test.test_get_health_monitor_singleton()
    print("✅ Singleton test passed")
    
    print("🎉 All health monitoring tests passed!")