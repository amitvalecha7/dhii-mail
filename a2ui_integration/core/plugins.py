"""
Plugin Base Classes for dhii Mail Kernel
Provides base implementations for different types of plugins
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import DomainModule, PluginConfig, PluginType, PluginStatus, Capability
from .shared_services import get_shared_services, EventType, Event

logger = logging.getLogger(__name__)


class BasePlugin(DomainModule):
    """Base plugin class that all plugins should inherit from"""
    
    def __init__(self, plugin_id: str, name: str, version: str, description: str, plugin_type: PluginType):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.description = description
        self.plugin_type = plugin_type
        self._capabilities: List[Capability] = []
        self._initialized = False
        self.shared_services = get_shared_services()
        
        # Register capabilities
        self._register_capabilities()
    
    @property
    def domain(self) -> str:
        """Return the domain name this plugin handles"""
        return self.plugin_type.value
    
    @property
    def capabilities(self) -> List[Capability]:
        """Return list of capabilities this plugin provides"""
        return self._capabilities
    
    def _register_capabilities(self):
        """Register plugin capabilities - override in subclasses"""
        pass
    
    def add_capability(self, capability: Capability):
        """Add a capability to this plugin"""
        self._capabilities.append(capability)
        logger.info(f"Added capability {capability.id} to plugin {self.plugin_id}")
    
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            logger.info(f"Initializing plugin {self.plugin_id}")
            await self._initialize_plugin()
            self._initialized = True
            
            # Publish initialization event
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_initialized_{self.plugin_id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_ENABLED,
                source=self.plugin_id,
                timestamp=datetime.now(),
                data={"plugin_id": self.plugin_id, "plugin_name": self.name}
            ))
            
            logger.info(f"Plugin {self.plugin_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize plugin {self.plugin_id}: {e}")
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_error_{self.plugin_id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_ERROR,
                source=self.plugin_id,
                timestamp=datetime.now(),
                data={"error": str(e), "error_type": type(e).__name__, "context": "initialization"}
            ))
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the plugin"""
        try:
            logger.info(f"Shutting down plugin {self.plugin_id}")
            await self._shutdown_plugin()
            self._initialized = False
            
            # Publish shutdown event
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_shutdown_{self.plugin_id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_DISABLED,
                source=self.plugin_id,
                timestamp=datetime.now(),
                data={"plugin_id": self.plugin_id, "plugin_name": self.name}
            ))
            
            logger.info(f"Plugin {self.plugin_id} shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to shutdown plugin {self.plugin_id}: {e}")
            return False
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific capability"""
        if not self._initialized:
            raise RuntimeError(f"Plugin {self.plugin_id} not initialized")
        
        # Find the capability
        capability = next((cap for cap in self._capabilities if cap.id == capability_id), None)
        if not capability:
            raise ValueError(f"Capability {capability_id} not found in plugin {self.plugin_id}")
        
        try:
            logger.info(f"Executing capability {capability_id} in plugin {self.plugin_id}")
            result = await self._execute_capability(capability_id, params)
            
            # Publish capability executed event
            await self.shared_services.event_bus.publish(Event(
                id=f"capability_executed_{capability_id}_{datetime.now().isoformat()}",
                type=EventType.CAPABILITY_EXECUTED,
                source=self.plugin_id,
                timestamp=datetime.now(),
                data={"capability_id": capability_id, "params": params, "result_size": len(str(result))}
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute capability {capability_id} in plugin {self.plugin_id}: {e}")
            await self.shared_services.event_bus.publish(Event(
                id=f"plugin_error_{self.plugin_id}_{datetime.now().isoformat()}",
                type=EventType.PLUGIN_ERROR,
                source=self.plugin_id,
                timestamp=datetime.now(),
                data={"capability_id": capability_id, "error": str(e), "error_type": type(e).__name__}
            ))
            raise
    
    # Abstract methods for subclasses
    async def _initialize_plugin(self):
        """Plugin-specific initialization - override in subclasses"""
        pass
    
    async def _shutdown_plugin(self):
        """Plugin-specific shutdown - override in subclasses"""
        pass
    
    @abstractmethod
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific capability - must be implemented by subclasses"""
        pass


class EmailPlugin(BasePlugin):
    """Email management plugin"""
    
    def __init__(self):
        super().__init__(
            plugin_id="email_manager",
            name="Email Manager",
            version="1.0.0",
            description="Manages email accounts, messages, and operations",
            plugin_type=PluginType.EMAIL
        )
    
    def _register_capabilities(self):
        """Register email-related capabilities"""
        capabilities = [
            Capability(
                id="email.get_inbox",
                domain="email",
                name="Get Inbox",
                description="Retrieve inbox messages",
                input_schema={"type": "object", "properties": {"account_id": {"type": "string"}}},
                output_schema={"type": "array", "items": {"type": "object"}},
                side_effects=["read"]
            ),
            Capability(
                id="email.send_message",
                domain="email",
                name="Send Message",
                description="Send an email message",
                input_schema={
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string"},
                        "to": {"type": "array", "items": {"type": "string"}},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["account_id", "to", "subject", "body"]
                },
                output_schema={"type": "object", "properties": {"message_id": {"type": "string"}}},
                side_effects=["write", "send"],
                requires_auth=True
            ),
            Capability(
                id="email.search_messages",
                domain="email",
                name="Search Messages",
                description="Search email messages",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "account_id": {"type": "string"},
                        "folder": {"type": "string", "default": "inbox"}
                    },
                    "required": ["query"]
                },
                output_schema={"type": "array", "items": {"type": "object"}},
                side_effects=["read"]
            )
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    async def _initialize_plugin(self):
        """Initialize email plugin"""
        # Initialize email-specific resources
        logger.info("Initializing email plugin resources")
        # This would set up SMTP/IMAP connections, etc.
        pass
    
    async def _shutdown_plugin(self):
        """Shutdown email plugin"""
        # Cleanup email resources
        logger.info("Shutting down email plugin resources")
        pass
    
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email capability"""
        if capability_id == "email.get_inbox":
            return await self._get_inbox(params)
        elif capability_id == "email.send_message":
            return await self._send_message(params)
        elif capability_id == "email.search_messages":
            return await self._search_messages(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _get_inbox(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inbox messages"""
        # Mock implementation - would integrate with existing email_manager
        return {
            "messages": [
                {"id": "1", "subject": "Welcome to dhii Mail", "from": "system@dhii.com", "date": datetime.now().isoformat()}
            ],
            "total": 1
        }
    
    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send email message"""
        # Mock implementation - would integrate with existing email_manager
        return {"message_id": f"msg_{datetime.now().timestamp()}", "status": "sent"}
    
    async def _search_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search email messages"""
        # Mock implementation - would integrate with existing email_manager
        return {"messages": [], "query": params.get("query", ""), "total": 0}


class CalendarPlugin(BasePlugin):
    """Calendar management plugin"""
    
    def __init__(self):
        super().__init__(
            plugin_id="calendar_manager",
            name="Calendar Manager",
            version="1.0.0",
            description="Manages calendar events and scheduling",
            plugin_type=PluginType.CALENDAR
        )
    
    def _register_capabilities(self):
        """Register calendar-related capabilities"""
        capabilities = [
            Capability(
                id="calendar.get_events",
                domain="calendar",
                name="Get Events",
                description="Retrieve calendar events",
                input_schema={
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "format": "date"},
                        "end_date": {"type": "string", "format": "date"},
                        "calendar_id": {"type": "string"}
                    }
                },
                output_schema={"type": "array", "items": {"type": "object"}},
                side_effects=["read"]
            ),
            Capability(
                id="calendar.create_event",
                domain="calendar",
                name="Create Event",
                description="Create a calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "start_time": {"type": "string", "format": "date-time"},
                        "end_time": {"type": "string", "format": "date-time"},
                        "calendar_id": {"type": "string"}
                    },
                    "required": ["title", "start_time", "end_time"]
                },
                output_schema={"type": "object", "properties": {"event_id": {"type": "string"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            Capability(
                id="calendar.search_events",
                domain="calendar",
                name="Search Events",
                description="Search calendar events",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "calendar_id": {"type": "string"}
                    },
                    "required": ["query"]
                },
                output_schema={"type": "array", "items": {"type": "object"}},
                side_effects=["read"]
            )
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    async def _initialize_plugin(self):
        """Initialize calendar plugin"""
        logger.info("Initializing calendar plugin resources")
        pass
    
    async def _shutdown_plugin(self):
        """Shutdown calendar plugin"""
        logger.info("Shutting down calendar plugin resources")
        pass
    
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar capability"""
        if capability_id == "calendar.get_events":
            return await self._get_events(params)
        elif capability_id == "calendar.create_event":
            return await self._create_event(params)
        elif capability_id == "calendar.search_events":
            return await self._search_events(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _get_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get calendar events"""
        return {
            "events": [
                {"id": "1", "title": "Team Meeting", "start_time": datetime.now().isoformat(), "end_time": datetime.now().isoformat()}
            ],
            "total": 1
        }
    
    async def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event"""
        return {"event_id": f"event_{datetime.now().timestamp()}", "status": "created"}
    
    async def _search_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search calendar events"""
        return {"events": [], "query": params.get("query", ""), "total": 0}


class VideoPlugin(BasePlugin):
    """Video meeting management plugin"""
    
    def __init__(self):
        super().__init__(
            plugin_id="video_manager",
            name="Video Manager",
            version="1.0.0",
            description="Manages video meetings and conferencing",
            plugin_type=PluginType.CUSTOM
        )
    
    def _register_capabilities(self):
        """Register video-related capabilities"""
        capabilities = [
            Capability(
                id="video.create_meeting",
                domain="video",
                name="Create Meeting",
                description="Create a video meeting",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "start_time": {"type": "string", "format": "date-time"},
                        "duration_minutes": {"type": "integer", "default": 60}
                    },
                    "required": ["title"]
                },
                output_schema={"type": "object", "properties": {"meeting_id": {"type": "string"}, "join_url": {"type": "string"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            Capability(
                id="video.get_meetings",
                domain="video",
                name="Get Meetings",
                description="Retrieve video meetings",
                input_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["scheduled", "active", "completed"]},
                        "start_date": {"type": "string", "format": "date"}
                    }
                },
                output_schema={"type": "array", "items": {"type": "object"}},
                side_effects=["read"]
            )
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    async def _initialize_plugin(self):
        """Initialize video plugin"""
        logger.info("Initializing video plugin resources")
        pass
    
    async def _shutdown_plugin(self):
        """Shutdown video plugin"""
        logger.info("Shutting down video plugin resources")
        pass
    
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute video capability"""
        if capability_id == "video.create_meeting":
            return await self._create_meeting(params)
        elif capability_id == "video.get_meetings":
            return await self._get_meetings(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _create_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create video meeting"""
        return {
            "meeting_id": f"meeting_{datetime.now().timestamp()}",
            "join_url": f"https://meet.example.com/{datetime.now().timestamp()}",
            "status": "scheduled"
        }
    
    async def _get_meetings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get video meetings"""
        return {"meetings": [], "total": 0}


class MarketingPlugin(BasePlugin):
    """Marketing campaign management plugin"""
    
    def __init__(self):
        super().__init__(
            plugin_id="marketing_manager",
            name="Marketing Manager",
            version="1.0.0",
            description="Manages marketing campaigns and analytics",
            plugin_type=PluginType.MARKETING
        )
    
    def _register_capabilities(self):
        """Register marketing-related capabilities"""
        capabilities = [
            Capability(
                id="marketing.create_campaign",
                domain="marketing",
                name="Create Campaign",
                description="Create a marketing campaign",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "type": {"type": "string", "enum": ["email", "social", "webinar"]},
                        "target_audience": {"type": "string"}
                    },
                    "required": ["name", "type"]
                },
                output_schema={"type": "object", "properties": {"campaign_id": {"type": "string"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            Capability(
                id="marketing.get_campaigns",
                domain="marketing",
                name="Get Campaigns",
                description="Retrieve marketing campaigns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["draft", "active", "paused", "completed"]},
                        "type": {"type": "string"}
                    }
                },
                output_schema={"type": "array", "items": {"type": "object"}},
                side_effects=["read"]
            ),
            Capability(
                id="marketing.get_analytics",
                domain="marketing",
                name="Get Analytics",
                description="Get marketing analytics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "metric_type": {"type": "string", "enum": ["engagement", "conversion", "reach"]}
                    }
                },
                output_schema={"type": "object", "properties": {"metrics": {"type": "object"}}},
                side_effects=["read"]
            )
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    async def _initialize_plugin(self):
        """Initialize marketing plugin"""
        logger.info("Initializing marketing plugin resources")
        pass
    
    async def _shutdown_plugin(self):
        """Shutdown marketing plugin"""
        logger.info("Shutting down marketing plugin resources")
        pass
    
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute marketing capability"""
        if capability_id == "marketing.create_campaign":
            return await self._create_campaign(params)
        elif capability_id == "marketing.get_campaigns":
            return await self._get_campaigns(params)
        elif capability_id == "marketing.get_analytics":
            return await self._get_analytics(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _create_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create marketing campaign"""
        return {
            "campaign_id": f"campaign_{datetime.now().timestamp()}",
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
    
    async def _get_campaigns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get marketing campaigns"""
        return {"campaigns": [], "total": 0}
    
    async def _get_analytics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get marketing analytics"""
        return {
            "metrics": {
                "engagement_rate": 0.0,
                "conversion_rate": 0.0,
                "reach": 0
            }
        }


# Plugin factory for easy instantiation
def create_plugin(plugin_type: PluginType) -> BasePlugin:
    """Factory function to create plugins by type"""
    if plugin_type == PluginType.EMAIL:
        return EmailPlugin()
    elif plugin_type == PluginType.CALENDAR:
        return CalendarPlugin()
    elif plugin_type == PluginType.MARKETING:
        return MarketingPlugin()
    elif plugin_type == PluginType.CUSTOM:
        return VideoPlugin()
    else:
        raise ValueError(f"Unknown plugin type: {plugin_type}")


# Export commonly used plugin classes
__all__ = [
    'BasePlugin',
    'EmailPlugin',
    'CalendarPlugin',
    'VideoPlugin',
    'MarketingPlugin',
    'create_plugin'
]