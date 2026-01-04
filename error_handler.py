"""
Standardized Error Handling Utility for dhii-mail
Provides consistent error handling patterns across all modules
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone
from enum import Enum
import json

from a2ui_integration.core.logging import get_logger

logger = get_logger(__name__)

class ErrorCategory(Enum):
    """Error categories for consistent error classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    DATABASE = "database"
    NETWORK = "network"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    UNKNOWN = "unknown"
    NOT_FOUND = "not_found"
    RATE_LIMIT = "rate_limit"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AppError(Exception):
    """Base application exception with standardized error handling"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.code = code or f"{category.value.upper()}_ERROR"
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = datetime.now(timezone.utc)
        self.traceback = traceback.format_exc() if original_error else None
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "category": self.category.value,
                "severity": self.severity.value,
                "timestamp": self.timestamp.isoformat(),
                "details": self.details
            }
        }
    
    def __str__(self):
        return f"{self.code}: {self.message}"

class AuthenticationError(AppError):
    """Authentication-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

class AuthorizationError(AppError):
    """Authorization-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

class ValidationError(AppError):
    """Input validation errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )

class DatabaseError(AppError):
    """Database operation errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

class NetworkError(AppError):
    """Network-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class ExternalServiceError(AppError):
    """External service (email, calendar, etc.) errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class ResourceNotFoundError(AppError):
    """Resource not found errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.LOW,
            **kwargs
        )

class RateLimitError(AppError):
    """Rate limit exceeded errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class ErrorHandler:
    """Centralized error handling utility"""
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        log_level: int = logging.ERROR
    ) -> AppError:
        """
        Standardized error handling with automatic categorization
        
        Args:
            error: The original exception
            context: Additional context information
            log_level: Logging level for this error
            
        Returns:
            Standardized AppError instance
        """
        context = context or {}
        
        # Log the error with context
        logger.log(log_level, f"Error occurred: {str(error)}", extra={
            "error_type": type(error).__name__,
            "context": context,
            "traceback": traceback.format_exc()
        })
        
        # Categorize the error automatically
        if isinstance(error, AppError):
            return error
        elif isinstance(error, (ValueError, TypeError)):
            app_error = ValidationError(
                message=str(error),
                original_error=error,
                details=context
            )
        elif "auth" in str(error).lower() or "token" in str(error).lower():
            app_error = AuthenticationError(
                message=str(error),
                original_error=error,
                details=context
            )
        elif "permission" in str(error).lower() or "access" in str(error).lower():
            app_error = AuthorizationError(
                message=str(error),
                original_error=error,
                details=context
            )
        elif "connection" in str(error).lower() or "network" in str(error).lower():
            app_error = NetworkError(
                message=str(error),
                original_error=error,
                details=context
            )
        elif "database" in str(error).lower() or "sql" in str(error).lower():
            app_error = DatabaseError(
                message=str(error),
                original_error=error,
                details=context
            )
        elif any(service in str(error).lower() for service in ["email", "imap", "smtp", "calendar", "meeting"]):
            app_error = ExternalServiceError(
                message=str(error),
                original_error=error,
                details=context
            )
        else:
            app_error = AppError(
                message=str(error),
                original_error=error,
                details=context
            )
        
        return app_error
    
    @staticmethod
    def safe_execute(
        func,
        *args,
        context: Optional[Dict[str, Any]] = None,
        default_return: Any = None,
        **kwargs
    ) -> Any:
        """
        Safely execute a function with automatic error handling
        
        Args:
            func: Function to execute
            *args: Positional arguments
            context: Additional context for error handling
            default_return: Default value to return on error
            **kwargs: Keyword arguments
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error = ErrorHandler.handle_error(e, context)
            logger.error(f"Function {func.__name__} failed: {error.message}")
            return default_return
    
    @staticmethod
    def create_error_response(
        error: Union[Exception, AppError],
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response for API endpoints
        
        Args:
            error: The error to respond to
            status_code: HTTP status code
            context: Additional context
            
        Returns:
            Standardized error response dictionary
        """
        if not isinstance(error, AppError):
            error = ErrorHandler.handle_error(error, context)
        
        response = error.to_dict()
        response["status_code"] = status_code
        
        # Add development details in debug mode
        import os
        if os.getenv("DEBUG", "false").lower() == "true":
            response["error"]["traceback"] = error.traceback
            response["error"]["original_error"] = str(error.original_error) if error.original_error else None
        
        return response

# Global error handler instance
error_handler = ErrorHandler()

# Convenience functions for common error handling patterns
def handle_auth_error(message: str, **kwargs) -> AuthenticationError:
    """Create authentication error"""
    return AuthenticationError(message, **kwargs)

def handle_validation_error(message: str, **kwargs) -> ValidationError:
    """Create validation error"""
    return ValidationError(message, **kwargs)

def handle_database_error(message: str, **kwargs) -> DatabaseError:
    """Create database error"""
    return DatabaseError(message, **kwargs)

def handle_network_error(message: str, **kwargs) -> NetworkError:
    """Create network error"""
    return NetworkError(message, **kwargs)

def handle_external_service_error(message: str, **kwargs) -> ExternalServiceError:
    """Create external service error"""
    return ExternalServiceError(message, **kwargs)