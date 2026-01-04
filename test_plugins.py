#!/usr/bin/env python3
"""
Test plugin instances for kernel API testing
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from a2ui_integration.core.types import DomainModule, Capability

class TestEmailPlugin(DomainModule):
    """Test email plugin for kernel API testing"""
    
    def __init__(self):
        self.id = "test_email"
        self.name = "Test Email Plugin"
        self.version = "1.0.0"
        self.description = "Test email communication plugin"
        self._capabilities = [
            Capability(
                id="email.send",
                domain="communication",
                name="Send Email",
                description="Send an email message",
                input_schema={"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "message_id": {"type": "string"}}},
                side_effects=["email_sent"],
                requires_auth=False
            ),
            Capability(
                id="email.search",
                domain="communication",
                name="Search Emails",
                description="Search email messages",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "number"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "emails": {"type": "array"}}},
                side_effects=[],
                requires_auth=False
            )
        ]
    
    @property
    def domain(self) -> str:
        """Return the domain name this module handles"""
        return "communication"
    
    @property
    def capabilities(self) -> List[Capability]:
        """Return list of capabilities this module provides"""
        return self._capabilities
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability"""
        if capability_id == "email.send":
            return {
                "success": True,
                "message_id": f"test_msg_{hash(params.get('to', 'unknown'))}",
                "timestamp": datetime.now().isoformat()
            }
        elif capability_id == "email.search":
            return {
                "success": True,
                "emails": [
                    {
                        "id": "test_email_1",
                        "subject": "Test Email 1",
                        "from": "test@example.com",
                        "date": datetime.now().isoformat()
                    }
                ],
                "total": 1
            }
        else:
            raise ValueError(f"Capability {capability_id} not supported")
    
    async def initialize(self) -> bool:
        """Initialize the domain module"""
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the domain module"""
        return True
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search functionality"""
        if "email" in query.lower():
            return [
                {
                    "type": "capability",
                    "id": "email.send",
                    "name": "Send Email",
                    "description": "Send an email message"
                },
                {
                    "type": "capability",
                    "id": "email.search",
                    "name": "Search Emails",
                    "description": "Search email messages"
                }
            ]
        return []

class TestCalendarPlugin(DomainModule):
    """Test calendar plugin for kernel API testing"""
    
    def __init__(self):
        self.id = "test_calendar"
        self.name = "Test Calendar Plugin"
        self.version = "1.0.0"
        self.description = "Test calendar management plugin"
        self._capabilities = [
            Capability(
                id="calendar.create_event",
                domain="productivity",
                name="Create Event",
                description="Create a calendar event",
                input_schema={"type": "object", "properties": {"title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "event_id": {"type": "string"}}},
                side_effects=["event_created"],
                requires_auth=False
            ),
            Capability(
                id="calendar.find_availability",
                domain="productivity",
                name="Find Availability",
                description="Find available time slots",
                input_schema={"type": "object", "properties": {"date": {"type": "string"}, "duration_minutes": {"type": "number"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "available_slots": {"type": "array"}}},
                side_effects=[],
                requires_auth=False
            )
        ]
    
    @property
    def domain(self) -> str:
        """Return the domain name this module handles"""
        return "productivity"
    
    @property
    def capabilities(self) -> List[Capability]:
        """Return list of capabilities this module provides"""
        return self._capabilities
    
    async def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability"""
        if capability_id == "calendar.create_event":
            return {
                "success": True,
                "event_id": f"test_event_{hash(params.get('title', 'unknown'))}",
                "timestamp": datetime.now().isoformat()
            }
        elif capability_id == "calendar.find_availability":
            return {
                "success": True,
                "available_slots": [
                    {"start": "10:00", "end": "11:00"},
                    {"start": "14:00", "end": "15:00"}
                ]
            }
        else:
            raise ValueError(f"Capability {capability_id} not supported")
    
    async def initialize(self) -> bool:
        """Initialize the domain module"""
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the domain module"""
        return True
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search functionality"""
        if "calendar" in query.lower():
            return [
                {
                    "type": "capability",
                    "id": "calendar.create_event",
                    "name": "Create Event",
                    "description": "Create a calendar event"
                },
                {
                    "type": "capability",
                    "id": "calendar.find_availability",
                    "name": "Find Availability",
                    "description": "Find available time slots"
                }
            ]
        return []