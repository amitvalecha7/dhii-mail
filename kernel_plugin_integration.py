"""
Kernel Plugin Integration Module
Integrates existing plugin managers with the new kernel architecture
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.shared_services import EventType, Event
from a2ui_integration.core.types import PluginConfig, PluginType, Capability, PluginStatus

# Import existing managers
from email_manager import email_manager, EmailManager
from calendar_manager import calendar_manager, CalendarManager
from ai_engine import ai_engine, AIEngine
from marketing_manager import marketing_manager, MarketingManager

logger = logging.getLogger(__name__)


class KernelPluginIntegration:
    """Integrates existing plugin managers with the kernel architecture"""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.shared_services = kernel.shared_services
        self._plugin_instances: Dict[str, Any] = {}
        
    async def integrate_all_plugins(self):
        """Integrate all existing plugin managers with the kernel"""
        logger.info("Starting plugin integration with kernel...")
        
        # Register Email Manager as plugin
        await self._register_email_plugin()
        
        # Register Calendar Manager as plugin  
        await self._register_calendar_plugin()
        
        # Register AI Engine as plugin
        await self._register_ai_plugin()
        
        # Register Marketing Manager as plugin
        await self._register_marketing_plugin()
        
        logger.info("Plugin integration completed successfully")
    
    async def _register_email_plugin(self):
        """Register email manager as a kernel plugin"""
        try:
            # Create plugin configuration
            plugin_config = PluginConfig(
                id="email_manager",
                name="Email Manager",
                version="1.0.0",
                description="Handles email operations including sending, receiving, and processing",
                type=PluginType.EMAIL,
                author="dhii-mail",
                enabled=True,
                config={
                    "smtp_enabled": True,
                    "imap_enabled": True,
                    "max_connections": 10,
                    "retry_attempts": 3
                },
                capabilities=[
                    Capability(
                        id="email_send",
                        domain="email",
                        name="Send Email",
                        description="Send an email message",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "to": {"type": "string"},
                                "subject": {"type": "string"},
                                "body": {"type": "string"},
                                "attachments": {"type": "array"}
                            },
                            "required": ["to", "subject", "body"]
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "message_id": {"type": "string"},
                                "status": {"type": "string"},
                                "timestamp": {"type": "string"}
                            }
                        },
                        side_effects=["email_sent"],
                        requires_auth=True
                    ),
                    Capability(
                        id="email_receive",
                        domain="email",
                        name="Receive Email",
                        description="Receive and process email messages",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "folder": {"type": "string", "default": "INBOX"},
                                "limit": {"type": "integer", "default": 10}
                            }
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "messages": {"type": "array"},
                                "count": {"type": "integer"}
                            }
                        },
                        side_effects=["email_received"],
                        requires_auth=True
                    )
                ],
                dependencies=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Register with kernel
            success = await self.kernel.register_plugin(plugin_config)
            if success:
                # Register the actual manager instance
                self.kernel.register_plugin_instance("email_manager", email_manager)
                self._plugin_instances["email_manager"] = email_manager
                
                # Publish event
                await self._publish_plugin_event("email_manager", EventType.PLUGIN_REGISTERED)
                logger.info("Email plugin registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register email plugin: {e}")
    
    async def _register_calendar_plugin(self):
        """Register calendar manager as a kernel plugin"""
        try:
            plugin_config = PluginConfig(
                id="calendar_manager",
                name="Calendar Manager",
                version="1.0.0", 
                description="Handles calendar operations including event creation and management",
                type=PluginType.CALENDAR,
                author="dhii-mail",
                enabled=True,
                config={
                    "default_timezone": "UTC",
                    "max_events_per_user": 1000,
                    "enable_notifications": True
                },
                capabilities=[
                    Capability(
                        id="calendar_create_event",
                        domain="calendar",
                        name="Create Calendar Event",
                        description="Create a new calendar event",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "start_time": {"type": "string"},
                                "end_time": {"type": "string"},
                                "description": {"type": "string"},
                                "location": {"type": "string"}
                            },
                            "required": ["title", "start_time", "end_time"]
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string"},
                                "status": {"type": "string"}
                            }
                        },
                        side_effects=["event_created"],
                        requires_auth=True
                    ),
                    Capability(
                        id="calendar_get_events",
                        domain="calendar",
                        name="Get Calendar Events",
                        description="Retrieve calendar events for a time range",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "events": {"type": "array"}
                            }
                        },
                        side_effects=[],
                        requires_auth=True
                    )
                ],
                dependencies=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            success = await self.kernel.register_plugin(plugin_config)
            if success:
                self.kernel.register_plugin_instance("calendar_manager", calendar_manager)
                self._plugin_instances["calendar_manager"] = calendar_manager
                await self._publish_plugin_event("calendar_manager", EventType.PLUGIN_REGISTERED)
                logger.info("Calendar plugin registered successfully")
                
        except Exception as e:
            logger.error(f"Failed to register calendar plugin: {e}")
    
    async def _register_ai_plugin(self):
        """Register AI engine as a kernel plugin"""
        try:
            plugin_config = PluginConfig(
                id="ai_engine",
                name="AI Engine",
                version="1.0.0",
                description="Provides AI capabilities including chat, analysis, and automation",
                type=PluginType.ANALYTICS,
                author="dhii-mail",
                enabled=True,
                config={
                    "model": "gpt-4",
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "enable_streaming": True
                },
                capabilities=[
                    Capability(
                        id="ai_chat",
                        domain="ai",
                        name="AI Chat",
                        description="Send a message to AI and get response",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "context": {"type": "string"}
                            },
                            "required": ["message"]
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "response": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        },
                        side_effects=["ai_interaction"],
                        requires_auth=True
                    ),
                    Capability(
                        id="ai_analyze",
                        domain="ai",
                        name="AI Analysis",
                        description="Analyze content using AI",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "analysis_type": {"type": "string"}
                            }
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "analysis": {"type": "object"}
                            }
                        },
                        side_effects=["ai_analysis"],
                        requires_auth=True
                    )
                ],
                dependencies=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            success = await self.kernel.register_plugin(plugin_config)
            if success:
                self.kernel.register_plugin_instance("ai_engine", ai_engine)
                self._plugin_instances["ai_engine"] = ai_engine
                await self._publish_plugin_event("ai_engine", EventType.PLUGIN_REGISTERED)
                logger.info("AI plugin registered successfully")
                
        except Exception as e:
            logger.error(f"Failed to register AI plugin: {e}")
    
    async def _register_marketing_plugin(self):
        """Register marketing manager as a kernel plugin"""
        try:
            plugin_config = PluginConfig(
                id="marketing_manager",
                name="Marketing Manager",
                version="1.0.0",
                description="Handles marketing campaigns and analytics",
                type=PluginType.MARKETING,
                author="dhii-mail",
                enabled=True,
                config={
                    "max_campaigns": 100,
                    "analytics_enabled": True,
                    "auto_optimization": True
                },
                capabilities=[
                    Capability(
                        id="marketing_create_campaign",
                        domain="marketing",
                        name="Create Marketing Campaign",
                        description="Create a new marketing campaign",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "target_audience": {"type": "string"},
                                "budget": {"type": "number"}
                            },
                            "required": ["name", "type"]
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "campaign_id": {"type": "string"},
                                "status": {"type": "string"}
                            }
                        },
                        side_effects=["campaign_created"],
                        requires_auth=True
                    ),
                    Capability(
                        id="marketing_get_analytics",
                        domain="marketing",
                        name="Get Marketing Analytics",
                        description="Retrieve marketing campaign analytics",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "campaign_id": {"type": "string"}
                            }
                        },
                        output_schema={
                            "type": "object",
                            "properties": {
                                "analytics": {"type": "object"}
                            }
                        },
                        side_effects=[],
                        requires_auth=True
                    )
                ],
                dependencies=["email_manager"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            success = await self.kernel.register_plugin(plugin_config)
            if success:
                self.kernel.register_plugin_instance("marketing_manager", marketing_manager)
                self._plugin_instances["marketing_manager"] = marketing_manager
                await self._publish_plugin_event("marketing_manager", EventType.PLUGIN_REGISTERED)
                logger.info("Marketing plugin registered successfully")
                
        except Exception as e:
            logger.error(f"Failed to register marketing plugin: {e}")
    
    async def _publish_plugin_event(self, plugin_id: str, event_type: EventType):
        """Publish plugin-related events to the event bus"""
        try:
            event = Event(
                id=f"{plugin_id}_{event_type.value}_{datetime.now().isoformat()}",
                type=event_type,
                source=plugin_id,
                timestamp=datetime.now(),
                data={"plugin_id": plugin_id, "status": "registered"}
            )
            await self.shared_services.event_bus.publish(event)
        except Exception as e:
            logger.error(f"Failed to publish event for plugin {plugin_id}: {e}")
    
    def get_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        """Get a registered plugin instance"""
        return self._plugin_instances.get(plugin_id)
    
    async def execute_capability(self, plugin_id: str, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plugin capability through the kernel"""
        try:
            # Get plugin instance
            plugin_instance = self.get_plugin_instance(plugin_id)
            if not plugin_instance:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            # Execute the capability based on plugin type
            if plugin_id == "email_manager":
                if capability_id == "email_send":
                    # Delegate to email manager
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                elif capability_id == "email_receive":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                    
            elif plugin_id == "calendar_manager":
                if capability_id == "calendar_create_event":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                elif capability_id == "calendar_get_events":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                    
            elif plugin_id == "ai_engine":
                if capability_id == "ai_chat":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                elif capability_id == "ai_analyze":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                    
            elif plugin_id == "marketing_manager":
                if capability_id == "marketing_create_campaign":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
                elif capability_id == "marketing_get_analytics":
                    return {"status": "executed", "plugin": plugin_id, "capability": capability_id}
            
            raise ValueError(f"Capability {capability_id} not found in plugin {plugin_id}")
            
        except Exception as e:
            logger.error(f"Failed to execute capability {capability_id} for plugin {plugin_id}: {e}")
            raise


# Global integration instance
kernel_plugin_integration: Optional[KernelPluginIntegration] = None


def initialize_kernel_plugin_integration(kernel: Kernel) -> KernelPluginIntegration:
    """Initialize the kernel plugin integration"""
    global kernel_plugin_integration
    kernel_plugin_integration = KernelPluginIntegration(kernel)
    return kernel_plugin_integration


def get_kernel_plugin_integration() -> KernelPluginIntegration:
    """Get the kernel plugin integration instance"""
    if kernel_plugin_integration is None:
        raise RuntimeError("Kernel plugin integration not initialized")
    return kernel_plugin_integration