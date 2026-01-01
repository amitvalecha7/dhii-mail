"""
A2UI Glass Card Implementation for dhii Mail
Complete implementation of Apple-style glass morphism cards with theming
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import the glass theme manager
from a2ui_glass_theme_implementation import A2UIGlassThemeManager

@dataclass
class CardData:
    """Data model for card content"""
    title: str
    description: str
    icon: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: Optional[datetime] = None

class A2UICardFactory:
    """Factory for creating A2UI glass cards"""
    
    def __init__(self):
        self.glass_manager = A2UIGlassThemeManager()
        self.card_templates = self._initialize_card_templates()
    
    def _initialize_card_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize card templates with glass effects"""
        return {
            "welcome_card": {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "large",
                    "alignment": "center",
                    "padding": "48px",
                    "maxWidth": "520px",
                    "margin": "0 auto",
                    "textAlign": "center"
                }
            },
            "feature_card": {
                "type": "container", 
                "properties": {
                    "orientation": "vertical",
                    "spacing": "medium",
                    "alignment": "start",
                    "padding": "32px",
                    "minHeight": "200px"
                }
            },
            "progress_card": {
                "type": "container",
                "properties": {
                    "orientation": "vertical", 
                    "spacing": "small",
                    "alignment": "start",
                    "padding": "24px",
                    "minHeight": "120px"
                }
            },
            "security_card": {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "medium", 
                    "alignment": "start",
                    "padding": "32px",
                    "border": True
                }
            },
            "email_summary_card": {
                "type": "container",
                "properties": {
                    "orientation": "horizontal",
                    "spacing": "medium",
                    "alignment": "center",
                    "padding": "24px",
                    "minHeight": "80px"
                }
            }
        }
    
    def create_welcome_card(self, title: str, subtitle: str, description: str, 
                          primary_action: Dict[str, Any], secondary_action: Optional[Dict[str, Any]] = None,
                          glass_effect: str = "elevated") -> Dict[str, Any]:
        """Create a welcome card with glass effect"""
        
        # Base card structure
        card = self.card_templates["welcome_card"].copy()
        
        # Add glass effect
        card = self.glass_manager.apply_glass_effect(card, glass_effect)
        
        # Build card content
        card["children"] = [
            {
                "type": "image",
                "properties": {
                    "src": "/static/dhii-logo-glass.svg",
                    "alt": "dhii Mail Logo",
                    "width": 80,
                    "height": 80,
                    "border_radius": "circle",
                    "styles": {
                        "marginBottom": "24px",
                        "filter": "drop-shadow(0 4px 8px rgba(0,0,0,0.1))"
                    }
                }
            },
            {
                "type": "text",
                "properties": {
                    "content": title,
                    "variant": "heading1",
                    "size": "large",
                    "weight": "bold",
                    "color": "#111827",
                    "styles": {
                        "marginBottom": "12px"
                    }
                }
            },
            {
                "type": "text",
                "properties": {
                    "content": subtitle,
                    "variant": "heading3", 
                    "size": "medium",
                    "color": "#3B82F6",
                    "styles": {
                        "marginBottom": "16px"
                    }
                }
            },
            {
                "type": "text",
                "properties": {
                    "content": description,
                    "variant": "body",
                    "size": "medium",
                    "color": "#6B7280",
                    "align": "center",
                    "styles": {
                        "marginBottom": "32px",
                        "lineHeight": "1.6"
                    }
                }
            },
            {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "small",
                    "alignment": "center",
                    "styles": {
                        "width": "100%"
                    }
                },
                "children": [
                    self._create_glass_button(primary_action, "primary"),
                    secondary_action and self._create_glass_button(secondary_action, "text") or None
                ]
            }
        ]
        
        # Filter out None children
        card["children"] = [child for child in card["children"] if child is not None]
        
        return card
    
    def create_feature_card(self, icon: str, title: str, description: str, 
                          features: List[str], action: Dict[str, Any],
                          glass_effect: str = "standard") -> Dict[str, Any]:
        """Create a feature showcase card"""
        
        card = self.card_templates["feature_card"].copy()
        card = self.glass_manager.apply_glass_effect(card, glass_effect)
        
        card["children"] = [
            {
                "type": "container",
                "properties": {
                    "orientation": "horizontal",
                    "spacing": "medium",
                    "alignment": "center",
                    "styles": {
                        "marginBottom": "16px"
                    }
                },
                "children": [
                    {
                        "type": "container",
                        "properties": {
                            "styles": {
                                "background": "linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)",
                                "borderRadius": "16px",
                                "padding": "16px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "boxShadow": "0 4px 12px rgba(59, 130, 246, 0.3)"
                            }
                        },
                        "children": [
                            {
                                "type": "text",
                                "properties": {
                                    "content": icon,
                                    "variant": "body",
                                    "size": "large",
                                    "color": "#FFFFFF",
                                    "styles": {
                                        "fontSize": "24px"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "properties": {
                            "content": title,
                            "variant": "heading2",
                            "size": "large",
                            "weight": "bold",
                            "color": "#111827"
                        }
                    }
                ]
            },
            {
                "type": "text",
                "properties": {
                    "content": description,
                    "variant": "body",
                    "size": "medium",
                    "color": "#6B7280",
                    "styles": {
                        "marginBottom": "20px",
                        "lineHeight": "1.5"
                    }
                }
            },
            {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "small",
                    "alignment": "start",
                    "styles": {
                        "marginBottom": "24px"
                    }
                },
                "children": [
                    {
                        "type": "container",
                        "properties": {
                            "orientation": "horizontal",
                            "spacing": "small",
                            "alignment": "center"
                        },
                        "children": [
                            {
                                "type": "text",
                                "properties": {
                                    "content": "✓",
                                    "color": "#10B981",
                                    "weight": "bold"
                                }
                            },
                            {
                                "type": "text",
                                "properties": {
                                    "content": feature,
                                    "variant": "body",
                                    "size": "small",
                                    "color": "#374151"
                                }
                            }
                        ]
                    } for feature in features
                ]
            },
            self._create_glass_button(action, "secondary")
        ]
        
        return card
    
    def create_progress_card(self, current_step: int, total_steps: int, title: str,
                           description: str, progress_percentage: float,
                           glass_effect: str = "subtle") -> Dict[str, Any]:
        """Create a progress indicator card"""
        
        card = self.card_templates["progress_card"].copy()
        card = self.glass_manager.apply_glass_effect(card, glass_effect)
        
        card["children"] = [
            {
                "type": "container",
                "properties": {
                    "orientation": "horizontal",
                    "spacing": "medium",
                    "alignment": "center",
                    "styles": {
                        "marginBottom": "12px"
                    }
                },
                "children": [
                    {
                        "type": "container",
                        "properties": {
                            "styles": {
                                "background": f"conic-gradient(from 0deg, #3B82F6 0deg, #3B82F6 {progress_percentage * 3.6}deg, #E5E7EB {progress_percentage * 3.6}deg, #E5E7EB 360deg)",
                                "borderRadius": "50%",
                                "width": "48px",
                                "height": "48px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "position": "relative"
                            }
                        },
                        "children": [
                            {
                                "type": "container",
                                "properties": {
                                    "styles": {
                                        "background": "#FFFFFF",
                                        "borderRadius": "50%",
                                        "width": "36px",
                                        "height": "36px",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center"
                                    }
                                },
                                "children": [
                                    {
                                        "type": "text",
                                        "properties": {
                                            "content": f"{progress_percentage:.0f}%",
                                            "variant": "body",
                                            "size": "small",
                                            "weight": "bold",
                                            "color": "#3B82F6"
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "container",
                        "properties": {
                            "orientation": "vertical",
                            "spacing": "small",
                            "alignment": "start"
                        },
                        "children": [
                            {
                                "type": "text",
                                "properties": {
                                    "content": title,
                                    "variant": "heading3",
                                    "size": "medium",
                                    "weight": "bold",
                                    "color": "#111827"
                                }
                            },
                            {
                                "type": "text",
                                "properties": {
                                    "content": f"Step {current_step} of {total_steps}",
                                    "variant": "body",
                                    "size": "small",
                                    "color": "#6B7280"
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "type": "text",
                "properties": {
                    "content": description,
                    "variant": "body",
                    "size": "small",
                    "color": "#6B7280",
                    "styles": {
                        "lineHeight": "1.4"
                    }
                }
            },
            {
                "type": "container",
                "properties": {
                    "orientation": "horizontal",
                    "spacing": "small",
                    "alignment": "center",
                    "styles": {
                        "marginTop": "12px",
                        "height": "4px",
                        "background": "#E5E7EB",
                        "borderRadius": "2px",
                        "overflow": "hidden"
                    }
                },
                "children": [
                    {
                        "type": "container",
                        "properties": {
                            "styles": {
                                "width": f"{progress_percentage}%",
                                "height": "100%",
                                "background": "linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%)",
                                "borderRadius": "2px",
                                "transition": "width 0.5s ease-out"
                            }
                        }
                    }
                ]
            }
        ]
        
        return card
    
    def create_security_status_card(self, overall_status: str, security_score: int,
                                  two_factor_enabled: bool, encryption_status: str,
                                  recommendations: List[str], glass_effect: str = "standard") -> Dict[str, Any]:
        """Create a security status card with glass effect"""
        
        card = self.card_templates["security_card"].copy()
        card = self.glass_manager.apply_glass_effect(card, glass_effect)
        
        # Determine status color and icon
        status_config = {
            "secure": {"color": "#10B981", "icon": "🛡️", "text": "Secure"},
            "warning": {"color": "#F59E0B", "icon": "⚠️", "text": "Attention Needed"},
            "critical": {"color": "#EF4444", "icon": "🚨", "text": "Critical"}
        }
        
        status_info = status_config.get(overall_status, status_config["warning"])
        
        card["children"] = [
            {
                "type": "container",
                "properties": {
                    "orientation": "horizontal",
                    "spacing": "medium",
                    "alignment": "center",
                    "styles": {
                        "marginBottom": "20px"
                    }
                },
                "children": [
                    {
                        "type": "container",
                        "properties": {
                            "styles": {
                                "background": f"linear-gradient(135deg, {status_info['color']} 0%, {status_info['color']}80 100%)",
                                "borderRadius": "50%",
                                "width": "56px",
                                "height": "56px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "boxShadow": f"0 4px 12px {status_info['color']}30"
                            }
                        },
                        "children": [
                            {
                                "type": "text",
                                "properties": {
                                    "content": status_info["icon"],
                                    "variant": "body",
                                    "size": "large",
                                    "color": "#FFFFFF",
                                    "styles": {
                                        "fontSize": "24px"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "type": "container",
                        "properties": {
                            "orientation": "vertical",
                            "spacing": "small",
                            "alignment": "start"
                        },
                        "children": [
                            {
                                "type": "text",
                                "properties": {
                                    "content": "Security Status",
                                    "variant": "heading2",
                                    "size": "large",
                                    "weight": "bold",
                                    "color": "#111827"
                                }
                            },
                            {
                                "type": "container",
                                "properties": {
                                    "orientation": "horizontal",
                                    "spacing": "small",
                                    "alignment": "center"
                                },
                                "children": [
                                    {
                                        "type": "text",
                                        "properties": {
                                            "content": status_info["text"],
                                            "variant": "body",
                                            "size": "medium",
                                            "weight": "bold",
                                            "color": status_info["color"]
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "properties": {
                                            "content": f"• {security_score}/100",
                                            "variant": "body",
                                            "size": "medium",
                                            "color": "#6B7280",
                                            "weight": "bold"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "medium",
                    "alignment": "start"
                },
                "children": [
                    self._create_security_item("Two-Factor Authentication", 
                                             "Enabled" if two_factor_enabled else "Not Enabled",
                                             "#10B981" if two_factor_enabled else "#EF4444"),
                    self._create_security_item("Email Encryption", 
                                             encryption_status.capitalize(),
                                             "#10B981" if encryption_status == "enabled" else "#F59E0B")
                ]
            }
        ]
        
        if recommendations:
            card["children"].append({
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "small",
                    "alignment": "start",
                    "styles": {
                        "marginTop": "16px",
                        "paddingTop": "16px",
                        "borderTop": "1px solid rgba(0, 0, 0, 0.1)"
                    }
                },
                "children": [
                    {
                        "type": "text",
                        "properties": {
                            "content": "Recommendations",
                            "variant": "heading3",
                            "size": "small",
                            "weight": "bold",
                            "color": "#374151",
                            "styles": {
                                "marginBottom": "8px"
                            }
                        }
                    }
                ] + [
                    {
                        "type": "text",
                        "properties": {
                            "content": f"• {rec}",
                            "variant": "body",
                            "size": "small",
                            "color": "#6B7280"
                        }
                    } for rec in recommendations
                ]
            })
        
        return card
    
    def create_email_summary_card(self, folder_name: str, unread_count: int, 
                                total_count: int, recent_senders: List[str],
                                glass_effect: str = "subtle") -> Dict[str, Any]:
        """Create an email summary card"""
        
        card = self.card_templates["email_summary_card"].copy()
        card = self.glass_manager.apply_glass_effect(card, glass_effect)
        
        card["children"] = [
            {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "small",
                    "alignment": "center",
                    "styles": {
                        "width": "60px",
                        "height": "60px",
                        "background": "linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)",
                        "borderRadius": "12px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "boxShadow": "0 4px 12px rgba(59, 130, 246, 0.3)"
                    }
                },
                "children": [
                    {
                        "type": "text",
                        "properties": {
                            "content": "📧",
                            "variant": "body",
                            "size": "large",
                            "color": "#FFFFFF",
                            "styles": {
                                "fontSize": "24px"
                            }
                        }
                    }
                ]
            },
            {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "small",
                    "alignment": "start",
                    "styles": {
                        "flex": "1"
                    }
                },
                "children": [
                    {
                        "type": "container",
                        "properties": {
                            "orientation": "horizontal",
                            "spacing": "small",
                            "alignment": "center"
                        },
                        "children": [
                            {
                                "type": "text",
                                "properties": {
                                    "content": folder_name,
                                    "variant": "heading3",
                                    "size": "medium",
                                    "weight": "bold",
                                    "color": "#111827"
                                }
                            },
                            {
                                "type": "container",
                                "properties": {
                                    "styles": {
                                        "background": "#EF4444" if unread_count > 0 else "#10B981",
                                        "borderRadius": "10px",
                                        "padding": "4px 8px",
                                        "minWidth": "20px",
                                        "textAlign": "center"
                                    }
                                },
                                "children": [
                                    {
                                        "type": "text",
                                        "properties": {
                                            "content": str(unread_count),
                                            "variant": "body",
                                            "size": "small",
                                            "weight": "bold",
                                            "color": "#FFFFFF"
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "properties": {
                            "content": f"{total_count} total messages",
                            "variant": "body",
                            "size": "small",
                            "color": "#6B7280"
                        }
                    }
                ]
            },
            {
                "type": "container",
                "properties": {
                    "orientation": "vertical",
                    "spacing": "small",
                    "alignment": "end",
                    "styles": {
                        "textAlign": "right"
                    }
                },
                "children": [
                    {
                        "type": "text",
                        "properties": {
                            "content": "Recent",
                            "variant": "body",
                            "size": "small",
                            "color": "#6B7280"
                        }
                    }
                ] + [
                    {
                        "type": "text",
                        "properties": {
                            "content": sender,
                            "variant": "body",
                            "size": "small",
                            "color": "#374151",
                            "weight": "medium"
                        }
                    } for sender in recent_senders[:3]
                ]
            }
        ]
        
        return card
    
    def _create_glass_button(self, action: Dict[str, Any], variant: str = "primary") -> Dict[str, Any]:
        """Create a glass button with proper styling"""
        
        button = {
            "type": "button",
            "properties": {
                "label": action.get("label", "Click Me"),
                "variant": variant,
                "size": "large",
                "onClick": action.get("action", "handleClick"),
                "styles": {
                    "width": "100%",
                    "marginBottom": variant == "text" and "0" or "0"
                }
            },
            "actions": ["click"]
        }
        
        # Apply glass button styling
        if variant == "primary":
            button = self.glass_manager.apply_glass_effect(button, "glass_button")
        else:
            button["properties"]["styles"].update({
                "background": "transparent",
                "border": "1px solid rgba(59, 130, 246, 0.3)",
                "color": "#3B82F6"
            })
        
        return button
    
    def _create_security_item(self, label: str, value: str, color: str) -> Dict[str, Any]:
        """Create a security status item"""
        
        return {
            "type": "container",
            "properties": {
                "orientation": "horizontal",
                "spacing": "small",
                "alignment": "center",
                "styles": {
                    "padding": "12px",
                    "background": "rgba(255, 255, 255, 0.3)",
                    "borderRadius": "8px",
                    "border": "1px solid rgba(255, 255, 255, 0.2)"
                }
            },
            "children": [
                {
                    "type": "text",
                    "properties": {
                        "content": label,
                        "variant": "body",
                        "size": "small",
                        "color": "#374151",
                        "weight": "medium"
                    }
                },
                {
                    "type": "container",
                    "properties": {
                        "styles": {
                            "flex": "1"
                        }
                    }
                },
                {
                    "type": "text",
                    "properties": {
                        "content": value,
                        "variant": "body",
                        "size": "small",
                        "weight": "bold",
                        "color": color
                    }
                }
            ]
        }

class A2UICardRenderer:
    """Renders A2UI cards with glass effects"""
    
    def __init__(self):
        self.factory = A2UICardFactory()
    
    def render_onboarding_sequence(self) -> List[Dict[str, Any]]:
        """Render complete onboarding sequence with glass cards"""
        
        return [
            self.factory.create_welcome_card(
                title="Welcome to dhii Mail",
                subtitle="Secure • Intelligent • Beautiful",
                description="Experience email reimagined with AI-powered features, military-grade security, and stunning design that adapts to your workflow.",
                primary_action={
                    "label": "Get Started",
                    "action": "start_onboarding"
                },
                secondary_action={
                    "label": "Learn More",
                    "action": "show_features"
                },
                glass_effect="elevated"
            ),
            
            self.factory.create_feature_card(
                icon="🛡️",
                title="Bank-Level Security",
                description="Your emails are protected with end-to-end encryption, zero-knowledge architecture, and advanced threat detection.",
                features=[
                    "End-to-end encryption",
                    "Zero data tracking", 
                    "Advanced threat protection",
                    "Secure key management"
                ],
                action={
                    "label": "Continue",
                    "action": "next_step"
                },
                glass_effect="standard"
            ),
            
            self.factory.create_feature_card(
                icon="🤖",
                title="AI-Powered Intelligence",
                description="Smart categorization, predictive replies, and intelligent search that understands context and intent.",
                features=[
                    "Smart email categorization",
                    "Predictive text replies",
                    "Contextual search",
                    "Meeting scheduling AI"
                ],
                action={
                    "label": "Continue",
                    "action": "next_step"
                },
                glass_effect="standard"
            ),
            
            self.factory.create_security_status_card(
                overall_status="secure",
                security_score=95,
                two_factor_enabled=True,
                encryption_status="enabled",
                recommendations=[
                    "Enable biometric authentication",
                    "Set up recovery codes"
                ],
                glass_effect="standard"
            ),
            
            self.factory.create_progress_card(
                current_step=3,
                total_steps=5,
                title="Account Setup",
                description="Setting up your secure email environment",
                progress_percentage=60.0,
                glass_effect="subtle"
            )
        ]
    
    def render_dashboard_cards(self) -> List[Dict[str, Any]]:
        """Render dashboard cards with email summaries"""
        
        return [
            self.factory.create_email_summary_card(
                folder_name="Inbox",
                unread_count=12,
                total_count=156,
                recent_senders=[
                    "John Appleseed",
                    "Sarah Johnson", 
                    "Mike Chen"
                ],
                glass_effect="subtle"
            ),
            
            self.factory.create_email_summary_card(
                folder_name="Sent",
                unread_count=0,
                total_count=89,
                recent_senders=[
                    "You → Alex Smith",
                    "You → Team Lead",
                    "You → Support"
                ],
                glass_effect="subtle"
            ),
            
            self.factory.create_security_status_card(
                overall_status="secure",
                security_score=98,
                two_factor_enabled=True,
                encryption_status="enabled",
                recommendations=[],
                glass_effect="standard"
            )
        ]

# Usage example
if __name__ == "__main__":
    renderer = A2UICardRenderer()
    
    # Generate onboarding sequence
    onboarding_cards = renderer.render_onboarding_sequence()
    print(f"Generated {len(onboarding_cards)} onboarding cards")
    
    # Generate dashboard cards  
    dashboard_cards = renderer.render_dashboard_cards()
    print(f"Generated {len(dashboard_cards)} dashboard cards")
    
    # Example: Render a single welcome card
    factory = A2UICardFactory()
    welcome_card = factory.create_welcome_card(
        title="Welcome to dhii Mail",
        subtitle="Beautiful • Secure • Intelligent",
        description="Experience the future of email with stunning glass morphism design.",
        primary_action={"label": "Get Started", "action": "start_onboarding"},
        glass_effect="elevated"
    )
    
    print(f"Welcome card generated with {len(welcome_card.get('children', []))} child components")