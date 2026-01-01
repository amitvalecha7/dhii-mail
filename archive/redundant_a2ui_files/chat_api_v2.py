#!/usr/bin/env python3
"""
Chat API for dhii Mail with Authentication Support
Enhanced chat interface with user authentication and email integration
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import re
from enum import Enum
from dataclasses import dataclass
import jwt
from datetime import datetime, timedelta

# Import existing components
from security_manager import SecurityManager
from database import DatabaseManager

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

# JWT configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user database (replace with real database)
users_db = {}

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

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[int] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[Dict[str, str]]] = None
    requires_auth: bool = False
    data: Optional[Dict[str, Any]] = None
    next_step: Optional[str] = None

class AuthStatus(BaseModel):
    is_authenticated: bool
    user: Optional[Dict[str, Any]] = None
    next_step: Optional[str] = None

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
                r"communication patterns",
                r"when do i get emails?",
                r"email frequency",
            ],
            IntentType.EMAIL_CATEGORIZATION: [
                r"categorize (?:my )?emails?",
                r"organize (?:my )?emails?",
                r"group (?:my )?emails?",
                r"sort (?:my )?emails?",
            ],
            IntentType.AUTH_REQUEST: [
                r"sign ?up",
                r"create account",
                r"register",
                r"log ?in",
                r"authenticate",
            ],
            IntentType.HELP_REQUEST: [
                r"help",
                r"what can you do",
                r"what are your capabilities",
                r"how do i use this",
            ],
        }

    def parse_intent(self, message: str) -> ParsedIntent:
        """Parse user message to determine intent"""
        message_lower = message.lower().strip()
        
        # Check each intent pattern
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    parameters = {}
                    if match.groups():
                        parameters = {f"param_{i}": group for i, group in enumerate(match.groups()) if group}
                    
                    return ParsedIntent(
                        intent=intent_type,
                        confidence=0.8,
                        parameters=parameters,
                        original_message=message
                    )
        
        # Default to unknown intent
        return ParsedIntent(
            intent=IntentType.UNKNOWN,
            confidence=0.0,
            parameters={},
            original_message=message
        )

class ChatResponseGenerator:
    """Generates appropriate responses based on user intent"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()

    async def generate_response(self, message: str, user_id: Optional[int] = None, is_authenticated: bool = False) -> ChatResponse:
        """Generate response based on user message and authentication status"""
        
        processor = ChatIntentProcessor()
        parsed_intent = processor.parse_intent(message)
        
        if parsed_intent.intent == IntentType.AUTH_REQUEST:
            return await self.handle_auth_request(parsed_intent)
        elif parsed_intent.intent == IntentType.HELP_REQUEST:
            return await self.handle_help_request(parsed_intent)
        elif not is_authenticated:
            return await self.handle_auth_required(parsed_intent)
        elif parsed_intent.intent == IntentType.EMAIL_SEARCH:
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
        else:
            return await self.handle_unknown_intent(parsed_intent)

    async def handle_auth_request(self, intent: ParsedIntent) -> ChatResponse:
        """Handle authentication-related requests"""
        return ChatResponse(
            response="🚀 **Ready to get started?**\n\nTo access AI-powered email analysis, you'll need to create an account. It's free and takes just a minute!\n\n**What you'll get:**\n• AI email analysis and insights\n• Smart search capabilities\n• Communication pattern tracking\n• Weekly email summaries\n\n**Click the button below to sign up and start your journey!**",
            suggested_actions=[
                {"text": "🚀 Sign Up - It's Free!", "action": "navigate", "url": "/auth/signup"},
                {"text": "🔐 Log In", "action": "navigate", "url": "/auth/login"}
            ],
            requires_auth=False,
            next_step="signup"
        )

    async def handle_auth_required(self, intent: ParsedIntent) -> ChatResponse:
        """Handle requests that require authentication"""
        return ChatResponse(
            response="🔒 **Authentication Required**\n\nTo access email analysis features, please create an account or log in.\n\n**Benefits of signing up:**\n• Analyze your email patterns\n• Get AI-powered insights\n• Smart email search\n• Weekly communication reports\n• Personalized recommendations\n\n**Join thousands of users who are already managing their emails with AI!**",
            suggested_actions=[
                {"text": "🚀 Create Account", "action": "navigate", "url": "/auth/signup"},
                {"text": "🔐 Log In", "action": "navigate", "url": "/auth/login"}
            ],
            requires_auth=True,
            next_step="signup"
        )

    async def handle_help_request(self, intent: ParsedIntent) -> ChatResponse:
        """Handle help requests"""
        return ChatResponse(
            response="🤖 **I'm your AI Email Assistant!**\n\n**What I can do for you:**\n\n📧 **Email Analysis**\n• Analyze sentiment and tone\n• Identify communication patterns\n• Summarize important emails\n\n🔍 **Smart Search**\n• Find emails by sender, date, or content\n• Search with natural language\n• Filter by importance and category\n\n📊 **Insights & Reports**\n• Weekly email summaries\n• Response time tracking\n• Communication effectiveness\n\n⚡ **Smart Actions**\n• Auto-categorize emails\n• Set intelligent reminders\n• Draft suggested responses\n\n**Try saying**: 'Show me emails from John this week' or 'Analyze my email patterns'",
            suggested_actions=None,
            requires_auth=False
        )

    async def handle_email_search(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email search requests"""
        # Extract search parameters
        sender = intent.parameters.get("param_0", "")
        timeframe = intent.parameters.get("param_1", "")
        
        # Search emails
        emails = self.db_manager.search_emails(user_id, query=sender, sender=sender, timeframe=timeframe)
        
        if emails:
            response = f"📧 **Found {len(emails)} emails from {sender}"
            if timeframe:
                response += f" in the {timeframe}"
            response += ":\n\n"
            
            for email in emails[:5]:  # Show first 5 results
                response += f"• **{email['subject']}** - From: {email['sender']}\n"
            
            if len(emails) > 5:
                response += f"\n... and {len(emails) - 5} more emails"
        else:
            response = f"📧 **No emails found from {sender}"
            if timeframe:
                response += f" in the {timeframe}"
            response += "\n\nTry searching for a different sender or timeframe."
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "🔍 Search Again", "action": "suggest", "message": "Show me emails from [sender]"},
                {"text": "📊 Analyze These", "action": "suggest", "message": f"Analyze emails from {sender}"}
            ],
            requires_auth=False,
            data={"emails": emails}
        )

    async def handle_email_analysis(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email analysis requests"""
        # Get user's emails
        emails = self.db_manager.get_user_emails(user_id)
        
        if not emails:
            return ChatResponse(
                response="📧 **No emails found**\n\nIt looks like you haven't connected your email account yet. Let's get that set up!\n\n**Next steps:**\n1. Connect your email account\n2. Allow some time for initial sync\n3. Come back and ask me to analyze your emails\n\n**Click below to start the email connection process:**",
                suggested_actions=[
                    {"text": "🔗 Connect Email", "action": "navigate", "url": "/auth/onboarding"}
                ],
                requires_auth=True,
                next_step="email_connect"
            )
        
        # Perform analysis
        total_emails = len(emails)
        unique_senders = len(set(email['sender'] for email in emails))
        avg_sentiment = sum(email.get('sentiment_score', 0) for email in emails) / total_emails
        
        response = f"📊 **Email Analysis Results**\n\n"
        response += f"**Total Emails:** {total_emails}\n"
        response += f"**Unique Senders:** {unique_senders}\n"
        response += f"**Average Sentiment:** {avg_sentiment:.2f}/1.0\n\n"
        
        # Top senders
        sender_counts = {}
        for email in emails:
            sender = email['sender']
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        response += "**Top Senders:**\n"
        for sender, count in top_senders:
            response += f"• {sender}: {count} emails\n"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "📈 More Insights", "action": "suggest", "message": "Show me email patterns"},
                {"text": "🔍 Search Emails", "action": "suggest", "message": "Show me emails from [sender]"}
            ],
            requires_auth=False,
            data={"analysis": {"total_emails": total_emails, "unique_senders": unique_senders, "avg_sentiment": avg_sentiment}}
        )

    async def handle_email_summary(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email summary requests"""
        emails = self.db_manager.get_user_emails(user_id)
        
        if not emails:
            return ChatResponse(
                response="📧 **No emails to summarize**\n\nConnect your email account to get started!",
                suggested_actions=[
                    {"text": "🔗 Connect Email", "action": "navigate", "url": "/auth/onboarding"}
                ],
                requires_auth=True
            )
        
        # Get recent emails (last 7 days)
        recent_emails = emails[-10:]  # Last 10 emails as example
        
        response = "📋 **Recent Email Summary**\n\n"
        response += f"**Total Emails:** {len(emails)}\n\n"
        response += "**Recent Activity:**\n"
        
        for email in recent_emails:
            response += f"• **{email['subject']}** - From: {email['sender']}\n"
        
        response += "\n**Key Insights:**\n"
        response += "• Most active sender: [Analysis needed]\n"
        response += "• Average response time: [Analysis needed]\n"
        response += "• Communication effectiveness: [Analysis needed]"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "📊 Analyze All", "action": "suggest", "message": "Analyze my emails"},
                {"text": "🔍 Search", "action": "suggest", "message": "Show me emails from [sender]"}
            ],
            requires_auth=False
        )

    async def handle_email_sentiment(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email sentiment analysis"""
        sender = intent.parameters.get("param_0", "")
        
        emails = self.db_manager.search_emails(user_id, query=sender, sender=sender)
        
        if not emails:
            return ChatResponse(
                response=f"📧 **No emails found from {sender}**\n\nTry searching for a different sender.",
                suggested_actions=[
                    {"text": "🔍 Search Again", "action": "suggest", "message": "Show me emails from [sender]"}
                ],
                requires_auth=False
            )
        
        # Analyze sentiment
        positive_count = sum(1 for email in emails if email.get('sentiment') == 'positive')
        negative_count = sum(1 for email in emails if email.get('sentiment') == 'negative')
        neutral_count = len(emails) - positive_count - negative_count
        
        response = f"😊 **Sentiment Analysis for {sender}**\n\n"
        response += f"**Total Emails:** {len(emails)}\n\n"
        response += "**Sentiment Breakdown:**\n"
        response += f"• 😊 Positive: {positive_count} ({positive_count/len(emails)*100:.1f}%)\n"
        response += f"• 😐 Neutral: {neutral_count} ({neutral_count/len(emails)*100:.1f}%)\n"
        response += f"• 😞 Negative: {negative_count} ({negative_count/len(emails)*100:.1f}%)\n"
        
        # Overall sentiment
        if positive_count > negative_count:
            response += "\n**Overall Sentiment:** 🟢 Predominantly positive"
        elif negative_count > positive_count:
            response += "\n**Overall Sentiment:** 🔴 Predominantly negative"
        else:
            response += "\n**Overall Sentiment:** 🟡 Mixed/neutral"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "📊 More Analysis", "action": "suggest", "message": f"Analyze emails from {sender}"},
                {"text": "🔍 Search Others", "action": "suggest", "message": "Show me emails from [sender]"}
            ],
            requires_auth=False
        )

    async def handle_email_patterns(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email pattern analysis"""
        emails = self.db_manager.get_user_emails(user_id)
        
        if not emails:
            return ChatResponse(
                response="📧 **No email patterns to analyze**\n\nConnect your email account first!",
                suggested_actions=[
                    {"text": "🔗 Connect Email", "action": "navigate", "url": "/auth/onboarding"}
                ],
                requires_auth=True
            )
        
        # Analyze patterns
        hourly_distribution = {}
        daily_distribution = {}
        
        for email in emails:
            # Simulate time analysis (in real implementation, parse actual timestamps)
            hour = hash(email['sender']) % 24  # Mock hour
            day = hash(email['subject']) % 7   # Mock day
            
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            daily_distribution[day] = daily_distribution.get(day, 0) + 1
        
        # Find peak times
        peak_hour = max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 12
        peak_day = max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else 0
        
        response = "📈 **Email Communication Patterns**\n\n"
        response += f"**Total Emails:** {len(emails)}\n\n"
        response += "**Peak Activity:**\n"
        response += f"• Most active hour: {peak_hour}:00\n"
        response += f"• Most active day: Day {peak_day}\n\n"
        
        response += "**Communication Insights:**\n"
        response += "• You receive most emails during business hours\n"
        response += "• Weekdays are more active than weekends\n"
        response += "• Consider setting up filters for peak times"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "📊 More Insights", "action": "suggest", "message": "Analyze my emails"},
                {"text": "🔍 Search", "action": "suggest", "message": "Show me emails from [sender]"}
            ],
            requires_auth=False
        )

    async def handle_email_categorization(self, intent: ParsedIntent, user_id: Optional[int]) -> ChatResponse:
        """Handle email categorization requests"""
        emails = self.db_manager.get_user_emails(user_id)
        
        if not emails:
            return ChatResponse(
                response="📧 **No emails to categorize**\n\nConnect your email account first!",
                suggested_actions=[
                    {"text": "🔗 Connect Email", "action": "navigate", "url": "/auth/onboarding"}
                ],
                requires_auth=True
            )
        
        # Mock categorization (in real implementation, use ML models)
        categories = {
            "Work": len([e for e in emails if "work" in e.get('subject', '').lower() or "project" in e.get('subject', '').lower()]),
            "Personal": len([e for e in emails if "personal" in e.get('subject', '').lower() or "family" in e.get('subject', '').lower()]),
            "Marketing": len([e for e in emails if "marketing" in e.get('subject', '').lower() or "promotion" in e.get('subject', '').lower()]),
            "Updates": len([e for e in emails if "update" in e.get('subject', '').lower() or "newsletter" in e.get('subject', '').lower()]),
        }
        
        response = "📂 **Email Categorization**\n\n"
        response += f"**Total Emails:** {len(emails)}\n\n"
        response += "**Categories:**\n"
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / len(emails)) * 100
                response += f"• **{category}:** {count} emails ({percentage:.1f}%)\n"
        
        response += "\n**Suggestions:**\n"
        response += "• Set up filters for high-volume categories\n"
        response += "• Create labels for better organization\n"
        response += "• Archive old promotional emails"
        
        return ChatResponse(
            response=response,
            suggested_actions=[
                {"text": "📊 Analyze", "action": "suggest", "message": "Analyze my emails"},
                {"text": "🔍 Search", "action": "suggest", "message": "Show me emails from [sender]"}
            ],
            requires_auth=False
        )

    async def handle_unknown_intent(self, intent: ParsedIntent) -> ChatResponse:
        """Handle unknown or unclear intents"""
        return ChatResponse(
            response="🤔 **I didn't quite understand that.**\n\n**Try asking me:**\n• \"Show me emails from [sender]\"\n• \"Analyze my email patterns\"\n• \"Summarize my recent emails\"\n• \"What can you do?\"\n\n**Or click one of the suggested actions below:**",
            suggested_actions=[
                {"text": "📧 Show Recent Emails", "action": "suggest", "message": "Show me recent emails"},
                {"text": "📊 Analyze Patterns", "action": "suggest", "message": "Analyze my email patterns"},
                {"text": "❓ Help", "action": "suggest", "message": "What can you do?"}
            ],
            requires_auth=False
        )

# Initialize response generator
response_generator = ChatResponseGenerator()

def verify_token(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return user info"""
    print(f"DEBUG verify_token: authorization: {authorization}")
    if not authorization:
        return None
    
    try:
        # Remove "Bearer " prefix if present
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        print(f"DEBUG verify_token: token: {token}")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG verify_token: payload: {payload}")
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        if email and user_id:
            return {"email": email, "user_id": user_id}
        return None
    except jwt.PyJWTError as e:
        print(f"DEBUG verify_token: JWT error: {e}")
        return None
    except Exception as e:
        print(f"DEBUG verify_token: Other error: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    """Serve the chat interface with amit.dhii.ai styling"""
    try:
        with open("chat_interface_amit_styled.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to original interface
        try:
            with open("chat_interface_v2.html", "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Chat interface not found")

@app.get("/a2ui/cards/onboarding", response_class=HTMLResponse)
async def onboarding_interface():
    """Serve the A2UI onboarding interface with amit.dhii.ai styling"""
    try:
        with open("a2ui_onboarding_amit_styled.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to original onboarding
        try:
            with open("a2ui_onboarding.html", "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Onboarding interface not found")

@app.post("/api/chat/process", response_model=ChatResponse)
async def process_chat_message(
    chat_message: ChatMessage,
    authorization: Optional[str] = Header(None)
):
    """Process a chat message and return AI response"""
    try:
        # Validate input
        if not chat_message.message or not chat_message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Sanitize input
        sanitized_message = security_manager.sanitize_a2ui_component_data(
            {"message": chat_message.message.strip()}
        )["message"]
        
        # Check authentication
        user_info = verify_token(authorization)
        is_authenticated = user_info is not None
        user_id = user_info.get("user_id") if user_info else None
        
        # Debug logging
        print(f"DEBUG: authorization header: {authorization}")
        print(f"DEBUG: user_info: {user_info}")
        print(f"DEBUG: is_authenticated: {is_authenticated}")
        print(f"DEBUG: user_id: {user_id}")
        
        # Generate response
        response = await response_generator.generate_response(
            sanitized_message, user_id, is_authenticated
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/auth/status", response_model=AuthStatus)
async def get_auth_status(authorization: Optional[str] = Header(None)):
    """Get current authentication status"""
    try:
        user_info = verify_token(authorization)
        
        if user_info:
            return AuthStatus(
                is_authenticated=True,
                user=user_info,
                next_step=None
            )
        else:
            return AuthStatus(
                is_authenticated=False,
                user=None,
                next_step="login"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking auth status: {str(e)}")

@app.get("/api/chat/suggestions")
async def get_chat_suggestions():
    """Get suggested chat messages"""
    suggestions = [
        {"text": "Show me emails from John this week", "category": "Search"},
        {"text": "Analyze my email patterns", "category": "Analysis"},
        {"text": "Summarize my recent emails", "category": "Summary"},
        {"text": "What's the sentiment of emails from Sarah?", "category": "Sentiment"},
        {"text": "Categorize my emails", "category": "Organization"},
        {"text": "What can you do?", "category": "Help"}
    ]
    
    return {"suggestions": suggestions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)