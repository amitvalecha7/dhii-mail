"""
dhii Mail - Middleware
Request/response middleware for logging, rate limiting, and security.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import time
import logging
from typing import Optional
import json
from database import get_db

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests = {}  # identifier: [(timestamp, count)]
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited."""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            (timestamp, count) for timestamp, count in self.requests[identifier]
            if timestamp > hour_ago
        ]
        
        # Count requests in time windows
        minute_count = sum(count for timestamp, count in self.requests[identifier] if timestamp > minute_ago)
        hour_count = sum(count for timestamp, count in self.requests[identifier])
        
        # Check limits
        if minute_count >= self.requests_per_minute:
            return True
        if hour_count >= self.requests_per_hour:
            return True
        
        # Record this request
        self.requests[identifier].append((now, 1))
        return False
    
    def cleanup(self):
        """Clean up old request records."""
        now = time.time()
        hour_ago = now - 3600
        
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                (timestamp, count) for timestamp, count in self.requests[identifier]
                if timestamp > hour_ago
            ]
            if not self.requests[identifier]:
                del self.requests[identifier]

# Global rate limiter instance
rate_limiter = RateLimiter()

def setup_middleware(app: FastAPI):
    """Setup all middleware for the application."""
    
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Log all requests and responses."""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url.path} "
            f"in {process_time:.3f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Apply rate limiting to requests."""
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        # Get identifier (IP address or user ID if authenticated)
        identifier = request.client.host
        
        # Check for authentication token to apply user-specific rate limiting
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For authenticated users, use a combination of user ID and IP
            # This allows for more granular rate limiting
            try:
                # Extract user identifier from token (simplified approach)
                identifier = f"user_auth_{identifier}"
            except Exception:
                # Fall back to IP-based if token parsing fails
                pass
        
        # Check rate limit
        if rate_limiter.is_rate_limited(identifier):
            logger.warning(f"Rate limit exceeded for {identifier}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": 60}
            )
        
        return await call_next(request)
    
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        """Add security headers to responses."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    @app.middleware("http")
    async def database_session_middleware(request: Request, call_next):
        """Ensure database connection is available for each request."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Database error in request {request.url.path}: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Database error"}
            )

def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection
    return request.client.host if request.client else "unknown"

def log_request(request: Request, response: Response, duration: float):
    """Log request details for analytics and debugging."""
    log_data = {
        "timestamp": time.time(),
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "status_code": response.status_code,
        "duration": duration,
        "client_ip": get_client_ip(request),
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "content_length": response.headers.get("Content-Length", 0)
    }
    
    # Log at appropriate level
    if response.status_code >= 500:
        logger.error(f"Server error: {log_data}")
    elif response.status_code >= 400:
        logger.warning(f"Client error: {log_data}")
    else:
        logger.info(f"Request completed: {log_data}")

def sanitize_request_data(data: dict) -> dict:
    """Sanitize sensitive data from request logs."""
    sensitive_keys = ['password', 'token', 'secret', 'key', 'auth', 'credential']
    sanitized = {}
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value
    
    return sanitized