"""
dhii Mail - FastAPI Application
Main application entry point with authentication, email, and AI endpoints.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import authentication system
from auth import AuthManager, get_current_user

# Import database system
from database import DatabaseManager

# Import error handling system
from error_handler import ErrorHandler, AppError, ValidationError, AuthenticationError, AuthorizationError, ExternalServiceError, ResourceNotFoundError

# Import WebSocket manager
from enhanced_websocket_manager import EnhancedWebSocketManager, ChatMessage, enhanced_websocket_manager

# Import AI engine
from ai_engine import AIEngine, ai_engine

# Import calendar manager
from calendar_manager import CalendarManager, calendar_manager, CalendarEvent, TimeSlot

# Import email manager
from email_manager import EmailManager, email_manager, EmailMessage, EmailAccount

# Import video manager
from video_manager import VideoManager, video_manager, VideoMeeting, VideoMeetingCreate, VideoMeetingUpdate

# Import marketing manager
from marketing_manager import MarketingManager, marketing_manager, MarketingCampaign, CampaignCreate, CampaignUpdate, CampaignStatus, CampaignType

# Import security manager
from security_manager import security_manager, SecurityEvent

# Import middleware
from backend.core.middleware import setup_middleware

# Import error handler
from error_handler import ErrorHandler, AppError, AuthenticationError, AuthorizationError, ValidationError, DatabaseError, NetworkError, ExternalServiceError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database manager
db_manager = DatabaseManager()

def get_db():
    """Get database manager instance."""
    return db_manager

# Initialize authentication manager with environment-based secret key
auth_manager = AuthManager(secret_key=os.getenv("JWT_SECRET_KEY", "dhii-mail-secret-key-for-development"))

# Export auth_manager for use by auth.py
from auth import auth_manager as _auth_manager_ref
import auth
auth.auth_manager = auth_manager

# Pydantic models for request/response
class UserRegistration(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str

# Chat-based authentication model
class ChatAuthRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatAuthResponse(BaseModel):
    response: str
    requires_input: bool = False
    session_id: Optional[str] = None
    auth_result: Optional[Dict[str, Any]] = None
    login_card: Optional[Dict[str, Any]] = None  # Login card for visual authentication

# WebSocket chat models
class ChatMessageRequest(BaseModel):
    message: str
    session_id: str
    access_token: Optional[str] = None
    message_type: str = "text"  # text, voice, file
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    message: str
    sender: str = "ai"
    message_type: str = "text"
    timestamp: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    requires_input: bool = False
    ui_components: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None

# Create FastAPI application
app = FastAPI(
    title="dhii Mail",
    description="AI-powered email management system",
    version="1.0.0"
)

# Import configuration
from config import settings

# SECURITY: CORS configuration loaded from environment variables
# This prevents hard-coded origins and allows secure configuration per environment
cors_config = settings.get_cors_config()  # Environment-driven CORS - validated secure
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],  # From environment: CORS_ALLOW_ORIGINS
    allow_credentials=cors_config["allow_credentials"],  # From environment: CORS_ALLOW_CREDENTIALS
    allow_methods=cors_config["allow_methods"],  # From environment: CORS_ALLOW_METHODS
    allow_headers=cors_config["allow_headers"],  # From environment: CORS_ALLOW_HEADERS
)

# Setup additional middleware (rate limiting, security headers, logging)
setup_middleware(app)

# Import and include updated A2UI router for all-A2UI architecture
from a2ui_integration.a2ui_router_updated import router as a2ui_router_updated
app.include_router(a2ui_router_updated)

# Import and include Skill Store router for plugin management
from a2ui_integration.skill_store import skill_store_router, initialize_skill_store
from a2ui_integration.plugin_manager import PluginManager

# Initialize plugin manager and skill store
plugin_manager = PluginManager()
initialize_skill_store(plugin_manager)
app.include_router(skill_store_router)

# Remove old static file mounting - A2UI will be served through API only
# app.mount("/static", StaticFiles(directory="a2ui_integration/client"), name="a2ui_static")

# Root endpoint - API information (A2UI-only architecture)
@app.get("/")
async def root():
    """Main API endpoint with A2UI service information."""
    return {
        "app": "dhii Mail - A2UI Edition",
        "version": "1.0.0",
        "status": "running",
        "architecture": "all-a2ui",
        "description": "AI-powered email management with A2UI interface",
        "a2ui_endpoints": {
            "dashboard": "/api/a2ui/dashboard",
            "email": "/api/a2ui/email/inbox",
            "calendar": "/api/a2ui/calendar",
            "meetings": "/api/a2ui/meetings",
            "tasks": "/api/a2ui/tasks",
            "analytics": "/api/a2ui/analytics",
            "settings": "/api/a2ui/settings",
            "chat": "/api/a2ui/chat",
            "components": "/api/a2ui/components"
        },
        "api_docs": "/docs",
        "health_check": "/health",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Remove old A2UI interface endpoint - now served through API only
# @app.get("/a2ui", response_class=HTMLResponse)
# async def a2ui_interface():
#     """Serve A2UI meeting assistant interface."""
#     try:
#         with open("a2ui_integration/client/index.html", "r") as f:
#             html_content = f.read()
#         return HTMLResponse(content=html_content)
#     except FileNotFoundError:
#         logger.error("A2UI interface not found, falling back to JSON response")
#         return JSONResponse(
#             content={
#                 "app": "dhii Mail with A2UI",
#                 "version": "1.0.0",
#                 "status": "running",
#                 "interface": "A2UI Meeting Assistant",
#                 "message": "A2UI interface loading...",
#                 "features": [
#                     "Multi-tenant email management",
#                     "AI-powered email processing",
#                     "Local SMTP server",
#                     "External mailbox integration",
#                     "PASETO authentication",
#                     "WebSocket real-time updates",
#                     "A2UI chat-based authentication",
#                     "A2UI login card authentication (visual forms)",
#                     "Rate limiting and security middleware",
#                     "A2UI meeting assistant integration"
#                 ],
#                 "endpoints": {
#                     "auth": "/auth/login",
#                     "email": "/email/inbox",
#                     "calendar": "/calendar/events",
#                     "video": "/video/meetings",
#                     "a2ui": "/api/a2ui/chat",
#                     "websocket": "/ws/a2ui/{user_email}"
#                 }
#             }
#         )

# A2UI Interface endpoint - serves the new all-A2UI client
@app.get("/a2ui", response_class=HTMLResponse)
async def a2ui_interface():
    """Serve A2UI interface for all-A2UI architecture with standardized error handling."""
    try:
        with open("a2ui_integration/client/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
        
    except FileNotFoundError as e:
        error = ErrorHandler.handle_error(
            e, 
            {"endpoint": "a2ui_interface", "file": "a2ui_integration/client/index.html"}
        )
        return JSONResponse(
            status_code=404,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "a2ui_interface"})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint with standardized error handling."""
    try:
        # Check database connection
        db = get_db()
        stats = db.get_database_stats()
        
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "stats": stats
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "health_check"})
        return JSONResponse(
            status_code=503,
            content=error.to_dict()
        )

# Authentication endpoints
@app.post("/auth/register")
async def register_user(user: UserRegistration):
    """Register a new user with standardized error handling."""
    try:
        # Validate input
        if not user.email or not user.username or not user.password:
            raise ValidationError("Email, username, and password are required")
        
        result = auth_manager.create_user(
            email=user.email,
            username=user.username,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if result is None:
            raise ValidationError("User already exists")
            
        return result
        
    except (ValidationError, ValueError) as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "register_user", "user": user.username})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "register_user", "user": user.username})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/auth/login")
async def login_user(user: UserLogin):
    """Login user and return tokens with standardized error handling."""
    try:
        # Validate input
        if not user.username or not user.password:
            raise ValidationError("Username and password are required")
            
        result = auth_manager.authenticate_user(user.username, user.password)
        if not result:
            raise AuthenticationError("Invalid credentials")
        
        # Create tokens
        access_token = auth_manager.create_token(result['id'], 'access')
        refresh_token = auth_manager.create_token(result['id'], 'refresh')
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": result
        }
        
    except AuthenticationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "login_user", "username": user.username})
        return JSONResponse(
            status_code=401,
            content=error.to_dict()
        )
    except (ValidationError, ValueError) as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "login_user", "username": user.username})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "login_user", "username": user.username})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/auth/refresh")
async def refresh_token(token: TokenRefresh):
    """Refresh access token with standardized error handling."""
    try:
        # Validate input
        if not token.refresh_token:
            raise ValidationError("Refresh token is required")
            
        # Verify refresh token
        user_data = auth_manager.verify_token(token.refresh_token, 'refresh')
        if not user_data:
            raise AuthenticationError("Invalid refresh token")
        
        # Create new access token
        new_access_token = auth_manager.create_token(user_data['user_id'], 'access')
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except AuthenticationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "refresh_token"})
        return JSONResponse(
            status_code=401,
            content=error.to_dict()
        )
    except (ValidationError, ValueError) as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "refresh_token"})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "refresh_token"})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/auth/logout")
async def logout_user(request: Request):
    """Logout user (invalidate token) with standardized error handling."""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Invalid authorization header")
        
        token = auth_header.split(" ")[1]
        result = auth_manager.logout_user(token)
        return result
        
    except AuthenticationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "logout_user"})
        return JSONResponse(
            status_code=401,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "logout_user"})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

# A2UI Form-based Authentication (handles login cards)
class FormAuthRequest(BaseModel):
    action: str  # 'login', 'register', 'forgot_password'
    form_data: Dict[str, str]
    session_id: Optional[str] = None

@app.post("/auth/form", response_model=ChatAuthResponse)
async def form_authenticate(request: FormAuthRequest):
    """
    A2UI Form-based authentication endpoint.
    Handles login card form submissions.
    """
    try:
        action = request.action.lower()
        form_data = request.form_data
        session_id = request.session_id or "default"
        
        if action == 'login':
            # Handle login form submission
            username = form_data.get('username', '').strip()
            password = form_data.get('password', '').strip()
            
            if not username or not password:
                return ChatAuthResponse(
                    response="Please provide both username and password.",
                    requires_input=True,
                    session_id=session_id
                )
            
            # Attempt authentication
            user_data = auth_manager.authenticate_user(username, password)
            if user_data:
                # Create tokens
                access_token = auth_manager.create_token(user_data['id'], 'access')
                refresh_token = auth_manager.create_token(user_data['id'], 'refresh')
                
                return ChatAuthResponse(
                    response=f"Welcome back, {user_data['first_name'] or user_data['username']}! You've been successfully logged in.",
                    requires_input=False,
                    session_id=session_id,
                    auth_result={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "user": user_data
                    }
                )
            else:
                return ChatAuthResponse(
                    response="Invalid credentials. Please check your username and password and try again.",
                    requires_input=True,
                    session_id=session_id,
                    login_card={
                        "type": "login_form",
                        "title": "Sign In Failed",
                        "message": "Invalid username or password",
                        "fields": [
                            {"name": "username", "type": "text", "placeholder": "Username or Email", "required": True, "value": username},
                            {"name": "password", "type": "password", "placeholder": "Password", "required": True}
                        ],
                        "actions": [
                            {"type": "submit", "label": "Sign In", "action": "login"},
                            {"type": "link", "label": "Don't have an account? Register", "action": "register"}
                        ]
                    }
                )
        
        elif action == 'register':
            # Handle registration form submission
            email = form_data.get('email', '').strip()
            username = form_data.get('username', '').strip()
            first_name = form_data.get('first_name', '').strip()
            last_name = form_data.get('last_name', '').strip()
            password = form_data.get('password', '').strip()
            
            # Validate required fields
            missing_fields = []
            if not email: missing_fields.append("email")
            if not username: missing_fields.append("username")
            if not first_name: missing_fields.append("first name")
            if not last_name: missing_fields.append("last name")
            if not password: missing_fields.append("password")
            
            if missing_fields:
                return ChatAuthResponse(
                    response=f"Please provide the following required fields: {', '.join(missing_fields)}",
                    requires_input=True,
                    session_id=session_id
                )
            
            # Create user
            result = auth_manager.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            if result:
                # Create tokens
                access_token = auth_manager.create_token(result['id'], 'access')
                refresh_token = auth_manager.create_token(result['id'], 'refresh')
                
                return ChatAuthResponse(
                    response=f"Welcome to dhii Mail, {first_name}! Your account has been created and you're now logged in.",
                    requires_input=False,
                    session_id=session_id,
                    auth_result={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "user": result
                    }
                )
            else:
                return ChatAuthResponse(
                    response="We couldn't create your account. This might be because the email or username is already taken. Please try different credentials.",
                    requires_input=True,
                    session_id=session_id,
                    login_card={
                        "type": "registration_form",
                        "title": "Registration Failed",
                        "message": "Email or username may already be taken",
                        "fields": [
                            {"name": "email", "type": "email", "placeholder": "Email Address", "required": True, "value": email},
                            {"name": "username", "type": "text", "placeholder": "Username", "required": True, "value": username},
                            {"name": "first_name", "type": "text", "placeholder": "First Name", "required": True, "value": first_name},
                            {"name": "last_name", "type": "text", "placeholder": "Last Name", "required": True, "value": last_name},
                            {"name": "password", "type": "password", "placeholder": "Password", "required": True}
                        ],
                        "actions": [
                            {"type": "submit", "label": "Create Account", "action": "register"},
                            {"type": "link", "label": "Already have an account? Sign In", "action": "login"}
                        ]
                    }
                )
        
        else:
            return ChatAuthResponse(
                response="Invalid action. Please try again.",
                requires_input=True,
                session_id=session_id
            )
            
    except Exception as e:
        logger.error(f"Form authentication error: {e}")
        return ChatAuthResponse(
            response="Sorry, I encountered an error. Please try again.",
            requires_input=True,
            session_id=request.session_id
        )

# A2UI Chat-based Authentication with Login Card Integration
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    access_token: Optional[str] = None  # Optional token to check auth status

@app.post("/chat", response_model=ChatAuthResponse)
async def chat_with_auth(request: ChatRequest):
    """
    Main chat endpoint that checks authentication status first.
    If user is not authenticated, provides login/signup cards.
    """
    try:
        # Check if user is authenticated
        user_data = None
        if request.access_token:
            user_data = auth_manager.verify_token(request.access_token, 'access')
        
        # If user is authenticated, proceed with normal chat
        if user_data:
            return ChatAuthResponse(
                response=f"Hello {user_data.get('first_name', user_data.get('username'))}! How can I help you today?",
                requires_input=True,
                session_id=request.session_id or "default"
            )
        
        # If not authenticated, provide login card
        return ChatAuthResponse(
            response="Welcome to dhii Mail! Please sign in to continue:",
            requires_input=False,
            session_id=request.session_id or "default",
            login_card={
                "type": "auth_choice_card",
                "title": "Welcome to dhii Mail",
                "message": "Your AI-powered email management system",
                "actions": [
                    {"type": "button", "label": "Sign In", "action": "show_login", "primary": True},
                    {"type": "button", "label": "Create Account", "action": "show_register", "primary": False}
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Chat auth check error: {e}")
        return ChatAuthResponse(
            response="Welcome to dhii Mail! Please sign in to continue:",
            requires_input=False,
            session_id=request.session_id or "default",
            login_card={
                "type": "auth_choice_card",
                "title": "Welcome to dhii Mail",
                "message": "Your AI-powered email management system",
                "actions": [
                    {"type": "button", "label": "Sign In", "action": "show_login", "primary": True},
                    {"type": "button", "label": "Create Account", "action": "show_register", "primary": False}
                ]
            }
        )

# A2UI Login Card Actions Handler
class CardActionRequest(BaseModel):
    action: str  # 'show_login', 'show_register', 'submit_login', 'submit_register'
    session_id: Optional[str] = None
    form_data: Optional[Dict[str, str]] = None

@app.post("/auth/card/action", response_model=ChatAuthResponse)
async def handle_card_action(request: CardActionRequest):
    """
    Handle actions from login cards (button clicks, form submissions).
    """
    try:
        action = request.action.lower()
        session_id = request.session_id or "default"
        
        if action == 'show_login':
            return ChatAuthResponse(
                response="Please sign in to continue:",
                requires_input=False,
                session_id=session_id,
                login_card={
                    "type": "login_form",
                    "title": "Sign In to dhii Mail",
                    "fields": [
                        {"name": "username", "type": "text", "placeholder": "Username or Email", "required": True},
                        {"name": "password", "type": "password", "placeholder": "Password", "required": True}
                    ],
                    "actions": [
                        {"type": "submit", "label": "Sign In", "action": "submit_login"},
                        {"type": "link", "label": "Don't have an account? Register", "action": "show_register"}
                    ]
                }
            )
        
        elif action == 'show_register':
            return ChatAuthResponse(
                response="Create your dhii Mail account:",
                requires_input=False,
                session_id=session_id,
                login_card={
                    "type": "registration_form",
                    "title": "Create Your Account",
                    "fields": [
                        {"name": "email", "type": "email", "placeholder": "Email Address", "required": True},
                        {"name": "username", "type": "text", "placeholder": "Username", "required": True},
                        {"name": "first_name", "type": "text", "placeholder": "First Name", "required": True},
                        {"name": "last_name", "type": "text", "placeholder": "Last Name", "required": True},
                        {"name": "password", "type": "password", "placeholder": "Password", "required": True}
                    ],
                    "actions": [
                        {"type": "submit", "label": "Create Account", "action": "submit_register"},
                        {"type": "link", "label": "Already have an account? Sign In", "action": "show_login"}
                    ]
                }
            )
        
        elif action == 'submit_login':
            form_data = request.form_data or {}
            username = form_data.get('username', '').strip()
            password = form_data.get('password', '').strip()
            
            if not username or not password:
                return ChatAuthResponse(
                    response="Please provide both username and password.",
                    requires_input=True,
                    session_id=session_id
                )
            
            # Attempt authentication
            user_data = auth_manager.authenticate_user(username, password)
            if user_data:
                # Create tokens
                access_token = auth_manager.create_token(user_data['id'], 'access')
                refresh_token = auth_manager.create_token(user_data['id'], 'refresh')
                
                return ChatAuthResponse(
                    response=f"Welcome back, {user_data['first_name'] or user_data['username']}! You've been successfully logged in. How can I help you today?",
                    requires_input=True,
                    session_id=session_id,
                    auth_result={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "user": user_data
                    }
                )
            else:
                return ChatAuthResponse(
                    response="Invalid credentials. Please check your username and password.",
                    requires_input=False,
                    session_id=session_id,
                    login_card={
                        "type": "login_form",
                        "title": "Sign In Failed",
                        "message": "Invalid username or password",
                        "fields": [
                            {"name": "username", "type": "text", "placeholder": "Username or Email", "required": True, "value": username},
                            {"name": "password", "type": "password", "placeholder": "Password", "required": True}
                        ],
                        "actions": [
                            {"type": "submit", "label": "Sign In", "action": "submit_login"},
                            {"type": "link", "label": "Don't have an account? Register", "action": "show_register"}
                        ]
                    }
                )
        
        elif action == 'submit_register':
            form_data = request.form_data or {}
            email = form_data.get('email', '').strip()
            username = form_data.get('username', '').strip()
            first_name = form_data.get('first_name', '').strip()
            last_name = form_data.get('last_name', '').strip()
            password = form_data.get('password', '').strip()
            
            # Validate required fields
            missing_fields = []
            if not email: missing_fields.append("email")
            if not username: missing_fields.append("username")
            if not first_name: missing_fields.append("first name")
            if not last_name: missing_fields.append("last name")
            if not password: missing_fields.append("password")
            
            if missing_fields:
                return ChatAuthResponse(
                    response=f"Please provide the following required fields: {', '.join(missing_fields)}",
                    requires_input=True,
                    session_id=session_id
                )
            
            # Create user
            result = auth_manager.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            if result:
                # Create tokens
                access_token = auth_manager.create_token(result['id'], 'access')
                refresh_token = auth_manager.create_token(result['id'], 'refresh')
                
                return ChatAuthResponse(
                    response=f"Welcome to dhii Mail, {first_name}! Your account has been created and you're now logged in. How can I help you today?",
                    requires_input=True,
                    session_id=session_id,
                    auth_result={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "user": result
                    }
                )
            else:
                return ChatAuthResponse(
                    response="We couldn't create your account. The email or username may already be taken.",
                    requires_input=False,
                    session_id=session_id,
                    login_card={
                        "type": "registration_form",
                        "title": "Registration Failed",
                        "message": "Email or username may already be taken",
                        "fields": [
                            {"name": "email", "type": "email", "placeholder": "Email Address", "required": True, "value": email},
                            {"name": "username", "type": "text", "placeholder": "Username", "required": True, "value": username},
                            {"name": "first_name", "type": "text", "placeholder": "First Name", "required": True, "value": first_name},
                            {"name": "last_name", "type": "text", "placeholder": "Last Name", "required": True, "value": last_name},
                            {"name": "password", "type": "password", "placeholder": "Password", "required": True}
                        ],
                        "actions": [
                            {"type": "submit", "label": "Create Account", "action": "submit_register"},
                            {"type": "link", "label": "Already have an account? Sign In", "action": "show_login"}
                        ]
                    }
                )
        
        else:
            return ChatAuthResponse(
                response="Invalid action. Please try again.",
                requires_input=True,
                session_id=session_id
            )
            
    except Exception as e:
        logger.error(f"Card action error: {e}")
        return ChatAuthResponse(
            response="Sorry, I encountered an error. Please try again.",
            requires_input=True,
            session_id=request.session_id
        )

# A2UI Chat-based Authentication (fallback for specific auth requests)
@app.post("/auth/chat", response_model=ChatAuthResponse)
async def chat_authenticate(request: ChatAuthRequest):
    """
    A2UI Chat-based authentication endpoint.
    Allows users to authenticate through natural language conversation.
    """
    try:
        message = request.message.lower().strip()
        session_id = request.session_id or "default"
        
        # Initialize session context if needed
        if not hasattr(chat_authenticate, '_sessions'):
            chat_authenticate._sessions = {}
        
        if session_id not in chat_authenticate._sessions:
            chat_authenticate._sessions[session_id] = {
                'step': 'welcome',
                'username': None,
                'email': None,
                'first_name': None,
                'last_name': None,
                'password': None
            }
        
        session = chat_authenticate._sessions[session_id]
        
        # Handle different conversation steps
        if session['step'] == 'welcome':
            if any(word in message for word in ['login', 'sign in', 'log in']):
                session['step'] = 'login_username'
                return ChatAuthResponse(
                    response="I'll help you log in. What's your username or email address?",
                    requires_input=True,
                    session_id=session_id
                )
            elif any(word in message for word in ['register', 'sign up', 'create account']):
                session['step'] = 'register_email'
                return ChatAuthResponse(
                    response="Great! I'll help you create an account. What's your email address?",
                    requires_input=True,
                    session_id=session_id
                )
            else:
                return ChatAuthResponse(
                    response="Hi! I can help you with authentication. Would you like to login or register?",
                    requires_input=True,
                    session_id=session_id
                )
        
        # Login flow
        elif session['step'] == 'login_username':
            session['username'] = message
            session['step'] = 'login_password'
            return ChatAuthResponse(
                response=f"Got it! What's your password, {message}?",
                requires_input=True,
                session_id=session_id
            )
        
        elif session['step'] == 'login_password':
            username = session['username']
            password = message
            
            try:
                # First check if user exists
                user_exists = auth_manager.get_user_by_username(username)
                if not user_exists:
                    # User doesn't exist, offer to register
                    session['step'] = 'welcome'
                    return ChatAuthResponse(
                        response=f"I couldn't find an account for '{username}'. Would you like to register instead? Say 'login' or 'register'.",
                        requires_input=True,
                        session_id=session_id
                    )
                
                # Attempt authentication
                user_data = auth_manager.authenticate_user(username, password)
                if user_data:
                    # Create tokens
                    access_token = auth_manager.create_token(user_data['id'], 'access')
                    refresh_token = auth_manager.create_token(user_data['id'], 'refresh')
                    
                    # Clear session
                    del chat_authenticate._sessions[session_id]
                    
                    return ChatAuthResponse(
                        response=f"Welcome back, {user_data['first_name'] or user_data['username']}! You've been successfully logged in.",
                        requires_input=False,
                        session_id=session_id,
                        auth_result={
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "bearer",
                            "user": user_data
                        }
                    )
                else:
                    # Invalid password, but user exists
                    session['step'] = 'login_password'
                    return ChatAuthResponse(
                        response="That password doesn't seem right. Please try again with the correct password.",
                        requires_input=True,
                        session_id=session_id
                    )
            except Exception as e:
                logger.error(f"Chat login error: {e}")
                session['step'] = 'welcome'
                return ChatAuthResponse(
                    response="Sorry, I encountered an error. Would you like to try again? Say 'login' or 'register'.",
                    requires_input=True,
                    session_id=session_id
                )
        
        # Registration flow
        elif session['step'] == 'register_email':
            session['email'] = message
            session['step'] = 'register_username'
            return ChatAuthResponse(
                response="Perfect! Now, what username would you like to use?",
                requires_input=True,
                session_id=session_id
            )
        
        elif session['step'] == 'register_username':
            session['username'] = message
            session['step'] = 'register_first_name'
            return ChatAuthResponse(
                response="Nice username! What's your first name?",
                requires_input=True,
                session_id=session_id
            )
        
        elif session['step'] == 'register_first_name':
            session['first_name'] = message
            session['step'] = 'register_last_name'
            return ChatAuthResponse(
                response="And your last name?",
                requires_input=True,
                session_id=session_id
            )
        
        elif session['step'] == 'register_last_name':
            session['last_name'] = message
            session['step'] = 'register_password'
            return ChatAuthResponse(
                response="Finally, create a secure password for your account.",
                requires_input=True,
                session_id=session_id
            )
        
        elif session['step'] == 'register_password':
            session['password'] = message
            
            try:
                # Create user account
                result = auth_manager.create_user(
                    email=session['email'],
                    username=session['username'],
                    password=session['password'],
                    first_name=session['first_name'],
                    last_name=session['last_name']
                )
                
                if result:
                    user_data = result
                    
                    # Create tokens
                    access_token = auth_manager.create_token(user_data['id'], 'access')
                    refresh_token = auth_manager.create_token(user_data['id'], 'refresh')
                    
                    # Clear session
                    del chat_authenticate._sessions[session_id]
                    
                    return ChatAuthResponse(
                        response=f"Welcome to dhii Mail, {user_data['first_name']}! Your account has been created and you're now logged in.",
                        requires_input=False,
                        session_id=session_id,
                        auth_result={
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "bearer",
                            "user": user_data
                        }
                    )
                else:
                    session['step'] = 'register_email'
                    return ChatAuthResponse(
                        response="I couldn't create your account. Let's start over. What's your email address?",
                        requires_input=True,
                        session_id=session_id
                    )
            except Exception as e:
                logger.error(f"Chat registration error: {e}")
                session['step'] = 'welcome'
                return ChatAuthResponse(
                    response="Sorry, I encountered an error during registration. Would you like to try again? Say 'login' or 'register'.",
                    requires_input=True,
                    session_id=session_id
                )
        
        # Handle unexpected input
        else:
            session['step'] = 'welcome'
            return ChatAuthResponse(
                response="I didn't understand that. Would you like to login or register?",
                requires_input=True,
                session_id=session_id
            )
            
    except Exception as e:
        logger.error(f"Chat authentication error: {e}")
        return ChatAuthResponse(
            response="Sorry, I encountered an error. Please try again with 'login' or 'register'.",
            requires_input=True,
            session_id=request.session_id
        )

# Enhanced WebSocket endpoint for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Enhanced WebSocket endpoint for real-time chat with AI integration."""
    
    # Generate session ID for this connection
    session_id = f"ws_{client_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    
    # Establish connection through enhanced WebSocket manager
    connection = await enhanced_websocket_manager.connect(websocket, client_id, session_id)
    
    try:
        # Send initial connection message
        await connection.send_message({
            "type": "system",
            "message": "Connected to dhii Mail AI Assistant",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actions": [
                {"type": "button", "label": "Start Chat", "action": "start_chat"},
                {"type": "button", "label": "View Features", "action": "show_features"}
            ]
        })
        
        while True:
            # Receive message from client
            message_data = await connection.receive_message()
            
            if not message_data:
                continue
            
            # Parse message
            try:
                chat_request = ChatMessageRequest(**message_data)
            except Exception as e:
                logger.error(f"Invalid message format from {client_id}: {e}")
                await connection.send_message({
                    "type": "error",
                    "message": "Invalid message format. Please check your request.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                continue
            
            # Process user message
            logger.info(f"Processing message from {client_id}: {chat_request.message[:50]}...")
            
            # Check authentication if token provided
            user_id = None
            is_authenticated = False
            if chat_request.access_token:
                try:
                    token_data = auth_manager.verify_token(chat_request.access_token)
                    if token_data:
                        user_id = token_data.get('user_id')
                        is_authenticated = True
                        enhanced_websocket_manager.update_user_authentication(client_id, user_id, True)
                except Exception as e:
                    logger.warning(f"Token verification failed for {client_id}: {e}")
            
            # Send user message acknowledgment
            user_message = ChatMessage(
                id=f"msg_user_{datetime.now(timezone.utc).timestamp()}",
                sender="user",
                content=chat_request.message,
                timestamp=datetime.now(timezone.utc),
                session_id=chat_request.session_id,
                metadata={"client_id": client_id, "authenticated": is_authenticated}
            )
            
            # Add to message history
            enhanced_websocket_manager.add_message(chat_request.session_id, user_message)
            
            # Echo user message back (with proper formatting)
            await connection.send_message({
                "type": "user_message",
                "message": user_message.content,
                "sender": user_message.sender,
                "timestamp": user_message.timestamp.isoformat(),
                "message_id": user_message.id,
                "session_id": user_message.session_id
            })
            
            # Process with AI engine
            try:
                # Create context for AI
                ai_context = {
                    "client_id": client_id,
                    "session_id": chat_request.session_id,
                    "user_id": user_id,
                    "is_authenticated": is_authenticated,
                    "message_history": [
                        {
                            "sender": msg.sender,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat()
                        }
                        for msg in enhanced_websocket_manager.get_session_messages(chat_request.session_id)[-10:]
                    ]
                }
                
                # Get AI response
                ai_response = await ai_engine.process_message(chat_request.message, ai_context)
                
                # Create AI message
                ai_message = ChatMessage(
                    id=f"msg_ai_{datetime.now(timezone.utc).timestamp()}",
                    sender="ai",
                    content=ai_response.message,
                    timestamp=datetime.now(timezone.utc),
                    session_id=chat_request.session_id,
                    metadata={
                        "intent": ai_response.intent.intent,
                        "confidence": ai_response.intent.confidence,
                        "entities": ai_response.intent.entities
                    }
                )
                
                # Add to message history
                enhanced_websocket_manager.add_message(chat_request.session_id, ai_message)
                
                # Send AI response
                response_data = {
                    "type": "ai_message",
                    "message": ai_message.content,
                    "sender": ai_message.sender,
                    "timestamp": ai_message.timestamp.isoformat(),
                    "message_id": ai_message.id,
                    "session_id": ai_message.session_id,
                    "intent": ai_response.intent.intent,
                    "confidence": ai_response.intent.confidence,
                    "requires_input": ai_response.requires_user_input
                }
                
                # Add actions if available
                if ai_response.actions:
                    response_data["actions"] = ai_response.actions
                
                # Add UI components if available
                if ai_response.ui_components:
                    response_data["ui_components"] = ai_response.ui_components
                
                await connection.send_message(response_data)
                
                # Log AI response for debugging
                logger.info(f"AI response to {client_id}: {ai_response.message[:50]}... (intent: {ai_response.intent.intent})")
                
            except Exception as e:
                logger.error(f"AI processing error for {client_id}: {e}")
                await connection.send_message({
                    "type": "error",
                    "message": "Sorry, I encountered an error processing your message. Please try again.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
        await enhanced_websocket_manager.disconnect(client_id)
        
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        await enhanced_websocket_manager.disconnect(client_id)
        try:
            await websocket.close()
        except:
            pass

# WebSocket status endpoint
@app.get("/ws/status")
async def get_websocket_status():
    """Get WebSocket connection status and statistics"""
    try:
        stats = enhanced_websocket_manager.get_connection_stats()
        return {
            "success": True,
            "status": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get WebSocket status"
            }
        )

# Video Conferencing Endpoints
@app.post("/video/meetings")
async def create_video_meeting(
    meeting: VideoMeetingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new video meeting."""
    try:
        user_email = current_user['email']
        new_meeting = video_manager.create_meeting(meeting, user_email)
        
        return {
            "success": True,
            "meeting": {
                "id": new_meeting.id,
                "title": new_meeting.title,
                "description": new_meeting.description,
                "start_time": new_meeting.start_time.isoformat(),
                "end_time": new_meeting.end_time.isoformat() if new_meeting.end_time else None,
                "meeting_url": new_meeting.meeting_url,
                "password": new_meeting.password,
                "participants": new_meeting.participants,
                "status": new_meeting.status
            }
        }
    except Exception as e:
        logger.error(f"Error creating video meeting: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to create video meeting"
            }
        )

@app.get("/video/meetings")
async def get_user_meetings(
    current_user: dict = Depends(get_current_user)
):
    """Get all meetings for the current user."""
    try:
        user_email = current_user['email']
        meetings = video_manager.list_user_meetings(user_email)
        
        return {
            "success": True,
            "meetings": [
                {
                    "id": meeting.id,
                    "title": meeting.title,
                    "description": meeting.description,
                    "start_time": meeting.start_time.isoformat(),
                    "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
                    "organizer_email": meeting.organizer_email,
                    "participants": meeting.participants,
                    "meeting_url": meeting.meeting_url,
                    "password": meeting.password,
                    "status": meeting.status,
                    "created_at": meeting.created_at.isoformat()
                }
                for meeting in meetings
            ]
        }
    except Exception as e:
        logger.error(f"Error getting user meetings: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get meetings"
            }
        )

@app.get("/video/meetings/{meeting_id}")
async def get_meeting_details(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific meeting."""
    try:
        meeting = video_manager.get_meeting(meeting_id)
        
        # Check if user has access to this meeting
        user_email = current_user['email']
        if meeting.organizer_email != user_email and user_email not in meeting.participants:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Access denied to this meeting"
                }
            )
        
        return {
            "success": True,
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "description": meeting.description,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
                "organizer_email": meeting.organizer_email,
                "participants": meeting.participants,
                "meeting_url": meeting.meeting_url,
                "password": meeting.password,
                "status": meeting.status,
                "created_at": meeting.created_at.isoformat(),
                "recording_url": meeting.recording_url,
                "transcription": meeting.transcription
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Meeting not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error getting meeting details: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get meeting details"
            }
        )

@app.put("/video/meetings/{meeting_id}")
async def update_video_meeting(
    meeting_id: str,
    meeting_update: VideoMeetingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing video meeting."""
    try:
        # First check if user owns this meeting
        existing_meeting = video_manager.get_meeting(meeting_id)
        if existing_meeting.organizer_email != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Only the meeting organizer can update the meeting"
                }
            )
        
        updated_meeting = video_manager.update_meeting(meeting_id, meeting_update)
        
        return {
            "success": True,
            "meeting": {
                "id": updated_meeting.id,
                "title": updated_meeting.title,
                "description": updated_meeting.description,
                "start_time": updated_meeting.start_time.isoformat(),
                "end_time": updated_meeting.end_time.isoformat() if updated_meeting.end_time else None,
                "participants": updated_meeting.participants,
                "status": updated_meeting.status
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Meeting not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error updating video meeting: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to update meeting"
            }
        )

@app.delete("/video/meetings/{meeting_id}")
async def delete_video_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a video meeting."""
    try:
        # First check if user owns this meeting
        existing_meeting = video_manager.get_meeting(meeting_id)
        if existing_meeting.organizer_email != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Only the meeting organizer can delete the meeting"
                }
            )
        
        video_manager.delete_meeting(meeting_id)
        
        return {
            "success": True,
            "message": "Meeting deleted successfully"
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Meeting not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error deleting video meeting: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to delete meeting"
            }
        )

@app.post("/video/meetings/{meeting_id}/start")
async def start_video_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start a video meeting."""
    try:
        # First check if user has access to this meeting
        existing_meeting = video_manager.get_meeting(meeting_id)
        user_email = current_user['email']
        if (existing_meeting.organizer_email != user_email and 
            user_email not in existing_meeting.participants):
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Access denied to this meeting"
                }
            )
        
        started_meeting = video_manager.start_meeting(meeting_id)
        
        return {
            "success": True,
            "meeting": {
                "id": started_meeting.id,
                "title": started_meeting.title,
                "meeting_url": started_meeting.meeting_url,
                "password": started_meeting.password,
                "status": started_meeting.status
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Meeting not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error starting video meeting: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to start meeting"
            }
        )

@app.post("/video/meetings/{meeting_id}/end")
async def end_video_meeting(
    meeting_id: str,
    recording_url: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """End a video meeting."""
    try:
        # First check if user owns this meeting
        existing_meeting = video_manager.get_meeting(meeting_id)
        if existing_meeting.organizer_email != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Only the meeting organizer can end the meeting"
                }
            )
        
        ended_meeting = video_manager.end_meeting(meeting_id, recording_url)
        
        return {
            "success": True,
            "meeting": {
                "id": ended_meeting.id,
                "title": ended_meeting.title,
                "status": ended_meeting.status,
                "recording_url": ended_meeting.recording_url
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Meeting not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error ending video meeting: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to end meeting"
            }
        )

@app.get("/video/meetings/{meeting_id}/analytics")
async def get_meeting_analytics(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a specific meeting."""
    try:
        # First check if user has access to this meeting
        existing_meeting = video_manager.get_meeting(meeting_id)
        user_email = current_user['email']
        if (existing_meeting.organizer_email != user_email and 
            user_email not in existing_meeting.participants):
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Access denied to this meeting analytics"
                }
            )
        
        analytics = video_manager.get_meeting_analytics(meeting_id)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Meeting not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error getting meeting analytics: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get meeting analytics"
            }
        )

# Marketing Campaign Endpoints
@app.post("/marketing/campaigns")
async def create_marketing_campaign(
    campaign: CampaignCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new marketing campaign."""
    try:
        user_email = current_user['email']
        new_campaign = marketing_manager.create_campaign(campaign, user_email)
        
        return {
            "success": True,
            "campaign": {
                "id": new_campaign.id,
                "name": new_campaign.name,
                "description": new_campaign.description,
                "campaign_type": new_campaign.campaign_type,
                "status": new_campaign.status,
                "subject_line": new_campaign.subject_line,
                "sender_email": new_campaign.sender_email,
                "sender_name": new_campaign.sender_name,
                "recipient_segments": new_campaign.recipient_segments,
                "scheduled_time": new_campaign.scheduled_time.isoformat() if new_campaign.scheduled_time else None,
                "created_at": new_campaign.created_at.isoformat(),
                "tags": new_campaign.tags,
                "is_ab_test": new_campaign.is_ab_test
            }
        }
    except Exception as e:
        logger.error(f"Error creating marketing campaign: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to create marketing campaign"
            }
        )

@app.get("/marketing/campaigns")
async def get_user_campaigns(
    status: Optional[CampaignStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all campaigns for the current user."""
    try:
        user_email = current_user['email']
        campaigns = marketing_manager.list_campaigns(user_email, status)
        
        return {
            "success": True,
            "campaigns": [
                {
                    "id": campaign.id,
                    "name": campaign.name,
                    "description": campaign.description,
                    "campaign_type": campaign.campaign_type,
                    "status": campaign.status,
                    "subject_line": campaign.subject_line,
                    "sender_email": campaign.sender_email,
                    "sender_name": campaign.sender_name,
                    "recipient_count": campaign.recipient_count,
                    "scheduled_time": campaign.scheduled_time.isoformat() if campaign.scheduled_time else None,
                    "sent_time": campaign.sent_time.isoformat() if campaign.sent_time else None,
                    "created_at": campaign.created_at.isoformat(),
                    "tags": campaign.tags,
                    "metrics": {
                        "emails_sent": campaign.metrics.emails_sent,
                        "emails_delivered": campaign.metrics.emails_delivered,
                        "emails_opened": campaign.metrics.emails_opened,
                        "emails_clicked": campaign.metrics.emails_clicked,
                        "open_rate": campaign.metrics.open_rate,
                        "click_rate": campaign.metrics.click_rate
                    }
                }
                for campaign in campaigns
            ]
        }
    except Exception as e:
        logger.error(f"Error getting user campaigns: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get campaigns"
            }
        )

@app.get("/marketing/campaigns/{campaign_id}")
async def get_campaign_details(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific campaign."""
    try:
        campaign = marketing_manager.get_campaign(campaign_id)
        
        # Check if user owns this campaign
        if campaign.created_by != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Access denied to this campaign"
                }
            )
        
        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "campaign_type": campaign.campaign_type,
                "status": campaign.status,
                "subject_line": campaign.subject_line,
                "email_template": campaign.email_template,
                "sender_email": campaign.sender_email,
                "sender_name": campaign.sender_name,
                "recipient_segments": campaign.recipient_segments,
                "recipient_count": campaign.recipient_count,
                "scheduled_time": campaign.scheduled_time.isoformat() if campaign.scheduled_time else None,
                "sent_time": campaign.sent_time.isoformat() if campaign.sent_time else None,
                "created_at": campaign.created_at.isoformat(),
                "updated_at": campaign.updated_at.isoformat(),
                "tags": campaign.tags,
                "is_ab_test": campaign.is_ab_test,
                "ab_test_variants": campaign.ab_test_variants,
                "metrics": {
                    "emails_sent": campaign.metrics.emails_sent,
                    "emails_delivered": campaign.metrics.emails_delivered,
                    "emails_bounced": campaign.metrics.emails_bounced,
                    "emails_opened": campaign.metrics.emails_opened,
                    "emails_clicked": campaign.metrics.emails_clicked,
                    "emails_unsubscribed": campaign.metrics.emails_unsubscribed,
                    "open_rate": campaign.metrics.open_rate,
                    "click_rate": campaign.metrics.click_rate,
                    "bounce_rate": campaign.metrics.bounce_rate,
                    "unsubscribe_rate": campaign.metrics.unsubscribe_rate
                }
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Campaign not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error getting campaign details: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get campaign details"
            }
        )

@app.put("/marketing/campaigns/{campaign_id}")
async def update_marketing_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing marketing campaign."""
    try:
        # First check if user owns this campaign
        existing_campaign = marketing_manager.get_campaign(campaign_id)
        if existing_campaign.created_by != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Only the campaign creator can update the campaign"
                }
            )
        
        updated_campaign = marketing_manager.update_campaign(campaign_id, campaign_update)
        
        return {
            "success": True,
            "campaign": {
                "id": updated_campaign.id,
                "name": updated_campaign.name,
                "description": updated_campaign.description,
                "subject_line": updated_campaign.subject_line,
                "email_template": updated_campaign.email_template,
                "sender_email": updated_campaign.sender_email,
                "sender_name": updated_campaign.sender_name,
                "recipient_segments": updated_campaign.recipient_segments,
                "scheduled_time": updated_campaign.scheduled_time.isoformat() if updated_campaign.scheduled_time else None,
                "status": updated_campaign.status,
                "tags": updated_campaign.tags
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Campaign not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error updating marketing campaign: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to update campaign"
            }
        )

@app.delete("/marketing/campaigns/{campaign_id}")
async def delete_marketing_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a marketing campaign."""
    try:
        # First check if user owns this campaign
        existing_campaign = marketing_manager.get_campaign(campaign_id)
        if existing_campaign.created_by != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Only the campaign creator can delete the campaign"
                }
            )
        
        marketing_manager.delete_campaign(campaign_id)
        
        return {
            "success": True,
            "message": "Campaign deleted successfully"
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Campaign not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error deleting marketing campaign: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to delete campaign"
            }
        )

@app.post("/marketing/campaigns/{campaign_id}/send")
async def send_marketing_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Send a marketing campaign immediately."""
    try:
        # First check if user owns this campaign
        existing_campaign = marketing_manager.get_campaign(campaign_id)
        if existing_campaign.created_by != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Only the campaign creator can send the campaign"
                }
            )
        
        sent_campaign = marketing_manager.send_campaign(campaign_id)
        
        return {
            "success": True,
            "campaign": {
                "id": sent_campaign.id,
                "name": sent_campaign.name,
                "status": sent_campaign.status,
                "sent_time": sent_campaign.sent_time.isoformat() if sent_campaign.sent_time else None
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Campaign not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error sending marketing campaign: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to send campaign"
            }
        )

@app.get("/marketing/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a specific campaign."""
    try:
        # First check if user owns this campaign
        existing_campaign = marketing_manager.get_campaign(campaign_id)
        if existing_campaign.created_by != current_user['email']:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "Access denied to this campaign analytics"
                }
            )
        
        analytics = marketing_manager.get_campaign_analytics(campaign_id)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Campaign not found"
                }
            )
        raise e
    except Exception as e:
        logger.error(f"Error getting campaign analytics: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get campaign analytics"
            }
        )

@app.get("/marketing/dashboard")
async def get_marketing_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get marketing dashboard data."""
    try:
        user_email = current_user['email']
        dashboard_data = marketing_manager.get_marketing_dashboard(user_email)
        
        return {
            "success": True,
            "dashboard": dashboard_data
        }
    except Exception as e:
        logger.error(f"Error getting marketing dashboard: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get marketing dashboard"
            }
        )

@app.get("/marketing/templates")
async def get_email_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get available email templates."""
    try:
        templates = marketing_manager.get_email_templates()
        
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Error getting email templates: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to get email templates"
            }
        )

# Email endpoints
@app.get("/emails")
async def get_emails(
    folder: str = Query("INBOX", description="Email folder"),
    limit: int = Query(50, description="Number of emails to retrieve"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get user's emails with standardized error handling."""
    try:
        user_id = current_user['id']
        emails = email_manager.get_emails(user_id, folder, limit, offset)
        
        return {
            "success": True,
            "emails": [email.dict() for email in emails],
            "count": len(emails),
            "folder": folder
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_emails", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_emails", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/emails/send")
async def send_email(
    email_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send an email with standardized error handling."""
    try:
        user_id = current_user['id']
        
        # Validate input
        required_fields = ['subject', 'recipient', 'body']
        for field in required_fields:
            if field not in email_data or not email_data[field]:
                raise ValidationError(f"Missing required field: {field}")
        
        # Create email message
        message = EmailMessage(
            subject=email_data.get('subject', ''),
            sender=email_data.get('sender', ''),
            recipient=email_data.get('recipient', ''),
            body=email_data.get('body', ''),
            html_body=email_data.get('html_body'),
            date=datetime.now(timezone.utc),
            message_id=email_data.get('message_id')
        )
        
        # Get account ID from request
        account_id = email_data.get('account_id')
        if not account_id:
            # Get first active account for user
            conn = sqlite3.connect(email_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM email_accounts 
                WHERE user_id = ? AND is_active = 1 
                ORDER BY id LIMIT 1
            """, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                account_id = result[0]
            else:
                raise ValidationError("No email account configured")
        
        # Send email
        success = email_manager.send_email(message, account_id)
        
        if success:
            return {
                "success": True,
                "message": "Email sent successfully"
            }
        else:
            raise ExternalServiceError("Failed to send email")
            
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "send_email", "user_id": user_id})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except ExternalServiceError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "send_email", "user_id": user_id})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "send_email", "user_id": user_id})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

# AI endpoints (placeholder)
@app.post("/ai/summarize")
async def summarize_email():
    """Summarize email content."""
    return {"message": "AI summarize endpoint - coming soon"}

@app.post("/ai/classify")
async def classify_email():
    """Classify email content."""
    return {"message": "AI classify endpoint - coming soon"}

# Calendar endpoints
@app.post("/calendar/events")
async def create_calendar_event(
    event: CalendarEvent,
    current_user: dict = Depends(get_current_user)
):
    """Create a new calendar event."""
    try:
        user_id = current_user['id']
        event_id = calendar_manager.create_event(event, user_id)
        
        if event_id:
            return {
                "success": True,
                "event_id": event_id,
                "message": "Event created successfully"
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Failed to create event. Time slot may be unavailable."
                }
            )
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error"
            }
        )

@app.get("/calendar/events")
async def get_calendar_events(
    start_date: str = Query(..., description="Start date in ISO format"),
    end_date: str = Query(..., description="End date in ISO format"),
    current_user: dict = Depends(get_current_user)
):
    """Get calendar events for a date range."""
    try:
        user_id = current_user['id']
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        events = calendar_manager.get_events(user_id, start_dt, end_dt)
        
        return {
            "success": True,
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "location": event.location,
                    "attendees": event.attendees,
                    "organizer": event.organizer,
                    "status": event.status
                }
                for event in events
            ]
        }
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error"
            }
        )

@app.get("/calendar/availability")
async def get_availability(
    date: str = Query(..., description="Date to check availability for"),
    duration_minutes: int = Query(30, description="Meeting duration in minutes"),
    current_user: dict = Depends(get_current_user)
):
    """Get available time slots for a specific date."""
    try:
        user_id = current_user['id']
        
        # Parse date
        target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        available_slots = calendar_manager.get_availability(user_id, target_date, duration_minutes)
        
        return {
            "success": True,
            "date": target_date.date().isoformat(),
            "duration_minutes": duration_minutes,
            "available_slots": [
                {
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat(),
                    "duration_minutes": slot.duration_minutes
                }
                for slot in available_slots
            ]
        }
    except Exception as e:
        logger.error(f"Error getting availability: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error"
            }
        )

# Email Management Endpoints

@app.post("/email/accounts")
async def add_email_account(
    account: EmailAccount,
    current_user: dict = Depends(get_current_user)
):
    """Add a new email account for the authenticated user with standardized error handling."""
    try:
        user_id = current_user['id']
        account.user_id = user_id  # Set the user_id from the authenticated user
        account_id = email_manager.add_email_account(account)
        
        if account_id:
            return {
                "success": True,
                "account_id": account_id,
                "message": "Email account added successfully"
            }
        else:
            raise ExternalServiceError("Failed to add email account. Please check your credentials.")
            
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "add_email_account", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except ExternalServiceError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "add_email_account", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "add_email_account", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.get("/email/accounts")
async def get_email_accounts(
    current_user: dict = Depends(get_current_user)
):
    """Get all email accounts for the authenticated user with standardized error handling."""
    try:
        user_id = current_user['id']
        accounts = email_manager.get_email_accounts(user_id)
        
        return {
            "success": True,
            "accounts": [
                {
                    "id": acc.id,
                    "email_address": acc.email_address,
                    "provider": acc.provider,
                    "is_active": acc.is_active,
                    "created_at": acc.created_at.isoformat()
                }
                for acc in accounts
            ]
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_email_accounts", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_email_accounts", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/email/send")
async def send_email(
    email_message: EmailMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send an email using the authenticated user's account with standardized error handling."""
    try:
        user_id = current_user['id']
        
        # Validate email message
        if not email_message.subject or not email_message.body or not email_message.recipient:
            raise ValidationError("Email must have subject, body, and recipient")
        
        # Check if user has email accounts
        accounts = email_manager.get_email_accounts(user_id)
        if not accounts:
            raise ValidationError("No email accounts configured. Please add an email account first.")
        
        # Use the first active account
        account = next((acc for acc in accounts if acc.is_active), accounts[0])
        
        # Send the email
        message_id = email_manager.send_email(user_id, account.id, email_message)
        
        if message_id:
            return {
                "success": True,
                "message_id": message_id,
                "message": "Email sent successfully"
            }
        else:
            raise ExternalServiceError("Failed to send email. Please check your account settings.")
            
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "send_email", "user_id": user_id})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except ExternalServiceError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "send_email", "user_id": user_id})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "send_email", "user_id": user_id})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.get("/email/inbox")
async def get_inbox(
    account_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get emails from the authenticated user's inbox with standardized error handling."""
    try:
        user_id = current_user['id']
        
        # Get email accounts
        accounts = email_manager.get_email_accounts(user_id)
        if not accounts:
            raise ValidationError("No email accounts configured. Please add an email account first.")
        
        # Use specific account or first available
        if account_id:
            account = next((acc for acc in accounts if acc.id == account_id), None)
            if not account:
                raise ValidationError("Email account not found")
        else:
            account = accounts[0]
        
        # Get emails from inbox
        emails = email_manager.get_emails(user_id, account.id, limit=limit)
        
        return {
            "success": True,
            "emails": [
                {
                    "id": email.id,
                    "subject": email.subject,
                    "sender": email.sender,
                    "recipients": email.recipients,
                    "body": email.body,
                    "is_read": email.is_read,
                    "created_at": email.created_at.isoformat()
                }
                for email in emails
            ],
            "account": {
                "id": account.id,
                "email_address": account.email_address,
                "provider": account.provider
            }
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_inbox", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_inbox", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.delete("/email/accounts/{account_id}")
async def delete_email_account(
    account_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an email account for the authenticated user with standardized error handling."""
    try:
        user_id = current_user['id']
        success = email_manager.delete_email_account(user_id, account_id)
        
        if success:
            return {
                "success": True,
                "message": "Email account deleted successfully"
            }
        else:
            raise ResourceNotFoundError("Failed to delete email account or account not found")
            
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "delete_email_account", "user_id": current_user.get('id'), "account_id": account_id})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except ResourceNotFoundError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "delete_email_account", "user_id": current_user.get('id'), "account_id": account_id})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "delete_email_account", "user_id": current_user.get('id'), "account_id": account_id})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

# Security endpoints
@app.post("/security/validate-password")
async def validate_password(
    password_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate password strength with standardized error handling."""
    try:
        password = password_data.get("password", "")
        if not password:
            raise ValidationError("Password is required")
            
        result = security_manager.validate_password_strength(password)
        return {
            "success": True,
            "validation_result": result
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "validate_password", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "validate_password", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.get("/security/events")
async def get_security_events(
    user_email: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get security events (admin only) with standardized error handling."""
    try:
        # Check if user is admin (simplified check - in production, use proper role management)
        if current_user.get('email') != 'admin@dhii.ai':
            raise AuthorizationError("Admin access required")
        
        events = security_manager.get_security_events(
            user_email=user_email,
            event_type=event_type,
            severity=severity,
            limit=limit
        )
        
        return {
            "success": True,
            "events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "user_email": event.user_email,
                    "ip_address": event.ip_address,
                    "severity": event.severity,
                    "details": event.details
                }
                for event in events
            ],
            "total": len(events)
        }
        
    except AuthorizationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_security_events", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=403,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_security_events", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.get("/security/summary")
async def get_security_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get security summary statistics with standardized error handling."""
    try:
        summary = security_manager.get_security_summary()
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "get_security_summary", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/security/encrypt-data")
async def encrypt_sensitive_data(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Encrypt sensitive data with standardized error handling."""
    try:
        sensitive_data = data.get("data", "")
        if not sensitive_data:
            raise ValidationError("Data to encrypt is required")
            
        encrypted = security_manager.encrypt_sensitive_data(sensitive_data)
        return {
            "success": True,
            "encrypted_data": encrypted
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "encrypt_sensitive_data", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "encrypt_sensitive_data", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/security/decrypt-data")
async def decrypt_sensitive_data(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Decrypt sensitive data with standardized error handling."""
    try:
        encrypted_data = data.get("encrypted_data", "")
        if not encrypted_data:
            raise ValidationError("Encrypted data is required")
            
        decrypted = security_manager.decrypt_sensitive_data(encrypted_data)
        return {
            "success": True,
            "decrypted_data": decrypted
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "decrypt_sensitive_data", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "decrypt_sensitive_data", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

@app.post("/security/sanitize-input")
async def sanitize_input(
    input_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Sanitize user input with standardized error handling."""
    try:
        input_text = input_data.get("input", "")
        if not input_text:
            raise ValidationError("Input text is required")
            
        sanitized = security_manager.sanitize_input(input_text)
        return {
            "success": True,
            "sanitized_input": sanitized
        }
        
    except ValidationError as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "sanitize_input", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=400,
            content=error.to_dict()
        )
    except Exception as e:
        error = ErrorHandler.handle_error(e, {"endpoint": "sanitize_input", "user_id": current_user.get('id')})
        return JSONResponse(
            status_code=500,
            content=error.to_dict()
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )

# A2UI Meeting Assistant Integration
try:
    from a2ui_integration.a2ui_fastapi import *
    logger.info("A2UI meeting assistant integration loaded")
except ImportError as e:
    logger.warning(f"A2UI integration not available: {e}")
