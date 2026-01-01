"""
dhii Mail - Security Manager
Advanced security features for enterprise email management.
"""

import hashlib
import secrets
import re
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr
import jwt
from cryptography.fernet import Fernet
import bcrypt

logger = logging.getLogger(__name__)

class SecurityConfig(BaseModel):
    """Security configuration settings."""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    enable_2fa: bool = False
    encryption_key_rotation_days: int = 90
    audit_log_retention_days: int = 365

class SecurityEvent(BaseModel):
    """Security event for audit logging."""
    id: str
    timestamp: datetime
    event_type: str
    user_email: Optional[str] = None
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    severity: str = "info"  # info, warning, error, critical

class LoginAttempt(BaseModel):
    """Track login attempts for brute force protection."""
    ip_address: str
    email: Optional[str] = None
    timestamp: datetime
    success: bool
    user_agent: str

class SecurityManager:
    """Advanced security management for dhii Mail."""
    
    def __init__(self, config: SecurityConfig = SecurityConfig()):
        self.config = config
        self.encryption_key = self._generate_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.failed_attempts: Dict[str, List[LoginAttempt]] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        self.security_events: List[SecurityEvent] = []
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for data protection."""
        return Fernet.generate_key()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to policy."""
        errors = []
        
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters long")
        
        if self.config.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config.password_require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if self.config.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'admin', 'letmein', 'welcome']
        if password.lower() in weak_passwords:
            errors.append("Password is too common, please choose a stronger password")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength_score": max(0, 100 - (len(errors) * 20))
        }
    
    def check_brute_force_protection(self, ip_address: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Check if IP address or email is locked due to brute force attempts."""
        now = datetime.now(timezone.utc)
        
        # Check account lockout
        if email and email in self.locked_accounts:
            lockout_end = self.locked_accounts[email]
            if now < lockout_end:
                remaining_minutes = int((lockout_end - now).total_seconds() / 60)
                return {
                    "is_locked": True,
                    "reason": "account_lockout",
                    "locked_until": lockout_end.isoformat(),
                    "remaining_minutes": remaining_minutes
                }
            else:
                # Lockout expired, remove from locked accounts
                del self.locked_accounts[email]
        
        # Check IP-based lockout
        if ip_address in self.locked_accounts:
            lockout_end = self.locked_accounts[ip_address]
            if now < lockout_end:
                remaining_minutes = int((lockout_end - now).total_seconds() / 60)
                return {
                    "is_locked": True,
                    "reason": "ip_lockout",
                    "locked_until": lockout_end.isoformat(),
                    "remaining_minutes": remaining_minutes
                }
            else:
                # Lockout expired, remove from locked accounts
                del self.locked_accounts[ip_address]
        
        return {"is_locked": False}
    
    def record_login_attempt(self, ip_address: str, email: Optional[str], success: bool, user_agent: str):
        """Record login attempt for brute force protection."""
        now = datetime.now(timezone.utc)
        attempt = LoginAttempt(
            ip_address=ip_address,
            email=email,
            timestamp=now,
            success=success,
            user_agent=user_agent
        )
        
        # Store attempt
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        self.failed_attempts[ip_address].append(attempt)
        
        # Clean old attempts (keep last hour)
        one_hour_ago = now - timedelta(hours=1)
        self.failed_attempts[ip_address] = [
            a for a in self.failed_attempts[ip_address] 
            if a.timestamp > one_hour_ago
        ]
        
        # Check for lockout conditions
        if not success:
            recent_failures = [
                a for a in self.failed_attempts[ip_address] 
                if not a.success and a.timestamp > (now - timedelta(minutes=15))
            ]
            
            if len(recent_failures) >= self.config.max_login_attempts:
                # Lock the IP address
                lockout_end = now + timedelta(minutes=self.config.lockout_duration_minutes)
                self.locked_accounts[ip_address] = lockout_end
                
                # Also lock the email if provided
                if email:
                    self.locked_accounts[email] = lockout_end
                
                self.log_security_event(
                    "brute_force_detected",
                    ip_address,
                    email,
                    user_agent,
                    {"failures": len(recent_failures), "lockout_duration": self.config.lockout_duration_minutes},
                    "warning"
                )
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token."""
        return secrets.token_urlsafe(length)
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"]', '', input_data)
        # Limit length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized.strip()
    
    def sanitize_a2ui_component_data(self, component_data: dict) -> dict:
        """Sanitize A2UI component data for secure rendering."""
        sanitized_data = {}
        
        for key, value in component_data.items():
            if isinstance(value, str):
                # Apply stricter sanitization for component properties
                sanitized_value = re.sub(r'[<>"\'\\]', '', value)
                sanitized_value = re.sub(r'javascript:', '', sanitized_value, flags=re.IGNORECASE)
                sanitized_value = re.sub(r'on\w+\s*=', '', sanitized_value, flags=re.IGNORECASE)
                sanitized_data[key] = sanitized_value[:500]  # Stricter length limit
            elif isinstance(value, dict):
                sanitized_data[key] = self.sanitize_a2ui_component_data(value)
            elif isinstance(value, list):
                sanitized_data[key] = [
                    self.sanitize_a2ui_component_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized_data[key] = value
        
        return sanitized_data
    
    def validate_a2ui_component_properties(self, component_type: str, properties: dict) -> tuple[bool, list[str]]:
        """Validate A2UI component properties against security rules."""
        errors = []
        
        # Define allowed properties for each component type
        allowed_properties = {
            "text": {"content", "variant", "size", "color", "align"},
            "button": {"label", "variant", "size", "icon", "disabled"},
            "container": {"orientation", "spacing", "alignment", "border", "border_radius"},
            "form": {"fields", "submit_label", "validation"},
            "progress_indicator_card": {"title", "current_step", "total_steps", "progress_percentage", "status"},
            "feature_card": {"title", "description", "icon", "highlight"},
            "security_status_card": {"overall_status", "security_score", "two_factor_enabled", "encryption_status", "recommendations"}
        }
        
        # Check if component type is allowed
        if component_type not in allowed_properties:
            errors.append(f"Component type '{component_type}' is not allowed")
            return False, errors
        
        # Check for suspicious property names
        for prop_name in properties.keys():
            if prop_name not in allowed_properties[component_type]:
                errors.append(f"Property '{prop_name}' is not allowed for component '{component_type}'")
            
            # Check for suspicious property values
            if isinstance(properties[prop_name], str):
                if re.search(r'<script|javascript:|on\w+\s*=', properties[prop_name], re.IGNORECASE):
                    errors.append(f"Property '{prop_name}' contains potentially dangerous content")
        
        # Validate specific property values
        if component_type == "button" and "variant" in properties:
            allowed_variants = {"primary", "secondary", "text", "danger"}
            if properties["variant"] not in allowed_variants:
                errors.append(f"Button variant '{properties['variant']}' is not allowed")
        
        if component_type == "text" and "variant" in properties:
            allowed_variants = {"heading1", "heading2", "heading3", "body", "error"}
            if properties["variant"] not in allowed_variants:
                errors.append(f"Text variant '{properties['variant']}' is not allowed")
        
        return len(errors) == 0, errors
    
    def validate_a2ui_action(self, action_name: str, action_params: dict) -> tuple[bool, list[str]]:
        """Validate A2UI actions against security allowlist."""
        errors = []
        
        # Define allowed actions
        allowed_actions = {
            "start_onboarding",
            "submit_account_info",
            "import_gmail",
            "import_outlook",
            "skip_import",
            "enable_2fa",
            "setup_authenticator",
            "setup_sms",
            "skip_2fa",
            "learn_more_video",
            "learn_more_marketing",
            "learn_more_security",
            "complete_onboarding",
            "retry_import",
            "view_security_details"
        }
        
        if action_name not in allowed_actions:
            errors.append(f"Action '{action_name}' is not allowed")
            return False, errors
        
        # Validate action parameters
        if action_name.startswith("import_"):
            if "provider" in action_params:
                allowed_providers = {"gmail", "outlook", "yahoo"}
                if action_params["provider"] not in allowed_providers:
                    errors.append(f"Import provider '{action_params['provider']}' is not allowed")
        
        if action_name == "submit_account_info":
            required_fields = {"email", "password", "full_name"}
            missing_fields = required_fields - set(action_params.keys())
            if missing_fields:
                errors.append(f"Missing required fields: {missing_fields}")
        
        return len(errors) == 0, errors
    
    def validate_email_format(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def log_security_event(self, event_type: str, ip_address: str, user_email: Optional[str], 
                          user_agent: str, details: Dict[str, Any], severity: str = "info"):
        """Log security event for audit purposes."""
        event = SecurityEvent(
            id=self.generate_secure_token(16),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            severity=severity
        )
        
        self.security_events.append(event)
        
        # Log to system logger
        log_message = f"Security Event: {event_type} from {ip_address}"
        if user_email:
            log_message += f" for user {user_email}"
        
        if severity == "critical":
            logger.critical(log_message)
        elif severity == "error":
            logger.error(log_message)
        elif severity == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def get_security_events(self, user_email: Optional[str] = None, 
                           event_type: Optional[str] = None, 
                           severity: Optional[str] = None,
                           limit: int = 100) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        events = self.security_events
        
        if user_email:
            events = [e for e in events if e.user_email == user_email]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    def cleanup_old_events(self, days: int = 30):
        """Clean up old security events."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        self.security_events = [
            e for e in self.security_events 
            if e.timestamp > cutoff_date
        ]
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary statistics."""
        now = datetime.now(timezone.utc)
        
        # Count events in last 24 hours
        last_24h = now - timedelta(hours=24)
        recent_events = [e for e in self.security_events if e.timestamp > last_24h]
        
        # Count locked accounts
        active_lockouts = [
            (identifier, lockout_time) for identifier, lockout_time in self.locked_accounts.items()
            if lockout_time > now
        ]
        
        return {
            "total_events": len(self.security_events),
            "events_last_24h": len(recent_events),
            "active_lockouts": len(active_lockouts),
            "failed_login_attempts": len([
                e for e in recent_events 
                if e.event_type == "login_failed"
            ]),
            "brute_force_detections": len([
                e for e in recent_events 
                if e.event_type == "brute_force_detected"
            ]),
            "critical_events": len([
                e for e in recent_events 
                if e.severity == "critical"
            ])
        }

# Global security manager instance
security_manager = SecurityManager()