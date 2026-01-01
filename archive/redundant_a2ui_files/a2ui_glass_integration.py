"""
A2UI Glass Theme Integration for dhii Mail
Integrates glass theme with existing A2UI components and FastAPI endpoints
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import os

# Import A2UI components
from a2ui_card_implementation import A2UICardRenderer, A2UICardFactory
from a2ui_glass_theme_implementation import A2UIGlassThemeManager
from security_manager import SecurityManager

app = FastAPI(title="dhii Mail A2UI API", version="1.0.0")

# Initialize managers
glass_theme_manager = A2UIGlassThemeManager()
card_renderer = A2UICardRenderer()
card_factory = A2UICardFactory()
security_manager = SecurityManager()

class A2UIThemeService:
    """Service for managing A2UI themes and components"""
    
    def __init__(self):
        self.current_theme = "apple_glass"
        self.theme_variants = {
            "light": "standard",
            "dark": "elevated", 
            "auto": "subtle"
        }
        self.user_preferences = {}
    
    def get_theme_for_user(self, user_id: str) -> str:
        """Get theme variant for user"""
        return self.user_preferences.get(user_id, "standard")
    
    def set_user_theme(self, user_id: str, theme_variant: str):
        """Set user theme preference"""
        if theme_variant in self.theme_variants:
            self.user_preferences[user_id] = theme_variant
        else:
            self.user_preferences[user_id] = "standard"

# Initialize theme service
theme_service = A2UIThemeService()

@app.get("/a2ui/theme/css")
async def get_glass_theme_css():
    """Get complete glass theme CSS"""
    css_content = glass_theme_manager.get_glass_css_classes()
    return JSONResponse(content={"css": css_content})

@app.get("/a2ui/cards/onboarding")
async def get_onboarding_cards():
    """Get complete onboarding card sequence with glass effects"""
    try:
        cards = card_renderer.render_onboarding_sequence()
        
        # Apply security sanitization
        sanitized_cards = []
        for card in cards:
            sanitized_card = security_manager.sanitize_a2ui_component_data(card)
            
            # Validate component properties
            is_valid, errors = security_manager.validate_a2ui_component_properties(
                card.get("type", "container"), 
                card.get("properties", {})
            )
            
            if is_valid:
                sanitized_cards.append(sanitized_card)
            else:
                # Log security validation errors
                print(f"Card validation errors: {errors}")
                # Still include card but with safe defaults
                sanitized_cards.append(sanitized_card)
        
        return JSONResponse(content={
            "cards": sanitized_cards,
            "total_cards": len(sanitized_cards),
            "theme": "apple_glass",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating onboarding cards: {str(e)}")

@app.get("/a2ui/cards/dashboard")
async def get_dashboard_cards():
    """Get dashboard cards with email summaries"""
    try:
        cards = card_renderer.render_dashboard_cards()
        
        # Apply security sanitization
        sanitized_cards = []
        for card in cards:
            sanitized_card = security_manager.sanitize_a2ui_component_data(card)
            sanitized_cards.append(sanitized_card)
        
        return JSONResponse(content={
            "cards": sanitized_cards,
            "total_cards": len(sanitized_cards),
            "theme": "apple_glass",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard cards: {str(e)}")

@app.post("/a2ui/cards/custom")
async def create_custom_card(card_request: Dict[str, Any]):
    """Create a custom card with glass effects"""
    try:
        card_type = card_request.get("card_type", "feature")
        properties = card_request.get("properties", {})
        glass_effect = card_request.get("glass_effect", "standard")
        
        # Create card based on type
        if card_type == "welcome":
            card = card_factory.create_welcome_card(
                title=properties.get("title", "Welcome"),
                subtitle=properties.get("subtitle", ""),
                description=properties.get("description", ""),
                primary_action=properties.get("primary_action", {"label": "Continue", "action": "next"}),
                secondary_action=properties.get("secondary_action"),
                glass_effect=glass_effect
            )
        elif card_type == "feature":
            card = card_factory.create_feature_card(
                icon=properties.get("icon", "⭐"),
                title=properties.get("title", "Feature"),
                description=properties.get("description", ""),
                features=properties.get("features", []),
                action=properties.get("action", {"label": "Continue", "action": "next"}),
                glass_effect=glass_effect
            )
        elif card_type == "progress":
            card = card_factory.create_progress_card(
                current_step=properties.get("current_step", 1),
                total_steps=properties.get("total_steps", 5),
                title=properties.get("title", "Progress"),
                description=properties.get("description", ""),
                progress_percentage=properties.get("progress_percentage", 0),
                glass_effect=glass_effect
            )
        elif card_type == "security":
            card = card_factory.create_security_status_card(
                overall_status=properties.get("overall_status", "secure"),
                security_score=properties.get("security_score", 100),
                two_factor_enabled=properties.get("two_factor_enabled", True),
                encryption_status=properties.get("encryption_status", "enabled"),
                recommendations=properties.get("recommendations", []),
                glass_effect=glass_effect
            )
        elif card_type == "email_summary":
            card = card_factory.create_email_summary_card(
                folder_name=properties.get("folder_name", "Inbox"),
                unread_count=properties.get("unread_count", 0),
                total_count=properties.get("total_count", 0),
                recent_senders=properties.get("recent_senders", []),
                glass_effect=glass_effect
            )
        else:
            # Generic container card
            card = {
                "type": "container",
                "properties": properties,
                "children": card_request.get("children", [])
            }
            card = glass_theme_manager.apply_glass_effect(card, glass_effect)
        
        # Apply security sanitization
        sanitized_card = security_manager.sanitize_a2ui_component_data(card)
        
        # Validate actions
        if "actions" in card_request:
            for action in card_request["actions"]:
                is_valid, errors = security_manager.validate_a2ui_action(
                    action.get("name", ""), 
                    action.get("parameters", {})
                )
                if not is_valid:
                    print(f"Action validation errors: {errors}")
        
        return JSONResponse(content={
            "card": sanitized_card,
            "card_type": card_type,
            "glass_effect": glass_effect,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating custom card: {str(e)}")

@app.post("/a2ui/actions/validate")
async def validate_a2ui_action(action_request: Dict[str, Any]):
    """Validate A2UI actions for security"""
    try:
        action_name = action_request.get("action_name", "")
        action_params = action_request.get("action_params", {})
        
        # Validate action
        is_valid, errors = security_manager.validate_a2ui_action(action_name, action_params)
        
        # Log security event
        security_manager.log_security_event(
            event_type="a2ui_action_validation",
            ip_address="127.0.0.1",  # Would come from request
            user_email=action_request.get("user_email"),
            user_agent="A2UI Client",
            details={
                "action_name": action_name,
                "is_valid": is_valid,
                "errors": errors
            },
            severity="warning" if not is_valid else "info"
        )
        
        return JSONResponse(content={
            "is_valid": is_valid,
            "errors": errors,
            "action_name": action_name,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating action: {str(e)}")

@app.get("/a2ui/components/surface/{surface_id}")
async def get_surface_components(surface_id: str):
    """Get all components for a specific surface with glass theme"""
    try:
        # Define surfaces and their components
        surfaces = {
            "onboarding_welcome": card_renderer.render_onboarding_sequence()[0],
            "onboarding_features": card_renderer.render_onboarding_sequence()[1:3],
            "onboarding_security": card_renderer.render_onboarding_sequence()[3],
            "onboarding_progress": card_renderer.render_onboarding_sequence()[4],
            "dashboard_summary": card_renderer.render_dashboard_cards()
        }
        
        if surface_id not in surfaces:
            raise HTTPException(status_code=404, detail=f"Surface '{surface_id}' not found")
        
        components = surfaces[surface_id]
        
        # Apply glass theme based on surface type
        if "onboarding" in surface_id:
            glass_effect = "elevated" if "welcome" in surface_id else "standard"
        else:
            glass_effect = "subtle"
        
        # Apply theme to components
        if isinstance(components, list):
            themed_components = []
            for component in components:
                themed_component = glass_theme_manager.apply_glass_effect(component, glass_effect)
                themed_components.append(themed_component)
            components = themed_components
        else:
            components = glass_theme_manager.apply_glass_effect(components, glass_effect)
        
        return JSONResponse(content={
            "surface_id": surface_id,
            "components": components,
            "glass_effect": glass_effect,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting surface components: {str(e)}")

@app.get("/a2ui/health")
async def get_a2ui_health():
    """Health check for A2UI system"""
    try:
        # Test card generation
        test_card = card_factory.create_welcome_card(
            title="Health Check",
            subtitle="System Operational",
            description="A2UI system is running smoothly",
            primary_action={"label": "OK", "action": "health_ok"},
            glass_effect="subtle"
        )
        
        # Test security validation
        is_valid, errors = security_manager.validate_a2ui_component_properties(
            "container", test_card.get("properties", {})
        )
        
        return JSONResponse(content={
            "status": "healthy",
            "card_generation": "operational",
            "security_validation": "operational" if is_valid else "degraded",
            "validation_errors": errors if errors else [],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Static CSS endpoint for glass theme
@app.get("/a2ui/static/glass-theme.css")
async def get_glass_theme_css_file():
    """Serve glass theme CSS as a file"""
    from fastapi.responses import PlainTextResponse
    
    css_content = glass_theme_manager.get_glass_css_classes()
    return PlainTextResponse(content=css_content, media_type="text/css")

# Demo HTML endpoint
@app.get("/a2ui/demo")
async def get_glass_theme_demo():
    """Serve the glass theme demo HTML file"""
    demo_file_path = os.path.join(os.path.dirname(__file__), "a2ui_glass_demo.html")
    if os.path.exists(demo_file_path):
        return FileResponse(demo_file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Demo file not found")

# WebSocket endpoint for real-time theme updates (placeholder)
@app.websocket("/a2ui/ws/theme")
async def websocket_theme_endpoint(websocket):
    """WebSocket endpoint for real-time theme updates"""
    await websocket.accept()
    try:
        while True:
            # Wait for theme change requests
            data = await websocket.receive_text()
            theme_request = json.loads(data)
            
            # Process theme change
            user_id = theme_request.get("user_id")
            new_theme = theme_request.get("theme_variant")
            
            if user_id and new_theme:
                theme_service.set_user_theme(user_id, new_theme)
                
                # Send confirmation
                await websocket.send_text(json.dumps({
                    "type": "theme_updated",
                    "user_id": user_id,
                    "theme_variant": new_theme,
                    "timestamp": datetime.now().isoformat()
                }))
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    
    print("🍎 Starting dhii Mail A2UI Glass Theme Server")
    print("Available endpoints:")
    print("  - GET  /a2ui/theme/css")
    print("  - GET  /a2ui/cards/onboarding") 
    print("  - GET  /a2ui/cards/dashboard")
    print("  - POST /a2ui/cards/custom")
    print("  - GET  /a2ui/static/glass-theme.css")
    print("  - GET  /a2ui/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8006)