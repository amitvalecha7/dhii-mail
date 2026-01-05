import logging
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.core.middleware import database_session_middleware
from a2ui_integration.core.logging import get_logger
from middleware.logging_middleware import setup_logging_middleware
from middleware.apm import setup_apm
from error_handler import ErrorHandler, ErrorCategory

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

# 2. Database session middleware
app.middleware("http")(database_session_middleware)

# 3. CORS middleware (innermost of standard middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint to verify API is running."""
    logger.info("Root endpoint accessed")
    return {"message": "DHII Mail API is running"}

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

# Import and include routers
# from routers import auth, users
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/users", tags=["users"])

# A2UI Router
from a2ui_integration.a2ui_router import router as a2ui_router
app.include_router(a2ui_router)

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
        # Create context from request
        context = {
            "path": str(request.url.path),
            "method": str(request.method),
            "client_host": request.client.host if request.client else "unknown"
        }
        
        # Handle error using centralized ErrorHandler
        # This logs the error structurally and returns a standardized AppError
        app_error = ErrorHandler.handle_error(exc, context=context)
        
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
