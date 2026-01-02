"""
AI Engine for dhii Mail
Handles natural language processing, intent recognition, and AI responses
"""

import os
import json
import logging
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

# Import managers (avoid circular import)
from calendar_manager import CalendarManager, calendar_manager
from email_manager import EmailManager, email_manager

logger = logging.getLogger(__name__)

class AIIntent(BaseModel):
    """AI intent recognition model"""
    intent: str  # 'schedule_meeting', 'send_email', 'check_calendar', 'general_chat'
    confidence: float
    entities: Dict[str, Any] = {}
    response_type: str = 'text'  # 'text', 'form', 'action', 'ui_component'

class AIResponse(BaseModel):
    """AI response model"""
    message: str
    intent: AIIntent
    actions: List[Dict[str, Any]] = []
    ui_components: Optional[Dict[str, Any]] = None
    requires_user_input: bool = False
    session_data: Optional[Dict[str, Any]] = None

class AIEngine:
    """AI Engine for processing user messages and generating responses"""
    
    def __init__(self):
        self.system_prompt = """You are dhii, an AI assistant for email and calendar management. 
        
Your capabilities include:
- Scheduling meetings and managing calendar events
- Sending emails and managing email communications  
- Checking availability and finding suitable meeting times
- Managing contacts and email lists
- Creating and sending calendar invites
- Setting up video conferences

When users ask about these topics, be helpful and provide clear, actionable responses.

For scheduling requests, gather:
- Meeting title/purpose
- Date and time preferences
- Duration
- Attendees (if any)
- Location (physical or virtual)

For email requests, gather:
- Recipients
- Subject
- Message content
- Any attachments or special formatting

Always confirm details before taking actions, and provide clear feedback about what you're doing."""
        
        # OpenRouter configuration
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.use_openrouter = bool(self.openrouter_api_key)
        
        # Fallback model when OpenRouter is not available
        self.fallback_model = "pattern-based"
        
        # Calendar manager integration
        self.calendar_manager = calendar_manager
        
        # Mock intent patterns for fallback
        self.intent_patterns = {
            'schedule_meeting': [
                'schedule', 'book', 'meeting', 'appointment', 'meet', 'calendar',
                'available', 'free time', 'busy', 'when can we', 'let\'s meet'
            ],
            'send_email': [
                'send email', 'email', 'message', 'contact', 'reach out', 'write to',
                'compose', 'reply', 'forward', 'mail', 'send message', 'write email',
                'draft email', 'new email'
            ],
            'check_calendar': [
                'check calendar', 'what\'s on my calendar', 'my schedule',
                'upcoming events', 'today\'s meetings', 'this week'
            ],
            'create_contact': [
                'add contact', 'new contact', 'save contact', 'contact info',
                'phone number', 'email address'
            ],
            'video_conference': [
                'video call', 'video meeting', 'zoom', 'teams', 'conference',
                'virtual meeting', 'online meeting'
            ]
        }
    
    def detect_intent(self, message: str) -> AIIntent:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Enhanced calendar intent detection
        if any(phrase in message_lower for phrase in ['what\'s on my calendar', 'check my calendar', 'show my calendar', 'what\'s on my schedule']):
            entities = self._extract_entities(message, 'check_calendar')
            return AIIntent(
                intent='check_calendar',
                confidence=0.9,
                entities=entities,
                response_type='text'
            )
        
        # Enhanced email intent detection
        if any(phrase in message_lower for phrase in ['send an email to', 'email', 'compose email', 'write email to', 'send message to']):
            entities = self._extract_entities(message, 'send_email')
            return AIIntent(
                intent='send_email',
                confidence=0.9,
                entities=entities,
                response_type='text'
            )
        
        # Check for specific intents
        for intent_type, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Calculate confidence based on keyword matches
                    confidence = 0.8 if any(kw in message_lower for kw in keywords[:3]) else 0.6
                    
                    # Extract entities based on intent
                    entities = self._extract_entities(message, intent_type)
                    
                    return AIIntent(
                        intent=intent_type,
                        confidence=confidence,
                        entities=entities,
                        response_type=self._get_response_type(intent_type)
                    )
        
        # Default to general chat
        return AIIntent(
            intent='general_chat',
            confidence=0.9,
            entities={},
            response_type='text'
        )
    
    def _extract_entities(self, message: str, intent_type: str) -> Dict[str, Any]:
        """Extract relevant entities from message based on intent"""
        entities = {}
        message_lower = message.lower()
        
        if intent_type == 'schedule_meeting':
            # Extract time-related entities
            if 'tomorrow' in message_lower:
                entities['date'] = 'tomorrow'
            elif 'today' in message_lower:
                entities['date'] = 'today'
            elif 'next week' in message_lower:
                entities['date'] = 'next_week'
            
            # Extract duration
            if 'hour' in message_lower:
                entities['duration'] = '1 hour'
            elif '30 minutes' in message_lower or 'half hour' in message_lower:
                entities['duration'] = '30 minutes'
            
            # Extract time preferences
            import re
            time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm)?'
            time_match = re.search(time_pattern, message, re.IGNORECASE)
            if time_match:
                entities['time'] = time_match.group(0)
        
        elif intent_type == 'check_calendar':
            # Extract date range for calendar check
            if 'today' in message_lower:
                entities['date_range'] = 'today'
            elif 'tomorrow' in message_lower:
                entities['date_range'] = 'tomorrow'
            elif 'this week' in message_lower:
                entities['date_range'] = 'this_week'
            elif 'next week' in message_lower:
                entities['date_range'] = 'next_week'
            elif 'next monday' in message_lower:
                entities['date_range'] = 'next_monday'
            elif 'availability' in message_lower or 'available' in message_lower:
                entities['check_availability'] = True
        
        elif intent_type == 'send_email':
            # Extract email addresses
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, message)
            if emails:
                entities['recipients'] = emails
            
            # Extract subject if mentioned
            if 'subject' in message_lower:
                # Look for "subject:" or "subject is" patterns
                subject_patterns = [
                    r'subject:\s*([^,\.\n]+)',
                    r'subject is\s+([^,\.\n]+)',
                    r'about\s+([^,\.\n]+)',
                    r'regarding\s+([^,\.\n]+)'
                ]
                
                for pattern in subject_patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        subject_text = match.group(1).strip()
                        if subject_text and len(subject_text) < 200:
                            entities['subject'] = subject_text
                            break
            
            # Extract message content if mentioned
            if any(word in message_lower for word in ['saying', 'message', 'tell', 'write']):
                # Look for message content after keywords
                message_patterns = [
                    r'saying\s+(.+)',
                    r'message\s+is\s+(.+)',
                    r'tell\s+them\s+(.+)',
                    r'write\s+that\s+(.+)'
                ]
                
                for pattern in message_patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        message_text = match.group(1).strip()
                        if message_text and len(message_text) < 1000:
                            entities['message'] = message_text
                            break
        
        return entities
    
    def _get_response_type(self, intent_type: str) -> str:
        """Determine response type based on intent"""
        response_types = {
            'schedule_meeting': 'form',
            'send_email': 'form',
            'check_calendar': 'data',
            'create_contact': 'form',
            'video_conference': 'form',
            'general_chat': 'text'
        }
        return response_types.get(intent_type, 'text')
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Process user message and generate AI response"""
        if context is None:
            context = {}
        
        # Detect intent
        intent = self.detect_intent(message)
        
        # Try to get response from OpenRouter first
        response_message = None
        if self.use_openrouter:
            try:
                response_message = await self._generate_openrouter_response(message, context)
                logger.info(f"Using OpenRouter for response generation")
            except Exception as e:
                logger.warning(f"OpenRouter failed, falling back to pattern-based: {e}")
        
        # Fallback to pattern-based response if OpenRouter not available or failed
        if not response_message:
            response_message = self._generate_response(message, intent, context)
        
        # Generate actions if needed
        actions = self._generate_actions(intent, context)
        
        # Generate UI components if needed
        ui_components = self._generate_ui_components(intent, context)
        
        return AIResponse(
            message=response_message,
            intent=intent,
            actions=actions,
            ui_components=ui_components,
            requires_user_input=self._requires_user_input(intent),
            session_data=self._update_session_data(intent, context)
        )
    
    def _generate_response(self, message: str, intent: AIIntent, context: Dict[str, Any]) -> str:
        """Generate appropriate response based on intent"""
        
        if intent.intent == 'schedule_meeting':
            if not intent.entities:
                return "I'd be happy to help you schedule a meeting! Could you tell me more details? For example: 'Schedule a 30-minute meeting for tomorrow at 2 PM' or 'Book a meeting with John next week'."
            else:
                # Check availability if user context is available
                availability_check = ""
                if context and 'user_id' in context and 'date' in intent.entities:
                    user_id = context['user_id']
                    target_date = self._parse_date_entity(intent.entities['date'])
                    
                    if target_date:
                        duration = 30  # Default 30 minutes
                        if 'duration' in intent.entities:
                            duration = self._parse_duration_entity(intent.entities['duration'])
                        
                        available_slots = self.calendar_manager.get_availability(
                            user_id, target_date, duration
                        )
                        
                        if available_slots:
                            availability_check = f" I found {len(available_slots)} available time slots for {target_date.strftime('%A, %B %d')}."
                        else:
                            availability_check = f" I don't see any available slots on {target_date.strftime('%A, %B %d')}. Would you like to check a different date?"
                
                # Acknowledge entities found
                response_parts = ["Great! I can help you schedule that meeting."]
                
                if 'date' in intent.entities:
                    response_parts.append(f"Date: {intent.entities['date']}")
                if 'time' in intent.entities:
                    response_parts.append(f"Time: {intent.entities['time']}")
                if 'duration' in intent.entities:
                    response_parts.append(f"Duration: {intent.entities['duration']}")
                
                response_parts.append(availability_check)
                response_parts.append("Would you like me to proceed with scheduling this meeting?")
                return " ".join(response_parts)
        
        elif intent.intent == 'send_email':
            # Check if we have email accounts for the user
            email_accounts = []
            if context and 'user_id' in context:
                from email_manager import email_manager
                email_accounts = email_manager.get_email_accounts(context['user_id'])
            
            if not email_accounts:
                return "I can help you send emails, but you'll need to set up an email account first. Would you like me to help you configure your email settings?"
            
            if 'recipients' in intent.entities:
                recipients = ', '.join(intent.entities['recipients'])
                response_parts = [f"I'll help you send an email to {recipients}."]
                
                if 'subject' in intent.entities:
                    response_parts.append(f"Subject: '{intent.entities['subject']}'")
                
                if 'message' in intent.entities:
                    response_parts.append("I have your message content ready.")
                
                response_parts.append("Would you like me to compose the email for you?")
                return " ".join(response_parts)
            else:
                return "I can help you send an email. Who would you like to email, and what should the message say?"
        
        elif intent.intent == 'check_calendar':
            # Try to get actual calendar data if user context is available
            if context and 'user_id' in context:
                user_id = context['user_id']
                
                # Check if this is an availability check
                if intent.entities.get('check_availability'):
                    # Get availability for a specific date
                    target_date = datetime.now(timezone.utc)
                    if 'date_range' in intent.entities:
                        if intent.entities['date_range'] == 'tomorrow':
                            target_date = datetime.now(timezone.utc) + timedelta(days=1)
                        elif intent.entities['date_range'] == 'next_monday':
                            # Find next Monday
                            days_until_monday = (7 - datetime.now(timezone.utc).weekday()) % 7
                            if days_until_monday == 0:
                                days_until_monday = 7
                            target_date = datetime.now(timezone.utc) + timedelta(days=days_until_monday)
                    
                    duration = 30  # Default 30 minutes
                    available_slots = self.calendar_manager.get_availability(user_id, target_date, duration)
                    
                    if available_slots:
                        return f"You have {len(available_slots)} available {duration}-minute time slots on {target_date.strftime('%A, %B %d')}. Would you like me to schedule a meeting?"
                    else:
                        return f"I don't see any available {duration}-minute slots on {target_date.strftime('%A, %B %d')}. Would you like to check a different date or duration?"
                
                # Regular calendar check
                today = datetime.now(timezone.utc)
                
                # Get today's events
                events = self.calendar_manager.get_events(
                    user_id, 
                    today.replace(hour=0, minute=0, second=0, microsecond=0),
                    today.replace(hour=23, minute=59, second=59, microsecond=999999)
                )
                
                if events:
                    response_parts = ["Here's your schedule for today:"]
                    for event in events:
                        start_time = event.start_time.strftime("%I:%M %p")
                        end_time = event.end_time.strftime("%I:%M %p")
                        response_parts.append(f"• {start_time} - {end_time}: {event.title}")
                    
                    if len(events) > 3:
                        response_parts.append(f"\nYou have {len(events)} events today.")
                    
                    response_parts.append("\nWould you like to see more details or check a different date?")
                    return "\n".join(response_parts)
                else:
                    return "You have no events scheduled for today. Would you like to schedule a meeting or check a different date?"
            
            return "Let me check your calendar. Would you like to see today's schedule, this week's events, or check availability for a specific date?"
        
        elif intent.intent == 'create_contact':
            return "I can help you add a new contact. What's their name and contact information?"
        
        elif intent.intent == 'video_conference':
            return "I can set up a video conference for you. Would you like to create a meeting room now?"
        
        else:  # general_chat
            return self._generate_general_response(message, context)
    
    def _generate_general_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate general chat response with enhanced context awareness and error handling"""
        message_lower = message.lower().strip()
        
        # Enhanced greeting responses with context awareness
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in message_lower for greeting in greetings):
            # Check if user has been active recently
            if self._is_new_session(context):
                return "Hello! I'm dhii, your AI assistant for email and calendar management. I can help you schedule meetings, send emails, check your calendar, and more. What would you like to accomplish today?"
            else:
                return "Hello again! Welcome back. How can I assist you with your email and calendar management today?"
        
        # Enhanced gratitude responses
        thanks = ['thank', 'thanks', 'appreciate', 'grateful']
        if any(thank in message_lower for thank in thanks):
            gratitude_responses = [
                "You're welcome! I'm happy to help. Is there anything else I can assist you with?",
                "My pleasure! Feel free to ask if you need help with anything else.",
                "Glad I could help! What else would you like to accomplish today?"
            ]
            return gratitude_responses[hash(message) % len(gratitude_responses)]
        
        # Enhanced help requests
        help_words = ['help', 'assist', 'support', 'guide']
        if any(help_word in message_lower for help_word in help_words):
            return "I can help you with a variety of tasks:\n\n📧 **Email Management**: Send emails, check inbox, manage drafts\n📅 **Calendar Scheduling**: Schedule meetings, check availability, view events\n👥 **Contact Management**: Create and manage contacts\n🎥 **Video Conferences**: Set up meeting rooms\n\nWhat would you like to do? Just tell me naturally, like 'Schedule a meeting for tomorrow' or 'Send an email to John'."
        
        # Handle unclear or ambiguous requests
        if self._is_ambiguous_request(message_lower):
            return "I'm not quite sure what you'd like to do. Could you provide more details? For example:\n\n• 'Schedule a 30-minute meeting for tomorrow at 2 PM'\n• 'Send an email to john@example.com about the project update'\n• 'Check my calendar for today'\n• 'What meetings do I have this week?'\n\nWhat would you like to accomplish?"
        
        # Handle requests for capabilities or features
        capability_words = ['what can you do', 'your capabilities', 'features', 'abilities', 'what do you do']
        if any(capability in message_lower for capability in capability_words):
            return "I'm dhii, your AI assistant specialized in email and calendar management. Here's what I can help you with:\n\n📧 **Email Features**:\n   • Send emails to individuals or groups\n   • Check your email accounts and inbox\n   • Manage email drafts\n   • Set up email accounts\n\n📅 **Calendar Features**:\n   • Schedule meetings and appointments\n   • Check your availability\n   • View your daily/weekly schedule\n   • Find available time slots\n\n👥 **Contact Management**:\n   • Create new contacts\n   • Manage contact information\n\n🎥 **Video Conferences**:\n   • Create video meeting rooms\n   • Set up conference calls\n\nJust tell me what you'd like to do in natural language!"
        
        # Handle status check requests
        status_words = ['status', 'how are you', 'what\'s up', 'how\'s it going']
        if any(status_word in message_lower for status_word in status_words):
            return "I'm doing great and ready to help you manage your emails and calendar! What can I assist you with today?"
        
        # Handle goodbye/farewell
        goodbye_words = ['bye', 'goodbye', 'see you', 'farewell', 'talk to you later']
        if any(goodbye in message_lower for goodbye in goodbye_words):
            return "Goodbye! Feel free to reach out anytime you need help with your email or calendar management. Have a great day!"
        
        # Handle confusion or error states
        confusion_words = ['confused', 'don\'t understand', 'lost', 'stuck']
        if any(confusion in message_lower for confusion in confusion_words):
            return "I understand you might be having some difficulty. Let me help clarify what I can do:\n\n• **For meetings**: Say 'Schedule a meeting for [date] at [time]'\n• **For emails**: Say 'Send an email to [person] about [subject]'\n• **For calendar**: Say 'Check my calendar for [date]'\n• **For help**: Say 'What can you do?' or 'Help me with [task]'\n\nWhat would you like to accomplish?"
        
        # Enhanced default response with more context and guidance
        return "I understand you're reaching out, but I'm not quite sure what specific task you'd like help with. I specialize in:\n\n• Email management and sending\n• Calendar scheduling and meetings\n• Contact management\n• Video conference setup\n\nCould you tell me more specifically what you'd like to do? For example: 'I want to schedule a meeting' or 'I need to send an email'."
    
    def _is_new_session(self, context: Dict[str, Any]) -> bool:
        """Check if this is a new user session"""
        if not context or 'session_data' not in context:
            return True
        
        session_data = context['session_data']
        if 'conversation_history' not in session_data:
            return True
        
        # Check if last interaction was more than 30 minutes ago
        if session_data['conversation_history']:
            last_interaction = session_data['conversation_history'][-1]
            if 'timestamp' in last_interaction:
                try:
                    last_time = datetime.fromisoformat(last_interaction['timestamp'])
                    time_diff = datetime.now(timezone.utc) - last_time
                    return time_diff.total_seconds() > 1800  # 30 minutes
                except (ValueError, AttributeError):
                    return True
        
        return True
    
    def _is_ambiguous_request(self, message: str) -> bool:
        """Check if the user request is ambiguous or unclear"""
        # Common ambiguous patterns
        ambiguous_patterns = [
            r'\b(do|make|create|schedule|send|check)\s+it\b',
            r'\b(do|make|create|schedule|send|check)\s+that\b',
            r'\b(do|make|create|schedule|send|check)\s+this\b',
            r'\b(something|anything|everything)\b',
            r'^\s*(yes|no|maybe|ok|sure)\s*$',
            r'\b(thing|stuff|work|project)\b.*\b(do|make|create|schedule|send|check)\b',
            r'^\s*\?\s*$',  # Just a question mark
            r'^\s*help\s*$',  # Just "help"
            r'^\s*i\s+(don\'t|do\s+not)\s+know\s*$',
            r'^\s*i\s+need\s+(to\s+)?\b(do|make|create|schedule|send|check)\b\s+something\s*$'
        ]
        
        for pattern in ambiguous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        # Check if message is too short and doesn't contain specific entities
        if len(message) < 10 and not any(word in message for word in ['email', 'meeting', 'calendar', 'schedule', 'send']):
            return True
        
        return False
    
    def _generate_general_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate general chat response"""
        # Simple pattern-based responses for now
        message_lower = message.lower()
        
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in message_lower for greeting in greetings):
            return "Hello! I'm dhii, your AI assistant for email and calendar management. How can I help you today?"
        
        thanks = ['thank', 'thanks', 'appreciate']
        if any(thank in message_lower for thank in thanks):
            return "You're welcome! Is there anything else I can help you with?"
        
        help_words = ['help', 'assist', 'support']
        if any(help_word in message_lower for help_word in help_words):
            return "I can help you with scheduling meetings, sending emails, managing your calendar, creating contacts, and setting up video conferences. What would you like to do?"
        
        # Default response
        return "I understand you're reaching out. I can help you with email management, calendar scheduling, and meeting coordination. What would you like to accomplish?"
    
    def _generate_actions(self, intent: AIIntent, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate available actions based on intent"""
        actions = []
        
        if intent.intent == 'schedule_meeting' and intent.entities:
            actions.append({
                "type": "button",
                "label": "Schedule Meeting",
                "action": "schedule_meeting",
                "data": intent.entities
            })
        
        elif intent.intent == 'send_email' and 'recipients' in intent.entities:
            actions.append({
                "type": "button", 
                "label": "Compose Email",
                "action": "compose_email",
                "data": intent.entities
            })
        elif intent.intent == 'send_email' and not 'recipients' in intent.entities:
            # Show email setup if no email accounts configured
            if context and 'user_id' in context:
                from email_manager import email_manager
                email_accounts = email_manager.get_email_accounts(context['user_id'])
                if not email_accounts:
                    actions.append({
                        "type": "button",
                        "label": "Setup Email Account",
                        "action": "setup_email",
                        "data": {}
                    })
        
        elif intent.intent == 'check_calendar':
            actions.append({
                "type": "button",
                "label": "View Calendar",
                "action": "view_calendar",
                "data": {}
            })
        
        elif intent.intent == 'video_conference':
            actions.append({
                "type": "button",
                "label": "Create Video Room",
                "action": "create_video_room",
                "data": {}
            })
        
        return actions
    
    def _generate_ui_components(self, intent: AIIntent, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate UI components based on intent"""
        
        if intent.response_type == 'form':
            if intent.intent == 'schedule_meeting':
                return {
                    "type": "meeting_form",
                    "title": "Schedule Meeting",
                    "fields": [
                        {"name": "title", "type": "text", "placeholder": "Meeting Title", "required": True},
                        {"name": "date", "type": "date", "placeholder": "Date", "required": True},
                        {"name": "time", "type": "time", "placeholder": "Time", "required": True},
                        {"name": "duration", "type": "select", "options": ["30 minutes", "1 hour", "2 hours"], "required": True},
                        {"name": "attendees", "type": "email_list", "placeholder": "Attendee Emails (comma separated)", "required": False},
                        {"name": "location", "type": "text", "placeholder": "Location or Video Link", "required": False},
                        {"name": "description", "type": "textarea", "placeholder": "Description", "required": False}
                    ],
                    "actions": [
                        {"type": "submit", "label": "Schedule Meeting", "action": "schedule_meeting"},
                        {"type": "cancel", "label": "Cancel", "action": "cancel"}
                    ]
                }
            
            elif intent.intent == 'send_email':
                return {
                    "type": "email_form",
                    "title": "Compose Email",
                    "fields": [
                        {"name": "to", "type": "email_list", "placeholder": "To (comma separated emails)", "required": True, "value": intent.entities.get('recipients', [])},
                        {"name": "subject", "type": "text", "placeholder": "Subject", "required": True, "value": intent.entities.get('subject', '')},
                        {"name": "message", "type": "textarea", "placeholder": "Message", "required": True, "value": intent.entities.get('message', '')}
                    ],
                    "actions": [
                        {"type": "submit", "label": "Send Email", "action": "send_email"},
                        {"type": "save_draft", "label": "Save Draft", "action": "save_draft"},
                        {"type": "cancel", "label": "Cancel", "action": "cancel"}
                    ]
                }
        
        return None
    
    def _parse_date_entity(self, date_entity: str) -> Optional[datetime]:
        """Parse date entity string to datetime object"""
        try:
            # Handle relative dates like "tomorrow", "next week", etc.
            today = datetime.now(timezone.utc)
            
            date_entity = date_entity.lower().strip()
            
            if date_entity == "today":
                return today
            elif date_entity == "tomorrow":
                return today + timedelta(days=1)
            elif date_entity == "next week":
                return today + timedelta(weeks=1)
            elif date_entity == "this week":
                return today
            elif date_entity.startswith("in ") and "days" in date_entity:
                # Handle "in 3 days"
                words = date_entity.split()
                for i, word in enumerate(words):
                    if word.isdigit():
                        days = int(word)
                        return today + timedelta(days=days)
            
            # Try to parse as specific date
            try:
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d", "%b %d"]:
                    try:
                        parsed = datetime.strptime(date_entity, fmt)
                        # If year not specified, use current year
                        if parsed.year == 1900:
                            parsed = parsed.replace(year=today.year)
                        return parsed.replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date entity '{date_entity}': {e}")
            return None
    
    def _parse_duration_entity(self, duration_entity: str) -> int:
        """Parse duration entity string to minutes"""
        try:
            duration_entity = duration_entity.lower().strip()
            
            if duration_entity == "30 minutes":
                return 30
            elif duration_entity == "1 hour":
                return 60
            elif duration_entity == "2 hours":
                return 120
            elif duration_entity == "15 minutes":
                return 15
            elif duration_entity == "45 minutes":
                return 45
            elif duration_entity == "1.5 hours" or duration_entity == "90 minutes":
                return 90
            
            # Try to extract number from string
            import re
            numbers = re.findall(r'\d+', duration_entity)
            if numbers:
                number = int(numbers[0])
                if "hour" in duration_entity:
                    return number * 60
                elif "minute" in duration_entity:
                    return number
            
            return 30  # Default to 30 minutes
            
        except Exception as e:
            logger.error(f"Error parsing duration entity '{duration_entity}': {e}")
            return 30
    
    def _requires_user_input(self, intent: AIIntent) -> bool:
        """Determine if response requires user input"""
        return intent.response_type in ['form', 'data_request']
    
    def _update_session_data(self, intent: AIIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update session data based on intent"""
        session_data = context.get('session_data', {}).copy()
        
        # Store intent information for context
        session_data['last_intent'] = intent.intent
        session_data['last_entities'] = intent.entities
        session_data['last_confidence'] = intent.confidence
        
        # Update conversation context
        if 'conversation_history' not in session_data:
            session_data['conversation_history'] = []
        
        # Add current intent to history (limit to last 10)
        session_data['conversation_history'].append({
            'intent': intent.intent,
            'entities': intent.entities,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        if len(session_data['conversation_history']) > 10:
            session_data['conversation_history'] = session_data['conversation_history'][-10:]
        
        return session_data
    
    async def _call_openrouter_api(self, messages: List[Dict[str, str]], model: str = "meta-llama/llama-3.1-8b-instruct") -> Optional[str]:
        """Call OpenRouter API for AI response with enhanced error handling and retry logic"""
        if not self.use_openrouter:
            return None
        
        # Validate API key
        if not self.openrouter_api_key or self.openrouter_api_key.strip() == "":
            logger.warning("OpenRouter API key not configured")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dhii-mail.local",
            "X-Title": "dhii Mail AI Assistant"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        # Implement retry logic with exponential backoff
        max_retries = 3
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                    async with session.post(self.openrouter_api_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            if 'choices' in result and len(result['choices']) > 0:
                                content = result['choices'][0]['message']['content'].strip()
                                logger.info(f"OpenRouter API call successful on attempt {attempt + 1}")
                                return content
                            else:
                                logger.warning(f"OpenRouter API returned empty choices on attempt {attempt + 1}")
                                return None
                        elif response.status == 429:  # Rate limit
                            logger.warning(f"OpenRouter API rate limit hit on attempt {attempt + 1}")
                            if attempt < max_retries - 1:
                                delay = base_delay * (2 ** attempt)  # Exponential backoff
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error("OpenRouter API rate limit exceeded after all retries")
                                return None
                        elif response.status >= 500:  # Server error
                            logger.warning(f"OpenRouter API server error {response.status} on attempt {attempt + 1}")
                            if attempt < max_retries - 1:
                                delay = base_delay * (2 ** attempt)  # Exponential backoff
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"OpenRouter API server error {response.status} after all retries")
                                return None
                        else:
                            error_text = await response.text()
                            logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                            return None
                            
            except asyncio.TimeoutError:
                logger.warning(f"OpenRouter API timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error("OpenRouter API timeout after all retries")
                    return None
                    
            except aiohttp.ClientError as e:
                logger.warning(f"OpenRouter API client error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"OpenRouter API client error after all retries: {e}")
                    return None
                    
            except Exception as e:
                logger.error(f"OpenRouter API unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"OpenRouter API unexpected error after all retries: {e}")
                    return None
        
        logger.error("OpenRouter API call failed after all retry attempts")
        return None
    
    async def _generate_openrouter_response(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using OpenRouter API with enhanced context and error handling"""
        try:
            # Build enhanced system prompt with current context
            enhanced_system_prompt = self._build_enhanced_system_prompt(context)
            
            # Build conversation history with better context preservation
            messages = [{"role": "system", "content": enhanced_system_prompt}]
            
            # Add recent conversation history for context (last 5 interactions)
            if 'conversation_history' in context and context['conversation_history']:
                recent_history = context['conversation_history'][-5:]
                for item in recent_history:
                    if 'intent' in item and 'entities' in item:
                        # Add user intent as user message
                        user_content = f"Previous request: Intent was '{item['intent']}'"
                        if item['entities']:
                            user_content += f" with entities: {json.dumps(item['entities'])}"
                        messages.append({"role": "user", "content": user_content})
                        
                        # Add assistant response as assistant message
                        assistant_content = "I processed that request and am ready for your next question."
                        messages.append({"role": "assistant", "content": assistant_content})
            
            # Add current message with context about available capabilities
            current_context = self._get_current_context_for_openrouter(context)
            enhanced_user_message = f"{message}\n\nContext: {current_context}"
            messages.append({"role": "user", "content": enhanced_user_message})
            
            # Try to get response from OpenRouter with fallback handling
            response = await self._call_openrouter_api(messages)
            
            if response:
                logger.info(f"OpenRouter response generated successfully")
                
                # Validate response quality
                if self._is_valid_openrouter_response(response):
                    return response
                else:
                    logger.warning("OpenRouter response failed quality validation, falling back to pattern-based")
                    return None
            
            logger.info("OpenRouter API returned no response, will fall back to pattern-based")
            return None
            
        except Exception as e:
            logger.error(f"Error generating OpenRouter response: {e}")
            return None
    
    def _build_enhanced_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build enhanced system prompt with current context"""
        base_prompt = self.system_prompt
        
        # Add user context if available
        user_context = ""
        if context and 'user_id' in context:
            user_context += f" You are assisting user {context['user_id']}."
        
        # Add email/calendar context if available
        if context and 'user_email' in context:
            user_context += f" User email: {context['user_email']}."
        
        # Add current time context
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        user_context += f" Current time: {current_time}."
        
        enhanced_prompt = f"""{base_prompt}

Current Context:{user_context}

You are dhii, a specialized AI assistant for email and calendar management. Your responses should be:
- Helpful and specific to email/calendar tasks
- Natural and conversational
- Action-oriented with clear next steps
- Context-aware of the user's previous requests
- Professional but friendly

When responding:
1. Acknowledge the user's request clearly
2. Provide relevant, actionable information
3. Suggest specific next steps or alternatives
4. Keep responses concise but comprehensive
5. Use appropriate formatting (bullet points, emojis) when helpful"""
        
        return enhanced_prompt
    
    def _get_current_context_for_openrouter(self, context: Dict[str, Any]) -> str:
        """Get current context information for OpenRouter"""
        context_parts = []
        
        # Add email account context
        if context and 'user_id' in context:
            from email_manager import email_manager
            try:
                email_accounts = email_manager.get_email_accounts(context['user_id'])
                if email_accounts:
                    context_parts.append(f"User has {len(email_accounts)} email account(s) configured")
                else:
                    context_parts.append("User has no email accounts configured yet")
            except Exception:
                context_parts.append("Email account status unknown")
        
        # Add calendar context
        context_parts.append("Calendar integration available")
        
        # Add recent activity context
        if context and 'conversation_history' in context and context['conversation_history']:
            recent_intents = [item['intent'] for item in context['conversation_history'][-3:] if 'intent' in item]
            if recent_intents:
                context_parts.append(f"Recent user activities: {', '.join(set(recent_intents))}")
        
        return "; ".join(context_parts) if context_parts else "Email and calendar management system ready"
    
    def _is_valid_openrouter_response(self, response: str) -> bool:
        """Validate OpenRouter response quality"""
        if not response or not response.strip():
            return False
        
        response = response.strip()
        
        # Check for obviously problematic responses
        if len(response) < 5:  # Too short
            return False
        
        if len(response) > 2000:  # Too long for typical responses
            return False
        
        # Check for repetitive or nonsensical patterns
        if response.count(response[:20]) > 3:  # Highly repetitive
            return False
        
        # Check for inappropriate content (basic filter)
        inappropriate_words = ['<script', 'javascript:', 'data:', 'vbscript:', 'onload', 'onerror']
        if any(word in response.lower() for word in inappropriate_words):
            return False
        
        # Check if response is relevant to email/calendar context
        relevant_keywords = ['email', 'meeting', 'calendar', 'schedule', 'send', 'appointment', 'contact']
        if not any(keyword in response.lower() for keyword in relevant_keywords):
            # If no relevant keywords, check if it's a general greeting/help response
            general_keywords = ['hello', 'hi', 'help', 'assist', 'welcome', 'good']
            if not any(keyword in response.lower() for keyword in general_keywords):
                logger.warning("OpenRouter response lacks relevant context keywords")
                return False
        
        return True

# Global AI engine instance
ai_engine = AIEngine()

# Export the engine and models
__all__ = ['AIEngine', 'AIIntent', 'AIResponse', 'ai_engine']