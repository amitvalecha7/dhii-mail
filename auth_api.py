#!/usr/bin/env python3
"""
Signup/Login Flow API for dhii Mail
Handles authentication with A2UI glass-themed cards
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
import json
import jwt
from datetime import datetime, timedelta
import bcrypt
from uuid import uuid4

# Import existing components
from security_manager import SecurityManager
from a2ui_card_implementation import A2UICardRenderer
from config import settings

app = FastAPI(title="dhii Mail Auth API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
security_manager = SecurityManager()
card_renderer = A2UICardRenderer()

# SECURITY: JWT configuration loaded from environment-driven settings
# This prevents hard-coded secrets and allows secure configuration per environment
SECRET_KEY = settings.jwt_secret_key  # From environment: JWT_SECRET_KEY - validated secure
ALGORITHM = "HS256"  # Standard JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

# Mock user database (replace with real database)
users_db = {}
sessions_db = {}

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    next_step: Optional[str] = None
    cards: Optional[List[Dict[str, Any]]] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.get("/auth/signup", response_class=HTMLResponse)
async def get_signup_page():
    """Serve the signup flow with A2UI glass cards"""
    try:
        # Generate signup flow cards
        cards = card_renderer.render_onboarding_sequence()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dhii Mail - Sign Up</title>
    <link rel="stylesheet" href="/a2ui/static/glass-theme.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .signup-container {{
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
        }}

        .progress-bar {{
            glass-standard;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}

        .progress-steps {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}

        .progress-step {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .progress-step.active {{
            background: rgba(59, 130, 246, 0.8);
            transform: scale(1.1);
        }}

        .progress-step.completed {{
            background: rgba(34, 197, 94, 0.8);
        }}

        .progress-bar h3 {{
            color: white;
            font-size: 16px;
            margin-bottom: 5px;
        }}

        .progress-bar p {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
        }}

        .card-container {{
            glass-elevated;
            padding: 30px;
            margin-bottom: 20px;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            color: white;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
        }}

        .form-group input {{
            width: 100%;
            glass-subtle;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
        }}

        .form-group input:focus {{
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}

        .form-group input::placeholder {{
            color: rgba(255, 255, 255, 0.5);
        }}

        .form-actions {{
            display: flex;
            gap: 12px;
            justify-content: space-between;
            margin-top: 30px;
        }}

        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}

        .btn-primary {{
            glass-button;
            color: white;
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        .btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }}

        .error-message {{
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fecaca;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 20px;
            display: none;
        }}

        .success-message {{
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #bbf7d0;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 20px;
            display: none;
        }}

        .loading-spinner {{
            display: none;
            text-align: center;
            padding: 20px;
        }}

        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid rgba(59, 130, 246, 0.8);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .welcome-text {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .welcome-text h2 {{
            color: white;
            font-size: 24px;
            margin-bottom: 10px;
        }}

        .welcome-text p {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            line-height: 1.5;
        }}

        .feature-list {{
            margin: 20px 0;
        }}

        .feature-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }}

        .feature-icon {{
            width: 20px;
            height: 20px;
            fill: rgba(59, 130, 246, 0.8);
        }}

        @media (max-width: 480px) {{
            .signup-container {{
                padding: 10px;
            }}
            
            .card-container {{
                padding: 20px;
            }}
            
            .form-actions {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="signup-container">
        <div class="progress-bar">
            <div class="progress-steps">
                <div class="progress-step active" id="step1">1</div>
                <div class="progress-step" id="step2">2</div>
                <div class="progress-step" id="step3">3</div>
                <div class="progress-step" id="step4">4</div>
            </div>
            <h3>Step 1 of 4: Create Your Account</h3>
            <p>Join thousands of users managing their emails with AI</p>
        </div>

        <div class="card-container">
            <div class="welcome-text">
                <h2>Welcome to dhii Mail! 🚀</h2>
                <p>Experience the future of email management with our AI-powered assistant. Get started in just a few steps.</p>
            </div>

            <div class="error-message" id="errorMessage"></div>
            <div class="success-message" id="successMessage"></div>

            <form id="signupForm">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="you@example.com" required>
                </div>

                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name" placeholder="John Doe" required>
                </div>

                <div class="form-group">
                    <label for="company">Company (Optional)</label>
                    <input type="text" id="company" name="company" placeholder="Your Company">
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="••••••••" required minlength="8">
                </div>

                <div class="feature-list">
                    <div class="feature-item">
                        <svg class="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <span>AI-powered email analysis</span>
                    </div>
                    <div class="feature-item">
                        <svg class="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                        </svg>
                        <span>Smart categorization & insights</span>
                    </div>
                    <div class="feature-item">
                        <svg class="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                        </svg>
                        <span>Natural language search</span>
                    </div>
                </div>

                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="window.location.href='/auth/login'">
                        Already have an account?
                    </button>
                    <button type="submit" class="btn btn-primary" id="submitBtn">
                        Create Account
                    </button>
                </div>
            </form>

            <div class="loading-spinner" id="loadingSpinner">
                <div class="spinner"></div>
                <p style="color: white; margin-top: 10px;">Creating your account...</p>
            </div>
        </div>
    </div>

    <script>
        class SignupFlow {{
            constructor() {{
                this.form = document.getElementById('signupForm');
                this.submitBtn = document.getElementById('submitBtn');
                this.loadingSpinner = document.getElementById('loadingSpinner');
                this.errorMessage = document.getElementById('errorMessage');
                this.successMessage = document.getElementById('successMessage');
                
                this.initializeEventListeners();
            }}

            initializeEventListeners() {{
                this.form.addEventListener('submit', (e) => this.handleSubmit(e));
                
                // Real-time validation
                document.getElementById('email').addEventListener('blur', () => this.validateEmail());
                document.getElementById('password').addEventListener('input', () => this.validatePassword());
            }}

            async handleSubmit(e) {{
                e.preventDefault();
                
                if (!this.validateForm()) {{
                    return;
                }}

                this.showLoading();
                
                try {{
                    const formData = new FormData(this.form);
                    const data = {{
                        email: formData.get('email'),
                        name: formData.get('name'),
                        company: formData.get('company'),
                        password: formData.get('password')
                    }};

                    const response = await fetch('/auth/api/signup', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(data)
                    }});

                    const result = await response.json();

                    if (result.success) {{
                        this.showSuccess('Account created successfully! Redirecting to onboarding...');
                        setTimeout(() => {{
                            window.location.href = '/auth/onboarding?token=' + result.token;
                        }}, 2000);
                    }} else {{
                        this.showError(result.message || 'Signup failed. Please try again.');
                    }}
                }} catch (error) {{
                    console.error('Signup error:', error);
                    this.showError('Network error. Please check your connection and try again.');
                }} finally {{
                    this.hideLoading();
                }}
            }}

            validateForm() {{
                const email = document.getElementById('email').value;
                const name = document.getElementById('name').value;
                const password = document.getElementById('password').value;

                if (!email || !name || !password) {{
                    this.showError('Please fill in all required fields.');
                    return false;
                }}

                if (!this.validateEmail()) {{
                    return false;
                }}

                if (password.length < 8) {{
                    this.showError('Password must be at least 8 characters long.');
                    return false;
                }}

                return true;
            }}

            validateEmail() {{
                const email = document.getElementById('email').value;
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                
                if (email && !emailRegex.test(email)) {{
                    this.showError('Please enter a valid email address.');
                    return false;
                }}
                
                this.hideError();
                return true;
            }}

            validatePassword() {{
                const password = document.getElementById('password').value;
                const strength = this.checkPasswordStrength(password);
                
                // Update password field styling based on strength
                const passwordInput = document.getElementById('password');
                passwordInput.style.borderColor = strength.color;
            }}

            checkPasswordStrength(password) {{
                let strength = 0;
                if (password.length >= 8) strength++;
                if (password.match(/[a-z]+/)) strength++;
                if (password.match(/[A-Z]+/)) strength++;
                if (password.match(/[0-9]+/)) strength++;
                if (password.match(/[$@#&!]+/)) strength++;

                const levels = [
                    {{ text: 'Very Weak', color: '#ef4444' }},
                    {{ text: 'Weak', color: '#f97316' }},
                    {{ text: 'Fair', color: '#eab308' }},
                    {{ text: 'Good', color: '#22c55e' }},
                    {{ text: 'Strong', color: '#10b981' }}
                ];

                return levels[strength] || levels[0];
            }}

            showLoading() {{
                this.form.style.display = 'none';
                this.loadingSpinner.style.display = 'block';
                this.submitBtn.disabled = true;
            }}

            hideLoading() {{
                this.form.style.display = 'block';
                this.loadingSpinner.style.display = 'none';
                this.submitBtn.disabled = false;
            }}

            showError(message) {{
                this.errorMessage.textContent = message;
                this.errorMessage.style.display = 'block';
                this.successMessage.style.display = 'none';
            }}

            showSuccess(message) {{
                this.successMessage.textContent = message;
                this.successMessage.style.display = 'block';
                this.errorMessage.style.display = 'none';
            }}

            hideError() {{
                this.errorMessage.style.display = 'none';
            }}
        }}

        // Initialize signup flow
        const signupFlow = new SignupFlow();
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving signup page: {str(e)}")

@app.post("/auth/api/signup")
async def api_signup(user_data: UserSignup):
    """API endpoint for user signup"""
    try:
        # Validate input
        if not user_data.email or not user_data.password or not user_data.name:
            return AuthResponse(
                success=False,
                message="Please provide all required fields"
            )
        
        # Check if user already exists
        if user_data.email in users_db:
            return AuthResponse(
                success=False,
                message="User with this email already exists"
            )
        
        # Create new user
        user_id = str(uuid4())
        hashed_password = hash_password(user_data.password)
        
        users_db[user_data.email] = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "company": user_data.company,
            "password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "email_connected": False,
            "onboarding_completed": False
        }
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email, "user_id": user_id},
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            success=True,
            message="Account created successfully",
            token=access_token,
            user={
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name,
                "company": user_data.company
            },
            next_step="onboarding"
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Signup failed: {str(e)}"
        )

@app.get("/auth/login", response_class=HTMLResponse)
async def get_login_page():
    """Serve the login page with A2UI glass theme"""
    try:
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dhii Mail - Log In</title>
    <link rel="stylesheet" href="/a2ui/static/glass-theme.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-container {
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
        }

        .card-container {
            glass-elevated;
            padding: 40px;
        }

        .welcome-text {
            text-align: center;
            margin-bottom: 30px;
        }

        .welcome-text h2 {
            color: white;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .welcome-text p {
            color: rgba(255, 255, 255, 0.7);
            font-size: 16px;
        }

        .error-message {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fecaca;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 20px;
            display: none;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: white;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .form-group input {
            width: 100%;
            glass-subtle;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
        }

        .form-group input:focus {
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-group input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        .form-actions {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 30px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-primary {
            glass-button;
            color: white;
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .signup-link {
            text-align: center;
            margin-top: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
        }

        .signup-link a {
            color: rgba(59, 130, 246, 0.8);
            text-decoration: none;
            font-weight: 500;
        }

        .signup-link a:hover {
            text-decoration: underline;
        }

        .loading-spinner {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid rgba(59, 130, 246, 0.8);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 480px) {
            .login-container {
                padding: 10px;
            }
            
            .card-container {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="card-container">
            <div class="welcome-text">
                <h2>Welcome Back! 👋</h2>
                <p>Log in to continue managing your emails with AI</p>
            </div>

            <div class="error-message" id="errorMessage"></div>

            <form id="loginForm">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="you@example.com" required>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="••••••••" required>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-primary" id="submitBtn">
                        Log In
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="window.location.href='/auth/signup'">
                        Create New Account
                    </button>
                </div>
            </form>

            <div class="loading-spinner" id="loadingSpinner">
                <div class="spinner"></div>
                <p style="color: white; margin-top: 10px;">Logging you in...</p>
            </div>

            <div class="signup-link">
                <p>Forgot your password? <a href="/auth/forgot-password">Reset it here</a></p>
            </div>
        </div>
    </div>

    <script>
        class LoginFlow {
            constructor() {
                this.form = document.getElementById('loginForm');
                this.submitBtn = document.getElementById('submitBtn');
                this.loadingSpinner = document.getElementById('loadingSpinner');
                this.errorMessage = document.getElementById('errorMessage');
                
                this.initializeEventListeners();
            }

            initializeEventListeners() {
                this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            }

            async handleSubmit(e) {
                e.preventDefault();
                
                if (!this.validateForm()) {
                    return;
                }

                this.showLoading();
                
                try {
                    const formData = new FormData(this.form);
                    const data = {
                        email: formData.get('email'),
                        password: formData.get('password')
                    };

                    const response = await fetch('/auth/api/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (result.success) {
                        // Store token and redirect to dashboard
                        localStorage.setItem('access_token', result.token);
                        window.location.href = '/dashboard';
                    } else {
                        this.showError(result.message || 'Login failed. Please check your credentials.');
                    }
                } catch (error) {
                    console.error('Login error:', error);
                    this.showError('Network error. Please check your connection and try again.');
                } finally {
                    this.hideLoading();
                }
            }

            validateForm() {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;

                if (!email || !password) {
                    this.showError('Please enter both email and password.');
                    return false;
                }

                return true;
            }

            showLoading() {
                this.form.style.display = 'none';
                this.loadingSpinner.style.display = 'block';
                this.submitBtn.disabled = true;
            }

            hideLoading() {
                this.form.style.display = 'block';
                this.loadingSpinner.style.display = 'none';
                this.submitBtn.disabled = false;
            }

            showError(message) {
                this.errorMessage.textContent = message;
                this.errorMessage.style.display = 'block';
            }
        }

        // Initialize login flow
        const loginFlow = new LoginFlow();
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving login page: {str(e)}")

@app.post("/auth/api/login")
async def api_login(user_data: UserLogin):
    """API endpoint for user login"""
    try:
        # Find user
        user = None
        for email, user_info in users_db.items():
            if email == user_data.email:
                user = user_info
                break
        
        if not user:
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user["password"]):
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email, "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            token=access_token,
            user={
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "company": user.get("company")
            }
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Login failed: {str(e)}"
        )

@app.get("/auth/onboarding", response_class=HTMLResponse)
async def get_onboarding_page(token: str):
    """Serve the onboarding flow with A2UI glass cards"""
    try:
        # Validate token and get user info
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            user = users_db.get(email)
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Generate onboarding cards
        cards = card_renderer.render_onboarding_sequence()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dhii Mail - Onboarding</title>
    <link rel="stylesheet" href="/a2ui/static/glass-theme.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .onboarding-container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        .progress-header {{
            glass-standard;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}

        .progress-header h2 {{
            color: white;
            font-size: 24px;
            margin-bottom: 10px;
        }}

        .progress-header p {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
        }}

        .cards-container {{
            display: grid;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .action-buttons {{
            glass-standard;
            padding: 20px;
            text-align: center;
        }}

        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin: 0 10px;
        }}

        .btn-primary {{
            glass-button;
            color: white;
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        @media (max-width: 768px) {{
            .onboarding-container {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="onboarding-container">
        <div class="progress-header">
            <h2>Welcome, {user['name']}! 🎉</h2>
            <p>Let's get your email account connected and start using AI-powered features</p>
        </div>
        
        <div class="cards-container" id="cardsContainer">
            <!-- A2UI cards will be rendered here -->
        </div>
        
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="skipOnboarding()">
                Skip for now
            </button>
            <button class="btn btn-primary" onclick="completeOnboarding()">
                Complete Setup
            </button>
        </div>
    </div>

    <script>
        // A2UI cards data
        const cards = {json.dumps(cards)};
        
        class OnboardingFlow {{
            constructor() {{
                this.cardsContainer = document.getElementById('cardsContainer');
                this.currentCardIndex = 0;
                this.userToken = '{token}';
                
                this.renderCards();
            }}

            renderCards() {{
                this.cardsContainer.innerHTML = '';
                
                cards.forEach((card, index) => {{
                    const cardElement = this.createCardElement(card, index);
                    this.cardsContainer.appendChild(cardElement);
                }});
            }}

            createCardElement(card, index) {{
                const cardDiv = document.createElement('div');
                cardDiv.className = 'glass-elevated';
                cardDiv.style.padding = '24px';
                cardDiv.style.marginBottom = '16px';
                cardDiv.style.borderRadius = '12px';
                
                cardDiv.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                        <div style="width: 48px; height: 48px; background: rgba(59, 130, 246, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 24px;">${{card.icon || '📧'}}</span>
                        </div>
                        <div>
                            <h3 style="color: white; font-size: 18px; margin-bottom: 4px;">${{card.title}}</h3>
                            <p style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">${{card.subtitle}}</p>
                        </div>
                    </div>
                    <p style="color: rgba(255, 255, 255, 0.8); font-size: 14px; line-height: 1.5; margin-bottom: 16px;">${{card.description}}</p>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        ${{card.actions.map(action => `
                            <button class="btn btn-primary" onclick="handleCardAction('${{action.id}}', '${{action.type}}')">
                                ${{action.text}}
                            </button>
                        `).join('')}}
                    </div>
                `;
                
                return cardDiv;
            }}
        }}

        function handleCardAction(actionId, actionType) {{
            console.log('Card action:', actionId, actionType);
            
            // Handle different card actions
            switch(actionType) {{
                case 'connect_email':
                    connectEmail();
                    break;
                case 'setup_preferences':
                    setupPreferences();
                    break;
                case 'tutorial':
                    startTutorial();
                    break;
                case 'import_contacts':
                    importContacts();
                    break;
                default:
                    console.log('Unknown action type:', actionType);
            }}
        }}

        async function connectEmail() {{
            alert('Email connection wizard would open here. This would guide through IMAP/OAuth setup.');
        }}

        function setupPreferences() {{
            alert('Preferences setup would open here. Configure AI analysis settings, notifications, etc.');
        }}

        function startTutorial() {{
            alert('Interactive tutorial would start here. Show key features and how to use them.');
        }}

        function importContacts() {{
            alert('Contact import would open here. Import from email, CSV, or other sources.');
        }}

        async function completeOnboarding() {{
            try {{
                const response = await fetch('/auth/api/complete-onboarding', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + document.querySelector('.onboarding-container').dataset.token
                    }}
                }});

                const result = await response.json();
                
                if (result.success) {{
                    window.location.href = '/dashboard';
                }} else {{
                    alert('Failed to complete onboarding: ' + result.message);
                }}
            }} catch (error) {{
                console.error('Onboarding completion error:', error);
                alert('Network error. Please try again.');
            }}
        }}

        function skipOnboarding() {{
            if (confirm('Are you sure you want to skip onboarding? You can complete setup later from your dashboard.')) {{
                window.location.href = '/dashboard';
            }}
        }}

        // Initialize onboarding flow
        const onboardingFlow = new OnboardingFlow();
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving onboarding page: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)