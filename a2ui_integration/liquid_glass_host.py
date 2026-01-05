"""
Liquid Glass Component Host - Issue #83
Dynamic composition engine for Application Layer 3.0
Core: Dynamic Composition, Result Aggregation, Streaming UI
Architecture 3.0 Standard: Self-Healing UI & Skeleton Streaming
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class ComponentType(Enum):
    """Visual primitives for dynamic component mapping"""
    STATS_GRID = "stats_grid"
    DATA_LIST = "data_list"
    HERO_CARD = "hero_card"
    ACTION_BAR = "action_bar"
    FORM = "form"
    CHART = "chart"
    CALENDAR = "calendar"
    TABS = "tabs"
    MODAL = "modal"

@dataclass
class ComponentBoundary:
    """Self-healing boundary for isolated plugin execution"""
    component_id: str
    plugin_name: str
    fallback_component: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 2

class LiquidGlassHost:
    """
    Liquid Glass Component Host - The Body (Frontend Host)
    
    Core Responsibilities:
    1. Dynamic Composition: Arbitrary plugin dictionaries → Visual Primitives
    2. Streaming UI: Real-time updates via Server-Sent Events (SSE)
    3. Self-Healing: Isomorphic Error Boundaries for plugin failure resilience
    4. Skeleton Streaming: Optimistic rendering for <200ms latency hiding
    """
    
    def __init__(self):
        self.active_streams: Dict[str, AsyncGenerator] = {}
        self.component_registry: Dict[str, ComponentType] = {}
        self.error_boundaries: Dict[str, ComponentBoundary] = {}
        self.skeleton_templates = self._create_skeleton_templates()
    
    def _create_skeleton_templates(self) -> Dict[ComponentType, Dict[str, Any]]:
        """Create skeleton templates for optimistic rendering"""
        return {
            ComponentType.STATS_GRID: {
                "component": {"StatsGrid": {"loading": True, "skeleton": True, "columns": 3}}
            },
            ComponentType.DATA_LIST: {
                "component": {"DataList": {"loading": True, "skeleton": True, "items": 5}}
            },
            ComponentType.HERO_CARD: {
                "component": {"HeroCard": {"loading": True, "skeleton": True}}
            },
            ComponentType.ACTION_BAR: {
                "component": {"ActionBar": {"loading": True, "skeleton": True}}
            }
        }
    
    async def compose_ui(self, plugin_data: Dict[str, Any], intent_type: str) -> Dict[str, Any]:
        """
        Dynamic composition: Transform plugin dictionaries into visual primitives
        The UI "becomes" what the user needs (CRM, Inbox, Planner modes)
        """
        try:
            # Generative Schema Engine: Map arbitrary data to visual components
            component_mapping = await self._generate_schema_mapping(plugin_data, intent_type)
            
            # Create self-healing boundaries for each component
            composition = await self._create_composition_with_boundaries(component_mapping)
            
            return {
                "composition": composition,
                "metadata": {
                    "intent_type": intent_type,
                    "composed_at": datetime.now().isoformat(),
                    "component_count": len(composition)
                }
            }
            
        except Exception as e:
            logger.error(f"Composition failed: {e}")
            return self._create_fallback_composition(intent_type)
    
    async def _generate_schema_mapping(self, plugin_data: Dict[str, Any], intent_type: str) -> List[Dict[str, Any]]:
        """Generative Schema Engine: Dynamic component mapping"""
        components = []
        
        # Interpretive UI: The app becomes what the user needs
        if intent_type == "crm":
            components.extend(await self._map_crm_components(plugin_data))
        elif intent_type == "inbox":
            components.extend(await self._map_inbox_components(plugin_data))
        elif intent_type == "planner":
            components.extend(await self._map_planner_components(plugin_data))
        else:
            # Generic mapping for unknown intents
            components.extend(await self._map_generic_components(plugin_data))
        
        return components
    
    async def _map_crm_components(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map CRM data to visual primitives"""
        components = []
        
        # Stats Grid for KPIs
        if "stats" in data:
            components.append({
                "type": ComponentType.STATS_GRID,
                "data": data["stats"],
                "priority": "high"
            })
        
        # Data List for contacts/leads
        if "contacts" in data:
            components.append({
                "type": ComponentType.DATA_LIST,
                "data": data["contacts"],
                "priority": "medium"
            })
        
        # Action Bar for quick actions
        if "actions" in data:
            components.append({
                "type": ComponentType.ACTION_BAR,
                "data": data["actions"],
                "priority": "high"
            })
        
        return components
    
    async def _map_inbox_components(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map Inbox data to visual primitives"""
        components = []
        
        # Hero Card for important emails
        if "important_emails" in data:
            components.append({
                "type": ComponentType.HERO_CARD,
                "data": data["important_emails"],
                "priority": "high"
            })
        
        # Data List for email threads
        if "emails" in data:
            components.append({
                "type": ComponentType.DATA_LIST,
                "data": data["emails"],
                "priority": "medium"
            })
        
        return components
    
    async def _map_planner_components(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map Planner data to visual primitives"""
        components = []
        
        # Calendar for scheduling
        if "events" in data:
            components.append({
                "type": ComponentType.CALENDAR,
                "data": data["events"],
                "priority": "high"
            })
        
        # Stats Grid for productivity metrics
        if "metrics" in data:
            components.append({
                "type": ComponentType.STATS_GRID,
                "data": data["metrics"],
                "priority": "medium"
            })
        
        return components
    
    async def _map_generic_components(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generic mapping for unknown data structures"""
        components = []
        
        # Try to infer component types from data structure
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    # List data → Data List
                    components.append({
                        "type": ComponentType.DATA_LIST,
                        "data": value,
                        "priority": "medium",
                        "title": key
                    })
                elif isinstance(value, dict) and "value" in value:
                    # Metric data → Stats Grid
                    components.append({
                        "type": ComponentType.STATS_GRID,
                        "data": {key: value},
                        "priority": "low"
                    })
        
        return components
    
    async def _create_composition_with_boundaries(self, component_mapping: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create composition with self-healing error boundaries"""
        composition = []
        
        for i, comp_data in enumerate(component_mapping):
            comp_id = f"comp_{i}_{comp_data['type'].value}"
            
            # Create error boundary for this component
            boundary = ComponentBoundary(
                component_id=comp_id,
                plugin_name=comp_data.get("plugin", "unknown"),
                fallback_component=self.skeleton_templates.get(comp_data["type"])
            )
            self.error_boundaries[comp_id] = boundary
            
            try:
                # Render actual component within error boundary
                component = await self._render_component(comp_data)
                composition.append({
                    "id": comp_id,
                    "component": component,
                    "boundary": {
                        "has_boundary": True,
                        "retry_count": boundary.retry_count
                    }
                })
                
            except Exception as e:
                logger.warning(f"Component {comp_id} failed: {e}")
                
                # Self-healing: Use fallback component
                if boundary.fallback_component:
                    composition.append({
                        "id": comp_id,
                        "component": boundary.fallback_component,
                        "boundary": {
                            "has_boundary": True,
                            "error": str(e),
                            "retry_count": boundary.retry_count,
                            "fallback": True
                        }
                    })
                
                # Schedule retry if within limits
                if boundary.retry_count < boundary.max_retries:
                    boundary.retry_count += 1
                    asyncio.create_task(self._retry_component(comp_id, comp_data))
        
        return composition
    
    async def _render_component(self, comp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render individual component based on type and data"""
        comp_type = comp_data["type"]
        data = comp_data["data"]
        
        if comp_type == ComponentType.STATS_GRID:
            return self._render_stats_grid(data)
        elif comp_type == ComponentType.DATA_LIST:
            return self._render_data_list(data)
        elif comp_type == ComponentType.HERO_CARD:
            return self._render_hero_card(data)
        elif comp_type == ComponentType.ACTION_BAR:
            return self._render_action_bar(data)
        else:
            # Fallback for unknown component types
            return {
                "component": {
                    "Fallback": {
                        "message": f"Unknown component type: {comp_type}",
                        "data": data
                    }
                }
            }
    
    def _render_stats_grid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render stats grid component"""
        stats = []
        for key, value in data.items():
            stats.append({
                "label": key,
                "value": value.get("value", 0),
                "trend": value.get("trend", "neutral")
            })
        
        return {
            "component": {
                "StatsGrid": {
                    "stats": stats,
                    "columns": min(len(stats), 4),
                    "variant": "default"
                }
            }
        }
    
    def _render_data_list(self, data: List[Any]) -> Dict[str, Any]:
        """Render data list component"""
        items = []
        for item in data:
            if isinstance(item, dict):
                items.append({
                    "title": item.get("title", "Item"),
                    "description": item.get("description", ""),
                    "metadata": item.get("metadata", {})
                })
            else:
                items.append({"title": str(item)})
        
        return {
            "component": {
                "DataList": {
                    "items": items,
                    "selectable": True,
                    "searchable": True
                }
            }
        }
    
    def _render_hero_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render hero card component"""
        return {
            "component": {
                "HeroCard": {
                    "title": data.get("title", "Important"),
                    "subtitle": data.get("subtitle", ""),
                    "content": data.get("content", ""),
                    "actions": data.get("actions", []),
                    "variant": data.get("variant", "primary")
                }
            }
        }
    
    def _render_action_bar(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Render action bar component"""
        actions = []
        for action in data:
            actions.append({
                "label": action.get("label", "Action"),
                "action": action.get("action", "noop"),
                "variant": action.get("variant", "default")
            })
        
        return {
            "component": {
                "ActionBar": {
                    "actions": actions,
                    "position": "bottom",
                    "sticky": True
                }
            }
        }
    
    async def _retry_component(self, comp_id: str, comp_data: Dict[str, Any]):
        """Self-healing: Retry failed component execution"""
        await asyncio.sleep(1)  # Wait before retry
        
        boundary = self.error_boundaries.get(comp_id)
        if boundary and boundary.retry_count < boundary.max_retries:
            try:
                # Retry the component
                component = await self._render_component(comp_data)
                
                # Update the composition via streaming
                await self._stream_component_update(comp_id, component)
                
                logger.info(f"Component {comp_id} recovered after retry")
                
            except Exception as e:
                logger.error(f"Component {comp_id} retry failed: {e}")
    
    async def _stream_component_update(self, comp_id: str, component: Dict[str, Any]):
        """Stream component updates to connected clients"""
        # This would integrate with your WebSocket/SSE implementation
        update_event = {
            "type": "component_update",
            "component_id": comp_id,
            "component": component,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to all active streams
        for stream_id, stream in self.active_streams.items():
            try:
                await stream.asend(update_event)
            except Exception as e:
                logger.warning(f"Failed to stream to {stream_id}: {e}")
    
    def _create_fallback_composition(self, intent_type: str) -> Dict[str, Any]:
        """Create fallback composition when everything fails"""
        return {
            "composition": [
                {
                    "id": "fallback_1",
                    "component": {
                        "HeroCard": {
                            "title": "Temporary Glitch",
                            "subtitle": "We're having trouble loading your content",
                            "content": "Please try again in a moment. The system is working to recover.",
                            "variant": "warning"
                        }
                    },
                    "boundary": {"has_boundary": False}
                }
            ],
            "metadata": {
                "intent_type": intent_type,
                "composed_at": datetime.now().isoformat(),
                "fallback": True,
                "component_count": 1
            }
        }
    
    # Streaming Consumer Methods
    async def create_stream(self, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a new streaming session for real-time UI updates"""
        async def stream_generator():
            try:
                # Send initial connection event
                yield {
                    "type": "connected",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Keep stream alive
                while True:
                    await asyncio.sleep(30)  # Heartbeat
                    yield {
                        "type": "heartbeat",
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except asyncio.CancelledError:
                logger.info(f"Stream {session_id} closed")
            finally:
                if session_id in self.active_streams:
                    del self.active_streams[session_id]
        
        stream = stream_generator()
        self.active_streams[session_id] = stream
        return stream
    
    async def stream_composition_updates(self, composition: Dict[str, Any], session_id: str):
        """Stream composition updates as they become available"""
        # Send skeleton first (optimistic execution)
        skeleton = self._create_skeleton_composition(composition["metadata"]["intent_type"])
        await self._stream_event(session_id, {
            "type": "skeleton",
            "composition": skeleton,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send actual composition when ready
        await self._stream_event(session_id, {
            "type": "composition",
            "composition": composition,
            "timestamp": datetime.now().isoformat()
        })
    
    def _create_skeleton_composition(self, intent_type: str) -> Dict[str, Any]:
        """Create skeleton composition for optimistic rendering"""
        # Based on intent type, create appropriate skeleton
        if intent_type == "crm":
            components = [
                {"type": ComponentType.STATS_GRID, "skeleton": True},
                {"type": ComponentType.DATA_LIST, "skeleton": True},
                {"type": ComponentType.ACTION_BAR, "skeleton": True}
            ]
        elif intent_type == "inbox":
            components = [
                {"type": ComponentType.HERO_CARD, "skeleton": True},
                {"type": ComponentType.DATA_LIST, "skeleton": True}
            ]
        elif intent_type == "planner":
            components = [
                {"type": ComponentType.CALENDAR, "skeleton": True},
                {"type": ComponentType.STATS_GRID, "skeleton": True}
            ]
        else:
            components = [
                {"type": ComponentType.DATA_LIST, "skeleton": True}
            ]
        
        return {
            "composition": components,
            "metadata": {
                "intent_type": intent_type,
                "skeleton": True,
                "composed_at": datetime.now().isoformat()
            }
        }
    
    async def _stream_event(self, session_id: str, event: Dict[str, Any]):
        """Send event to specific streaming session"""
        if session_id in self.active_streams:
            try:
                await self.active_streams[session_id].asend(event)
            except Exception as e:
                logger.warning(f"Failed to send event to {session_id}: {e}")

# Example usage
def create_liquid_glass_host() -> LiquidGlassHost:
    """Factory function to create Liquid Glass Host instance"""
    return LiquidGlassHost()