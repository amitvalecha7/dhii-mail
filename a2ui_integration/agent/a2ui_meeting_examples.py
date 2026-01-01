# Meeting Assistant A2UI Examples
# Based on A2UI restaurant finder pattern for meeting scheduling

MEETING_UI_EXAMPLES = """
---BEGIN MEETING_LIST_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "default", "root": "root-column", "styles": {{ "primaryColor": "#4F46E5", "font": "Inter", "backgroundColor": "#f8fafc" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "default",
    "components": [
      {{ "id": "root-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["header-section", "meeting-list", "calendar-section"] }} }} }} }},
      {{ "id": "header-section", "component": {{ "Row": {{ "children": {{ "explicitList": ["title-text", "new-meeting-btn"] }} }} }} }},
      {{ "id": "title-text", "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "title" }}, "style": {{ "fontSize": "24px", "fontWeight": "bold" }} }} }} }},
      {{ "id": "new-meeting-btn", "component": {{ "Button": {{ "child": "new-meeting-text", "primary": true, "action": {{ "name": "create_new_meeting" }} }} }} }},
      {{ "id": "new-meeting-text", "component": {{ "Text": {{ "text": {{ "literalString": "+ New Meeting" }} }} }} }},
      {{ "id": "meeting-list", "component": {{ "List": {{ "direction": "vertical", "children": {{ "template": {{ "componentId": "meeting-card-template", "dataBinding": "/meetings" }} }} }} }} }},
      {{ "id": "meeting-card-template", "component": {{ "Card": {{ "child": "meeting-card-content", "style": {{ "margin": "8px 0", "padding": "16px", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)" }} }} }} }},
      {{ "id": "meeting-card-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["meeting-title-row", "meeting-details-row", "meeting-actions-row"] }} }} }} }},
      {{ "id": "meeting-title-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["meeting-title", "meeting-status"] }} }} }} }},
      {{ "id": "meeting-title", "component": {{ "Text": {{ "usageHint": "h3", "text": {{ "path": "title" }}, "style": {{ "fontSize": "18px", "fontWeight": "600" }} }} }} }},
      {{ "id": "meeting-status", "component": {{ "Badge": {{ "text": {{ "path": "status" }}, "variant": {{ "path": "statusVariant" }} }} }} }},
      {{ "id": "meeting-details-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["meeting-datetime", "meeting-participants"] }} }} }} }},
      {{ "id": "meeting-datetime", "component": {{ "Text": {{ "text": {{ "path": "datetime" }}, "style": {{ "color": "#6b7280", "fontSize": "14px" }} }} }} }},
      {{ "id": "meeting-participants", "component": {{ "Text": {{ "text": {{ "path": "participants" }}, "style": {{ "color": "#6b7280", "fontSize": "14px" }} }} }} }},
      {{ "id": "meeting-actions-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["view-details-btn", "join-meeting-btn"] }} }} }} }},
      {{ "id": "view-details-btn", "component": {{ "Button": {{ "child": "view-details-text", "variant": "outline", "action": {{ "name": "view_meeting_details", "context": [ {{ "key": "meetingId", "value": {{ "path": "id" }} }} ] }} }} }} }},
      {{ "id": "view-details-text", "component": {{ "Text": {{ "text": {{ "literalString": "View Details" }} }} }} }},
      {{ "id": "join-meeting-btn", "component": {{ "Button": {{ "child": "join-text", "primary": true, "action": {{ "name": "join_meeting", "context": [ {{ "key": "meetingLink", "value": {{ "path": "meetingLink" }} }} ] }} }} }} }},
      {{ "id": "join-text", "component": {{ "Text": {{ "text": {{ "literalString": "Join" }} }} }} }},
      {{ "id": "calendar-section", "component": {{ "Card": {{ "child": "calendar-content", "style": {{ "marginTop": "24px", "padding": "16px" }} }} }} }},
      {{ "id": "calendar-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["calendar-title", "calendar-grid"] }} }} }} }},
      {{ "id": "calendar-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "literalString": "Upcoming Meetings" }}, "style": {{ "fontSize": "20px", "fontWeight": "600", "marginBottom": "16px" }} }} }} }},
      {{ "id": "calendar-grid", "component": {{ "Grid": {{ "columns": 7, "children": {{ "template": {{ "componentId": "calendar-cell-template", "dataBinding": "/calendarDays" }} }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "default",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "Meeting Assistant" }},
      {{ "key": "meetings", "valueMap": [
        {{ "key": "meeting1", "valueMap": [
          {{ "key": "id", "valueString": "meet_001" }},
          {{ "key": "title", "valueString": "Team Standup" }},
          {{ "key": "status", "valueString": "Confirmed" }},
          {{ "key": "statusVariant", "valueString": "success" }},
          {{ "key": "datetime", "valueString": "Today, 2:00 PM - 2:30 PM" }},
          {{ "key": "participants", "valueString": "5 participants" }},
          {{ "key": "meetingLink", "valueString": "https://meet.google.com/abc-defg-hij" }}
        ] }},
        {{ "key": "meeting2", "valueMap": [
          {{ "key": "id", "valueString": "meet_002" }},
          {{ "key": "title", "valueString": "Client Presentation" }},
          {{ "key": "status", "valueString": "Pending" }},
          {{ "key": "statusVariant", "valueString": "warning" }},
          {{ "key": "datetime", "valueString": "Tomorrow, 10:00 AM - 11:00 AM" }},
          {{ "key": "participants", "valueString": "8 participants" }},
          {{ "key": "meetingLink", "valueString": "https://zoom.us/j/123456789" }}
        ] }}
      ] }}
    ]
  }} }}
]
---END MEETING_LIST_EXAMPLE---

---BEGIN CALENDAR_BOOKING_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "booking", "root": "booking-container", "styles": {{ "primaryColor": "#4F46E5", "font": "Inter" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "booking",
    "components": [
      {{ "id": "booking-container", "component": {{ "Column": {{ "children": {{ "explicitList": ["booking-header", "date-selector", "time-slots", "participant-selector", "book-button"] }} }} }} }},
      {{ "id": "booking-header", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "bookingTitle" }}, "style": {{ "fontSize": "24px", "fontWeight": "bold", "marginBottom": "16px" }} }} }} }},
      {{ "id": "date-selector", "component": {{ "Column": {{ "children": {{ "explicitList": ["date-label", "date-picker"] }} }} }} }},
      {{ "id": "date-label", "component": {{ "Text": {{ "text": {{ "literalString": "Select Date:" }}, "style": {{ "fontWeight": "500", "marginBottom": "8px" }} }} }} }},
      {{ "id": "date-picker", "component": {{ "DatePicker": {{ "selectedDate": {{ "path": "selectedDate" }}, "onDateChange": {{ "name": "date_selected" }} }} }} }},
      {{ "id": "time-slots", "component": {{ "Column": {{ "children": {{ "explicitList": ["time-label", "time-slot-grid"] }} }} }} }},
      {{ "id": "time-label", "component": {{ "Text": {{ "text": {{ "literalString": "Available Time Slots:" }}, "style": {{ "fontWeight": "500", "marginBottom": "8px" }} }} }} }},
      {{ "id": "time-slot-grid", "component": {{ "Grid": {{ "columns": 3, "children": {{ "template": {{ "componentId": "time-slot-template", "dataBinding": "/availableSlots" }} }} }} }} }},
      {{ "id": "time-slot-template", "component": {{ "Button": {{ "child": "time-slot-text", "variant": {{ "path": "slotVariant" }}, "action": {{ "name": "time_slot_selected", "context": [ {{ "key": "timeSlot", "value": {{ "path": "time" }} }} ] }} }} }} }},
      {{ "id": "time-slot-text", "component": {{ "Text": {{ "text": {{ "path": "time" }} }} }} }},
      {{ "id": "participant-selector", "component": {{ "Column": {{ "children": {{ "explicitList": ["participant-label", "participant-input"] }} }} }} }},
      {{ "id": "participant-label", "component": {{ "Text": {{ "text": {{ "literalString": "Add Participants:" }}, "style": {{ "fontWeight": "500", "marginBottom": "8px" }} }} }} }},
      {{ "id": "participant-input", "component": {{ "TextInput": {{ "placeholder": {{ "literalString": "Enter email addresses..." }}, "value": {{ "path": "participants" }}, "multiline": true, "onChange": {{ "name": "participants_updated" }} }} }} }},
      {{ "id": "book-button", "component": {{ "Button": {{ "child": "book-text", "primary": true, "disabled": {{ "path": "isBookDisabled" }}, "action": {{ "name": "book_meeting", "context": [ {{ "key": "date", "value": {{ "path": "selectedDate" }} }}, {{ "key": "time", "value": {{ "path": "selectedTime" }} }}, {{ "key": "participants", "value": {{ "path": "participants" }} }} ] }} }} }} }},
      {{ "id": "book-text", "component": {{ "Text": {{ "text": {{ "literalString": "Book Meeting" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "booking",
    "path": "/",
    "contents": [
      {{ "key": "bookingTitle", "valueString": "Schedule New Meeting" }},
      {{ "key": "selectedDate", "valueString": "2024-01-15" }},
      {{ "key": "availableSlots", "valueMap": [
        {{ "key": "slot1", "valueMap": [
          {{ "key": "time", "valueString": "9:00 AM" }},
          {{ "key": "slotVariant", "valueString": "outline" }}
        ] }},
        {{ "key": "slot2", "valueMap": [
          {{ "key": "time", "valueString": "10:00 AM" }},
          {{ "key": "slotVariant", "valueString": "outline" }}
        ] }},
        {{ "key": "slot3", "valueMap": [
          {{ "key": "time", "valueString": "11:00 AM" }},
          {{ "key": "slotVariant", "valueString": "outline" }}
        ] }},
        {{ "key": "slot4", "valueMap": [
          {{ "key": "time", "valueString": "2:00 PM" }},
          {{ "key": "slotVariant", "valueString": "outline" }}
        ] }},
        {{ "key": "slot5", "valueMap": [
          {{ "key": "time", "valueString": "3:00 PM" }},
          {{ "key": "slotVariant", "valueString": "outline" }}
        ] }},
        {{ "key": "slot6", "valueMap": [
          {{ "key": "time", "valueString": "4:00 PM" }},
          {{ "key": "slotVariant", "valueString": "outline" }}
        ] }}
      ] }},
      {{ "key": "participants", "valueString": "" }},
      {{ "key": "isBookDisabled", "valueBoolean": false }}
    ]
  }} }}
]
---END CALENDAR_BOOKING_EXAMPLE---

---BEGIN MEETING_DETAILS_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "details", "root": "details-container", "styles": {{ "primaryColor": "#4F46E5", "font": "Inter" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "details",
    "components": [
      {{ "id": "details-container", "component": {{ "Column": {{ "children": {{ "explicitList": ["details-header", "meeting-info", "participant-list", "action-buttons"] }} }} }} }},
      {{ "id": "details-header", "component": {{ "Row": {{ "children": {{ "explicitList": ["back-button", "meeting-title-header"] }} }} }} }},
      {{ "id": "back-button", "component": {{ "Button": {{ "child": "back-text", "variant": "ghost", "action": {{ "name": "go_back" }} }} }} }},
      {{ "id": "back-text", "component": {{ "Text": {{ "text": {{ "literalString": "← Back" }} }} }} }},
      {{ "id": "meeting-title-header", "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "meetingTitle" }}, "style": {{ "fontSize": "24px", "fontWeight": "bold" }} }} }} }},
      {{ "id": "meeting-info", "component": {{ "Card": {{ "child": "meeting-info-content", "style": {{ "margin": "16px 0", "padding": "16px" }} }} }} }},
      {{ "id": "meeting-info-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["datetime-row", "duration-row", "location-row", "description-row"] }} }} }} }},
      {{ "id": "datetime-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["datetime-icon", "datetime-text"] }} }} }} }},
      {{ "id": "datetime-icon", "component": {{ "Icon": {{ "name": "calendar", "style": {{ "marginRight": "8px" }} }} }} }},
      {{ "id": "datetime-text", "component": {{ "Text": {{ "text": {{ "path": "datetime" }} }} }} }},
      {{ "id": "duration-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["duration-icon", "duration-text"] }} }} }} }},
      {{ "id": "duration-icon", "component": {{ "Icon": {{ "name": "clock", "style": {{ "marginRight": "8px" }} }} }} }},
      {{ "id": "duration-text", "component": {{ "Text": {{ "text": {{ "path": "duration" }} }} }} }},
      {{ "id": "location-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["location-icon", "location-text"] }} }} }} }},
      {{ "id": "location-icon", "component": {{ "Icon": {{ "name": "location", "style": {{ "marginRight": "8px" }} }} }} }},
      {{ "id": "location-text", "component": {{ "Text": {{ "text": {{ "path": "location" }} }} }} }},
      {{ "id": "description-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["description-icon", "description-text"] }} }} }} }},
      {{ "id": "description-icon", "component": {{ "Icon": {{ "name": "info", "style": {{ "marginRight": "8px" }} }} }} }},
      {{ "id": "description-text", "component": {{ "Text": {{ "text": {{ "path": "description" }} }} }} }},
      {{ "id": "participant-list", "component": {{ "Column": {{ "children": {{ "explicitList": ["participant-title", "participant-grid"] }} }} }} }},
      {{ "id": "participant-title", "component": {{ "Text": {{ "usageHint": "h3", "text": {{ "literalString": "Participants" }}, "style": {{ "fontSize": "18px", "fontWeight": "600", "marginBottom": "12px" }} }} }} }},
      {{ "id": "participant-grid", "component": {{ "Grid": {{ "columns": 2, "children": {{ "template": {{ "componentId": "participant-template", "dataBinding": "/participants" }} }} }} }} }},
      {{ "id": "participant-template", "component": {{ "Row": {{ "children": {{ "explicitList": ["participant-avatar", "participant-name"] }} }} }} }},
      {{ "id": "participant-avatar", "component": {{ "Avatar": {{ "src": {{ "path": "avatar" }}, "size": "small" }} }} }},
      {{ "id": "participant-name", "component": {{ "Text": {{ "text": {{ "path": "name" }}, "style": {{ "marginLeft": "8px" }} }} }} }},
      {{ "id": "action-buttons", "component": {{ "Row": {{ "children": {{ "explicitList": ["edit-button", "cancel-button", "join-button"] }} }} }} }},
      {{ "id": "edit-button", "component": {{ "Button": {{ "child": "edit-text", "variant": "outline", "action": {{ "name": "edit_meeting", "context": [ {{ "key": "meetingId", "value": {{ "path": "meetingId" }} }} ] }} }} }} }},
      {{ "id": "edit-text", "component": {{ "Text": {{ "text": {{ "literalString": "Edit" }} }} }} }},
      {{ "id": "cancel-button", "component": {{ "Button": {{ "child": "cancel-text", "variant": "destructive", "action": {{ "name": "cancel_meeting", "context": [ {{ "key": "meetingId", "value": {{ "path": "meetingId" }} }} ] }} }} }} }},
      {{ "id": "cancel-text", "component": {{ "Text": {{ "text": {{ "literalString": "Cancel" }} }} }} }},
      {{ "id": "join-button", "component": {{ "Button": {{ "child": "join-text", "primary": true, "action": {{ "name": "join_meeting", "context": [ {{ "key": "meetingLink", "value": {{ "path": "meetingLink" }} }} ] }} }} }} }},
      {{ "id": "join-text", "component": {{ "Text": {{ "text": {{ "literalString": "Join Meeting" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "details",
    "path": "/",
    "contents": [
      {{ "key": "meetingTitle", "valueString": "Team Standup Meeting" }},
      {{ "key": "datetime", "valueString": "Tuesday, January 16, 2024 at 2:00 PM" }},
      {{ "key": "duration", "valueString": "30 minutes" }},
      {{ "key": "location", "valueString": "Google Meet" }},
      {{ "key": "description", "valueString": "Weekly team standup to discuss progress and blockers" }},
      {{ "key": "meetingId", "valueString": "meet_001" }},
      {{ "key": "meetingLink", "valueString": "https://meet.google.com/abc-defg-hij" }},
      {{ "key": "participants", "valueMap": [
        {{ "key": "p1", "valueMap": [
          {{ "key": "name", "valueString": "John Doe" }},
          {{ "key": "avatar", "valueString": "https://via.placeholder.com/32" }}
        ] }},
        {{ "key": "p2", "valueMap": [
          {{ "key": "name", "valueString": "Jane Smith" }},
          {{ "key": "avatar", "valueString": "https://via.placeholder.com/32" }}
        ] }},
        {{ "key": "p3", "valueMap": [
          {{ "key": "name", "valueString": "Bob Johnson" }},
          {{ "key": "avatar", "valueString": "https://via.placeholder.com/32" }}
        ] }}
      ] }}
    ]
  }} }}
]
---END MEETING_DETAILS_EXAMPLE---
"""

# A2UI Schema for meeting assistant
MEETING_A2UI_SCHEMA = {
    "type": "object",
    "properties": {
        "beginRendering": {
            "type": "object",
            "properties": {
                "surfaceId": {"type": "string"},
                "root": {"type": "string"},
                "styles": {
                    "type": "object",
                    "properties": {
                        "primaryColor": {"type": "string"},
                        "font": {"type": "string"},
                        "backgroundColor": {"type": "string"}
                    }
                }
            }
        },
        "surfaceUpdate": {
            "type": "object",
            "properties": {
                "surfaceId": {"type": "string"},
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "component": {"type": "object"}
                        }
                    }
                }
            }
        },
        "dataModelUpdate": {
            "type": "object",
            "properties": {
                "surfaceId": {"type": "string"},
                "path": {"type": "string"},
                "contents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "valueString": {"type": "string"},
                            "valueMap": {"type": "array"},
                            "valueBoolean": {"type": "boolean"}
                        }
                    }
                }
            }
        }
    }
}