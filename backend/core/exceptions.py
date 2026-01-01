"""
dhii Mail - Exception Handlers
Global exception handling for the application.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)

class DhiiMailException(HTTPException):
    """Base exception for dhii Mail application."""
    pass

class AuthenticationException(DhiiMailException):
    """Authentication-related exceptions."""
    pass

class AuthorizationException(DhiiMailException):
    """Authorization-related exceptions."""
    pass

class ValidationException(DhiiMailException):
    """Validation-related exceptions."""
    pass

class DatabaseException(DhiiMailException):
    """Database-related exceptions."""
    pass

class EmailException(DhiiMailException):
    """Email-related exceptions."""
    pass

class AIException(DhiiMailException):
    """AI service-related exceptions."""
    pass

def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the application."""
    
    @app.exception_handler(DhiiMailException)
    async def dhii_mail_exception_handler(request: Request, exc: DhiiMailException):
        """Handle dhii Mail specific exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "type": exc.__class__.__name__,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "type": "HTTPException",
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors."""
        logger.error(f"ValueError: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "error": str(exc),
                "type": "ValueError",
                "status_code": 400
            }
        )
    
    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        """Handle key errors."""
        logger.error(f"KeyError: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "error": f"Missing required field: {exc}",
                "type": "KeyError",
                "status_code": 400
            }
        )
    
    @app.exception_handler(TypeError)
    async def type_error_handler(request: Request, exc: TypeError):
        """Handle type errors."""
        logger.error(f"TypeError: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "error": str(exc),
                "type": "TypeError",
                "status_code": 400
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "type": exc.__class__.__name__,
                "status_code": 500,
                "detail": str(exc) if __debug__ else "An error occurred"
            }
        )

def create_error_response(error: str, status_code: int = 400, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "error": error,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        response["details"] = details
    
    return response

def log_error(error_type: str, message: str, details: Dict[str, Any] = None, level: str = "error"):
    """Log errors with context."""
    log_data = {
        "type": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        log_data["details"] = details
    
    if level == "error":
        logger.error(log_data)
    elif level == "warning":
        logger.warning(log_data)
    elif level == "info":
        logger.info(log_data)
    else:
        logger.debug(log_data)