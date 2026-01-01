"""
AI Engine for dhii Mail
Handles natural language processing, intent recognition, and AI responses
"""

import os
import json
import logging
import asyncio
import aiohttp
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
        """Call OpenRouter API for AI response"""
        if not self.use_openrouter:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dhii-mail.local",  # Replace with your actual domain
            "X-Title": "dhii Mail AI Assistant"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openrouter_api_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content'].strip()
                    else:
                        logger.error(f"OpenRouter API error: {response.status} - {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            return None
    
    async def _generate_openrouter_response(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using OpenRouter API"""
        # Build conversation history
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history if available
        if 'conversation_history' in context:
            for item in context['conversation_history'][-5:]:  # Last 5 messages
                messages.append({"role": "user", "content": f"Intent: {item['intent']}"})
                messages.append({"role": "assistant", "content": f"Entities: {json.dumps(item['entities'])}"})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Try to get response from OpenRouter
        response = await self._call_openrouter_api(messages)
        
        if response:
            logger.info(f"OpenRouter response generated successfully")
            return response
        
        return None

# Global AI engine instance
ai_engine = AIEngine()

# Export the engine and models
__all__ = ['AIEngine', 'AIIntent', 'AIResponse', 'ai_engine']