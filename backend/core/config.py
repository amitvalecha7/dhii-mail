"""
dhii Mail - Core Configuration
Application settings and configuration management.
"""

import os
from typing import Optional, List
from pydantic import BaseSettings
import secrets

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "dhii Mail"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Database
    database_url: str = "dhii_mail.db"
    
    # Security
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 120  # 2 hours
    refresh_token_expire_days: int = 30
    algorithm: str = "paseto"
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # AI Providers
    openrouter_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # Email Settings
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # File Storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # WebSocket
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings