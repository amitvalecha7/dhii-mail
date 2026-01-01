"""
dhii Mail - Authentication System
PASETO (Platform-Agnostic Security Tokens) based authentication with secure token management.
"""

import pyseto
from datetime import datetime, timezone, timedelta
import secrets
import bcrypt
from typing import Optional, Dict, Any, List
import json
import logging
from database import get_db

# FastAPI imports (only used in get_current_user function)
try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages user authentication using PASETO tokens."""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.db = get_db()
        self.token_lifetime = {
            'access': timedelta(hours=2),
            'refresh': timedelta(days=30),
            'api': timedelta(days=365)
        }
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_user(self, email: str, username: str, password: str, 
                   first_name: str = "", last_name: str = "", 
                   tenant_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Create a new user account."""
        try:
            # Check if user already exists
            existing = self.db.execute_query(
                "SELECT id FROM users WHERE email = ? OR username = ?",
                (email, username)
            )
            if existing:
                logger.warning(f"User already exists: {email} or {username}")
                return None
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Insert user
            self.db.execute_update(
                """INSERT INTO users (email, username, password_hash, first_name, last_name) 
                   VALUES (?, ?, ?, ?, ?)""",
                (email, username, password_hash, first_name, last_name)
            )
            
            # Get created user
            user = self.db.execute_query(
                "SELECT * FROM users WHERE email = ?", (email,)
            )
            if not user:
                return None
            
            user_data = user[0]
            
            # Add to tenant if specified
            if tenant_id:
                self.db.execute_update(
                    "INSERT INTO user_tenants (user_id, tenant_id, role) VALUES (?, ?, ?)",
                    (user_data['id'], tenant_id, 'member')
                )
            
            logger.info(f"User created successfully: {email}")
            return user_data
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (without authentication)."""
        try:
            user = self.db.execute_query(
                "SELECT * FROM users WHERE username = ? AND is_active = TRUE",
                (username,)
            )
            
            if user:
                return user[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username/email and password."""
        try:
            # Find user by email or username
            user = self.db.execute_query(
                """SELECT * FROM users 
                   WHERE (email = ? OR username = ?) AND is_active = TRUE""",
                (username_or_email, username_or_email)
            )
            
            if not user:
                logger.warning(f"User not found: {username_or_email}")
                return None
            
            user_data = user[0]
            
            # Verify password
            if not self.verify_password(password, user_data['password_hash']):
                logger.warning(f"Invalid password for user: {username_or_email}")
                return None
            
            # Update last login
            self.db.execute_update(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_data['id'],)
            )
            
            logger.info(f"User authenticated: {username_or_email}")
            return user_data
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def create_token(self, user_id: int, token_type: str = 'access', 
                    scopes: Optional[List[str]] = None) -> Optional[str]:
        """Create a PASETO token for a user."""
        try:
            if token_type not in self.token_lifetime:
                raise ValueError(f"Invalid token type: {token_type}")
            
            # Create token payload
            now = datetime.now(timezone.utc)
            expires_at = now + self.token_lifetime[token_type]
            
            payload = {
                'user_id': user_id,
                'token_type': token_type,
                'scopes': scopes or ['read'],
                'issued_at': now.isoformat(),
                'expires_at': expires_at.isoformat(),
                'token_id': secrets.token_urlsafe(16)
            }
            
            # Create PASETO token
            key = pyseto.Key.new(4, 'local', self.secret_key.encode('utf-8'))
            token = pyseto.encode(key, json.dumps(payload))
            
            # Store token in database
            self.db.execute_update(
                """INSERT INTO auth_tokens 
                   (user_id, token_id, token_hash, purpose, scopes, expires_at) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    payload['token_id'],
                    self._hash_token(token.decode('utf-8')),
                    token_type,
                    json.dumps(scopes or ['read']),
                    expires_at.isoformat()
                )
            )
            
            logger.info(f"Token created for user {user_id}: {token_type}")
            return token.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            return None
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """Verify a PASETO token and return user data."""
        try:
            # Decode token
            logger.debug(f"Verifying token: {token[:50]}...")
            key = pyseto.Key.new(4, 'local', self.secret_key.encode('utf-8'))
            logger.debug(f"Token type: {type(token)}")
            token_bytes = token if isinstance(token, bytes) else token.encode('utf-8')
            logger.debug(f"Token bytes length: {len(token_bytes)}")
            decoded = pyseto.decode(key, token_bytes)
            
            payload = decoded.payload
            if isinstance(payload, bytes):
                payload = json.loads(payload.decode('utf-8'))
            elif isinstance(payload, str):
                payload = json.loads(payload)
            
            # Validate token type
            if payload.get('token_type') != token_type:
                logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('token_type')}")
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"Token expired for user {payload['user_id']}")
                return None
            
            # Check if token is revoked
            token_record = self.db.execute_query(
                "SELECT is_revoked FROM auth_tokens WHERE token_id = ? AND user_id = ?",
                (payload['token_id'], payload['user_id'])
            )
            
            if not token_record or token_record[0]['is_revoked']:
                logger.warning(f"Token revoked or not found: {payload['token_id']}")
                return None
            
            # Get user data
            user = self.db.execute_query(
                "SELECT * FROM users WHERE id = ? AND is_active = TRUE",
                (payload['user_id'],)
            )
            
            if not user:
                logger.warning(f"User not found or inactive: {payload['user_id']}")
                return None
            
            # Update token last used
            self.db.execute_update(
                "UPDATE auth_tokens SET last_used = CURRENT_TIMESTAMP WHERE token_id = ?",
                (payload['token_id'],)
            )
            
            user_data = user[0]
            user_data['token_payload'] = payload
            
            logger.info(f"Token verified for user {payload['user_id']}")
            return user_data
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            logger.error(f"Token verification error type: {type(e)}")
            import traceback
            logger.error(f"Token verification traceback: {traceback.format_exc()}")
            return None
    
    def revoke_token(self, token_id: str) -> bool:
        """Revoke a specific token."""
        try:
            result = self.db.execute_update(
                "UPDATE auth_tokens SET is_revoked = TRUE WHERE token_id = ?",
                (token_id,)
            )
            success = result > 0
            if success:
                logger.info(f"Token revoked: {token_id}")
            return success
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all tokens for a user."""
        try:
            result = self.db.execute_update(
                "UPDATE auth_tokens SET is_revoked = TRUE WHERE user_id = ?",
                (user_id,)
            )
            logger.info(f"Revoked {result} tokens for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"User token revocation failed: {e}")
            return 0
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from database."""
        try:
            result = self.db.execute_update(
                "DELETE FROM auth_tokens WHERE expires_at < CURRENT_TIMESTAMP"
            )
            if result > 0:
                logger.info(f"Cleaned up {result} expired tokens")
            return result
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            return 0
    
    def _hash_token(self, token: str) -> str:
        """Create a hash of the token for storage."""
        import hashlib
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
    
    def get_user_permissions(self, user_id: int, tenant_id: Optional[int] = None) -> Dict[str, Any]:
        """Get user permissions and roles."""
        try:
            # Get user roles across tenants
            roles = self.db.execute_query(
                """SELECT t.slug, ut.role, ut.permissions 
                   FROM user_tenants ut 
                   JOIN tenants t ON ut.tenant_id = t.id 
                   WHERE ut.user_id = ?""",
                (user_id,)
            )
            
            # Get specific tenant role if requested
            tenant_role = None
            if tenant_id:
                tenant_result = self.db.execute_query(
                    "SELECT role, permissions FROM user_tenants WHERE user_id = ? AND tenant_id = ?",
                    (user_id, tenant_id)
                )
                if tenant_result:
                    tenant_role = tenant_result[0]
            
            return {
                'global_roles': [{'tenant': r['slug'], 'role': r['role'], 'permissions': json.loads(r['permissions'] or '{}')} for r in roles],
                'tenant_role': tenant_role,
                'scopes': self._calculate_scopes(tenant_role['role'] if tenant_role else 'member')
            }
        except Exception as e:
            logger.error(f"Permission retrieval failed: {e}")
            return {'global_roles': [], 'tenant_role': None, 'scopes': ['read']}
    
    def _calculate_scopes(self, role: str) -> List[str]:
        """Calculate permission scopes based on role."""
        role_scopes = {
            'admin': ['read', 'write', 'delete', 'admin', 'manage_users', 'manage_tenants'],
            'moderator': ['read', 'write', 'delete', 'moderate'],
            'member': ['read', 'write'],
            'guest': ['read']
        }
        return role_scopes.get(role, ['read'])

# Global auth manager instance - will be set by main.py
auth_manager = None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
    """FastAPI dependency to get current user from JWT token."""
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI not available. Cannot use get_current_user dependency.")
    
    from fastapi import HTTPException, status
    
    # Ensure auth_manager is initialized
    if auth_manager is None:
        raise RuntimeError("AuthManager not initialized. Make sure main.py is imported first.")
    
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_manager.verify_token(token, 'access')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_auth() -> AuthManager:
    """Get the global authentication manager instance."""
    return auth_manager

def init_auth(secret_key: Optional[str] = None) -> AuthManager:
    """Initialize a new authentication manager."""
    global auth_manager
    auth_manager = AuthManager(secret_key)
    return auth_manager

if __name__ == "__main__":
    # Test authentication system
    logging.basicConfig(level=logging.INFO)
    
    print("Testing dhii Mail authentication system...")
    auth = get_auth()
    
    # Test user creation
    print("\n1. Creating test user...")
    user = auth.create_user(
        email="test@dhii.ai",
        username="testuser",
        password="test123",
        first_name="Test",
        last_name="User"
    )
    
    if user:
        print(f"✓ User created: {user['email']}")
        
        # Test authentication
        print("\n2. Testing authentication...")
        auth_user = auth.authenticate_user("test@dhii.ai", "test123")
        if auth_user:
            print("✓ Authentication successful")
            
            # Test token creation
            print("\n3. Creating access token...")
            token = auth.create_token(auth_user['id'], 'access', ['read', 'write'])
            if token:
                print(f"✓ Token created: {token[:50]}...")
                
                # Test token verification
                print("\n4. Verifying token...")
                verified_user = auth.verify_token(token, 'access')
                if verified_user:
                    print(f"✓ Token verified for user: {verified_user['email']}")
                else:
                    print("✗ Token verification failed")
            else:
                print("✗ Token creation failed")
        else:
            print("✗ Authentication failed")
    else:
        print("✗ User creation failed")
    
    print("\nAuthentication system ready!")