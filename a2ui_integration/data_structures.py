"""
Data structures for A2UI integration
Implements adjacency list model for component graph with A2UI-compliant operations
"""

import uuid
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

class OperationType(Enum):
    """A2UI operation types"""
    INSERT = "insert"
    UPDATE = "update"
    REMOVE = "remove"

@dataclass
class A2UIOperation:
    """A2UI-compliant operation for component graph"""
    type: OperationType
    node_id: str
    component_type: str
    props: Dict[str, Any]
    parent_id: Optional[str] = None
    index: Optional[int] = None

class ComponentNode:
    """Node in the component graph"""
    def __init__(self, component_type: str, props: Dict[str, Any] = None, node_id: str = None):
        self.id = node_id or str(uuid.uuid4())
        self.type = component_type
        self.props = props or {}
        self.children: List[str] = []

class ComponentGraph:
    """Adjacency list representation of UI component structure with A2UI operations"""
    def __init__(self):
        self.nodes: Dict[str, ComponentNode] = {}
        self.root_id: Optional[str] = None
        self.operations: List[A2UIOperation] = []
        
    def add_node(self, component_type: str, props: Dict[str, Any] = None, node_id: str = None) -> str:
        """Add a node to the graph and return its ID"""
        node = ComponentNode(component_type, props, node_id)
        self.nodes[node.id] = node
        if not self.root_id:
            self.root_id = node.id
        
        # Record operation for A2UI compliance
        self.operations.append(A2UIOperation(
            type=OperationType.INSERT,
            node_id=node.id,
            component_type=component_type,
            props=node.props
        ))
        
        return node.id
        
    def add_child(self, parent_id: str, child_id: str, index: Optional[int] = None):
        """Add a child to a parent node"""
        if parent_id in self.nodes and child_id in self.nodes:
            if index is not None:
                self.nodes[parent_id].children.insert(index, child_id)
            else:
                self.nodes[parent_id].children.append(child_id)
        else:
            raise ValueError(f"Parent {parent_id} or child {child_id} node not found")

    def update_node(self, node_id: str, props: Dict[str, Any]):
        """Update node properties"""
        if node_id in self.nodes:
            self.nodes[node_id].props.update(props)
            
            # Record operation for A2UI compliance
            self.operations.append(A2UIOperation(
                type=OperationType.UPDATE,
                node_id=node_id,
                component_type=self.nodes[node_id].type,
                props=props
            ))
        else:
            raise ValueError(f"Node {node_id} not found")

    def remove_node(self, node_id: str):
        """Remove a node and its children"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # Record operation for A2UI compliance
            self.operations.append(A2UIOperation(
                type=OperationType.REMOVE,
                node_id=node_id,
                component_type=node.type,
                props=node.props
            ))
            
            # Remove from parent's children
            for parent in self.nodes.values():
                if node_id in parent.children:
                    parent.children.remove(node_id)
            
            # Remove children recursively
            for child_id in node.children:
                self.remove_node(child_id)
            
            # Remove the node itself
            del self.nodes[node_id]
            
            # Update root if necessary
            if self.root_id == node_id:
                self.root_id = next(iter(self.nodes.keys())) if self.nodes else None

    def set_root(self, node_id: str):
        """Set the root node explicitly"""
        if node_id in self.nodes:
            self.root_id = node_id
        else:
            raise ValueError(f"Node {node_id} not found")

    def get_operations(self) -> List[Dict[str, Any]]:
        """Get A2UI-compliant operations list"""
        return [
            {
                "type": op.type.value,
                "nodeId": op.node_id,
                "componentType": op.component_type,
                "props": op.props,
                "parentId": op.parent_id,
                "index": op.index
            }
            for op in self.operations
        ]

    def to_adjacency_list(self) -> Dict[str, Any]:
        """Convert graph to A2UI adjacency list format"""
        return {
            "nodes": {
                node_id: {
                    "id": node.id,
                    "type": node.type,
                    "props": node.props,
                    "children": node.children
                }
                for node_id, node in self.nodes.items()
            },
            "rootId": self.root_id,
            "operations": self.get_operations()
        }

    def to_json(self) -> Dict[str, Any]:
        """Convert graph to nested JSON structure (backward compatibility)"""
        if not self.root_id:
            return {}
        return self._resolve_node(self.root_id)
        
    def _resolve_node(self, node_id: str) -> Dict[str, Any]:
        """Resolve node to nested JSON (backward compatibility)"""
        from .a2ui_components_extended import A2UIComponents
        
        node = self.nodes.get(node_id)
        if not node:
            return {}
            
        # Resolve children first
        children_components = [self._resolve_node(child_id) for child_id in node.children]
        
        # Use component factory
        component_factory = A2UIComponents()
        method_name = f"create_{self._to_snake_case(node.type)}"
        
        if not hasattr(component_factory, method_name):
            # Fallback for unknown types
            component_dict = {node.type: node.props.copy()}
            if children_components:
                component_dict[node.type]["components"] = children_components
            return {"component": component_dict}
            
        method = getattr(component_factory, method_name)
        props = node.props.copy()
        
        # Inject children into appropriate property based on type
        if node.type in ["Layout", "Grid", "Container"]:
            props["components"] = children_components
        
        try:
            return method(**props)
        except TypeError as e:
            print(f"Error creating component {node.type}: {e}")
            return {"component": {node.type: props}}

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def clear_operations(self):
        """Clear recorded operations"""
        self.operations = []

    def create_operation(self, operation_type: OperationType, node_id: str, component_type: str, 
                        props: Dict[str, Any], parent_id: Optional[str] = None, 
                        index: Optional[int] = None) -> A2UIOperation:
        """Create a new A2UI operation"""
        return A2UIOperation(
            type=operation_type,
            node_id=node_id,
            component_type=component_type,
            props=props,
            parent_id=parent_id,
            index=index
        )