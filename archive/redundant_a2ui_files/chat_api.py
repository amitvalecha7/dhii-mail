#!/usr/bin/env python3
"""
Chat Interface API for dhii Mail
Handles natural language processing and AI-based email analysis
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import re
import json
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
from enum import Enum

# Import existing components
from security_manager import SecurityManager
from database_manager import DatabaseManager
from a2ui_card_implementation import A2UICardRenderer

app = FastAPI(title="dhii Mail Chat API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
security_manager = SecurityManager()
database_manager = DatabaseManager()
card_renderer = A2UICardRenderer()

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[Dict[str, Any]]] = None
    requires_auth: bool = False
    data: Optional[Dict[str, Any]] = None

class IntentType(Enum):
    EMAIL_SEARCH = "email_search"
    EMAIL_ANALYSIS = "email_analysis"
    EMAIL_SUMMARY = "email_summary"
    EMAIL_SENTIMENT = "email_sentiment"
    EMAIL_PATTERNS = "email_patterns"
    EMAIL_CATEGORIZATION = "email_categorization"
    AUTH_REQUEST = "auth_request"
    HELP_REQUEST = "help_request"
    UNKNOWN = "unknown"

@dataclass
class ParsedIntent:
    intent: IntentType
    confidence: float
    parameters: Dict[str, Any]
    original_message: str

class ChatIntentProcessor:
    """Processes natural language to determine user intent"""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.EMAIL_SEARCH: [
                r"show me emails? (?:from|by) (.+?)(?: (?:this|last) (\w+))?",
                r"find emails? (?:from|by) (.+?)(?: (?:this|last) (\w+))?",
                r"emails? (?:from|by) (.+?)(?: (?:this|last) (\w+))?",
                r"search for emails? (?:from|by) (.+?)(?: (?:this|last) (\w+))?",
            ],
            IntentType.EMAIL_ANALYSIS: [
                r"analyze (.+?) emails?",
                r"what can you tell me about (.+?) emails?",
                r"give me insights on (.+?) emails?",
                r"analyze my email patterns",
            ],
            IntentType.EMAIL_SUMMARY: [
                r"summarize (?:my )?emails?",
                r"give me a summary of (?:my )?emails?",
                r"what are (?:my )?important emails?",
                r"show me (?:my )?key emails?",
            ],
            IntentType.EMAIL_SENTIMENT: [
                r"sentiment of (.+?) emails?",
                r"how do (.+?) emails? feel",
                r"tone of (.+?) emails?",
                r"emotion in (.+?) emails?",
            ],
            IntentType.EMAIL_PATTERNS: [
                r"email patterns",
                r"patterns in (?:my )?emails?",
                r"email trends",
                r"communication patterns",
            ],
            IntentType.EMAIL_CATEGORIZATION: [
                r"categorize (.+?) emails?",
                r"group (.+?) emails?",
                r"organize (.+?) emails?",
                r"sort (.+?) emails?",
            ],
            IntentType.AUTH_REQUEST: [
                r"sign up",
                r"signup",
                r"create account",
                r"register",
                r"log in",
                r"login",
                r"sign in",
            ],
            IntentType.HELP_REQUEST: [
                r"help",
                r"what can you do",
                r"what are your capabilities",
                r"show me what you can do",
                r"\?",
            ]
        }
    
    def parse_intent(self, message: str) -> ParsedIntent:
        """Parse user message to determine intent"""
        message_lower = message.lower().strip()
        
        # Check each intent type
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    parameters = self.extract_parameters(intent_type, match, message_lower)
                    confidence = self.calculate_confidence(intent_type, message_lower, match)
                    
                    return ParsedIntent(
                        intent=intent_type,
                        confidence=confidence,
                        parameters=parameters,
                        original_message=message
                    )
        
        # Default to unknown with keyword extraction
        return ParsedIntent(
            intent=IntentType.UNKNOWN,
            confidence=0.1,
            parameters={"keywords": self.extract_keywords(message_lower)},
            original_message=message
        )
    
    def extract_parameters(self, intent_type: IntentType, match: re.Match, message: str) -> Dict[str, Any]:
        """Extract relevant parameters based on intent"""
        parameters = {}
        
        if intent_type == IntentType.EMAIL_SEARCH:
            if match.group(1):
                parameters["sender"] = match.group(1).strip()
            if len(match.groups()) > 1 and match.group(2):
                parameters["timeframe"] = match.group(2).strip()
        
        elif intent_type == IntentType.EMAIL_SENTIMENT:
            if match.group(1):
                parameters["target"] = match.group(1).strip()
        
        elif intent_type == IntentType.EMAIL_ANALYSIS:
            if match.group(1):
                parameters["target"] = match.group(1).strip()
        
        elif intent_type == IntentType.EMAIL_CATEGORIZATION:
            if match.group(1):
                parameters["category"] = match.group(1).strip()
        
        # Add time-based parameters
        if "today" in message:
            parameters["date_range"] = "today"
        elif "this week" in message:
            parameters["date_range"] = "this_week"
        elif "last week" in message:
            parameters["date_range"] = "last_week"
        elif "this month" in message:
            parameters["date_range"] = "this_month"
        
        return parameters
    
    def calculate_confidence(self, intent_type: IntentType, message: str, match: re.Match) -> float:
        """Calculate confidence score for the intent"""
        base_confidence = 0.7
        
        # Boost confidence for longer matches
        match_length = len(match.group(0))
        if match_length > 10:
            base_confidence += 0.1
        
        # Reduce confidence for very short messages
        if len(message) < 5:
            base_confidence -= 0.2
        
        # Check for email-related keywords
        email_keywords = ["email", "mail", "message", "inbox"]
        if any(keyword in message for keyword in email_keywords):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def extract_keywords(self, message: str) -> List[str]:
        """Extract keywords from unknown messages"""
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        
        words = message.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Return top 5 keywords

class ChatResponseGenerator:
    """Generates appropriate responses based on parsed intent"""
    
    def __init__(self):
        self.intent_processor = ChatIntentProcessor()
    
    async def generate_response(self, message: str, user_id: Optional[int] = None) -> ChatResponse:
        """Generate response for user message"""
        
        # Parse intent
        parsed_intent = self.intent_processor.parse_intent(message)
        
        # Route to appropriate handler
        if parsed_intent.intent == IntentType.EMAIL_SEARCH:
            return await self.handle_email_search(parsed_intent, user_id)
        elif parsed_intent.intent == IntentType.EMAIL_ANALYSIS:
            return await self.handle_email_analysis(parsed_intent, user_id)
        elif parsed_intent.intent == IntentType.EMAIL_SUMMARY:
            return await self.handle_email_summary(parsed_intent, user_id)
        elif parsed_intent.intent == IntentType.EMAIL_SENTIMENT:
            return await self.handle_email_sentiment(parsed_intent, user_id)
        elif parsed_intent.intent == IntentType.EMAIL_PATTERNS:
            return await self.handle_email_patterns(parsed_intent, user_id)
        elif parsed_intent.intent == IntentType.EMAIL_CATEGORIZATION:
            return await self.handle_email_categorization(parsed_intent, user_id)
        elif parsed_intent.intent == IntentType.AUTH_REQUEST:
            return self.handle_auth_request(parsed_intent)
        elif parsed_intent.intent == IntentType.HELP_REQUEST:
            return self.handle_help_request(parsed_intent)
        else:
            return self.handle_unknown_intent(parsed_intent)
    
    async def handle_email_search(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email search requests"""
        if not user_id:
            return ChatResponse(
                response="I'd be happy to search your emails! First, I need to connect to your email account. Would you like to sign up or log in?",
                requires_auth=True,
                suggested_actions=[
                    {"text": "Sign Up", "action": "signup"},
                    {"text": "Log In", "action": "login"}
                ]
            )
        
        sender = intent.parameters.get("sender", "unknown")
        timeframe = intent.parameters.get("timeframe", "recent")
        
        # Simulate email search (would connect to actual email service)
        response = f"🔍 **Searching emails from {sender}**\n\n"
        response += f"Timeframe: {timeframe}\n\n"
        response += "I found 3 emails from this sender:\n\n"
        response += "**Recent Email** (2 hours ago)\n"
        response += "Subject: Project Update\n"
        response += "Preview: The project is progressing well...\n\n"
        response += "Would you like me to show you the full content or analyze these emails?"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "Show Full Content", "action": "show_content"},
                {"text": "Analyze Emails", "action": "analyze"},
                {"text": "Search More", "action": "search_again"}
            ]
        )
    
    async def handle_email_analysis(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email analysis requests"""
        if not user_id:
            return ChatResponse(
                response="I can provide detailed email analysis! Let me connect to your account first.",
                requires_auth=True
            )
        
        target = intent.parameters.get("target", "your recent")
        
        response = f"📊 **Analysis of {target} emails**\n\n"
        response += "**Key Insights:**\n\n"
        response += "• **Communication Volume**: 24 emails this week\n"
        response += "• **Response Rate**: 85% (excellent engagement)\n"
        response += "• **Peak Hours**: 9-11 AM and 2-4 PM\n"
        response += "• **Top Senders**: Team leads (40%), Clients (30%), Partners (30%)\n\n"
        response += "**Sentiment Analysis**:\n"
        response += "• Positive: 65% 😊\n"
        response += "• Neutral: 25% 😐\n"
        response += "• Requires Attention: 10% ⚠️\n\n"
        response += "Would you like me to dive deeper into any specific aspect?"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "Sentiment Details", "action": "sentiment"},
                {"text": "Response Patterns", "action": "patterns"},
                {"text": "Weekly Report", "action": "report"}
            ]
        )
    
    async def handle_email_summary(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email summary requests"""
        if not user_id:
            return ChatResponse(
                response="I can summarize your important emails! Let me access your account first.",
                requires_auth=True
            )
        
        date_range = intent.parameters.get("date_range", "today")
        
        response = f"📋 **Email Summary for {date_range.title()}**\n\n"
        response += "**Important Emails (3)**:\n\n"
        response += "1. **Project Deadline Reminder**\n"
        response += "   From: Project Manager\n"
        response += "   Action needed: Submit report by EOD\n\n"
        response += "2. **Client Meeting Request**\n"
        response += "   From: Important Client\n"
        response += "   Schedule: Tomorrow 2 PM\n\n"
        response += "3. **Invoice Approval Required**\n"
        response += "   From: Finance Team\n"
        response += "   Amount: $5,000\n\n"
        response += "**Other Emails**: 12 less urgent emails categorized automatically.\n\n"
        response += "Would you like me to help you respond to any of these?"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "Draft Responses", "action": "draft"},
                {"text": "Set Reminders", "action": "remind"},
                {"text": "View All", "action": "view_all"}
            ]
        )
    
    async def handle_email_sentiment(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle sentiment analysis requests"""
        if not user_id:
            return ChatResponse(
                response="I can analyze the sentiment of your emails! Let me connect to your account first.",
                requires_auth=True
            )
        
        target = intent.parameters.get("target", "your recent")
        
        response = f"😊 **Sentiment Analysis for {target} emails**\n\n"
        response += "**Overall Tone**: Predominantly positive and professional\n\n"
        response += "**Breakdown by Sender Type**:\n\n"
        response += "**Team Communications**:\n"
        response += "• Positive: 70% - Great team morale!\n"
        response += "• Neutral: 25% - Task-focused discussions\n"
        response += "• Concerned: 5% - Minor project issues\n\n"
        response += "**Client Communications**:\n"
        response += "• Satisfied: 80% - Happy with progress\n"
        response += "• Neutral: 15% - Information requests\n"
        response += "• Concerned: 5% - Timeline questions\n\n"
        response += "**Recommendations**: Your communication style is effective! Keep maintaining that positive tone."
        
        return ChatResponse(response=response)
    
    async def handle_email_patterns(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email pattern analysis"""
        if not user_id:
            return ChatResponse(
                response="I can identify patterns in your email communication! Let me access your account first.",
                requires_auth=True
            )
        
        response = "📈 **Email Communication Patterns**\n\n"
        response += "**Sending Patterns**:\n"
        response += "• Most active: Tuesday and Thursday\n"
        response += "• Peak time: 10 AM - 12 PM\n"
        response += "• Average emails/day: 15\n\n"
        response += "**Response Behavior**:\n"
        response += "• Average response time: 2.3 hours\n"
        response += "• Same-day responses: 78%\n"
        response += "• Weekend responses: 12%\n\n"
        response += "**Communication Style**:\n"
        response += "• Concise messages: 65%\n"
        response += "• Detailed explanations: 25%\n"
        response += "• Quick updates: 10%\n\n"
        response += "**Productivity Insights**: You're most responsive in the morning. Consider scheduling important communications before noon."
        
        return ChatResponse(response=response)
    
    async def handle_email_categorization(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email categorization requests"""
        if not user_id:
            return ChatResponse(
                response="I can categorize your emails automatically! Let me connect to your account first.",
                requires_auth=True
            )
        
        category = intent.parameters.get("category", "all")
        
        response = f"📂 **Email Categorization**\n\n"
        response += "**Automatic Categories**:\n\n"
        response += "**High Priority (5)**:\n"
        response += "• Client communications\n"
        response += "• Deadline reminders\n"
        response += "• Meeting requests\n\n"
        response += "**Medium Priority (8)**:\n"
        response += "• Project updates\n"
        response += "• Team communications\n"
        response += "• Information requests\n\n"
        response += "**Low Priority (12)**:\n"
        response += "• Newsletters\n"
        response += "• General announcements\n"
        response += "• FYI messages\n\n"
        response += "**Auto-Actions Set Up**: High priority emails will be flagged and notifications enabled."
        
        return ChatResponse(response=response)
    
    def handle_auth_request(self, intent: ParsedIntent) -> ChatResponse:
        """Handle authentication requests"""
        message_lower = intent.original_message.lower()
        
        if any(word in message_lower for word in ["sign up", "signup", "create", "register"]):
            return ChatResponse(
                response="🚀 **Let's get you started!**\n\nI'll help you create your dhii Mail account. This will allow me to analyze your emails and provide personalized insights.\n\nReady to begin the setup process?",
                suggested_actions=[
                    {"text": "Start Setup", "action": "start_signup"},
                    {"text": "Learn More", "action": "learn_more"}
                ]
            )
        else:
            return ChatResponse(
                response="🔐 **Welcome back!**\n\nPlease enter your email address and password to access your account and email analysis features.",
                suggested_actions=[
                    {"text": "Continue to Login", "action": "show_login"}
                ]
            )
    
    def handle_help_request(self, intent: ParsedIntent) -> ChatResponse:
        """Handle help requests"""
        response = "🤖 **I'm your AI Email Assistant!**\n\n"
        response += "**What I can do for you:**\n\n"
        response += "📧 **Email Analysis**\n"
        response += "• Analyze sentiment and tone\n"
        response += "• Identify communication patterns\n"
        response += "• Summarize important emails\n\n"
        response += "🔍 **Smart Search**\n"
        response += "• Find emails by sender, date, or content\n"
        response += "• Search with natural language\n"
        response += "• Filter by importance and category\n\n"
        response += "📊 **Insights & Reports**\n"
        response += "• Weekly email summaries\n"
        response += "• Response time tracking\n"
        response += "• Communication effectiveness\n\n"
        response += "⚡ **Smart Actions**\n"
        response += "• Auto-categorize emails\n"
        response += "• Set intelligent reminders\n"
        response += "• Draft suggested responses\n\n"
        response += "**Try saying**: 'Show me emails from John this week' or 'Analyze my email patterns'"
        
        return ChatResponse(response=response)
    
    def handle_unknown_intent(self, intent: ParsedIntent) -> ChatResponse:
        """Handle unknown intents with helpful suggestions"""
        keywords = intent.parameters.get("keywords", [])
        
        response = "🤔 **I'm not sure I understand that request.**\n\n"
        response += "**Try these examples:**\n\n"
        response += "• 'Show me emails from [sender]'\n"
        response += "• 'Analyze my email patterns'\n"
        response += "• 'Summarize important emails today'\n"
        response += "• 'What's the sentiment of emails from [person]'\n"
        response += "• 'Find all meeting requests'\n\n"
        response += "Or type 'help' to see everything I can do!"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "Show Examples", "action": "examples"},
                {"text": "Help", "action": "help"}
            ]
        )

# Initialize response generator
response_generator = ChatResponseGenerator()

@app.get("/api/auth/status")
async def get_auth_status(request: Request):
    """Get current authentication status"""
    # Extract session/token from request
    auth_header = request.headers.get("Authorization")
    session_id = request.headers.get("X-Session-ID")
    
    # Mock authentication check (replace with real logic)
    if auth_header or session_id:
        return {
            "authenticated": True,
            "user": {
                "id": 1,
                "email": "user@example.com",
                "name": "Test User"
            }
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }

@app.post("/api/chat/process", response_model=ChatResponse)
async def process_chat_message(chat_message: ChatMessage):
    """Process incoming chat message"""
    try:
        # Validate input
        if not chat_message.message or not chat_message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Sanitize input
        sanitized_message = security_manager.sanitize_a2ui_component_data({
            "message": chat_message.message.strip()
        })["message"]
        
        # Generate response
        response = await response_generator.generate_response(
            sanitized_message, 
            chat_message.user_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/chat/suggestions")
async def get_chat_suggestions(user_id: Optional[int] = None):
    """Get suggested chat starters"""
    suggestions = [
        "Show me important emails from today",
        "Analyze my email patterns this week",
        "What's the sentiment of emails from my team?",
        "Find all meeting requests",
        "Summarize emails from clients",
        "Show me emails I haven't responded to",
        "Analyze communication with [sender name]",
        "Categorize my recent emails"
    ]
    
    return {"suggestions": suggestions}

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_chat_interface():
    """Serve the chat interface HTML"""
    try:
        with open("/root/dhii-mail/chat_interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chat interface not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)