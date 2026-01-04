"""
Configuration management for dhii-mail
Handles environment-based configuration with support for dev/prod profiles
"""

import os
from typing import List, Optional
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Security
    # SECURITY: JWT secret loaded from environment variable JWT_SECRET_KEY
    # Default is for development only - production MUST set JWT_SECRET_KEY environment variable
    jwt_secret_key: str = Field(default="dhii-mail-secret-key-for-development", env="JWT_SECRET_KEY")
    # SECURITY: Encryption key loaded from environment variable ENCRYPTION_KEY  
    # Default is for development only - production MUST set ENCRYPTION_KEY environment variable
    encryption_key: str = Field(default="dhii-mail-encryption-key-32-chars-dev", env="ENCRYPTION_KEY")
    
    # Database
    database_url: str = Field(default="sqlite:///./dhii_mail.db", env="DATABASE_URL")
    
    # Email
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    
    # Google API
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    
    # CORS Configuration
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    # SECURITY: CORS origins loaded from environment variable CORS_ORIGINS
    # Default "*" is for development only - production should set specific origins
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    # SECURITY: CORS credentials loaded from environment variable CORS_ALLOW_CREDENTIALS
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    # SECURITY: CORS methods loaded from environment variable CORS_ALLOW_METHODS
    cors_allow_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="CORS_ALLOW_METHODS")
    # SECURITY: CORS headers loaded from environment variable CORS_ALLOW_HEADERS
    cors_allow_headers: str = Field(default="*", env="CORS_ALLOW_HEADERS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Application
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    
    # Server
    uvicorn_workers: int = Field(default=4, env="UVICORN_WORKERS")
    uvicorn_port: int = Field(default=8005, env="UVICORN_PORT")
    uvicorn_host: str = Field(default="0.0.0.0", env="UVICORN_HOST")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if not self.cors_origins:
            return []
        
        # Split by comma and clean up
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        
        # In development, allow localhost variants
        if self.is_development:
            localhost_origins = [
                "http://localhost:3000",
                "http://localhost:8005",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8005"
            ]
            # Add localhost origins if not already present
            for origin in localhost_origins:
                if origin not in origins:
                    origins.append(origin)
        
        # In production, be more restrictive with default origins
        elif self.is_production:
            # If using default origins in production, only allow explicitly configured ones
            default_origins = ["http://localhost:3000", "http://localhost:8005"]
            if all(origin in origins for origin in default_origins) and len(origins) == 2:
                # This means only default origins are set, be restrictive
                return []
        
        return origins
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Get CORS methods as a list"""
        if not self.cors_allow_methods:
            return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        
        return [method.strip().upper() for method in self.cors_allow_methods.split(",")]
    
    def get_cors_config(self) -> dict:
        """Get complete CORS configuration"""
        config = {
            "allow_origins": self.cors_origins_list,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_methods_list,
            "allow_headers": self.cors_allow_headers.split(",") if self.cors_allow_headers != "*" else ["*"]
        }
        
        # Production security hardening
        if self.is_production:
            # More restrictive defaults for production
            if not self.cors_origins or self.cors_origins == "http://localhost:3000,http://localhost:8005":
                # If no specific origins set for production, be restrictive
                config["allow_origins"] = []  # Must be explicitly configured
            
            # Disable credentials for better security unless explicitly needed
            # Check if CORS_ALLOW_CREDENTIALS was explicitly set in environment
            cors_cred_env = os.getenv("CORS_ALLOW_CREDENTIALS")
            if cors_cred_env is None:  # Only if not explicitly set in environment
                config["allow_credentials"] = False
            
            # More restrictive methods in production
            if not os.getenv("CORS_ALLOW_METHODS"):
                config["allow_methods"] = ["GET", "POST", "PUT", "DELETE"]
            
            # More restrictive headers in production
            if self.cors_allow_headers == "*":
                config["allow_headers"] = ["Authorization", "Content-Type", "X-Requested-With"]
        
        return config

# Global settings instance
settings = Settings()