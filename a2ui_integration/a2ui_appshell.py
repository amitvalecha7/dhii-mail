#!/usr/bin/env python3
"""
A2UI AppShell Component - Main application shell with ribbon and pane layout
Based on UI_UX_Component_Design.md specifications
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class RibbonTabType(Enum):
    """Types of ribbon tabs"""
    HOME = "home"
    EMAIL = "email"
    CALENDAR = "calendar"
    MEETINGS = "meetings"
    TASKS = "tasks"
    ANALYTICS = "analytics"
    SETTINGS = "settings"


@dataclass
class RibbonButton:
    """Ribbon button configuration"""
    id: str
    title: str
    icon: str
    action: str
    tooltip: str = ""
    enabled: bool = True
    variant: str = "default"  # default, primary, secondary, danger


@dataclass
class RibbonGroup:
    """Ribbon button group"""
    id: str
    title: str
    buttons: List[RibbonButton]


@dataclass
class RibbonTab:
    """Ribbon tab configuration"""
    id: str
    title: str
    type: RibbonTabType
    groups: List[RibbonGroup]


@dataclass
class PaneConfig:
    """Pane configuration"""
    id: str
    title: str
    width: int = 300
    min_width: int = 200
    max_width: int = 500
    resizable: bool = True
    collapsible: bool = True
    default_collapsed: bool = False
    content: Optional[Dict[str, Any]] = None


class A2UIAppShell:
    """A2UI AppShell component with ribbon and pane layout"""
    
    def __init__(self):
        self.tabs = self._initialize_default_tabs()
        self.active_tab = RibbonTabType.HOME
        self.panes = self._initialize_default_panes()
    
    def _initialize_default_tabs(self) -> List[RibbonTab]:
        """Initialize default ribbon tabs"""
        return [
            RibbonTab(
                id="home_tab",
                title="Home",
                type=RibbonTabType.HOME,
                groups=[
                    RibbonGroup(
                        id="navigation_group",
                        title="Navigation",
                        buttons=[
                            RibbonButton("nav_dashboard", "Dashboard", "dashboard", "navigate_dashboard", "Go to dashboard"),
                            RibbonButton("nav_email", "Email", "email", "navigate_email", "Go to email"),
                            RibbonButton("nav_calendar", "Calendar", "calendar", "navigate_calendar", "Go to calendar"),
                            RibbonButton("nav_meetings", "Meetings", "meetings", "navigate_meetings", "Go to meetings"),
                        ]
                    ),
                    RibbonGroup(
                        id="actions_group",
                        title="Actions",
                        buttons=[
                            RibbonButton("new_email", "New Email", "compose", "email_compose", "Compose new email"),
                            RibbonButton("new_meeting", "New Meeting", "add", "meeting_book", "Schedule new meeting"),
                            RibbonButton("search", "Search", "search", "open_command_palette", "Open command palette", variant="primary"),
                        ]
                    )
                ]
            ),
            RibbonTab(
                id="email_tab",
                title="Email",
                type=RibbonTabType.EMAIL,
                groups=[
                    RibbonGroup(
                        id="email_actions",
                        title="Actions",
                        buttons=[
                            RibbonButton("compose", "Compose", "compose", "email_compose", "Compose new email"),
                            RibbonButton("reply", "Reply", "reply", "email_reply", "Reply to email"),
                            RibbonButton("forward", "Forward", "forward", "email_forward", "Forward email"),
                            RibbonButton("delete", "Delete", "delete", "email_delete", "Delete email", variant="danger"),
                        ]
                    ),
                    RibbonGroup(
                        id="email_management",
                        title="Manage",
                        buttons=[
                            RibbonButton("archive", "Archive", "archive", "email_archive", "Archive email"),
                            RibbonButton("spam", "Mark Spam", "spam", "email_spam", "Mark as spam"),
                            RibbonButton("unread", "Mark Unread", "unread", "email_unread", "Mark as unread"),
                        ]
                    )
                ]
            ),
            RibbonTab(
                id="calendar_tab",
                title="Calendar",
                type=RibbonTabType.CALENDAR,
                groups=[
                    RibbonGroup(
                        id="calendar_actions",
                        title="Actions",
                        buttons=[
                            RibbonButton("new_event", "New Event", "add", "calendar_new_event", "Create new event"),
                            RibbonButton("today", "Today", "today", "calendar_today", "Go to today"),
                            RibbonButton("week", "Week View", "week", "calendar_week", "Week view"),
                            RibbonButton("month", "Month View", "month", "calendar_month", "Month view"),
                        ]
                    )
                ]
            ),
            RibbonTab(
                id="meetings_tab",
                title="Meetings",
                type=RibbonTabType.MEETINGS,
                groups=[
                    RibbonGroup(
                        id="meeting_actions",
                        title="Actions",
                        buttons=[
                            RibbonButton("schedule", "Schedule", "schedule", "meeting_book", "Schedule meeting"),
                            RibbonButton("join", "Join", "join", "meeting_join", "Join meeting"),
                            RibbonButton("record", "Record", "record", "meeting_record", "Record meeting"),
                        ]
                    )
                ]
            ),
            RibbonTab(
                id="settings_tab",
                title="Settings",
                type=RibbonTabType.SETTINGS,
                groups=[
                    RibbonGroup(
                        id="general_settings",
                        title="General",
                        buttons=[
                            RibbonButton("preferences", "Preferences", "settings", "settings_preferences", "Open preferences"),
                            RibbonButton("account", "Account", "account", "settings_account", "Account settings"),
                            RibbonButton("appearance", "Appearance", "appearance", "settings_appearance", "Change appearance"),
                        ]
                    )
                ]
            )
        ]
    
    def _initialize_default_panes(self) -> List[PaneConfig]:
        """Initialize default application panes"""
        return [
            PaneConfig(
                id="sidebar_pane",
                title="Navigation",
                width=250,
                min_width=200,
                max_width=400,
                resizable=True,
                collapsible=True,
                default_collapsed=False
            ),
            PaneConfig(
                id="main_pane",
                title="Main Content",
                width=800,
                min_width=600,
                resizable=False,
                collapsible=False
            ),
            PaneConfig(
                id="details_pane",
                title="Details",
                width=350,
                min_width=250,
                max_width=500,
                resizable=True,
                collapsible=True,
                default_collapsed=True
            )
        ]
    
    def get_tab_by_type(self, tab_type: RibbonTabType) -> Optional[RibbonTab]:
        """Get ribbon tab by type"""
        for tab in self.tabs:
            if tab.type == tab_type:
                return tab
        return None
    
    def set_active_tab(self, tab_type: RibbonTabType) -> bool:
        """Set the active ribbon tab"""
        if self.get_tab_by_type(tab_type):
            self.active_tab = tab_type
            return True
        return False
    
    def get_active_tab(self) -> Optional[RibbonTab]:
        """Get the currently active ribbon tab"""
        return self.get_tab_by_type(self.active_tab)
    
    def add_custom_tab(self, tab: RibbonTab) -> None:
        """Add a custom ribbon tab"""
        self.tabs.append(tab)
    
    def update_pane_content(self, pane_id: str, content: Dict[str, Any]) -> bool:
        """Update content of a specific pane"""
        for pane in self.panes:
            if pane.id == pane_id:
                pane.content = content
                return True
        return False
    
    def get_pane_config(self, pane_id: str) -> Optional[PaneConfig]:
        """Get configuration for a specific pane"""
        for pane in self.panes:
            if pane.id == pane_id:
                return pane
        return None
    
    def create_ribbon_component(self) -> Dict[str, Any]:
        """Create A2UI ribbon component"""
        active_tab = self.get_active_tab()
        if not active_tab:
            return {}
        
        return {
            "component": {
                "Ribbon": {
                    "tabs": [
                        {
                            "id": tab.id,
                            "title": tab.title,
                            "type": tab.type.value,
                            "active": tab.type == self.active_tab,
                            "groups": [
                                {
                                    "id": group.id,
                                    "title": group.title,
                                    "buttons": [
                                        {
                                            "id": button.id,
                                            "title": button.title,
                                            "icon": button.icon,
                                            "action": button.action,
                                            "tooltip": button.tooltip,
                                            "enabled": button.enabled,
                                            "variant": button.variant
                                        }
                                        for button in group.buttons
                                    ]
                                }
                                for group in tab.groups
                            ]
                        }
                        for tab in self.tabs
                    ],
                    "active_tab_id": active_tab.id,
                    "styles": {
                        "backgroundColor": "#f8fafc",
                        "borderBottom": "1px solid #e2e8f0",
                        "height": "60px"
                    }
                }
            }
        }
    
    def create_pane_component(self, pane_id: str, content: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create A2UI pane component"""
        pane = self.get_pane_config(pane_id)
        if not pane:
            return {}
        
        # Use provided content or pane's stored content
        pane_content = content or pane.content or {}
        
        return {
            "component": {
                "Pane": {
                    "id": pane.id,
                    "title": pane.title,
                    "width": pane.width,
                    "min_width": pane.min_width,
                    "max_width": pane.max_width,
                    "resizable": pane.resizable,
                    "collapsible": pane.collapsible,
                    "collapsed": pane.default_collapsed,
                    "content": pane_content,
                    "styles": {
                        "backgroundColor": "#ffffff",
                        "border": "1px solid #e2e8f0",
                        "borderRadius": "6px",
                        "overflow": "hidden"
                    }
                }
            }
        }
    
    def create_layout_component(self, layout_type: str = "three_pane") -> Dict[str, Any]:
        """Create A2UI layout component with ribbon and panes"""
        ribbon = self.create_ribbon_component()
        ribbon_component = ribbon.get("component", {}).get("Ribbon", {}) if ribbon else {}
        
        if layout_type == "three_pane":
            layout = {
                "component": {
                    "AppShell": {
                        "ribbon": ribbon_component,
                        "layout": {
                            "type": "three_pane",
                            "panes": [
                                self.create_pane_component("sidebar_pane"),
                                self.create_pane_component("main_pane"),
                                self.create_pane_component("details_pane")
                            ],
                            "orientation": "horizontal",
                            "sizes": [250, 800, 350]
                        },
                        "styles": {
                            "height": "100vh",
                            "display": "flex",
                            "flexDirection": "column",
                            "backgroundColor": "#f1f5f9"
                        }
                    }
                }
            }
        elif layout_type == "two_pane":
            layout = {
                "component": {
                    "AppShell": {
                        "ribbon": ribbon_component,
                        "layout": {
                            "type": "two_pane",
                            "panes": [
                                self.create_pane_component("sidebar_pane"),
                                self.create_pane_component("main_pane")
                            ],
                            "orientation": "horizontal",
                            "sizes": [250, 800]
                        },
                        "styles": {
                            "height": "100vh",
                            "display": "flex",
                            "flexDirection": "column",
                            "backgroundColor": "#f1f5f9"
                        }
                    }
                }
            }
        else:
            layout = {
                "component": {
                    "AppShell": {
                        "ribbon": ribbon_component,
                        "layout": {
                            "type": "single_pane",
                            "panes": [
                                self.create_pane_component("main_pane")
                            ]
                        },
                        "styles": {
                            "height": "100vh",
                            "display": "flex",
                            "flexDirection": "column",
                            "backgroundColor": "#f1f5f9"
                        }
                    }
                }
            }
        
        return layout
    
    def get_keyboard_shortcuts(self) -> List[Dict[str, Any]]:
        """Get all keyboard shortcuts from ribbon buttons"""
        shortcuts = []
        for tab in self.tabs:
            for group in tab.groups:
                for button in group.buttons:
                    if hasattr(button, 'shortcut') and button.shortcut:
                        shortcuts.append({
                            "key": button.shortcut,
                            "action": button.action,
                            "description": button.tooltip or button.title,
                            "context": tab.type.value
                        })
        return shortcuts