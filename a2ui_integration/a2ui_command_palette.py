"""
A2UI Command Palette - Keyboard-first command interface
Implements the command palette pattern from UI_UX_Component_Design.md
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CommandCategory(Enum):
    """Categories for commands"""
    NAVIGATION = "navigation"
    ACTION = "action"
    SEARCH = "search"
    SYSTEM = "system"
    EMAIL = "email"
    CALENDAR = "calendar"
    MEETING = "meeting"
    SETTINGS = "settings"

@dataclass
class Command:
    """Represents a command in the palette"""
    id: str
    name: str
    description: str
    category: CommandCategory
    action: str
    keywords: List[str]
    icon: Optional[str] = None
    shortcut: Optional[str] = None
    context: Optional[str] = None  # Required context (e.g., "email_selected")
    enabled: bool = True

class A2UICommandPalette:
    """
    Command palette for A2UI - provides keyboard-first command interface
    
    Features:
    - Fuzzy search across commands
    - Keyboard shortcuts
    - Context-aware commands
    - Command history
    - Categories and filtering
    """
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.command_history: List[str] = []  # Command IDs
        self.max_history_size = 20
        self.fuzzy_threshold = 0.3
        
        # Initialize default commands
        self._initialize_default_commands()
    
    def _initialize_default_commands(self):
        """Initialize the default command set"""
        default_commands = [
            # Navigation Commands
            Command("nav_dashboard", "Go to Dashboard", "Navigate to main dashboard", 
                   CommandCategory.NAVIGATION, "navigate_dashboard", 
                   ["home", "main", "start"], "home", "cmd+k cmd+h"),
            
            Command("nav_email", "Go to Email", "Navigate to email inbox",
                   CommandCategory.NAVIGATION, "navigate_email_inbox",
                   ["mail", "inbox", "messages"], "email", "cmd+k cmd+e"),
            
            Command("nav_calendar", "Go to Calendar", "Navigate to calendar view",
                   CommandCategory.NAVIGATION, "navigate_calendar",
                   ["schedule", "events", "dates"], "calendar", "cmd+k cmd+c"),
            
            Command("nav_meetings", "Go to Meetings", "Navigate to meetings list",
                   CommandCategory.NAVIGATION, "navigate_meetings",
                   ["appointments", "calls"], "meeting", "cmd+k cmd+m"),
            
            Command("nav_tasks", "Go to Tasks", "Navigate to task board",
                   CommandCategory.NAVIGATION, "navigate_tasks",
                   ["todo", "board", "kanban"], "task", "cmd+k cmd+t"),
            
            Command("nav_analytics", "Go to Analytics", "Navigate to analytics dashboard",
                   CommandCategory.NAVIGATION, "navigate_analytics",
                   ["reports", "insights", "data"], "analytics", "cmd+k cmd+a"),
            
            Command("nav_settings", "Go to Settings", "Navigate to settings page",
                   CommandCategory.NAVIGATION, "navigate_settings",
                   ["preferences", "config"], "settings", "cmd+k cmd+s"),
            
            # Email Commands
            Command("email_compose", "Compose Email", "Create new email",
                   CommandCategory.EMAIL, "email_compose",
                   ["write", "new", "create"], "compose", "cmd+n"),
            
            Command("email_refresh", "Refresh Emails", "Refresh email inbox",
                   CommandCategory.EMAIL, "email_refresh",
                   ["reload", "sync", "update"], "refresh", "cmd+r"),
            
            Command("email_search", "Search Emails", "Search in emails",
                   CommandCategory.EMAIL, "email_search",
                   ["find", "filter"], "search", "cmd+f"),
            
            Command("email_reply", "Reply to Email", "Reply to selected email",
                   CommandCategory.EMAIL, "email_reply",
                   ["answer", "respond"], "reply", "cmd+r", context="email_selected"),
            
            Command("email_forward", "Forward Email", "Forward selected email",
                   CommandCategory.EMAIL, "email_forward",
                   ["send", "share"], "forward", "cmd+shift+f", context="email_selected"),
            
            Command("email_delete", "Delete Email", "Delete selected email",
                   CommandCategory.EMAIL, "email_delete",
                   ["remove", "trash"], "delete", "cmd+backspace", context="email_selected"),
            
            # Calendar Commands
            Command("cal_today", "Go to Today", "Navigate to today in calendar",
                   CommandCategory.CALENDAR, "calendar_today",
                   ["current", "now"], "today", "cmd+shift+t"),
            
            Command("cal_new_event", "New Event", "Create calendar event",
                   CommandCategory.CALENDAR, "calendar_new_event",
                   ["appointment", "meeting"], "event", "cmd+shift+n"),
            
            Command("cal_month_view", "Month View", "Switch to month view",
                   CommandCategory.CALENDAR, "calendar_month_view",
                   ["monthly"], "month", "cmd+1"),
            
            Command("cal_week_view", "Week View", "Switch to week view",
                   CommandCategory.CALENDAR, "calendar_week_view",
                   ["weekly"], "week", "cmd+2"),
            
            Command("cal_day_view", "Day View", "Switch to day view",
                   CommandCategory.CALENDAR, "calendar_day_view",
                   ["daily"], "day", "cmd+3"),
            
            # Meeting Commands
            Command("meeting_book", "Book Meeting", "Schedule new meeting",
                   CommandCategory.MEETING, "meeting_book",
                   ["schedule", "arrange"], "book", "cmd+shift+m"),
            
            Command("meeting_start", "Start Meeting", "Start current meeting",
                   CommandCategory.MEETING, "meeting_start",
                   ["begin", "join"], "start", "cmd+shift+j", context="meeting_ready"),
            
            Command("meeting_cancel", "Cancel Meeting", "Cancel selected meeting",
                   CommandCategory.MEETING, "meeting_cancel",
                   ["delete", "remove"], "cancel", "cmd+shift+x", context="meeting_selected"),
            
            # System Commands
            Command("cmd_palette", "Command Palette", "Open command palette",
                   CommandCategory.SYSTEM, "open_command_palette",
                   ["commands", "palette", "cmd"], "palette", "cmd+k"),
            
            Command("help", "Help", "Show help and documentation",
                   CommandCategory.SYSTEM, "show_help",
                   ["docs", "support"], "help", "cmd+shift+?"),
            
            Command("settings", "Settings", "Open settings",
                   CommandCategory.SYSTEM, "open_settings",
                   ["preferences", "config"], "settings", "cmd+,"),
            
            Command("logout", "Logout", "Sign out of application",
                   CommandCategory.SYSTEM, "logout",
                   ["signout", "exit"], "logout", "cmd+shift+q"),
            
            # Search Commands
            Command("global_search", "Global Search", "Search across all content",
                   CommandCategory.SEARCH, "global_search",
                   ["find", "search", "everything"], "search", "cmd+shift+f"),
            
            Command("quick_search", "Quick Search", "Quick search in current view",
                   CommandCategory.SEARCH, "quick_search",
                   ["find", "local"], "search", "cmd+f"),
        ]
        
        for command in default_commands:
            self.register_command(command)
    
    def register_command(self, command: Command):
        """Register a new command"""
        self.commands[command.id] = command
        logger.info(f"Registered command: {command.id} - {command.name}")
    
    def unregister_command(self, command_id: str):
        """Unregister a command"""
        if command_id in self.commands:
            del self.commands[command_id]
            logger.info(f"Unregistered command: {command_id}")
    
    def search_commands(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search commands using fuzzy matching
        
        Args:
            query: Search query
            context: Current context for filtering
            
        Returns:
            List of matching commands with scores
        """
        if not query.strip():
            # Return recent commands if no query
            return self._get_recent_commands(context)
        
        query_lower = query.lower()
        matches = []
        
        for command in self.commands.values():
            # Skip disabled commands
            if not command.enabled:
                continue
            
            # Skip context-restricted commands if context doesn't match
            if command.context and not self._check_context(command.context, context):
                continue
            
            # Calculate fuzzy match score
            score = self._calculate_match_score(command, query_lower)
            
            if score >= self.fuzzy_threshold:
                matches.append({
                    "command": command,
                    "score": score,
                    "highlighted_name": self._highlight_match(command.name, query_lower),
                    "match_reason": self._get_match_reason(command, query_lower)
                })
        
        # Sort by score (descending) and then by usage frequency
        matches.sort(key=lambda x: (x["score"], -self._get_command_frequency(x["command"].id)), reverse=True)
        
        return matches[:10]  # Return top 10 matches
    
    def _calculate_match_score(self, command: Command, query: str) -> float:
        """Calculate fuzzy match score for a command"""
        score = 0.0
        
        # Exact name match (highest score)
        if query in command.name.lower():
            score += 1.0
        
        # Name starts with query
        elif command.name.lower().startswith(query):
            score += 0.8
        
        # Query in name (partial match)
        elif query in command.name.lower():
            score += 0.6
        
        # Keyword matches
        for keyword in command.keywords:
            if query in keyword.lower():
                score += 0.4
                break
        
        # Description match (lower score)
        if query in command.description.lower():
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _highlight_match(self, text: str, query: str) -> str:
        """Highlight matching parts of the text"""
        if not query:
            return text
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        if query_lower in text_lower:
            start = text_lower.find(query_lower)
            end = start + len(query)
            return f"{text[:start]}<mark>{text[start:end]}</mark>{text[end:]}"
        
        return text
    
    def _get_match_reason(self, command: Command, query: str) -> str:
        """Get reason why this command matched"""
        query_lower = query.lower()
        
        if query_lower in command.name.lower():
            return "Name match"
        elif any(query_lower in keyword.lower() for keyword in command.keywords):
            return "Keyword match"
        elif query_lower in command.description.lower():
            return "Description match"
        else:
            return "Fuzzy match"
    
    def _check_context(self, required_context: str, current_context: Optional[Dict[str, Any]]) -> bool:
        """Check if current context allows the command"""
        if not current_context:
            return False
        
        # Check specific context requirements
        context_checks = {
            "email_selected": current_context.get("email_selected", False),
            "meeting_selected": current_context.get("meeting_selected", False),
            "meeting_ready": current_context.get("meeting_ready", False),
            "text_selected": current_context.get("text_selected", False),
        }
        
        return context_checks.get(required_context, False)
    
    def _get_recent_commands(self, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get recently used commands"""
        recent = []
        
        for command_id in reversed(self.command_history[-5:]):  # Last 5 commands
            if command_id in self.commands:
                command = self.commands[command_id]
                
                # Skip context-restricted commands if context doesn't match
                if command.context and not self._check_context(command.context, context):
                    continue
                
                recent.append({
                    "command": command,
                    "score": 0.5,  # Medium score for recent commands
                    "highlighted_name": command.name,
                    "match_reason": "Recently used"
                })
        
        return recent
    
    def _get_command_frequency(self, command_id: str) -> int:
        """Get usage frequency of a command"""
        return self.command_history.count(command_id)
    
    def execute_command(self, command_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a command by ID
        
        Returns:
            Result dictionary with status and action information
        """
        if command_id not in self.commands:
            return {
                "success": False,
                "error": f"Command not found: {command_id}",
                "action": None
            }
        
        command = self.commands[command_id]
        
        # Check if command is enabled
        if not command.enabled:
            return {
                "success": False,
                "error": f"Command disabled: {command.name}",
                "action": None
            }
        
        # Check context requirements
        if command.context and not self._check_context(command.context, context):
            return {
                "success": False,
                "error": f"Command requires context: {command.context}",
                "action": None
            }
        
        # Add to history
        self._add_to_history(command_id)
        
        logger.info(f"Executed command: {command.name} (ID: {command_id})")
        
        return {
            "success": True,
            "action": command.action,
            "command": command,
            "context": context
        }
    
    def _add_to_history(self, command_id: str):
        """Add command to history"""
        self.command_history.append(command_id)
        
        # Maintain history size limit
        if len(self.command_history) > self.max_history_size:
            self.command_history.pop(0)
    
    def get_command_categories(self) -> List[Dict[str, Any]]:
        """Get available command categories"""
        categories = {}
        
        for command in self.commands.values():
            if not command.enabled:
                continue
                
            category = command.category.value
            if category not in categories:
                categories[category] = {
                    "name": category,
                    "display_name": category.replace("_", " ").title(),
                    "count": 0,
                    "commands": []
                }
            
            categories[category]["count"] += 1
            categories[category]["commands"].append({
                "id": command.id,
                "name": command.name,
                "shortcut": command.shortcut,
                "icon": command.icon
            })
        
        return list(categories.values())
    
    def get_keyboard_shortcuts(self) -> Dict[str, str]:
        """Get all keyboard shortcuts mapped to actions"""
        shortcuts = {}
        
        for command in self.commands.values():
            if command.shortcut and command.enabled:
                shortcuts[command.shortcut] = command.action
        
        return shortcuts
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        logger.info("Cleared command history")
    
    def disable_command(self, command_id: str):
        """Disable a command"""
        if command_id in self.commands:
            self.commands[command_id].enabled = False
            logger.info(f"Disabled command: {command_id}")
    
    def enable_command(self, command_id: str):
        """Enable a command"""
        if command_id in self.commands:
            self.commands[command_id].enabled = True
            logger.info(f"Enabled command: {command_id}")
    
    def get_palette_component(self, query: str = "", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get the command palette as an A2UI component
        
        Returns:
            A2UI component schema for command palette
        """
        search_results = self.search_commands(query, context)
        
        # Convert search results to list items
        items = []
        for result in search_results:
            command = result["command"]
            items.append({
                "id": command.id,
                "title": result["highlighted_name"],
                "subtitle": command.description,
                "icon": command.icon or "command",
                "shortcut": command.shortcut,
                "category": command.category.value,
                "match_reason": result["match_reason"],
                "score": result["score"],
                "action": command.action
            })
        
        return {
            "component": {
                "CommandPalette": {
                    "query": query,
                    "items": items,
                    "placeholder": "Type a command or search...",
                    "empty_state": {
                        "title": "No commands found",
                        "description": "Try different keywords or check your spelling"
                    },
                    "categories": self.get_command_categories(),
                    "keyboard_shortcuts": self.get_keyboard_shortcuts(),
                    "styles": {
                        "width": "600px",
                        "maxHeight": "400px",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "boxShadow": "0 10px 25px rgba(0,0,0,0.1)",
                        "border": "1px solid #e5e7eb"
                    }
                }
            }
        }