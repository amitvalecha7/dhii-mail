"""
Framework 2.0: OpenTelemetry Instrumentation
Telemetry and observability for plugin operations
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Fallback implementation
    class Status:
        pass
    class StatusCode:
        OK = "OK"
        ERROR = "ERROR"

# Configure logging
logger = logging.getLogger(__name__)

class PluginTelemetry:
    """Telemetry instrumentation for plugin operations"""
    
    def __init__(self, service_name: str = "plugin-framework", 
                 otlp_endpoint: Optional[str] = None):
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.tracer = None
        self._setup_telemetry()
    
    def _setup_telemetry(self):
        """Setup OpenTelemetry if available"""
        if not OTEL_AVAILABLE:
            logger.info("OpenTelemetry not available, using fallback telemetry")
            return
        
        try:
            # Configure tracer provider
            provider = TracerProvider()
            trace.set_tracer_provider(provider)
            
            # Create tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Setup OTLP exporter if endpoint provided
            if self.otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
                span_processor = BatchSpanProcessor(otlp_exporter)
                provider.add_span_processor(span_processor)
            
            # Instrument logging
            LoggingInstrumentor().instrument()
            
            logger.info("OpenTelemetry instrumentation configured")
            
        except Exception as e:
            logger.error(f"Failed to setup OpenTelemetry: {e}")
            self.tracer = None
    
    def instrument_plugin_load(self):
        """Instrument plugin loading - plugin_id extracted from function args"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract plugin_id from function arguments
                plugin_id = args[0] if args else kwargs.get('plugin_id', 'unknown')
                start_time = time.time()
                operation_name = f"plugin.{plugin_id}.load"
                
                if self.tracer:
                    with self.tracer.start_as_current_span(operation_name) as span:
                        span.set_attribute("plugin.id", plugin_id)
                        span.set_attribute("operation.type", "load")
                        
                        try:
                            result = func(*args, **kwargs)
                            span.set_status(Status(StatusCode.OK))
                            span.set_attribute("load.success", True)
                            return result
                        except Exception as e:
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            span.set_attribute("load.success", False)
                            span.set_attribute("error.message", str(e))
                            raise
                        finally:
                            duration = time.time() - start_time
                            span.set_attribute("operation.duration_ms", duration * 1000)
                else:
                    # Fallback logging
                    logger.info(f"Loading plugin: {plugin_id}")
                    try:
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        logger.info(f"Plugin {plugin_id} loaded successfully in {duration:.2f}s")
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        logger.error(f"Plugin {plugin_id} failed to load after {duration:.2f}s: {e}")
                        raise
            
            return wrapper
        return decorator
    
    def instrument_capability_execution(self, plugin_id: str, capability_id: str):
        """Instrument capability execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                operation_name = f"plugin.{plugin_id}.capability.{capability_id}"
                
                if self.tracer:
                    with self.tracer.start_as_current_span(operation_name) as span:
                        span.set_attribute("plugin.id", plugin_id)
                        span.set_attribute("capability.id", capability_id)
                        span.set_attribute("operation.type", "execute")
                        
                        try:
                            result = func(*args, **kwargs)
                            span.set_status(Status(StatusCode.OK))
                            span.set_attribute("execution.success", True)
                            return result
                        except Exception as e:
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            span.set_attribute("execution.success", False)
                            span.set_attribute("error.message", str(e))
                            span.set_attribute("error.type", type(e).__name__)
                            raise
                        finally:
                            duration = time.time() - start_time
                            span.set_attribute("operation.duration_ms", duration * 1000)
                else:
                    # Fallback logging
                    logger.info(f"Executing capability: {plugin_id}.{capability_id}")
                    try:
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        logger.info(f"Capability {plugin_id}.{capability_id} executed successfully in {duration:.2f}s")
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        logger.error(f"Capability {plugin_id}.{capability_id} failed after {duration:.2f}s: {e}")
                        raise
            
            return wrapper
        return decorator
    
    def record_plugin_health(self, plugin_id: str, health_status: str, 
                           message: Optional[str] = None, **kwargs):
        """Record plugin health status"""
        if self.tracer:
            operation_name = f"plugin.{plugin_id}.health"
            with self.tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("plugin.id", plugin_id)
                span.set_attribute("health.status", health_status)
                if message:
                    span.set_attribute("health.message", message)
                for key, value in kwargs.items():
                    span.set_attribute(f"health.{key}", value)
        else:
            # Fallback logging
            health_msg = f"Plugin {plugin_id} health: {health_status}"
            if message:
                health_msg += f" - {message}"
            if health_status == "healthy":
                logger.info(health_msg)
            else:
                logger.warning(health_msg)
    
    def record_metric(self, metric_name: str, value: float, 
                     plugin_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """Record a custom metric"""
        if self.tracer:
            operation_name = f"metric.{metric_name}"
            with self.tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("metric.name", metric_name)
                span.set_attribute("metric.value", value)
                if plugin_id:
                    span.set_attribute("plugin.id", plugin_id)
                if tags:
                    for key, tag_value in tags.items():
                        span.set_attribute(f"tag.{key}", tag_value)
        else:
            # Fallback logging
            metric_msg = f"Metric {metric_name}: {value}"
            if plugin_id:
                metric_msg += f" (plugin: {plugin_id})"
            if tags:
                tags_str = ", ".join([f"{k}={v}" for k, v in tags.items()])
                metric_msg += f" [{tags_str}]"
            logger.info(metric_msg)

# Global telemetry instance
telemetry = PluginTelemetry()

def get_telemetry() -> PluginTelemetry:
    """Get the global telemetry instance"""
    return telemetry