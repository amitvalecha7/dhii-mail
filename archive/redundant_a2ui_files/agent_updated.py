# Meeting Assistant Agent for A2UI Integration
# Updated to use database-backed meeting tools

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# Google ADK imports
from google.adk import LlmAgent, Agent
from google.adk.models import LiteLlm
from google.adk.types import types

# Import updated meeting tools
from meeting_tools_updated import (
    get_upcoming_meetings,
    get_available_time_slots,
    book_meeting,
    get_meeting_details,
    cancel_meeting,
    update_meeting
)

# Import prompt builder
from prompt_builder import (
    get_meeting_list_ui,
    get_booking_ui,
    get_meeting_details_ui,
    get_success_ui,
    get_error_ui
)

logger = logging.getLogger(__name__)

# Agent instruction
AGENT_INSTRUCTION = """
You are a helpful Meeting Assistant AI that helps users manage their meetings and calendar.

Your capabilities include:
1. Viewing upcoming meetings and calendar events
2. Scheduling new meetings with participants
3. Finding available time slots
4. Providing meeting details and information
5. Cancelling or updating existing meetings
6. Managing meeting preferences and settings

When users ask about meetings, you should:
- Be conversational and helpful
- Provide clear information about meetings
- Suggest available time slots when scheduling
- Confirm all details before booking meetings
- Handle errors gracefully

Use the provided tools to interact with the meeting system and generate appropriate A2UI JSON responses.
"""

def create_meeting_agent():
    """Create the meeting assistant agent with A2UI tools"""
    
    # Configure the LLM model
    model = LiteLlm(
        model="gemini-2.0-flash-exp",
        api_key=os.getenv("GOOGLE_API_KEY"),
        generation_config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.8,
            top_k=40
        )
    )
    
    # Create the agent with tools
    agent = LlmAgent(
        model=model,
        name="meeting-assistant",
        instruction=AGENT_INSTRUCTION,
        tools=[
            get_upcoming_meetings,
            get_available_time_slots,
            book_meeting,
            get_meeting_details,
            cancel_meeting,
            update_meeting
        ]
    )
    
    return agent

async def process_meeting_request(user_input: str, session_id: str = None, user_email: str = None) -> str:
    """Process a meeting-related request and return A2UI JSON"""
    
    try:
        # Create agent
        agent = create_meeting_agent()
        
        # Process the user input
        response = await agent.run_async(user_input)
        
        # Extract the agent's response and tool calls
        agent_response = response.text if hasattr(response, 'text') else str(response)
        
        # Parse the response to determine what A2UI to generate
        if "upcoming meetings" in user_input.lower() or "my meetings" in user_input.lower():
            return await handle_get_meetings(user_email)
        elif "available" in user_input.lower() and ("time" in user_input.lower() or "slot" in user_input.lower()):
            return await handle_get_available_slots(user_input, user_email)
        elif "book" in user_input.lower() or "schedule" in user_input.lower():
            return await handle_book_meeting(user_input, user_email)
        elif "details" in user_input.lower() or "info" in user_input.lower():
            return await handle_get_meeting_details(user_input, user_email)
        elif "cancel" in user_input.lower():
            return await handle_cancel_meeting(user_input, user_email)
        elif "update" in user_input.lower() or "change" in user_input.lower():
            return await handle_update_meeting(user_input, user_email)
        else:
            # Default response with meeting list
            return await handle_get_meetings(user_email)
            
    except Exception as e:
        logger.error(f"Error processing meeting request: {e}")
        return get_error_ui(f"Sorry, I encountered an error processing your request: {str(e)}")

async def handle_get_meetings(user_email: str = None) -> str:
    """Handle request for upcoming meetings"""
    try:
        meetings = get_upcoming_meetings(user_email=user_email, limit=10)
        
        if not meetings:
            return get_error_ui("You don't have any upcoming meetings scheduled.")
        
        return get_meeting_list_ui(meetings)
        
    except Exception as e:
        logger.error(f"Error getting meetings: {e}")
        return get_error_ui("Sorry, I couldn't retrieve your meetings. Please try again.")

async def handle_get_available_slots(user_input: str, user_email: str = None) -> str:
    """Handle request for available time slots"""
    try:
        # Extract date from user input (simplified parsing)
        date = extract_date_from_input(user_input)
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Extract duration if mentioned
        duration = extract_duration_from_input(user_input) or 30
        
        slots = get_available_time_slots(date, duration, user_email)
        
        if not slots:
            return get_error_ui(f"Sorry, no available time slots found for {date}.")
        
        return get_booking_ui(slots, date)
        
    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        return get_error_ui("Sorry, I couldn't check available time slots. Please try again.")

async def handle_book_meeting(user_input: str, user_email: str = None) -> str:
    """Handle meeting booking request"""
    try:
        # Extract meeting details from user input (simplified parsing)
        title = extract_title_from_input(user_input)
        date = extract_date_from_input(user_input)
        time = extract_time_from_input(user_input)
        participants = extract_participants_from_input(user_input)
        
        if not title:
            return get_error_ui("I need a title for the meeting. Could you please provide one?")
        
        if not date:
            return get_error_ui("I need a date for the meeting. Could you please provide one?")
        
        if not time:
            return get_error_ui("I need a time for the meeting. Could you please provide one?")
        
        # Book the meeting
        meeting_data = book_meeting(
            title=title,
            date=date,
            time=time,
            duration_minutes=30,
            participants=participants or [],
            description=user_input,  # Use full input as description for now
            user_email=user_email
        )
        
        return get_success_ui("Meeting booked successfully!", meeting_data)
        
    except Exception as e:
        logger.error(f"Error booking meeting: {e}")
        return get_error_ui(f"Sorry, I couldn't book the meeting: {str(e)}")

async def handle_get_meeting_details(user_input: str, user_email: str = None) -> str:
    """Handle request for meeting details"""
    try:
        # Extract meeting ID from user input (simplified parsing)
        meeting_id = extract_meeting_id_from_input(user_input)
        
        if not meeting_id:
            return get_error_ui("I need a meeting ID to show details. Could you please provide one?")
        
        meeting = get_meeting_details(meeting_id, user_email)
        
        if "error" in meeting:
            return get_error_ui(meeting["error"])
        
        return get_meeting_details_ui(meeting)
        
    except Exception as e:
        logger.error(f"Error getting meeting details: {e}")
        return get_error_ui("Sorry, I couldn't get the meeting details. Please try again.")

async def handle_cancel_meeting(user_input: str, user_email: str = None) -> str:
    """Handle meeting cancellation request"""
    try:
        # Extract meeting ID from user input (simplified parsing)
        meeting_id = extract_meeting_id_from_input(user_input)
        
        if not meeting_id:
            return get_error_ui("I need a meeting ID to cancel. Could you please provide one?")
        
        result = cancel_meeting(meeting_id, user_email)
        
        if "error" in result:
            return get_error_ui(result["error"])
        
        return get_success_ui("Meeting cancelled successfully!", result)
        
    except Exception as e:
        logger.error(f"Error canceling meeting: {e}")
        return get_error_ui(f"Sorry, I couldn't cancel the meeting: {str(e)}")

async def handle_update_meeting(user_input: str, user_email: str = None) -> str:
    """Handle meeting update request"""
    try:
        # Extract meeting ID and updates from user input (simplified parsing)
        meeting_id = extract_meeting_id_from_input(user_input)
        updates = extract_updates_from_input(user_input)
        
        if not meeting_id:
            return get_error_ui("I need a meeting ID to update. Could you please provide one?")
        
        if not updates:
            return get_error_ui("I need to know what to update. Could you please specify the changes?")
        
        result = update_meeting(meeting_id, updates, user_email)
        
        if "error" in result:
            return get_error_ui(result["error"])
        
        return get_success_ui("Meeting updated successfully!", result)
        
    except Exception as e:
        logger.error(f"Error updating meeting: {e}")
        return get_error_ui(f"Sorry, I couldn't update the meeting: {str(e)}")

# Helper functions for parsing user input
def extract_date_from_input(user_input: str) -> Optional[str]:
    """Extract date from user input (simplified)"""
    # This is a very basic implementation
    # In a real system, you'd use NLP or more sophisticated parsing
    
    import re
    from datetime import datetime
    
    # Look for date patterns
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or MM/DD/YY
        r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY or MM-DD-YY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, user_input)
        if match:
            date_str = match.group()
            try:
                # Normalize to YYYY-MM-DD format
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts[2]) == 2:
                        parts[2] = '20' + parts[2]
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                elif '-' in date_str and len(date_str.split('-')[0]) <= 2:
                    parts = date_str.split('-')
                    if len(parts[2]) == 2:
                        parts[2] = '20' + parts[2]
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                else:
                    return date_str
            except:
                continue
    
    # Check for relative dates
    if 'today' in user_input.lower():
        return datetime.now().strftime("%Y-%m-%d")
    elif 'tomorrow' in user_input.lower():
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    return None

def extract_time_from_input(user_input: str) -> Optional[str]:
    """Extract time from user input (simplified)"""
    import re
    
    # Look for time patterns
    time_patterns = [
        r'\d{1,2}:\d{2}\s*[APap][Mm]',  # HH:MM AM/PM
        r'\d{1,2}\s*[APap][Mm]',  # HH AM/PM
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, user_input)
        if match:
            time_str = match.group()
            # Normalize to HH:MM AM/PM format
            if ':' not in time_str:
                # Add :00 for single digit times
                time_str = re.sub(r'(\d+)(\s*[APap][Mm])', r'\1:00\2', time_str)
            return time_str.upper()
    
    return None

def extract_title_from_input(user_input: str) -> Optional[str]:
    """Extract meeting title from user input (simplified)"""
    # Look for quoted text or text after keywords
    import re
    
    # Look for quoted text
    match = re.search(r'["\']([^"\']+)["\']', user_input)
    if match:
        return match.group(1)
    
    # Look for text after keywords
    keywords = ['meeting about', 'meeting for', 'called', 'titled', 'named']
    for keyword in keywords:
        if keyword in user_input.lower():
            parts = user_input.lower().split(keyword)
            if len(parts) > 1:
                # Take the next few words
                words = parts[1].strip().split()
                return ' '.join(words[:6])  # Take up to 6 words
    
    return None

def extract_participants_from_input(user_input: str) -> List[str]:
    """Extract participant emails from user input (simplified)"""
    import re
    
    # Look for email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, user_input)
    
    return emails

def extract_duration_from_input(user_input: str) -> Optional[int]:
    """Extract meeting duration from user input (simplified)"""
    import re
    
    # Look for duration patterns
    duration_patterns = [
        r'(\d+)\s*minutes?',
        r'(\d+)\s*mins?',
        r'(\d+)\s*hour',
        r'(\d+)\s*hr',
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            value = int(match.group(1))
            if 'hour' in pattern or 'hr' in pattern:
                return value * 60
            else:
                return value
    
    return None

def extract_meeting_id_from_input(user_input: str) -> Optional[str]:
    """Extract meeting ID from user input (simplified)"""
    import re
    
    # Look for meeting ID patterns
    meeting_patterns = [
        r'meet_[a-zA-Z0-9_]+',
        r'\b[a-zA-Z0-9]{8,}\b',  # Generic alphanumeric ID
    ]
    
    for pattern in meeting_patterns:
        match = re.search(pattern, user_input)
        if match:
            return match.group()
    
    return None

def extract_updates_from_input(user_input: str) -> Dict[str, Any]:
    """Extract meeting updates from user input (simplified)"""
    updates = {}
    
    # Extract title
    title = extract_title_from_input(user_input)
    if title:
        updates['title'] = title
    
    # Extract date
    date = extract_date_from_input(user_input)
    if date:
        updates['date'] = date
    
    # Extract time
    time = extract_time_from_input(user_input)
    if time:
        updates['time'] = time
    
    # Extract duration
    duration = extract_duration_from_input(user_input)
    if duration:
        updates['duration_minutes'] = duration
    
    # Extract participants
    participants = extract_participants_from_input(user_input)
    if participants:
        updates['participants'] = participants
    
    return updates

# Export the main function
__all__ = ['process_meeting_request', 'create_meeting_agent']