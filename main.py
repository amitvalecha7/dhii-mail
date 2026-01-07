import logging
import time
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.core.middleware import database_session_middleware
from a2ui_integration.core.logging import get_logger
from middleware.logging_middleware import setup_logging_middleware
from middleware.apm import setup_apm
from error_handler import ErrorHandler, ErrorCategory
from error_tracking_service import ErrorTrackingService, ErrorContext, get_error_tracking_service
from a2ui_integration.core.kernel import Kernel
from a2ui_integration.kernel_router import router as kernel_router

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DHII Mail API",
    description="Backend API for DHII Mail application",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Setup middleware
# Note: Middleware is executed in reverse order of addition (LIFO)

# 0. APM (Advanced Monitoring) - Outermost
setup_apm(app)

# 1. Logging middleware
setup_logging_middleware(app)

# 2. Security Headers middleware (will execute after CORS)
# SECURITY: Add security headers as per security manifesto
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers based on security manifesto
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Add HSTS in production
    # SECURITY: Enable HSTS in production for HTTPS enforcement
    if os.environ.get('ENVIRONMENT', 'development').lower() == 'production':
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Add Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    return response

# 3. Database session middleware
app.middleware("http")(database_session_middleware)

# 4. CORS middleware (innermost of standard middleware)
# SECURITY: Configure CORS based on environment and security requirements
from config import settings
cors_config = settings.get_cors_config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# Initialize Intelligence Layer - temporarily disabled due to missing dependencies
# from intelligence_layer import initialize_intelligence_layer

# Global kernel instance
kernel = None

@app.on_event("startup")
async def startup_event():
    """Initialize Intelligence Layer and Kernel on application startup"""
    global kernel
    try:
        # Initialize kernel
        kernel = Kernel(db_path="kernel.db", secret_key="kernel-secret-key")
        await kernel.initialize()
        logger.info("Kernel initialized successfully")
        
        # Set kernel instance in kernel router
        import a2ui_integration.kernel_router as kernel_router_module
        kernel_router_module.kernel = kernel
        
        # Initialize Intelligence Layer - temporarily disabled due to missing dependencies
        # await initialize_intelligence_layer()
        # logger.info("Intelligence Layer initialized successfully")
        logger.info("Intelligence Layer initialization skipped - missing dependencies")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup Intelligence Layer on application shutdown"""
    try:
        # Temporarily disabled due to missing dependencies
        # from intelligence_layer import get_intelligence_layer
        # layer = get_intelligence_layer()
        # await layer.stop()
        # logger.info("Intelligence Layer stopped successfully")
        logger.info("Intelligence Layer shutdown skipped - missing dependencies")
    except Exception as e:
        logger.error(f"Failed to stop Intelligence Layer: {e}")

@app.get("/api")
async def root():
    """Root endpoint to verify API is running."""
    logger.info("Root endpoint accessed")
    return {"message": "DHII Mail API is running"}

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

# Import and include routers
from auth_api import app as auth_app
app.mount("/auth", auth_app)

# from routers import users
# app.include_router(users.router, prefix="/api/users", tags=["users"])

# A2UI Router - temporarily disabled due to missing dependencies
# from a2ui_integration.a2ui_router import router as a2ui_router
# app.include_router(a2ui_router)

# Kernel Router
app.include_router(kernel_router)

# Error Tracking API Endpoints
@app.get("/api/v1/errors/summary")
async def get_error_summary(hours: int = 24):
    """Get error summary for the last N hours"""
    try:
        error_tracking_service = get_error_tracking_service()
        summary = error_tracking_service.get_error_summary(hours)
        return summary
    except Exception as e:
        logger.error(f"Failed to get error summary: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve error summary"}
        )

@app.get("/api/v1/errors/{error_id}")
async def get_error_details(error_id: int):
    """Get detailed information about a specific error"""
    try:
        error_tracking_service = get_error_tracking_service()
        details = error_tracking_service.get_error_details(error_id)
        if details is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Error not found"}
            )
        return details
    except Exception as e:
        logger.error(f"Failed to get error details: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve error details"}
        )

@app.post("/api/v1/errors/{error_id}/acknowledge")
async def acknowledge_error(error_id: int, user_id: str):
    """Acknowledge an error"""
    try:
        error_tracking_service = get_error_tracking_service()
        success = error_tracking_service.acknowledge_error(error_id, user_id)
        if success:
            return {"message": "Error acknowledged successfully"}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to acknowledge error"}
            )
    except Exception as e:
        logger.error(f"Failed to acknowledge error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to acknowledge error"}
        )

@app.post("/api/v1/errors/{error_id}/resolve")
async def resolve_error(error_id: int, user_id: str, resolution_notes: str = ""):
    """Mark an error as resolved"""
    try:
        error_tracking_service = get_error_tracking_service()
        success = error_tracking_service.resolve_error(error_id, user_id, resolution_notes)
        if success:
            return {"message": "Error resolved successfully"}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to resolve error"}
            )
    except Exception as e:
        logger.error(f"Failed to resolve error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to resolve error"}
        )

# Kernel API Endpoints
@app.get("/api/kernel/health")
async def kernel_health():
    """Get kernel health status and metrics"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        plugins = await kernel.list_plugins()
        total_plugins = len(plugins)
        enabled_plugins = len([p for p in plugins if p.status.value == "enabled"])
        
        return {
            "status": "healthy",
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_plugins,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Kernel health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/kernel/metrics")
async def kernel_metrics():
    """Get kernel performance metrics"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        plugins = await kernel.list_plugins()
        total_usage = sum(p.usage_count for p in plugins)
        total_errors = sum(p.error_count for p in plugins)
        
        return {
            "total_usage": total_usage,
            "total_errors": total_errors,
            "total_plugins": len(plugins),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Kernel metrics failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/kernel/plugins")
async def list_kernel_plugins():
    """List all plugins managed by the kernel"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        plugins = await kernel.list_plugins()
        return {"plugins": [plugin.to_dict() for plugin in plugins]}
    except Exception as e:
        logger.error(f"Failed to list kernel plugins: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/kernel/plugins/{plugin_id}")
async def get_kernel_plugin(plugin_id: str):
    """Get specific plugin details from kernel"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        plugin = await kernel.get_plugin(plugin_id)
        if plugin is None:
            return JSONResponse(
                status_code=404,
                content={"status": "not_found", "message": f"Plugin {plugin_id} not found"}
            )
        
        return plugin.to_dict()
    except Exception as e:
        logger.error(f"Failed to get kernel plugin {plugin_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.put("/api/kernel/plugins/{plugin_id}/enable")
async def enable_kernel_plugin(plugin_id: str):
    """Enable a plugin in the kernel"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        success = await kernel.enable_plugin(plugin_id)
        if success:
            return {"status": "success", "message": f"Plugin {plugin_id} enabled"}
        else:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Failed to enable plugin {plugin_id}"}
            )
    except Exception as e:
        logger.error(f"Failed to enable kernel plugin {plugin_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.put("/api/kernel/plugins/{plugin_id}/disable")
async def disable_kernel_plugin(plugin_id: str):
    """Disable a plugin in the kernel"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        success = await kernel.disable_plugin(plugin_id)
        if success:
            return {"status": "success", "message": f"Plugin {plugin_id} disabled"}
        else:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Failed to disable plugin {plugin_id}"}
            )
    except Exception as e:
        logger.error(f"Failed to disable kernel plugin {plugin_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/kernel/plugins/{plugin_id}/health")
async def get_plugin_health(plugin_id: str):
    """Get health status of a specific plugin"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        plugin = await kernel.get_plugin(plugin_id)
        if plugin is None:
            return JSONResponse(
                status_code=404,
                content={"status": "not_found", "message": f"Plugin {plugin_id} not found"}
            )
        
        health_status = "healthy" if plugin.error_count == 0 else "degraded"
        return {
            "plugin_id": plugin_id,
            "status": health_status,
            "error_count": plugin.error_count,
            "usage_count": plugin.usage_count,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Failed to get plugin health {plugin_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.post("/api/kernel/capabilities/{capability_id}/execute")
async def execute_capability(capability_id: str, params: Dict[str, Any]):
    """Execute a capability through the kernel"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        result = await kernel.execute_capability(capability_id, params)
        return {"status": "success", "result": result}
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content={"status": "not_found", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Failed to execute capability {capability_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/kernel/events")
async def get_kernel_events(event_type: Optional[str] = None, limit: int = 100):
    """Get kernel event history"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        if event_type:
            events = kernel.shared_services.event_bus.get_event_history(
                event_type=event_type,
                limit=limit
            )
        else:
            events = kernel.shared_services.event_bus.get_event_history(limit=limit)
        
        return {"events": [event.to_dict() for event in events]}
    except Exception as e:
        logger.error(f"Failed to get kernel events: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/kernel/search")
async def search_kernel(query: str, domains: Optional[str] = None):
    """Search kernel capabilities and plugins"""
    try:
        if kernel is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "message": "Kernel not initialized"}
            )
        
        domain_list = domains.split(",") if domains else None
        results = await kernel.search(query, domain_list)
        return {"results": results}
    except Exception as e:
        logger.error(f"Failed to search kernel: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Plugin Registry Proxy
import httpx
from fastapi import HTTPException

@app.get("/api/v1/plugins")
async def list_plugins():
    """Proxy to plugin registry service"""
    try:
        async with httpx.AsyncClient() as client:
            # Direct call to plugin registry service (bypass nginx to avoid circular dependency)
            registry_url = "http://plugin-registry:5000/api/v1/plugins"
            response = await client.get(registry_url, timeout=10.0)
            return response.json()
    except Exception as e:
        logger.error(f"Plugin registry proxy error: {e}")
        # Fallback: return hardcoded plugins if service is unavailable
        return {
            "plugins": [
                {
                    "id": "com.dhiimail.marketing",
                    "name": "Marketing Genius",
                    "version": "1.0.0",
                    "description": "AI-powered marketing campaign generator",
                    "manifest_url": "/plugins/marketing/manifest.json"
                },
                {
                    "id": "com.dhiimail.finance",
                    "name": "Finance Flow",
                    "version": "1.2.0",
                    "description": "Invoice processing and expense tracking",
                    "manifest_url": "/plugins/finance/manifest.json"
                }
            ]
        }

@app.get("/api/v1/plugins/{plugin_id}")
async def get_plugin(plugin_id: str):
    """Proxy to plugin registry service for specific plugin"""
    try:
        async with httpx.AsyncClient() as client:
            registry_url = f"http://plugin-registry:5000/api/v1/plugins/{plugin_id}"
            response = await client.get(registry_url, timeout=10.0)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Plugin not found")
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Plugin registry proxy error: {e}")
        # Fallback: search in hardcoded plugins
        plugins = [
            {
                "id": "com.dhiimail.marketing",
                "name": "Marketing Genius",
                "version": "1.0.0",
                "description": "AI-powered marketing campaign generator",
                "manifest_url": "/plugins/marketing/manifest.json"
            },
            {
                "id": "com.dhiimail.finance",
                "name": "Finance Flow",
                "version": "1.2.0",
                "description": "Invoice processing and expense tracking",
                "manifest_url": "/plugins/finance/manifest.json"
            }
        ]
        plugin = next((p for p in plugins if p['id'] == plugin_id), None)
        if plugin:
            return plugin
        raise HTTPException(status_code=404, detail="Plugin not found")

# Serve React Frontend (Static Files)
from fastapi.staticfiles import StaticFiles
import os

# Path to the React build directory
# In development/local, it might be here:
react_dist_path = os.path.join(os.path.dirname(__file__), "a2ui_integration/client/dist")

# In Docker/Production, we might copy it to a simpler path, e.g., /app/static
if os.path.exists("/app/static"):
    react_dist_path = "/app/static"

if os.path.exists(react_dist_path):
    # Mount the static files
    app.mount("/", StaticFiles(directory=react_dist_path, html=True), name="static")
    logger.info(f"Serving React frontend from {react_dist_path}")
else:
    logger.warning(f"React build directory not found at {react_dist_path}. Frontend will not be served.")


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that catches all unhandled exceptions
    and returns a standardized JSON response.
    """
    try:
        # Create enhanced error context
        error_context = ErrorContext(
            user_id=getattr(request.state, 'user_id', None),
            session_id=getattr(request.state, 'session_id', None),
            request_id=getattr(request.state, 'request_id', None),
            endpoint=str(request.url.path),
            method=str(request.method),
            user_agent=request.headers.get('user-agent'),
            ip_address=request.client.host if request.client else "unknown",
            environment=os.environ.get("ENVIRONMENT", "development"),
            version=os.environ.get("APP_VERSION", "0.1.0"),
            server_name=os.environ.get("SERVER_NAME", "localhost"),
            deployment_id=os.environ.get("DEPLOYMENT_ID", "unknown")
        )
        
        # Handle error using centralized ErrorHandler
        # This logs the error structurally and returns a standardized AppError
        app_error = ErrorHandler.handle_error(exc, context=error_context.to_dict())
        
        # Track error with comprehensive metadata
        error_tracking_service = get_error_tracking_service()
        await error_tracking_service.track_error(app_error, error_context)
        
        # Determine HTTP status code based on error category
        status_code = 500
        if app_error.category == ErrorCategory.AUTHENTICATION:
            status_code = 401
        elif app_error.category == ErrorCategory.AUTHORIZATION:
            status_code = 403
        elif app_error.category == ErrorCategory.VALIDATION:
            status_code = 400
        elif app_error.category == ErrorCategory.NOT_FOUND:
            status_code = 404
        elif app_error.category == ErrorCategory.RATE_LIMIT:
            status_code = 429
            
        return JSONResponse(
            status_code=status_code,
            content=app_error.to_dict()
        )
    except Exception as e:
        # Fallback if handler fails
        import traceback
        import sys
        traceback.print_exc(file=sys.stdout)
        return JSONResponse(
            status_code=500,
            content={"error": "Critical error in exception handler", "details": str(e)}
        )

# Exception Catching Middleware
# Ensures that exceptions are caught and handled by the global handler,
# even when using TestClient or when ServerErrorMiddleware is bypassed.
    except Exception as exc:
        return await global_exception_handler(request, exc)

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8005)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()
    
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
