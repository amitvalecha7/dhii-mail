# Meeting Assistant Agent
# Based on A2UI restaurant finder pattern

import json
import logging
import os
from collections.abc import AsyncIterable
from typing import Any

import jsonschema
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from prompt_builder import (
    MEETING_A2UI_SCHEMA,
    get_meeting_ui_prompt,
    get_meeting_text_prompt,
    get_meeting_list_ui,
    get_booking_ui,
)
from meeting_tools import (
    get_upcoming_meetings,
    get_available_time_slots,
    book_meeting,
    get_meeting_details,
    cancel_meeting,
)

logger = logging.getLogger(__name__)

AGENT_INSTRUCTION = """
    You are a helpful meeting scheduling assistant. Your goal is to help users schedule, manage, and join meetings using a rich UI.

    To achieve this, you MUST follow this logic:

    1.  **For viewing upcoming meetings:**
        a. You MUST call the `get_upcoming_meetings` tool to retrieve the user's meetings.
        b. After receiving the data, you MUST generate the A2UI JSON for the meeting list interface using the appropriate UI example.

    2.  **For scheduling a new meeting:**
        a. You MUST call the `get_available_time_slots` tool to get available time slots for the requested date.
        b. After receiving the data, you MUST generate the A2UI JSON for the booking interface.

    3.  **For viewing meeting details:**
        a. You MUST call the `get_meeting_details` tool with the meeting ID.
        b. After receiving the data, you MUST generate the A2UI JSON for the meeting details interface.

    4.  **For booking a meeting (when you receive booking context):**
        a. You MUST call the `book_meeting` tool with the provided details.
        b. After successful booking, generate a confirmation UI.

    5.  **For canceling a meeting:**
        a. You MUST call the `cancel_meeting` tool with the meeting ID.
        b. After successful cancellation, generate a confirmation message.

    IMPORTANT: Always respond with valid A2UI JSON that follows the schema exactly. Do not include any explanatory text.
"""

def create_meeting_agent():
    """Create and configure the meeting assistant agent"""
    
    # Configure the LLM model
    model = LiteLlm(
        model="gemini-2.0-flash-exp",
        api_key=os.getenv("GOOGLE_API_KEY"),
        generation_config=types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=2048,
        ),
    )
    
    # Create the agent
    agent = LlmAgent(
        model=model,
        name="meeting-assistant",
        description="A helpful meeting scheduling assistant",
        instruction=AGENT_INSTRUCTION,
        tools=[
            get_upcoming_meetings,
            get_available_time_slots,
            book_meeting,
            get_meeting_details,
            cancel_meeting,
        ],
    )
    
    return agent

def create_runner():
    """Create the agent runner with services"""
    
    # Create services
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    artifact_service = InMemoryArtifactService()
    
    # Create agent
    agent = create_meeting_agent()
    
    # Create runner
    runner = Runner(
        app_name="meeting-assistant",
        agent=agent,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )
    
    return runner

async def process_meeting_request(user_input: str, session_id: str = None) -> str:
    """Process a meeting-related user request and return A2UI JSON"""
    
    try:
        # Create runner if no session ID provided
        if not session_id:
            runner = create_runner()
            session = runner.session_service.create_session(
                app_name="meeting-assistant",
                user_id="default_user",
            )
            session_id = session.id
        else:
            runner = create_runner()
        
        # Process the request
        result = await runner.run_async(
            user_input=user_input,
            session_id=session_id,
        )
        
        # Extract the response
        if result.artifacts and len(result.artifacts) > 0:
            # Try to get A2UI JSON from artifacts
            for artifact in result.artifacts:
                if hasattr(artifact, 'content') and artifact.content:
                    try:
                        # Validate JSON
                        json_content = json.loads(artifact.content)
                        if isinstance(json_content, list) and len(json_content) > 0:
                            return json.dumps(json_content, indent=2)
                    except json.JSONDecodeError:
                        continue
        
        # Fallback: try to get response from agent
        if result.response:
            response_text = result.response.text if hasattr(result.response, 'text') else str(result.response)
            
            # Try to parse as JSON
            try:
                json_response = json.loads(response_text)
                if isinstance(json_response, list):
                    return json.dumps(json_response, indent=2)
            except json.JSONDecodeError:
                pass
            
            # If not JSON, create a simple text UI
            text_ui = [
                {
                    "beginRendering": {
                        "surfaceId": "default",
                        "root": "root-container",
                        "styles": {"primaryColor": "#4F46E5", "font": "Inter"}
                    }
                },
                {
                    "surfaceUpdate": {
                        "surfaceId": "default",
                        "components": [
                            {
                                "id": "root-container",
                                "component": {
                                    "Column": {
                                        "children": {
                                            "explicitList": ["response-text"]
                                        }
                                    }
                                }
                            },
                            {
                                "id": "response-text",
                                "component": {
                                    "Text": {
                                        "text": {"literalString": response_text},
                                        "style": {"fontSize": "16px", "padding": "16px"}
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "dataModelUpdate": {
                        "surfaceId": "default",
                        "path": "/",
                        "contents": []
                    }
                }
            ]
            return json.dumps(text_ui, indent=2)
        
        # Default fallback UI
        default_ui = [
            {
                "beginRendering": {
                    "surfaceId": "default",
                    "root": "root-container",
                    "styles": {"primaryColor": "#4F46E5", "font": "Inter"}
                }
            },
            {
                "surfaceUpdate": {
                    "surfaceId": "default",
                    "components": [
                        {
                            "id": "root-container",
                            "component": {
                                "Column": {
                                    "children": {
                                        "explicitList": ["error-text"]
                                    }
                                }
                            }
                        },
                        {
                            "id": "error-text",
                            "component": {
                                "Text": {
                                    "text": {"literalString": "I couldn't process your request. Please try again."},
                                    "style": {"fontSize": "16px", "color": "#ef4444"}
                                }
                            }
                        }
                    ]
                }
            },
            {
                "dataModelUpdate": {
                    "surfaceId": "default",
                    "path": "/",
                    "contents": []
                }
            }
        ]
        return json.dumps(default_ui, indent=2)
        
    except Exception as e:
        logger.error(f"Error processing meeting request: {e}")
        
        # Error UI
        error_ui = [
            {
                "beginRendering": {
                    "surfaceId": "default",
                    "root": "root-container",
                    "styles": {"primaryColor": "#ef4444", "font": "Inter"}
                }
            },
            {
                "surfaceUpdate": {
                    "surfaceId": "default",
                    "components": [
                        {
                            "id": "root-container",
                            "component": {
                                "Column": {
                                    "children": {
                                        "explicitList": ["error-header", "error-message"]
                                    }
                                }
                            }
                        },
                        {
                            "id": "error-header",
                            "component": {
                                "Text": {
                                    "usageHint": "h2",
                                    "text": {"literalString": "Error"},
                                    "style": {"color": "#ef4444"}
                                }
                            }
                        },
                        {
                            "id": "error-message",
                            "component": {
                                "Text": {
                                    "text": {"literalString": f"An error occurred: {str(e)}"},
                                    "style": {"fontSize": "14px"}
                                }
                            }
                        }
                    ]
                }
            },
            {
                "dataModelUpdate": {
                    "surfaceId": "default",
                    "path": "/",
                    "contents": []
                }
            }
        ]
        return json.dumps(error_ui, indent=2)

# Export the main functions
__all__ = ['create_meeting_agent', 'create_runner', 'process_meeting_request']