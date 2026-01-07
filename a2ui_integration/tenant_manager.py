"""
Multi-Tenant Manager for A2UI
Handles tenant isolation, user context, and tenant-scoped operations
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import json

logger = logging.getLogger(__name__)

class Tenant(BaseModel):
    """Tenant model for multi-tenant isolation"""
    id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Tenant display name")
    domain: str = Field(..., description="Tenant domain for identification")
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    settings: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    max_users: Optional[int] = Field(default=None, description="Maximum users allowed")
    storage_quota: Optional[int] = Field(default=None, description="Storage quota in bytes")

class TenantUser(BaseModel):
    """User model with tenant context"""
    id: str = Field(..., description="User ID")
    tenant_id: str = Field(..., description="Associated tenant ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User display name")
    username: str = Field(..., description="Username for login")
    roles: List[str] = Field(default_factory=lambda: ["user"])
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(default=None)
    preferences: Dict[str, Any] = Field(default_factory=dict)

class TenantContext(BaseModel):
    """Context object for tenant-scoped operations"""
    tenant: Tenant
    user: TenantUser
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class TenantManager:
    """Central manager for tenant operations and isolation"""
    
    def __init__(self):
        # Mock tenant database (replace with real database)
        self._tenants: Dict[str, Tenant] = {}
        self._tenant_users: Dict[str, List[TenantUser]] = {}
        self._user_sessions: Dict[str, Dict[str, Any]] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock tenant data for testing"""
        # Create test tenant
        test_tenant = Tenant(
            id="tenant-001",
            name="Dhii Test Tenant",
            domain="test.dhii.ai",
            features=["email", "calendar", "meetings", "crm"],
            max_users=100,
            storage_quota=10 * 1024 * 1024 * 1024  # 10GB
        )
        
        # Create enterprise tenant
        enterprise_tenant = Tenant(
            id="tenant-002", 
            name="Enterprise Corp",
            domain="corp.enterprise.com",
            features=["email", "calendar", "meetings", "crm", "ai", "advanced_analytics"],
            max_users=1000,
            storage_quota=100 * 1024 * 1024 * 1024  # 100GB
        )
        
        self._tenants[test_tenant.id] = test_tenant
        self._tenants[enterprise_tenant.id] = enterprise_tenant
        
        # Create test users
        test_user = TenantUser(
            id="user-001",
            tenant_id="tenant-001",
            email="test@dhii.ai",
            name="Test User",
            username="testuser",
            roles=["admin", "user"],
            permissions=["read", "write", "delete", "admin"]
        )
        
        enterprise_user = TenantUser(
            id="user-002",
            tenant_id="tenant-002",
            email="admin@enterprise.com",
            name="Enterprise Admin",
            username="enterprise_admin",
            roles=["admin", "user"],
            permissions=["read", "write", "delete", "admin", "tenant_admin"]
        )
        
        self._tenant_users[test_tenant.id] = [test_user]
        self._tenant_users[enterprise_tenant.id] = [enterprise_user]
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        for tenant in self._tenants.values():
            if tenant.domain == domain:
                return tenant
        return None
    
    def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self._tenants.get(tenant_id)
    
    def get_user_by_email(self, email: str) -> Optional[TenantUser]:
        """Get user by email across all tenants"""
        for tenant_users in self._tenant_users.values():
            for user in tenant_users:
                if user.email == email:
                    return user
        return None
    
    def get_user_by_id(self, user_id: str, tenant_id: str) -> Optional[TenantUser]:
        """Get user by ID within specific tenant"""
        tenant_users = self._tenant_users.get(tenant_id, [])
        for user in tenant_users:
            if user.id == user_id:
                return user
        return None
    
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Get all users for a tenant"""
        return self._tenant_users.get(tenant_id, [])
    
    def create_user_session(self, user: TenantUser, session_data: Dict[str, Any]) -> str:
        """Create user session with tenant context"""
        session_id = f"{user.tenant_id}:{user.id}:{datetime.now().timestamp()}"
        
        session_info = {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "roles": user.roles,
            "permissions": user.permissions,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "session_data": session_data
        }
        
        self._user_sessions[session_id] = session_info
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[TenantContext]:
        """Validate session and return tenant context"""
        session_info = self._user_sessions.get(session_id)
        if not session_info:
            return None
        
        # Check if session is expired (24 hours)
        created_at = datetime.fromisoformat(session_info["created_at"])
        if (datetime.now() - created_at).total_seconds() > 86400:
            del self._user_sessions[session_id]
            return None
        
        # Get tenant and user
        tenant = self.get_tenant_by_id(session_info["tenant_id"])
        user = self.get_user_by_id(session_info["user_id"], session_info["tenant_id"])
        
        if not tenant or not user:
            return None
        
        # Update last activity
        session_info["last_activity"] = datetime.now().isoformat()
        
        return TenantContext(
            tenant=tenant,
            user=user,
            session_id=session_id
        )
    
    def check_user_permission(self, user: TenantUser, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in user.permissions
    
    def check_tenant_feature(self, tenant: Tenant, feature: str) -> bool:
        """Check if tenant has specific feature enabled"""
        return feature in tenant.features
    
    def enforce_tenant_isolation(self, tenant_id: str, resource_tenant_id: str) -> bool:
        """Enforce tenant isolation - ensure user can only access their tenant resources"""
        return tenant_id == resource_tenant_id
    
    def enforce_user_verse_boundary(self, user_id: str, resource_user_id: str, 
                                  permission_level: str = "own", 
                                  requesting_user_roles: List[str] = None) -> bool:
        """
        Enforce user-verse boundaries within tenant
        
        Args:
            user_id: The requesting user's ID
            resource_user_id: The resource owner's user ID
            permission_level: "own" (own data only), "team" (team data), "tenant" (all tenant data)
            requesting_user_roles: Optional list of requesting user's roles for permission checks
        
        Returns:
            True if access is allowed, False otherwise
        """
        # Super admin can access everything
        if permission_level == "super_admin":
            return True
            
        # User can always access their own data
        if user_id == resource_user_id:
            return True
            
        # Check permission levels
        if permission_level == "own":
            return False  # Can only access own data
        elif permission_level == "team":
            # Would need team membership lookup in real implementation
            return False  # For now, no team access
        elif permission_level == "tenant":
            # Check if user has tenant-wide permissions using provided roles
            if requesting_user_roles and "tenant_admin" in requesting_user_roles:
                return True
            return False
            
        return False
    
    def get_user_scoped_data(self, user_id: str, tenant_id: str, data_type: str,
                           requesting_user: TenantUser) -> Dict[str, Any]:
        """
        Get user-scoped data with proper boundary enforcement
        
        Args:
            user_id: Target user ID
            tenant_id: Tenant ID
            data_type: Type of data (emails, meetings, etc.)
            requesting_user: The user making the request
        
        Returns:
            Filtered data based on user-verse boundaries
        """
        # First enforce tenant isolation
        if not self.enforce_tenant_isolation(requesting_user.tenant_id, tenant_id):
            raise PermissionError("Cross-tenant access denied")
        
        # Determine permission level based on user roles
        permission_level = "own"
        if "tenant_admin" in requesting_user.roles:
            permission_level = "tenant"
        elif "team_lead" in requesting_user.roles:
            permission_level = "team"
        
        # Enforce user-verse boundaries
        if not self.enforce_user_verse_boundary(
            requesting_user.id, user_id, permission_level, requesting_user.roles
        ):
            raise PermissionError(f"Access denied: insufficient permissions for {data_type}")
        
        # Return user-scoped data (mock implementation)
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "data_type": data_type,
            "permission_level": permission_level,
            "can_access": True,
            "items": [],
            "count": 0
        }
    
    def create_user_verse_context(self, requesting_user: TenantUser, 
                                target_user_id: str) -> Dict[str, Any]:
        """
        Create a user-verse context for UI rendering
        
        Args:
            requesting_user: The user making the request
            target_user_id: The target user whose data is being accessed
        
        Returns:
            User-verse context with boundary information
        """
        # Determine permission level
        permission_level = "own"
        if "tenant_admin" in requesting_user.roles:
            permission_level = "tenant"
        elif "team_lead" in requesting_user.roles:
            permission_level = "team"
        
        # Check if access is allowed
        can_access = self.enforce_user_verse_boundary(
            requesting_user.id, target_user_id, permission_level, requesting_user.roles
        )
        
        return {
            "requesting_user_id": requesting_user.id,
            "target_user_id": target_user_id,
            "permission_level": permission_level,
            "can_access": can_access,
            "is_own_data": requesting_user.id == target_user_id,
            "is_tenant_admin": "tenant_admin" in requesting_user.roles,
            "boundary_enforced": True
        }
    
    def get_tenant_scoped_data(self, tenant_id: str, data_type: str) -> Dict[str, Any]:
        """Get tenant-scoped data (emails, meetings, etc.) - DEPRECATED: Use get_user_scoped_data instead"""
        # This method is deprecated in favor of user-scoped data access
        logger.warning("get_tenant_scoped_data is deprecated, use get_user_scoped_data for proper user-verse boundaries")
        return {
            "tenant_id": tenant_id,
            "data_type": data_type,
            "count": 0,
            "items": []
        }

# Global tenant manager instance
tenant_manager = TenantManager()

# FastAPI dependency for getting tenant context
async def get_tenant_context(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> TenantContext:
    """FastAPI dependency to get tenant context from JWT token"""
    from fastapi import HTTPException, status
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Decode JWT token to get session ID
        payload = jwt.decode(token, options={"verify_signature": False})
        session_id = payload.get("session_id")
        
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate session and get tenant context
        context = tenant_manager.validate_session(session_id)
        if not context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return context
        
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error validating tenant context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

# Mock tenant context for testing
async def get_mock_tenant_context() -> TenantContext:
    """Mock tenant context for testing purposes"""
    tenant = tenant_manager.get_tenant_by_id("tenant-001")
    user = tenant_manager.get_user_by_id("user-001", "tenant-001")
    
    return TenantContext(
        tenant=tenant,
        user=user,
        session_id="mock-session-123"
    )

# Permission checking dependency
class RequirePermission:
    """Dependency for checking specific permissions"""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    async def __call__(self, context: TenantContext = Depends(get_tenant_context)) -> TenantContext:
        if not tenant_manager.check_user_permission(context.user, self.permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {self.permission} required"
            )
        return context

# Feature checking dependency  
class RequireFeature:
    """Dependency for checking tenant features"""
    
    def __init__(self, feature: str):
        self.feature = feature
    
    async def __call__(self, context: TenantContext = Depends(get_tenant_context)) -> TenantContext:
        if not tenant_manager.check_tenant_feature(context.tenant, self.feature):
            raise HTTPException(
                status_code=403,
                detail=f"Feature not available: {self.feature}"
            )
        return context