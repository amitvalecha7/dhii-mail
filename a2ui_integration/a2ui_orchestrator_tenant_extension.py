    # Tenant-Aware Methods for Multi-Tenant Isolation
    def set_tenant_context(self, tenant_context: Dict[str, Any]) -> None:
        """Set tenant context for multi-tenant operations"""
        self.tenant_context = tenant_context
        logger.info(f"Tenant context set: {tenant_context.get('tenant_id', 'unknown')}")
    
    def get_tenant_scoped_context(self) -> Dict[str, Any]:
        """Get tenant-scoped context for UI rendering"""
        if not self.tenant_context:
            return {}
        
        return {
            "tenant_id": self.tenant_context.get("tenant_id"),
            "tenant_name": self.tenant_context.get("tenant_name"),
            "user_roles": self.tenant_context.get("user_roles", []),
            "user_permissions": self.tenant_context.get("user_permissions", []),
            "tenant_features": self.tenant_context.get("tenant_features", []),
            "is_tenant_admin": "tenant_admin" in self.tenant_context.get("user_permissions", []),
            "can_access_advanced_features": "advanced_analytics" in self.tenant_context.get("tenant_features", [])
        }
    
    def render_tenant_dashboard(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render tenant-specific dashboard with proper isolation"""
        tenant_context = self.get_tenant_scoped_context()
        
        # Merge tenant context with user context
        merged_context = {**context, **tenant_context}
        
        # Filter UI components based on tenant features
        filtered_context = self._filter_components_by_tenant_features(merged_context)
        
        # Render dashboard with tenant-specific data
        return self.render_ui(UIState.DASHBOARD, filtered_context)
    
    def _filter_components_by_tenant_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Filter UI components based on tenant features and permissions"""
        tenant_features = context.get("tenant_features", [])
        user_permissions = context.get("user_permissions", [])
        
        # Base features available to all tenants
        base_features = ["email", "calendar", "basic_analytics"]
        
        # Advanced features requiring specific tenant capabilities
        advanced_features = ["ai", "advanced_analytics", "crm", "automation"]
        
        # Filter available features
        available_features = []
        
        # Always include base features
        for feature in base_features:
            if feature in tenant_features or feature == "email":  # Email is always available
                available_features.append(feature)
        
        # Include advanced features only if tenant has them
        for feature in advanced_features:
            if feature in tenant_features:
                available_features.append(feature)
        
        # Filter navigation items based on available features
        navigation_items = []
        if "email" in available_features:
            navigation_items.extend(["inbox", "compose", "sent"])
        if "calendar" in available_features:
            navigation_items.extend(["calendar", "meetings"])
        if "basic_analytics" in available_features or "advanced_analytics" in available_features:
            navigation_items.append("analytics")
        if "crm" in available_features:
            navigation_items.append("crm")
        
        # Create filtered context
        filtered_context = context.copy()
        filtered_context["available_features"] = available_features
        filtered_context["navigation_items"] = navigation_items
        filtered_context["is_limited_tenant"] = len(tenant_features) < len(base_features + advanced_features)
        
        return filtered_context
    
    def validate_tenant_access(self, required_permission: str = None, required_feature: str = None) -> bool:
        """Validate tenant access for specific permission or feature"""
        if not self.tenant_context:
            logger.warning("No tenant context available for access validation")
            return False
        
        # Check tenant feature availability
        if required_feature:
            tenant_features = self.tenant_context.get("tenant_features", [])
            if required_feature not in tenant_features:
                logger.warning(f"Tenant lacks required feature: {required_feature}")
                return False
        
        # Check user permission
        if required_permission:
            user_permissions = self.tenant_context.get("user_permissions", [])
            if required_permission not in user_permissions:
                logger.warning(f"User lacks required permission: {required_permission}")
                return False
        
        return True
    
    def get_tenant_specific_data(self, data_type: str) -> Dict[str, Any]:
        """Get tenant-specific data with proper isolation"""
        if not self.tenant_context:
            return {"error": "No tenant context available"}
        
        tenant_id = self.tenant_context.get("tenant_id")
        if not tenant_id:
            return {"error": "No tenant ID in context"}
        
        # Mock tenant-specific data (replace with actual database queries)
        tenant_data = {
            "emails": {
                "total": 0,
                "unread": 0,
                "sent_today": 0,
                "items": []
            },
            "meetings": {
                "total": 0,
                "today": 0,
                "this_week": 0,
                "upcoming": []
            },
            "tasks": {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "overdue": 0
            },
            "analytics": {
                "email_open_rate": 0,
                "meeting_attendance": 0,
                "task_completion_rate": 0
            }
        }
        
        # Add tenant isolation metadata
        tenant_data["tenant_info"] = {
            "tenant_id": tenant_id,
            "tenant_name": self.tenant_context.get("tenant_name", "Unknown"),
            "user_roles": self.tenant_context.get("user_roles", []),
            "features": self.tenant_context.get("tenant_features", [])
        }
        
        return tenant_data.get(data_type, {"error": "Unknown data type"})
    
    def create_tenant_isolated_response(self, ui_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create tenant-isolated response with proper scoping"""
        tenant_context = self.get_tenant_scoped_context()
        
        # Add tenant metadata to response
        response = {
            "ui": ui_data,
            "tenant_context": tenant_context,
            "isolation_level": "tenant",
            "timestamp": datetime.now().isoformat(),
            "session_info": {
                "tenant_id": tenant_context.get("tenant_id"),
                "user_roles": tenant_context.get("user_roles"),
                "permissions": tenant_context.get("user_permissions")
            }
        }
        
        # Add security headers for tenant isolation
        response["security"] = {
            "tenant_scoped": True,
            "data_isolation": "strict",
            "access_control": "role_based"
        }
        
        return response