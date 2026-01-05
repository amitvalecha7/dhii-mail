"""
Data structures for A2UI integration
Implements adjacency list model for component graph
"""

import uuid
from typing import Dict, Any, List, Optional
from .a2ui_components_extended import A2UIComponents

class ComponentNode:
    """Node in the component graph"""
    def __init__(self, component_type: str, props: Dict[str, Any] = None, node_id: str = None):
        self.id = node_id or str(uuid.uuid4())
        self.type = component_type
        self.props = props or {}
        self.children: List[str] = []

class ComponentGraph:
    """Adjacency list representation of UI component structure"""
    def __init__(self):
        self.nodes: Dict[str, ComponentNode] = {}
        self.root_id: Optional[str] = None
        self.component_factory = A2UIComponents()
        
    def add_node(self, component_type: str, props: Dict[str, Any] = None, node_id: str = None) -> str:
        """Add a node to the graph and return its ID"""
        node = ComponentNode(component_type, props, node_id)
        self.nodes[node.id] = node
        if not self.root_id:
            self.root_id = node.id
        return node.id
        
    def add_child(self, parent_id: str, child_id: str):
        """Add a child to a parent node"""
        if parent_id in self.nodes and child_id in self.nodes:
            self.nodes[parent_id].children.append(child_id)
        else:
            raise ValueError(f"Parent {parent_id} or child {child_id} node not found")

    def set_root(self, node_id: str):
        """Set the root node explicitly"""
        if node_id in self.nodes:
            self.root_id = node_id
        else:
            raise ValueError(f"Node {node_id} not found")

    def to_json(self) -> Dict[str, Any]:
        """Convert graph to nested JSON structure"""
        if not self.root_id:
            return {}
        return self._resolve_node(self.root_id)
        
    def _resolve_node(self, node_id: str) -> Dict[str, Any]:
        node = self.nodes.get(node_id)
        if not node:
            return {}
            
        # Resolve children first
        children_components = [self._resolve_node(child_id) for child_id in node.children]
        
        # CamelCase to snake_case conversion for method name
        # e.g. "Layout" -> "create_layout", "ProgressBar" -> "create_progress_bar"
        # Simple heuristic: lowercase
        method_name = f"create_{self._to_snake_case(node.type)}"
        
        if not hasattr(self.component_factory, method_name):
            # Fallback for unknown types or if factory method doesn't exist
            # Construct a raw component dict
            component_dict = {node.type: node.props.copy()}
            if children_components:
                # If it has children but no factory method, assume 'components' or 'children' property?
                # Or just ignore? Let's add them to 'components' if generic container
                component_dict[node.type]["components"] = children_components
            return {"component": component_dict}
            
        method = getattr(self.component_factory, method_name)
        
        # Prepare props
        props = node.props.copy()
        
        # Inject children into appropriate property based on type
        if node.type == "Layout":
            props["components"] = children_components
        elif node.type == "Grid":
            props["components"] = children_components
        # Add other container types if needed
        
        try:
            return method(**props)
        except TypeError as e:
            # Handle argument mismatch
            print(f"Error creating component {node.type}: {e}")
            return {"component": {node.type: props}}

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
