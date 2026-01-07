"""
Email Plugin Models - Framework 2.0
Pydantic models for input/output validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

class SMTPConfig(BaseModel):
    """SMTP configuration model"""
    host: str = Field(..., description="SMTP server host")
    port: int = Field(..., description="SMTP server port")
    username: Optional[str] = Field(None, description="SMTP username")
    password: Optional[str] = Field(None, description="SMTP password")
    use_tls: bool = Field(True, description="Use TLS encryption")

class SendEmailInput(BaseModel):
    """Input model for sending email"""
    to_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    from_email: EmailStr = Field(..., description="Sender email address")
    smtp_config: SMTPConfig = Field(..., description="SMTP configuration")

class SendEmailOutput(BaseModel):
    """Output model for email sending"""
    status: str = Field(..., description="Email sending status")
    message_id: Optional[str] = Field(None, description="Message ID if successful")
    error: Optional[str] = Field(None, description="Error message if failed")

class TestConnectionInput(BaseModel):
    """Input model for testing SMTP connection"""
    smtp_config: SMTPConfig = Field(..., description="SMTP configuration to test")

class TestConnectionOutput(BaseModel):
    """Output model for connection test"""
    status: str = Field(..., description="Connection status")
    error: Optional[str] = Field(None, description="Error message if failed")