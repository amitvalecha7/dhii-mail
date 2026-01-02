# A2UI Glass Theme Implementation for dhii Mail

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GlassThemeConfig:
    """Configuration for Apple-style glass morphism theme"""
    backdrop_blur: str = "20px"
    background_opacity: str = "0.25"
    border_opacity: str = "0.2" 
    border_width: str = "1px"
    shadow_blur: str = "40px"
    shadow_opacity: str = "0.1"
    highlight_opacity: str = "0.15"
    saturation_factor: str = "1.8"

class A2UIGlassThemeManager:
    """Manages Apple-style glass morphism theming for A2UI components"""
    
    def __init__(self):
        self.theme_config = GlassThemeConfig()
        self.glass_presets = self._initialize_glass_presets()
        
    def _initialize_glass_presets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize glass effect presets"""
        return {
            "standard": {
                "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.05) 100%)",
                "backdropFilter": "blur(20px)",
                "WebkitBackdropFilter": "blur(20px)",
                "border": "1px solid rgba(255, 255, 255, 0.3)",
                "borderRadius": "16px",
                "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.1)",
                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            },
            "elevated": {
                "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.2) 100%)",
                "backdropFilter": "blur(30px) saturate(180%)",
                "WebkitBackdropFilter": "blur(30px) saturate(180%)",
                "border": "1px solid rgba(255, 255, 255, 0.4)",
                "borderRadius": "20px",
                "boxShadow": "0 16px 48px rgba(0, 0, 0, 0.15)",
                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            },
            "subtle": {
                "background": "rgba(255, 255, 255, 0.1)",
                "backdropFilter": "blur(10px)",
                "WebkitBackdropFilter": "blur(10px)",
                "border": "1px solid rgba(255, 255, 255, 0.2)",
                "borderRadius": "12px",
                "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.05)",
                "transition": "all 0.2s ease-out"
            },
            "glass_button": {
                "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%)",
                "backdropFilter": "blur(20px)",
                "WebkitBackdropFilter": "blur(20px)",
                "border": "1px solid rgba(255, 255, 255, 0.3)",
                "borderRadius": "12px",
                "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.1)",
                "color": "rgba(17, 24, 39, 0.9)",
                "fontWeight": "500",
                "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                "hover": {
                    "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 100%)",
                    "boxShadow": "0 12px 40px rgba(0, 0, 0, 0.15)",
                    "transform": "translateY(-1px)",
                    "border": "1px solid rgba(255, 255, 255, 0.4)"
                },
                "active": {
                    "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.05) 100%)",
                    "transform": "translateY(0) scale(0.98)",
                    "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.1)"
                }
            },
            "glass_input": {
                "background": "rgba(255, 255, 255, 0.2)",
                "backdropFilter": "blur(10px)",
                "WebkitBackdropFilter": "blur(10px)",
                "border": "1px solid rgba(255, 255, 255, 0.3)",
                "borderRadius": "12px",
                "padding": "12px 16px",
                "fontSize": "16px",
                "color": "rgba(17, 24, 39, 0.9)",
                "transition": "all 0.2s ease-out",
                "focus": {
                    "background": "rgba(255, 255, 255, 0.3)",
                    "border": "1px solid rgba(59, 130, 246, 0.5)",
                    "boxShadow": "0 0 0 3px rgba(59, 130, 246, 0.1)",
                    "outline": "none"
                },
                "placeholder": {
                    "color": "rgba(107, 114, 128, 0.6)"
                }
            }
        }
    
    def apply_glass_effect(self, component: Dict[str, Any], effect_type: str = "standard", 
                          custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply glass morphism effect to A2UI component"""
        
        # Get base glass styles
        glass_styles = self.glass_presets.get(effect_type, self.glass_presets["standard"]).copy()
        
        # Apply custom configuration if provided
        if custom_config:
            glass_styles.update(custom_config)
        
        # Ensure component has properties
        if "properties" not in component:
            component["properties"] = {}
        
        # Add glass styles to component
        if "styles" not in component["properties"]:
            component["properties"]["styles"] = {}
        
        component["properties"]["styles"].update(glass_styles)
        component["properties"]["className"] = f"glass-{effect_type}"
        
        # Add glass theme identifier
        component["properties"]["glass_theme"] = "apple_glass"
        component["properties"]["effect_type"] = effect_type
        
        return component
    
    def create_glass_component(self, base_type: str, properties: Dict[str, Any], 
                               effect_type: str = "standard") -> Dict[str, Any]:
        """Create a new glass component from scratch"""
        component = {
            "type": base_type,
            "properties": properties.copy()
        }
        
        return self.apply_glass_effect(component, effect_type)
    
    def get_glass_css_classes(self) -> str:
        """Generate CSS classes for glass effects"""
        css = """
/* Apple Glass Theme CSS */
.glass-standard {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-elevated {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.2) 100%);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-subtle {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease-out;
}

.glass-button {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  color: rgba(17, 24, 39, 0.9);
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.glass-button:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 100%);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.glass-button:active {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.05) 100%);
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.glass-input {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 16px;
  color: rgba(17, 24, 39, 0.9);
  transition: all 0.2s ease-out;
  width: 100%;
  box-sizing: border-box;
}

.glass-input:focus {
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.glass-input::placeholder {
  color: rgba(107, 114, 128, 0.6);
}

/* Fallback for browsers that don't support backdrop-filter */
@supports not (backdrop-filter: blur(20px)) {
  .glass-standard,
  .glass-elevated,
  .glass-subtle,
  .glass-button,
  .glass-input {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.1);
  }
}

/* Dark mode glass effects */
@media (prefers-color-scheme: dark) {
  .glass-standard {
    background: linear-gradient(135deg, rgba(31, 41, 55, 0.25) 0%, rgba(17, 24, 39, 0.05) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .glass-elevated {
    background: linear-gradient(135deg, rgba(31, 41, 55, 0.4) 0%, rgba(17, 24, 39, 0.2) 100%);
    border: 1px solid rgba(255, 255, 255, 0.15);
  }
  
  .glass-button {
    background: linear-gradient(135deg, rgba(31, 41, 55, 0.4) 0%, rgba(17, 24, 39, 0.1) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(243, 244, 246, 0.9);
  }
  
  .glass-input {
    background: rgba(31, 41, 55, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(243, 244, 246, 0.9);
  }
}
"""
        return css
    
    def create_dhii_mail_glass_components(self) -> Dict[str, Any]:
        """Create dhii Mail specific glass components"""
        
        # Glass onboarding welcome card
        glass_welcome_card = self.create_glass_component(
            "container",
            {
                "title": "Welcome to dhii Mail",
                "description": "Experience secure, intelligent email with AI-powered features",
                "styles": {
                    "padding": "48px",
                    "maxWidth": "480px",
                    "margin": "0 auto",
                    "textAlign": "center"
                }
            },
            "elevated"
        )
        
        # Glass email input field
        glass_email_field = self.create_glass_component(
            "form_field",
            {
                "label": "Email Address",
                "placeholder": "you@example.com",
                "type": "email",
                "required": true,
                "styles": {
                    "marginBottom": "24px"
                }
            },
            "glass_input"
        )
        
        # Glass primary button
        glass_primary_button = self.create_glass_component(
            "button",
            {
                "label": "Get Started",
                "variant": "primary",
                "size": "large",
                "styles": {
                    "width": "100%",
                    "marginBottom": "16px"
                }
            },
            "glass_button"
        )
        
        # Glass security status card
        glass_security_card = self.create_glass_component(
            "security_status_card",
            {
                "overall_status": "secure",
                "security_score": 95,
                "two_factor_enabled": true,
                "encryption_status": "enabled",
                "recommendations": [],
                "styles": {
                    "padding": "24px",
                    "marginBottom": "24px"
                }
            },
            "standard"
        )
        
        return {
            "glass_welcome_card": glass_welcome_card,
            "glass_email_field": glass_email_field,
            "glass_primary_button": glass_primary_button,
            "glass_security_card": glass_security_card
        }

# Usage examples
if __name__ == "__main__":
    # Initialize glass theme manager
    glass_manager = A2UIGlassThemeManager()
    
    # Get CSS classes
    css_classes = glass_manager.get_glass_css_classes()
    print("/* Glass Theme CSS Generated */")
    
    # Create a glass button
    glass_button = glass_manager.create_glass_component(
        "button",
        {
            "label": "Continue",
            "onClick": "nextStep()"
        },
        "glass_button"
    )
    
    # Apply glass effect to existing component
    existing_component = {
        "type": "container",
        "properties": {
            "title": "Secure Email Setup"
        }
    }
    
    glass_container = glass_manager.apply_glass_effect(existing_component, "elevated")
    
    # Get dhii Mail specific glass components
    dhii_glass_components = glass_manager.create_dhii_mail_glass_components()
    
    print(f"Created {len(dhii_glass_components)} glass components for dhii Mail")
    print(f"CSS classes generated: {len(css_classes)} characters")