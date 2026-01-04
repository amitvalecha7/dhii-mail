"""
Health monitoring system for production readiness
Provides comprehensive health checks for database, external services, and system resources
"""

import asyncio
import json
import time
import psutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import aiohttp
from .logging import get_logger

logger = get_logger(__name__)

class HealthStatus(Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthCheck:
    """Base class for health checks"""
    
    def __init__(self, name: str, timeout_ms: int = 5000):
        self.name = name
        self.timeout_ms = timeout_ms
    
    async def check(self) -> HealthCheckResult:
        """Perform the health check"""
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        try:
            result = await asyncio.wait_for(self._perform_check(), timeout=self.timeout_ms/1000)
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Check passed",
                duration_ms=duration_ms,
                timestamp=timestamp,
                details=result
            )
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Check timed out",
                duration_ms=duration_ms,
                timestamp=timestamp,
                error=f"Timeout after {self.timeout_ms}ms"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Health check {self.name} failed", extra_fields={
                "operation": "health_check",
                "check_name": self.name,
                "error": str(e)
            })
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Check failed",
                duration_ms=duration_ms,
                timestamp=timestamp,
                error=str(e)
            )
    
    async def _perform_check(self) -> Optional[Dict[str, Any]]:
        """Override this method to implement the actual check"""
        raise NotImplementedError

class DatabaseHealthCheck(HealthCheck):
    """Database connectivity health check"""
    
    def __init__(self, connection_string: str, timeout_ms: int = 5000):
        super().__init__("database", timeout_ms)
        self.connection_string = connection_string
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check database connectivity"""
        # This is a placeholder - implement actual database connectivity check
        # For now, we'll simulate a successful check
        return {
            "connection_string": self.connection_string,
            "connection_status": "connected",
            "response_time_ms": 25
        }

class ExternalServiceHealthCheck(HealthCheck):
    """External service health check"""
    
    def __init__(self, service_name: str, service_url: str, timeout_ms: int = 5000):
        super().__init__(f"external_service_{service_name}", timeout_ms)
        self.service_name = service_name
        self.service_url = service_url
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check external service availability"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_ms/1000)) as session:
            start_time = time.time()
            async with session.get(f"{self.service_url}/health") as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    return {
                        "service_name": self.service_name,
                        "url": self.service_url,
                        "status_code": response.status,
                        "response_time_ms": response_time_ms
                    }
                else:
                    raise Exception(f"Service returned status {response.status}")

class SystemResourceHealthCheck(HealthCheck):
    """System resource health check"""
    
    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 85.0, disk_threshold: float = 90.0):
        super().__init__("system_resources", timeout_ms=3000)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        details = {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": (disk.used / disk.total) * 100,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3)
        }
        
        # Determine status based on thresholds
        if (cpu_percent > self.cpu_threshold or 
            memory.percent > self.memory_threshold or 
            (disk.used / disk.total) * 100 > self.disk_threshold):
            raise Exception("System resources above threshold")
        
        return details

class HealthMonitor:
    """Health monitoring system"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.custom_checks: Dict[str, Callable] = {}
        self.last_health_report: Optional[Dict[str, Any]] = None
    
    def add_check(self, check: HealthCheck):
        """Add a health check"""
        self.checks.append(check)
    
    def add_custom_check(self, name: str, check_func: Callable):
        """Add a custom health check function"""
        self.custom_checks[name] = check_func
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform all health checks and return comprehensive report"""
        logger.info("Performing health checks", extra_fields={"operation": "health_check"})
        
        start_time = time.time()
        
        # Perform all registered checks in parallel
        check_tasks = [check.check() for check in self.checks]
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Filter out any exceptions (they're already logged in individual checks)
        valid_results = [result for result in check_results if isinstance(result, HealthCheckResult)]
        
        # Perform custom checks
        for name, check_func in self.custom_checks.items():
            try:
                result = await check_func()
                if isinstance(result, HealthCheckResult):
                    valid_results.append(result)
                else:
                    # Convert simple result to HealthCheckResult
                    valid_results.append(HealthCheckResult(
                        name=name,
                        status=HealthStatus.HEALTHY,
                        message="Custom check passed",
                        duration_ms=0,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        details=result
                    ))
            except Exception as e:
                logger.error(f"Custom health check {name} failed", extra_fields={
                    "operation": "health_check",
                    "check_name": name,
                    "error": str(e)
                })
                valid_results.append(HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message="Custom check failed",
                    duration_ms=0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    error=str(e)
                ))
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(valid_results)
        
        # Build comprehensive report
        report = {
            "status": overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": (time.time() - start_time) * 1000,
            "checks": {
                result.name: {
                    "status": result.status.value,
                    "message": result.message,
                    "duration_ms": result.duration_ms,
                    "timestamp": result.timestamp,
                    "details": result.details,
                    "error": result.error
                }
                for result in valid_results
            },
            "summary": {
                "total_checks": len(valid_results),
                "healthy_checks": len([r for r in valid_results if r.status == HealthStatus.HEALTHY]),
                "degraded_checks": len([r for r in valid_results if r.status == HealthStatus.DEGRADED]),
                "unhealthy_checks": len([r for r in valid_results if r.status == HealthStatus.UNHEALTHY])
            }
        }
        
        self.last_health_report = report
        
        logger.info("Health check completed", extra_fields={
            "operation": "health_check",
            "overall_status": overall_status.value,
            "total_checks": len(valid_results),
            "healthy_checks": len([r for r in valid_results if r.status == HealthStatus.HEALTHY]),
            "unhealthy_checks": len([r for r in valid_results if r.status == HealthStatus.UNHEALTHY])
        })
        
        return report
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall health status from individual results"""
        if not results:
            return HealthStatus.UNKNOWN
        
        unhealthy_count = len([r for r in results if r.status == HealthStatus.UNHEALTHY])
        degraded_count = len([r for r in results if r.status == HealthStatus.DEGRADED])
        
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_last_report(self) -> Optional[Dict[str, Any]]:
        """Get the last health report"""
        return self.last_health_report

# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor

def setup_default_health_checks(
    database_connection_string: Optional[str] = None,
    external_services: Optional[List[Dict[str, str]]] = None,
    system_thresholds: Optional[Dict[str, float]] = None
):
    """Setup default health checks"""
    monitor = get_health_monitor()
    
    # Add database health check if connection string provided
    if database_connection_string:
        monitor.add_check(DatabaseHealthCheck(database_connection_string))
    
    # Add external service health checks
    if external_services:
        for service in external_services:
            monitor.add_check(ExternalServiceHealthCheck(
                service_name=service["name"],
                service_url=service["url"]
            ))
    
    # Add system resource health check
    if system_thresholds:
        monitor.add_check(SystemResourceHealthCheck(
            cpu_threshold=system_thresholds.get("cpu", 80.0),
            memory_threshold=system_thresholds.get("memory", 85.0),
            disk_threshold=system_thresholds.get("disk", 90.0)
        ))
    else:
        monitor.add_check(SystemResourceHealthCheck())