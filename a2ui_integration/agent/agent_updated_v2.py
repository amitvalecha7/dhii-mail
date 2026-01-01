"""
Updated Meeting Assistant Agent for A2UI Integration
Uses the new database-compatible meeting tools
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

# Google ADK imports
from google.adk import Agent
from google.adk.models import LiteLlm
from google.genai import types

# Import the updated meeting tools
from .meeting_tools_updated_v2 import (
    get_upcoming_meetings,
    get_available_time_slots,
    book_meeting,
    get_meeting_details,
    cancel_meeting,
    update_meeting,
    get_user_meeting_preferences
)

logger = logging.getLogger(__name__)

# Agent instruction template
AGENT_INSTRUCTION = """You are a helpful meeting assistant that can help users manage their meetings.

You have access to the following tools:
- get_upcoming_meetings: Get user's upcoming meetings
- get_available_time_slots: Get available time slots for booking
- book_meeting: Book a new meeting
- get_meeting_details: Get detailed information about a meeting
- cancel_meeting: Cancel a meeting
- update_meeting: Update meeting details
- get_user_meeting_preferences: Get user's meeting preferences

When users ask about meetings, use these tools to help them. Be conversational and helpful.

For booking meetings:
1. Ask for required information (title, date, time, participants)
2. Use get_available_time_slots to show available times
3. Use book_meeting to create the meeting

For A2UI responses, format your output to be compatible with the A2UI component system.
"""

def create_meeting_agent() -> Agent:
    """Create and configure the meeting assistant agent"""
    
    # Configure the LLM model using Google AI Studio API directly
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    # Use Gemini directly through ADK's native integration
    from google.adk.models import Gemini
    model = Gemini(
        model="gemini-2.0-flash-exp",
        api_key=api_key,
        generation_config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.8,
            top_k=40
        )
    )
    
    # Create the agent with tools
    agent = Agent(
        model=model,
        name="meeting_assistant",
        instruction=AGENT_INSTRUCTION,
        tools=[
            get_upcoming_meetings,
            get_available_time_slots,
            book_meeting,
            get_meeting_details,
            cancel_meeting,
            update_meeting,
            get_user_meeting_preferences
        ]
    )
    
    return agent

def extract_date_from_input(user_input: str) -> str:
    """Extract date from user input"""
    import re
    from datetime import datetime, timedelta
    
    # Common date patterns
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
        r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
        r'(\d{2}-\d{2}-\d{4})',  # MM-DD-YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, user_input)
        if match:
            return match.group(1)
    
    # Handle relative dates
    if 'today' in user_input.lower():
        return datetime.now().strftime('%Y-%m-%d')
    elif 'tomorrow' in user_input.lower():
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'next week' in user_input.lower():
        return (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')
    
    # Default to today
    return datetime.now().strftime('%Y-%m-%d')

def extract_time_from_input(user_input: str) -> str:
    """Extract time from user input"""
    import re
    
    # Common time patterns
    time_patterns = [
        r'(\d{1,2}:\d{2})\s*(AM|PM|am|pm)?',  # 3:30 PM or 15:30
        r'(\d{1,2})\s*(AM|PM|am|pm)',          # 3 PM
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, user_input)
        if match:
            time_str = match.group(1)
            if len(match.groups()) > 1 and match.group(2):
                # Convert to 24-hour format
                if 'PM' in match.group(2).upper() and ':' in time_str:
                    hour, minute = time_str.split(':')
                    if int(hour) != 12:
                        hour = str(int(hour) + 12)
                    return f"{hour}:{minute}"
                elif 'PM' in match.group(2).upper():
                    hour = str(int(time_str) + 12) if int(time_str) != 12 else time_str
                    return f"{hour}:00"
            return time_str
    
    return None

async def run_meeting_agent_async(user_input: str, user_email: str = "demo@example.com") -> Dict[str, Any]:
    """Run the meeting assistant agent with user input (async version)"""
    
    try:
        # Create the agent
        agent = create_meeting_agent()
        
        # Create a session service and runner for the agent
        from google.adk import Runner, sessions
        session_service = sessions.InMemorySessionService()
        runner = Runner(agent=agent, session_service=session_service, app_name="meeting_assistant")
        
        # Run the agent with user input using debug method (async)
        events = await runner.run_debug(
            user_messages=user_input,
            user_id=user_email,
            session_id=f"session_{datetime.now().timestamp()}"
        )
        
        # Extract response from events
        response_parts = []
        for event in events:
            if hasattr(event, 'text'):
                response_parts.append(event.text)
            elif hasattr(event, 'content'):
                response_parts.append(event.content)
            elif isinstance(event, str):
                response_parts.append(event)
        
        response = ''.join(response_parts) if response_parts else "I processed your request successfully."
        
        return {
            "success": True,
            "response": response,
            "user_email": user_email
        }
        
    except Exception as e:
        logger.error(f"Error running meeting agent: {e}")
        
        # Handle specific error types
        error_message = str(e).lower()
        if "rate limit" in error_message or "quota exceeded" in error_message:
            fallback_response = "I'm currently experiencing high demand and have reached my API rate limit. Please try again in a few minutes, or I can help you with basic meeting information using my local tools."
        elif "api key" in error_message or "credentials" in error_message:
            fallback_response = "I'm having trouble connecting to my AI service. Please check your API key configuration, or I can help you with basic meeting information using my local tools."
        else:
            # Generic fallback response
            fallback_response = f"Hello! I'm your meeting assistant. I received your message: '{user_input}'. I can help you with scheduling meetings, checking your calendar, and managing your appointments. What would you like to do?"
        
        return {
            "success": True,
            "response": fallback_response,
            "user_email": user_email,
            "error": str(e)  # Include error for debugging
        }

# Keep the sync version for backward compatibility
def run_meeting_agent(user_input: str, user_email: str = "demo@example.com") -> Dict[str, Any]:
    """Run the meeting assistant agent with user input (sync version)"""
    
    try:
        # Create the agent
        agent = create_meeting_agent()
        
        # Create a session service and runner for the agent
        from google.adk import Runner, sessions
        session_service = sessions.InMemorySessionService()
        runner = Runner(agent=agent, session_service=session_service, app_name="meeting_assistant")
        
        # Run the agent with user input using debug method (async)
        import asyncio
        
        async def run_agent():
            events = await runner.run_debug(
                user_messages=user_input,
                user_id=user_email,
                session_id=f"session_{datetime.now().timestamp()}"
            )
            
            # Extract response from events
            response_parts = []
            for event in events:
                if hasattr(event, 'text'):
                    response_parts.append(event.text)
                elif hasattr(event, 'content'):
                    response_parts.append(event.content)
                elif isinstance(event, str):
                    response_parts.append(event)
            
            return ''.join(response_parts) if response_parts else "I processed your request successfully."
        
        response = asyncio.run(run_agent())
        
        return {
            "success": True,
            "response": response,
            "user_email": user_email
        }
        
    except Exception as e:
        logger.error(f"Error running meeting agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_email": user_email
        }

# Example usage
if __name__ == "__main__":
    # Test the agent
    test_inputs = [
        "Show me my upcoming meetings",
        "What meetings do I have today?",
        "Book a meeting with John tomorrow at 2 PM",
        "Cancel my meeting demo_001"
    ]
    
    for test_input in test_inputs:
        print(f"\nUser: {test_input}")
        result = run_meeting_agent(test_input)
        print(f"Agent: {result}")