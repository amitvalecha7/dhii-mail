"""
A2UI Renderer Implementation
Handles the rendering of A2UI components using adjacency list operations
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .types import A2UIComponent, AdjacencyOperation, A2UIRenderer

logger = logging.getLogger(__name__)


class A2UIAdjacencyRenderer(A2UIRenderer):
    """Renderer that uses adjacency list operations for A2UI generation"""
    
    def __init__(self):
        self.components: Dict[str, A2UIComponent] = {}
        self.operations: List[AdjacencyOperation] = []
    
    def create_component(self, component_type: str, properties: Dict[str, Any]) -> A2UIComponent:
        """Create a new A2UI component"""
        component_id = f"{component_type}_{len(self.components)}"
        
        component = A2UIComponent(
            id=component_id,
            type=component_type,
            properties=properties,
            children=[],
            parent_id=None
        )
        
        self.components[component_id] = component
        return component
    
    def build_adjacency_list(self, components: List[A2UIComponent]) -> List[AdjacencyOperation]:
        """Build adjacency list operations from components"""
        operations = []
        
        for component in components:
            # Create operation for this component
            operation = AdjacencyOperation(
                operation="insert",
                node_id=component.id,
                node_type=component.type,
                parent_id=component.parent_id,
                properties=component.properties,
                position=None
            )
            operations.append(operation)
            
            # Process children recursively
            if component.children:
                child_operations = self.build_adjacency_list(component.children)
                operations.extend(child_operations)
        
        return operations
    
    def render_dashboard(self, context: Dict[str, Any]) -> List[AdjacencyOperation]:
        """Render dashboard using adjacency list operations"""
        operations = []
        
        # Create main dashboard container
        dashboard_id = "dashboard_main"
        dashboard_props = {
            "className": "dashboard-container",
            "style": {
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "16px",
                "padding": "16px"
            }
        }
        
        dashboard_op = AdjacencyOperation(
            operation="insert",
            node_id=dashboard_id,
            node_type="container",
            parent_id=None,
            properties=dashboard_props,
            position=0
        )
        operations.append(dashboard_op)
        
        # Add header section
        header_id = "dashboard_header"
        header_props = {
            "className": "dashboard-header",
            "style": {
                "gridColumn": "1 / -1",
                "padding": "16px",
                "backgroundColor": "#f8f9fa",
                "borderRadius": "8px"
            }
        }
        
        header_op = AdjacencyOperation(
            operation="insert",
            node_id=header_id,
            node_type="section",
            parent_id=dashboard_id,
            properties=header_props,
            position=0
        )
        operations.append(header_op)
        
        # Add title
        title_id = "dashboard_title"
        title_props = {
            "text": context.get("title", "Dashboard"),
            "level": 1,
            "style": {"margin": "0"}
        }
        
        title_op = AdjacencyOperation(
            operation="insert",
            node_id=title_id,
            node_type="heading",
            parent_id=header_id,
            properties=title_props,
            position=0
        )
        operations.append(title_op)
        
        # Add plugin cards if plugins are provided
        plugins = context.get("plugins", [])
        for i, plugin in enumerate(plugins):
            card_id = f"plugin_card_{plugin['id']}"
            card_props = {
                "className": "plugin-card",
                "style": {
                    "padding": "16px",
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "8px",
                    "backgroundColor": "#ffffff"
                }
            }
            
            card_op = AdjacencyOperation(
                operation="insert",
                node_id=card_id,
                node_type="card",
                parent_id=dashboard_id,
                properties=card_props,
                position=i + 1
            )
            operations.append(card_op)
            
            # Add plugin name
            name_id = f"plugin_name_{plugin['id']}"
            name_props = {
                "text": plugin.get("name", "Unknown Plugin"),
                "level": 3,
                "style": {"margin": "0 0 8px 0"}
            }
            
            name_op = AdjacencyOperation(
                operation="insert",
                node_id=name_id,
                node_type="heading",
                parent_id=card_id,
                properties=name_props,
                position=0
            )
            operations.append(name_op)
            
            # Add plugin description
            desc_id = f"plugin_desc_{plugin['id']}"
            desc_props = {
                "text": plugin.get("description", ""),
                "style": {"margin": "0 0 8px 0", "color": "#666"}
            }
            
            desc_op = AdjacencyOperation(
                operation="insert",
                node_id=desc_id,
                node_type="text",
                parent_id=card_id,
                properties=desc_props,
                position=1
            )
            operations.append(desc_op)
            
            # Add status badge
            status_id = f"plugin_status_{plugin['id']}"
            status_props = {
                "text": plugin.get("status", "unknown").upper(),
                "style": {
                    "display": "inline-block",
                    "padding": "4px 8px",
                    "borderRadius": "4px",
                    "fontSize": "12px",
                    "fontWeight": "bold",
                    "backgroundColor": self._get_status_color(plugin.get("status", "unknown")),
                    "color": "white"
                }
            }
            
            status_op = AdjacencyOperation(
                operation="insert",
                node_id=status_id,
                node_type="badge",
                parent_id=card_id,
                properties=status_props,
                position=2
            )
            operations.append(status_op)
        
        return operations
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status badge"""
        colors = {
            "enabled": "#28a745",
            "disabled": "#6c757d",
            "error": "#dc3545",
            "installed": "#17a2b8",
            "unknown": "#6c757d"
        }
        return colors.get(status.lower(), "#6c757d")
    
    def render_plugin_store(self, context: Dict[str, Any]) -> List[AdjacencyOperation]:
        """Render plugin store using adjacency list operations"""
        operations = []
        
        # Create main store container
        store_id = "plugin_store_main"
        store_props = {
            "className": "plugin-store-container",
            "style": {
                "maxWidth": "1200px",
                "margin": "0 auto",
                "padding": "16px"
            }
        }
        
        store_op = AdjacencyOperation(
            operation="insert",
            node_id=store_id,
            node_type="container",
            parent_id=None,
            properties=store_props,
            position=0
        )
        operations.append(store_op)
        
        # Add header
        header_id = "store_header"
        header_props = {
            "className": "store-header",
            "style": {
                "textAlign": "center",
                "marginBottom": "32px"
            }
        }
        
        header_op = AdjacencyOperation(
            operation="insert",
            node_id=header_id,
            node_type="section",
            parent_id=store_id,
            properties=header_props,
            position=0
        )
        operations.append(header_op)
        
        # Add store title
        title_id = "store_title"
        title_props = {
            "text": "Skill Store",
            "level": 1,
            "style": {"margin": "0 0 16px 0"}
        }
        
        title_op = AdjacencyOperation(
            operation="insert",
            node_id=title_id,
            node_type="heading",
            parent_id=header_id,
            properties=title_props,
            position=0
        )
        operations.append(title_op)
        
        # Add store description
        desc_id = "store_description"
        desc_props = {
            "text": "Discover and manage plugins to extend your dhii Mail experience",
            "style": {"fontSize": "18px", "color": "#666"}
        }
        
        desc_op = AdjacencyOperation(
            operation="insert",
            node_id=desc_id,
            node_type="text",
            parent_id=header_id,
            properties=desc_props,
            position=1
        )
        operations.append(desc_op)
        
        # Add plugin grid
        grid_id = "plugin_grid"
        grid_props = {
            "className": "plugin-grid",
            "style": {
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fill, minmax(300px, 1fr))",
                "gap": "16px"
            }
        }
        
        grid_op = AdjacencyOperation(
            operation="insert",
            node_id=grid_id,
            node_type="grid",
            parent_id=store_id,
            properties=grid_props,
            position=1
        )
        operations.append(grid_op)
        
        # Add plugin cards
        plugins = context.get("plugins", [])
        for i, plugin in enumerate(plugins):
            card_id = f"store_plugin_card_{plugin['id']}"
            card_props = {
                "className": "store-plugin-card",
                "style": {
                    "padding": "16px",
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "8px",
                    "backgroundColor": "#ffffff",
                    "transition": "transform 0.2s, box-shadow 0.2s"
                }
            }
            
            card_op = AdjacencyOperation(
                operation="insert",
                node_id=card_id,
                node_type="card",
                parent_id=grid_id,
                properties=card_props,
                position=i
            )
            operations.append(card_op)
            
            # Add plugin name
            name_id = f"store_plugin_name_{plugin['id']}"
            name_props = {
                "text": plugin.get("name", "Unknown Plugin"),
                "level": 3,
                "style": {"margin": "0 0 8px 0"}
            }
            
            name_op = AdjacencyOperation(
                operation="insert",
                node_id=name_id,
                node_type="heading",
                parent_id=card_id,
                properties=name_props,
                position=0
            )
            operations.append(name_op)
            
            # Add plugin description
            desc_id = f"store_plugin_desc_{plugin['id']}"
            desc_props = {
                "text": plugin.get("description", ""),
                "style": {"margin": "0 0 16px 0", "color": "#666", "fontSize": "14px"}
            }
            
            desc_op = AdjacencyOperation(
                operation="insert",
                node_id=desc_id,
                node_type="text",
                parent_id=card_id,
                properties=desc_props,
                position=1
            )
            operations.append(desc_op)
            
            # Add install button
            button_id = f"store_plugin_install_{plugin['id']}"
            button_props = {
                "text": "Install",
                "variant": "primary",
                "style": {"width": "100%"},
                "onClick": {
                    "action": "install_plugin",
                    "pluginId": plugin['id']
                }
            }
            
            button_op = AdjacencyOperation(
                operation="insert",
                node_id=button_id,
                node_type="button",
                parent_id=card_id,
                properties=button_props,
                position=2
            )
            operations.append(button_op)
        
        return operations
    
    def render_error(self, error_message: str) -> List[AdjacencyOperation]:
        """Render error state using adjacency list operations"""
        operations = []
        
        # Create error container
        error_id = "error_container"
        error_props = {
            "className": "error-container",
            "style": {
                "padding": "16px",
                "backgroundColor": "#f8d7da",
                "border": "1px solid #f5c6cb",
                "borderRadius": "4px",
                "color": "#721c24"
            }
        }
        
        error_op = AdjacencyOperation(
            operation="insert",
            node_id=error_id,
            node_type="container",
            parent_id=None,
            properties=error_props,
            position=0
        )
        operations.append(error_op)
        
        # Add error icon
        icon_id = "error_icon"
        icon_props = {
            "type": "error",
            "style": {"marginRight": "8px"}
        }
        
        icon_op = AdjacencyOperation(
            operation="insert",
            node_id=icon_id,
            node_type="icon",
            parent_id=error_id,
            properties=icon_props,
            position=0
        )
        operations.append(icon_op)
        
        # Add error message
        message_id = "error_message"
        message_props = {
            "text": error_message,
            "style": {"display": "inline"}
        }
        
        message_op = AdjacencyOperation(
            operation="insert",
            node_id=message_id,
            node_type="text",
            parent_id=error_id,
            properties=message_props,
            position=1
        )
        operations.append(message_op)
        
        return operations