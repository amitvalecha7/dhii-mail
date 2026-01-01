# Meeting Assistant Prompt Builder
# Based on A2UI restaurant finder pattern

from .a2ui_meeting_examples import MEETING_UI_EXAMPLES, MEETING_A2UI_SCHEMA

def get_meeting_ui_prompt():
    """Generate UI prompt for meeting assistant"""
    return f"""
You are an AI assistant that generates A2UI JSON for meeting management interfaces.

IMPORTANT: You MUST respond ONLY with valid JSON that follows the A2UI schema exactly.
Do not include any explanatory text, markdown formatting, or code blocks.

A2UI Schema:
{MEETING_A2UI_SCHEMA}

Available UI Examples:
{MEETING_UI_EXAMPLES}

Instructions:
1. Choose the appropriate UI example based on the user's request
2. Replace placeholder data with actual meeting data
3. Ensure all JSON is valid and follows the schema exactly
4. Use appropriate component types (Card, Button, Text, List, Grid, etc.)
5. Include proper styling and layout

Respond ONLY with the A2UI JSON array, no additional text.
"""

def get_meeting_text_prompt():
    """Generate text prompt for meeting assistant"""
    return """
You are a helpful meeting scheduling assistant. Your goal is to help users schedule, manage, and join meetings.

You can help with:
- Scheduling new meetings
- Viewing existing meetings
- Finding available time slots
- Managing meeting participants
- Sending meeting invitations
- Joining meetings

Always be professional and helpful. Provide clear information about meeting times, participants, and logistics.
"""

def get_meeting_list_ui(meetings_data):
    """Generate A2UI JSON for meeting list"""
    import json
    
    # Build meetings array from data
    meetings_array = []
    for i, meeting in enumerate(meetings_data, 1):
        meeting_item = {
            "key": f"meeting{i}",
            "valueMap": [
                {"key": "id", "valueString": meeting.get("id", f"meet_{i:03d}")},
                {"key": "title", "valueString": meeting.get("title", f"Meeting {i}")},
                {"key": "status", "valueString": meeting.get("status", "Confirmed")},
                {"key": "statusVariant", "valueString": meeting.get("statusVariant", "success")},
                {"key": "datetime", "valueString": meeting.get("datetime", "TBD")},
                {"key": "participants", "valueString": meeting.get("participants", "No participants")},
                {"key": "meetingLink", "valueString": meeting.get("meetingLink", "#")}
            ]
        }
        meetings_array.append(meeting_item)
    
    # Build the complete A2UI JSON
    a2ui_json = [
        {
            "beginRendering": {
                "surfaceId": "default",
                "root": "root-column",
                "styles": {
                    "primaryColor": "#4F46E5",
                    "font": "Inter",
                    "backgroundColor": "#f8fafc"
                }
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "default",
                "components": [
                    {
                        "id": "root-column",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["header-section", "meeting-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-section",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["title-text", "new-meeting-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "title-text",
                        "component": {
                            "Text": {
                                "usageHint": "h1",
                                "text": {"path": "title"},
                                "style": {"fontSize": "24px", "fontWeight": "bold"}
                            }
                        }
                    },
                    {
                        "id": "new-meeting-btn",
                        "component": {
                            "Button": {
                                "child": "new-meeting-text",
                                "primary": True,
                                "action": {"name": "create_new_meeting"}
                            }
                        }
                    },
                    {
                        "id": "new-meeting-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "+ New Meeting"}
                            }
                        }
                    },
                    {
                        "id": "meeting-list",
                        "component": {
                            "List": {
                                "direction": "vertical",
                                "children": {
                                    "template": {
                                        "componentId": "meeting-card-template",
                                        "dataBinding": "/meetings"
                                    }
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-card-template",
                        "component": {
                            "Card": {
                                "child": "meeting-card-content",
                                "style": {
                                    "margin": "8px 0",
                                    "padding": "16px",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-card-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["meeting-title-row", "meeting-details-row", "meeting-actions-row"]
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-title-row",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["meeting-title", "meeting-status"]
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-title",
                        "component": {
                            "Text": {
                                "usageHint": "h3",
                                "text": {"path": "title"},
                                "style": {"fontSize": "18px", "fontWeight": "600"}
                            }
                        }
                    },
                    {
                        "id": "meeting-status",
                        "component": {
                            "Badge": {
                                "text": {"path": "status"},
                                "variant": {"path": "statusVariant"}
                            }
                        }
                    },
                    {
                        "id": "meeting-details-row",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["meeting-datetime", "meeting-participants"]
                                }
                            }
                        }
                    },
                    {
                        "id": "meeting-datetime",
                        "component": {
                            "Text": {
                                "text": {"path": "datetime"},
                                "style": {"color": "#6b7280", "fontSize": "14px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-participants",
                        "component": {
                            "Text": {
                                "text": {"path": "participants"},
                                "style": {"color": "#6b7280", "fontSize": "14px"}
                            }
                        }
                    },
                    {
                        "id": "meeting-actions-row",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["view-details-btn", "join-meeting-btn"]
                                }
                            }
                        }
                    },
                    {
                        "id": "view-details-btn",
                        "component": {
                            "Button": {
                                "child": "view-details-text",
                                "variant": "outline",
                                "action": {
                                    "name": "view_meeting_details",
                                    "context": [{"key": "meetingId", "value": {"path": "id"}}]
                                }
                            }
                        }
                    },
                    {
                        "id": "view-details-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "View Details"}
                            }
                        }
                    },
                    {
                        "id": "join-meeting-btn",
                        "component": {
                            "Button": {
                                "child": "join-text",
                                "primary": True,
                                "action": {
                                    "name": "join_meeting",
                                    "context": [{"key": "meetingLink", "value": {"path": "meetingLink"}}]
                                }
                            }
                        }
                    },
                    {
                        "id": "join-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Join"}
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
                "contents": [
                    {"key": "title", "valueString": "Meeting Assistant"},
                    {"key": "meetings", "valueMap": meetings_array}
                ]
            }
        }
    ]
    
    return json.dumps(a2ui_json, indent=2)

def get_booking_ui(available_slots, selected_date=None):
    """Generate A2UI JSON for meeting booking interface"""
    import json
    
    # Build time slots array
    slots_array = []
    for i, slot in enumerate(available_slots, 1):
        slot_item = {
            "key": f"slot{i}",
            "valueMap": [
                {"key": "time", "valueString": slot.get("time", "TBD")},
                {"key": "slotVariant", "valueString": slot.get("variant", "outline")}
            ]
        }
        slots_array.append(slot_item)
    
    # Build the complete booking A2UI JSON
    a2ui_json = [
        {
            "beginRendering": {
                "surfaceId": "booking",
                "root": "booking-container",
                "styles": {
                    "primaryColor": "#4F46E5",
                    "font": "Inter"
                }
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "booking",
                "components": [
                    {
                        "id": "booking-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["booking-header", "date-selector", "time-slots", "participant-selector", "book-button"]
                                }
                            }
                        }
                    },
                    {
                        "id": "booking-header",
                        "component": {
                            "Text": {
                                "usageHint": "h2",
                                "text": {"path": "bookingTitle"},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "marginBottom": "16px"}
                            }
                        }
                    },
                    {
                        "id": "date-selector",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["date-label", "date-picker"]
                                }
                            }
                        }
                    },
                    {
                        "id": "date-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Select Date:"},
                                "style": {"fontWeight": "500", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "date-picker",
                        "component": {
                            "DatePicker": {
                                "selectedDate": {"path": "selectedDate"},
                                "onDateChange": {"name": "date_selected"}
                            }
                        }
                    },
                    {
                        "id": "time-slots",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["time-label", "time-slot-grid"]
                                }
                            }
                        }
                    },
                    {
                        "id": "time-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Available Time Slots:"},
                                "style": {"fontWeight": "500", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "time-slot-grid",
                        "component": {
                            "Grid": {
                                "columns": 3,
                                "children": {
                                    "template": {
                                        "componentId": "time-slot-template",
                                        "dataBinding": "/availableSlots"
                                    }
                                }
                            }
                        }
                    },
                    {
                        "id": "time-slot-template",
                        "component": {
                            "Button": {
                                "child": "time-slot-text",
                                "variant": {"path": "slotVariant"},
                                "action": {
                                    "name": "time_slot_selected",
                                    "context": [{"key": "timeSlot", "value": {"path": "time"}}]
                                }
                            }
                        }
                    },
                    {
                        "id": "time-slot-text",
                        "component": {
                            "Text": {
                                "text": {"path": "time"}
                            }
                        }
                    },
                    {
                        "id": "participant-selector",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["participant-label", "participant-input"]
                                }
                            }
                        }
                    },
                    {
                        "id": "participant-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Add Participants:"},
                                "style": {"fontWeight": "500", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "participant-input",
                        "component": {
                            "TextInput": {
                                "placeholder": {"literalString": "Enter email addresses..."},
                                "value": {"path": "participants"},
                                "multiline": True,
                                "onChange": {"name": "participants_updated"}
                            }
                        }
                    },
                    {
                        "id": "book-button",
                        "component": {
                            "Button": {
                                "child": "book-text",
                                "primary": True,
                                "disabled": {"path": "isBookDisabled"},
                                "action": {
                                    "name": "book_meeting",
                                    "context": [
                                        {"key": "date", "value": {"path": "selectedDate"}},
                                        {"key": "time", "value": {"path": "selectedTime"}},
                                        {"key": "participants", "value": {"path": "participants"}}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": "book-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Book Meeting"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "booking",
                "path": "/",
                "contents": [
                    {"key": "bookingTitle", "valueString": "Schedule New Meeting"},
                    {"key": "selectedDate", "valueString": selected_date or "2024-01-15"},
                    {"key": "availableSlots", "valueMap": slots_array},
                    {"key": "participants", "valueString": ""},
                    {"key": "isBookDisabled", "valueBoolean": False}
                ]
            }
        }
    ]
    
    return json.dumps(a2ui_json, indent=2)