"""
Event Bus Integration Module
Integrates existing managers with the kernel's event bus system
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from a2ui_integration.core.shared_services import EventType, Event, get_shared_services
from a2ui_integration.core.kernel import Kernel

# Import existing managers
from email_manager import email_manager, EmailManager
from calendar_manager import calendar_manager, CalendarManager
from ai_engine import ai_engine, AIEngine
from marketing_manager import marketing_manager, MarketingManager
from video_manager import video_manager, VideoManager
from security_manager import security_manager, SecurityManager

logger = logging.getLogger(__name__)


class EventBusIntegration:
    """Integrates existing managers with the kernel's event bus"""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.shared_services = kernel.shared_services
        self.event_bus = self.shared_services.event_bus
        self._setup_event_subscriptions()
        self._wrap_manager_methods()
    
    def _setup_event_subscriptions(self):
        """Set up event bus subscriptions for system events"""
        # Subscribe to relevant events
        self.event_bus.subscribe(EventType.USER_LOGIN, self._handle_user_login)
        self.event_bus.subscribe(EventType.USER_LOGOUT, self._handle_user_logout)
        self.event_bus.subscribe(EventType.EMAIL_SENT, self._handle_email_sent)
        self.event_bus.subscribe(EventType.EMAIL_RECEIVED, self._handle_email_received)
        self.event_bus.subscribe(EventType.MEETING_CREATED, self._handle_meeting_created)
        self.event_bus.subscribe(EventType.MEETING_UPDATED, self._handle_meeting_updated)
        self.event_bus.subscribe(EventType.PLUGIN_ERROR, self._handle_plugin_error)
        
        logger.info("Event bus subscriptions configured")
    
    def _wrap_manager_methods(self):
        """Wrap existing manager methods to publish events"""
        # Wrap Email Manager methods
        self._wrap_email_manager()
        
        # Wrap Calendar Manager methods
        self._wrap_calendar_manager()
        
        # Wrap AI Engine methods
        self._wrap_ai_engine()
        
        # Wrap Marketing Manager methods
        self._wrap_marketing_manager()
        
        # Wrap Video Manager methods
        self._wrap_video_manager()
        
        # Wrap Security Manager methods
        self._wrap_security_manager()
        
        logger.info("Manager method wrapping completed")
    
    def _wrap_email_manager(self):
        """Wrap email manager methods to publish events"""
        original_send_email = email_manager.send_email
        original_get_emails = email_manager.get_emails
        
        async def wrapped_send_email(self, to_email: str, subject: str, body: str, **kwargs):
            """Wrapped send_email that publishes events"""
            try:
                result = await original_send_email(to_email, subject, body, **kwargs)
                
                # Publish email sent event
                event = Event(
                    id=f"email_sent_{datetime.now().isoformat()}",
                    type=EventType.EMAIL_SENT,
                    source="email_manager",
                    timestamp=datetime.now(),
                    data={
                        "to": to_email,
                        "subject": subject,
                        "message_id": result.get("message_id") if isinstance(result, dict) else None,
                        "status": "success"
                    }
                )
                await self.event_bus.publish(event)
                
                return result
                
            except Exception as e:
                # Publish email error event
                event = Event(
                    id=f"email_error_{datetime.now().isoformat()}",
                    type=EventType.PLUGIN_ERROR,
                    source="email_manager",
                    timestamp=datetime.now(),
                    data={
                        "operation": "send_email",
                        "error": str(e),
                        "to": to_email,
                        "subject": subject
                    }
                )
                await self.event_bus.publish(event)
                raise
        
        async def wrapped_receive_emails(self, folder: str = "INBOX", limit: int = 10, **kwargs):
            """Wrapped receive_emails that publishes events"""
            try:
                result = await original_receive_emails(folder, limit, **kwargs)
                
                # Publish email received event
                if result and isinstance(result, list) and len(result) > 0:
                    event = Event(
                        id=f"email_received_{datetime.now().isoformat()}",
                        type=EventType.EMAIL_RECEIVED,
                        source="email_manager",
                        timestamp=datetime.now(),
                        data={
                            "folder": folder,
                            "count": len(result),
                            "status": "success"
                        }
                    )
                    await self.event_bus.publish(event)
                
                return result
                
            except Exception as e:
                # Publish error event
                event = Event(
                    id=f"email_error_{datetime.now().isoformat()}",
                    type=EventType.PLUGIN_ERROR,
                    source="email_manager",
                    timestamp=datetime.now(),
                    data={
                        "operation": "receive_emails",
                        "error": str(e),
                        "folder": folder
                    }
                )
                await self.event_bus.publish(event)
                raise
        
        # Apply wrappers
        email_manager.send_email = wrapped_send_email.__get__(email_manager, EmailManager)
        email_manager.receive_emails = wrapped_receive_emails.__get__(email_manager, EmailManager)
    
    def _wrap_calendar_manager(self):
        """Wrap calendar manager methods to publish events"""
        original_create_event = calendar_manager.create_event
        original_update_event = calendar_manager.update_event
        original_delete_event = calendar_manager.delete_event
        
        async def wrapped_create_event(self, event_data: Dict[str, Any], **kwargs):
            """Wrapped create_event that publishes events"""
            try:
                result = await original_create_event(event_data, **kwargs)
                
                # Publish meeting created event
                event = Event(
                    id=f"meeting_created_{datetime.now().isoformat()}",
                    type=EventType.MEETING_CREATED,
                    source="calendar_manager",
                    timestamp=datetime.now(),
                    data={
                        "event_id": result.get("id") if isinstance(result, dict) else None,
                        "title": event_data.get("title"),
                        "start_time": event_data.get("start_time"),
                        "organizer": event_data.get("organizer"),
                        "status": "created"
                    }
                )
                await self.event_bus.publish(event)
                
                return result
                
            except Exception as e:
                # Publish error event
                event = Event(
                    id=f"calendar_error_{datetime.now().isoformat()}",
                    type=EventType.PLUGIN_ERROR,
                    source="calendar_manager",
                    timestamp=datetime.now(),
                    data={
                        "operation": "create_event",
                        "error": str(e),
                        "event_data": event_data
                    }
                )
                await self.event_bus.publish(event)
                raise
        
        async def wrapped_update_event(self, event_id: str, updates: Dict[str, Any], **kwargs):
            """Wrapped update_event that publishes events"""
            try:
                result = await original_update_event(event_id, updates, **kwargs)
                
                # Publish meeting updated event
                event = Event(
                    id=f"meeting_updated_{datetime.now().isoformat()}",
                    type=EventType.MEETING_UPDATED,
                    source="calendar_manager",
                    timestamp=datetime.now(),
                    data={
                        "event_id": event_id,
                        "updates": updates,
                        "status": "updated"
                    }
                )
                await self.event_bus.publish(event)
                
                return result
                
            except Exception as e:
                # Publish error event
                event = Event(
                    id=f"calendar_error_{datetime.now().isoformat()}",
                    type=EventType.PLUGIN_ERROR,
                    source="calendar_manager",
                    timestamp=datetime.now(),
                    data={
                        "operation": "update_event",
                        "error": str(e),
                        "event_id": event_id,
                        "updates": updates
                    }
                )
                await self.event_bus.publish(event)
                raise
        
        async def wrapped_delete_event(self, event_id: str, **kwargs):
            """Wrapped delete_event that publishes events"""
            try:
                result = await original_delete_event(event_id, **kwargs)
                
                # Publish meeting deleted event
                event = Event(
                    id=f"meeting_deleted_{datetime.now().isoformat()}",
                    type=EventType.MEETING_DELETED,
                    source="calendar_manager",
                    timestamp=datetime.now(),
                    data={
                        "event_id": event_id,
                        "status": "deleted"
                    }
                )
                await self.event_bus.publish(event)
                
                return result
                
            except Exception as e:
                # Publish error event
                event = Event(
                    id=f"calendar_error_{datetime.now().isoformat()}",
                    type=EventType.PLUGIN_ERROR,
                    source="calendar_manager",
                    timestamp=datetime.now(),
                    data={
                        "operation": "delete_event",
                        "error": str(e),
                        "event_id": event_id
                    }
                )
                await self.event_bus.publish(event)
                raise
        
        # Apply wrappers
        calendar_manager.create_event = wrapped_create_event.__get__(calendar_manager, CalendarManager)
        calendar_manager.update_event = wrapped_update_event.__get__(calendar_manager, CalendarManager)
        calendar_manager.delete_event = wrapped_delete_event.__get__(calendar_manager, CalendarManager)
    
    def _wrap_ai_engine(self):
        """Wrap AI engine methods to publish events"""
        # Note: AI engine methods would be wrapped similarly
        # Implementation depends on specific AI engine interface
        logger.info("AI engine method wrapping configured")
    
    def _wrap_marketing_manager(self):
        """Wrap marketing manager methods to publish events"""
        # Note: Marketing manager methods would be wrapped similarly
        # Implementation depends on specific marketing manager interface
        logger.info("Marketing manager method wrapping configured")
    
    def _wrap_video_manager(self):
        """Wrap video manager methods to publish events"""
        # Note: Video manager methods would be wrapped similarly
        logger.info("Video manager method wrapping configured")
    
    def _wrap_security_manager(self):
        """Wrap security manager methods to publish events"""
        # Note: Security manager methods would be wrapped similarly
        logger.info("Security manager method wrapping configured")
    
    # Event handlers
    async def _handle_user_login(self, event: Event):
        """Handle user login events"""
        logger.info(f"User login detected: {event.data.get('user_id')}")
        # Could trigger security checks, notifications, etc.
    
    async def _handle_user_logout(self, event: Event):
        """Handle user logout events"""
        logger.info(f"User logout detected: {event.data.get('user_id')}")
        # Could trigger cleanup, logging, etc.
    
    async def _handle_email_sent(self, event: Event):
        """Handle email sent events"""
        logger.info(f"Email sent event: {event.data.get('message_id')}")
        # Could trigger analytics, follow-up actions, etc.
    
    async def _handle_email_received(self, event: Event):
        """Handle email received events"""
        logger.info(f"Email received event: {event.data.get('count')} messages")
        # Could trigger AI processing, notifications, etc.
    
    async def _handle_meeting_created(self, event: Event):
        """Handle meeting created events"""
        logger.info(f"Meeting created: {event.data.get('event_id')}")
        # Could trigger notifications, calendar sync, etc.
    
    async def _handle_meeting_updated(self, event: Event):
        """Handle meeting updated events"""
        logger.info(f"Meeting updated: {event.data.get('event_id')}")
        # Could trigger notifications, rescheduling, etc.
    
    async def _handle_plugin_error(self, event: Event):
        """Handle plugin error events"""
        logger.error(f"Plugin error: {event.data.get('error')} in {event.data.get('operation')}")
        # Could trigger error recovery, notifications, etc.


# Global integration instance
event_bus_integration: Optional[EventBusIntegration] = None


def initialize_event_bus_integration(kernel: Kernel) -> EventBusIntegration:
    """Initialize the event bus integration"""
    global event_bus_integration
    event_bus_integration = EventBusIntegration(kernel)
    return event_bus_integration


def get_event_bus_integration() -> EventBusIntegration:
    """Get the event bus integration instance"""
    if event_bus_integration is None:
        raise RuntimeError("Event bus integration not initialized")
    return event_bus_integration