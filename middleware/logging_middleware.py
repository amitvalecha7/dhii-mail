"""
Logging Middleware for FastAPI
Provides request/response logging with correlation IDs and performance metrics
"""

import time
import uuid
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from a2ui_integration.core.logging import (
    get_logger, 
    set_correlation_id, 
    clear_correlation_id,
    get_correlation_id
)

logger = get_logger("middleware.logging")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate correlation ID if not present
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Set correlation ID for this request
        set_correlation_id(correlation_id)
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            "Incoming request",
            extra_fields={
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "headers": dict(request.headers),
                    "client_host": request.client.host if request.client else None,
                    "content_length": int(request.headers.get("content-length", 0))
                },
                "correlation_id": correlation_id
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            logger.info(
                "Request completed successfully",
                extra_fields={
                    "response": {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "duration_ms": round(duration_ms, 2)
                    },
                    "correlation_id": correlation_id
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration even for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "Request failed with exception",
                extra_fields={
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "duration_ms": round(duration_ms, 2)
                    },
                    "correlation_id": correlation_id
                }
            )
            
            # Re-raise the exception
            raise
            
        finally:
            # Clear correlation ID after request completes
            clear_correlation_id()

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Lightweight middleware that only adds correlation IDs"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Set correlation ID
        set_correlation_id(correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response
        response.headers["X-Correlation-ID"] = correlation_id
        
        # Clear correlation ID
        clear_correlation_id()
        
        return response

def setup_logging_middleware(app):
    """Setup logging middleware for FastAPI app"""
    # Add correlation ID middleware first
    app.add_middleware(CorrelationIDMiddleware)
    
    # Add full logging middleware
    app.add_middleware(LoggingMiddleware)
    
    logger.info("Logging middleware setup completed")