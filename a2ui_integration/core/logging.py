"""
Structured Logging System for dhii-mail
Provides JSON-formatted logging with correlation IDs and structured data
"""

import logging
import json
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from contextvars import ContextVar
import traceback
from pathlib import Path

# Context variable for correlation IDs
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        # Get correlation ID from context
        correlation_id = correlation_id_var.get()
        
        # Build the log entry
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': correlation_id or str(uuid.uuid4()),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add performance metrics if present
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        
        if hasattr(record, 'memory_usage_mb'):
            log_entry['memory_usage_mb'] = record.memory_usage_mb
        
        return json.dumps(log_entry, ensure_ascii=False)

class StructuredLogger:
    """Structured logger with correlation ID support"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _log_with_fields(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Log with structured fields"""
        if extra_fields is None:
            extra_fields = {}
        
        # Add any additional kwargs as extra fields
        extra_fields.update(kwargs)
        
        # Ensure correlation_id is in extra_fields
        if 'correlation_id' not in extra_fields:
            extra_fields['correlation_id'] = get_correlation_id()
        
        # Use the standard logging method with extra fields
        self.logger.log(level, message, extra={'extra_fields': extra_fields})
    
    def log(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Log with specific level and structured fields"""
        # Support 'extra' from standard logging calls for compatibility
        if 'extra' in kwargs:
            if extra_fields is None:
                extra_fields = {}
            extra_dict = kwargs.pop('extra')
            if isinstance(extra_dict, dict):
                extra_fields.update(extra_dict)
        
        self._log_with_fields(level, message, extra_fields, **kwargs)

    def info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Info level logging with structured fields"""
        self._log_with_fields(logging.INFO, message, extra_fields, **kwargs)
    
    def error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Error level logging with structured fields"""
        self._log_with_fields(logging.ERROR, message, extra_fields, **kwargs)
    
    def warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Warning level logging with structured fields"""
        self._log_with_fields(logging.WARNING, message, extra_fields, **kwargs)
    
    def debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Debug level logging with structured fields"""
        self._log_with_fields(logging.DEBUG, message, extra_fields, **kwargs)
    
    def critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Critical level logging with structured fields"""
        self._log_with_fields(logging.CRITICAL, message, extra_fields, **kwargs)
    
    def exception(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """Exception logging with structured fields"""
        self.logger.exception(message, extra=extra_fields or {})

def setup_structured_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup structured logging configuration"""
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create JSON formatter
    formatter = JSONFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # File handler if specified
    handlers = [console_handler]
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

def get_correlation_id() -> str:
    """Get current correlation ID or empty string if not set"""
    return correlation_id_var.get()

def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context"""
    correlation_id_var.set(correlation_id)

def clear_correlation_id():
    """Clear correlation ID from current context"""
    correlation_id_var.set('')

# Performance tracking utilities
class PerformanceTracker:
    """Context manager for tracking performance metrics"""
    
    def __init__(self, operation: str, logger: StructuredLogger):
        self.operation = operation
        self.logger = logger
        self.start_time = None
        self.start_memory = None
    
    def __enter__(self):
        self.start_time = time.time()
        # Note: Memory tracking would require psutil dependency
        # For now, we'll just track time
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                f"{self.operation} completed successfully",
                duration_ms=round(duration_ms, 2),
                operation=self.operation,
                status="success"
            )
        else:
            self.logger.error(
                f"{self.operation} failed",
                duration_ms=round(duration_ms, 2),
                operation=self.operation,
                status="failed",
                error_type=exc_type.__name__ if exc_type else None
            )

def get_logger(name: str) -> StructuredLogger:
    """Get structured logger instance"""
    return StructuredLogger(name)