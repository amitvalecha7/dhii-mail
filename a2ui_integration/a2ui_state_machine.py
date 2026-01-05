"""
A2UI State Machine - Handles UI state transitions and validation
Implements the state machine pattern from orchestrator_spec.md
"""

import logging
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class UIState(Enum):
    """Application UI states for A2UI orchestration"""
    DASHBOARD = "dashboard"
    EMAIL_INBOX = "email_inbox"
    EMAIL_COMPOSE = "email_compose"
    EMAIL_DETAIL = "email_detail"
    CALENDAR_VIEW = "calendar_view"
    MEETING_LIST = "meeting_list"
    MEETING_DETAIL = "meeting_detail"
    MEETING_BOOK = "meeting_book"
    TASK_BOARD = "task_board"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    CHAT = "chat"

@dataclass
class StateTransition:
    """Represents a state transition"""
    from_state: UIState
    to_state: UIState
    action: str
    context: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None

class A2UIStateMachine:
    """
    State machine for A2UI orchestration
    
    Implements:
    - Valid state transitions
    - State history tracking
    - Transition validation
    - Context preservation
    - Rollback capabilities
    """
    
    def __init__(self):
        self.current_state = UIState.DASHBOARD
        self.state_history: List[StateTransition] = []
        self.state_context: Dict[UIState, Dict[str, Any]] = {}
        self.max_history_size = 50
        
        # Define valid state transitions
        self.valid_transitions = self._define_valid_transitions()
        
        # Initialize state contexts
        self._initialize_state_contexts()
    
    def _define_valid_transitions(self) -> Dict[UIState, Set[UIState]]:
        """Define which states can transition to which other states"""
        return {
            UIState.DASHBOARD: {
                UIState.DASHBOARD, UIState.EMAIL_INBOX, UIState.EMAIL_COMPOSE, UIState.CALENDAR_VIEW, UIState.MEETING_LIST,
                UIState.MEETING_BOOK, UIState.TASK_BOARD, UIState.ANALYTICS, UIState.SETTINGS, UIState.CHAT
            },
            UIState.EMAIL_INBOX: {
                UIState.EMAIL_INBOX, UIState.EMAIL_DETAIL, UIState.EMAIL_COMPOSE, UIState.DASHBOARD,
                UIState.CALENDAR_VIEW, UIState.MEETING_LIST
            },
            UIState.EMAIL_DETAIL: {
                UIState.EMAIL_INBOX, UIState.EMAIL_COMPOSE, UIState.DASHBOARD
            },
            UIState.EMAIL_COMPOSE: {
                UIState.EMAIL_INBOX, UIState.EMAIL_DETAIL, UIState.DASHBOARD
            },
            UIState.CALENDAR_VIEW: {
                UIState.CALENDAR_VIEW, UIState.MEETING_BOOK, UIState.MEETING_DETAIL, UIState.DASHBOARD,
                UIState.EMAIL_INBOX
            },
            UIState.MEETING_LIST: {
                UIState.MEETING_DETAIL, UIState.MEETING_BOOK, UIState.DASHBOARD,
                UIState.CALENDAR_VIEW
            },
            UIState.MEETING_DETAIL: {
                UIState.MEETING_LIST, UIState.CALENDAR_VIEW, UIState.DASHBOARD, UIState.MEETING_BOOK
            },
            UIState.MEETING_BOOK: {
                UIState.MEETING_LIST, UIState.CALENDAR_VIEW, UIState.DASHBOARD
            },
            UIState.TASK_BOARD: {
                UIState.DASHBOARD, UIState.EMAIL_INBOX, UIState.CALENDAR_VIEW
            },
            UIState.ANALYTICS: {
                UIState.DASHBOARD, UIState.EMAIL_INBOX, UIState.CALENDAR_VIEW
            },
            UIState.SETTINGS: {
                UIState.DASHBOARD, UIState.EMAIL_INBOX, UIState.CALENDAR_VIEW
            },
            UIState.CHAT: {
                UIState.DASHBOARD, UIState.EMAIL_INBOX, UIState.CALENDAR_VIEW
            }
        }
    
    def _initialize_state_contexts(self):
        """Initialize empty contexts for all states"""
        for state in UIState:
            self.state_context[state] = {}
    
    def can_transition(self, from_state: UIState, to_state: UIState) -> bool:
        """Check if a transition is valid"""
        valid_targets = self.valid_transitions.get(from_state, set())
        return to_state in valid_targets
    
    def transition_to(self, to_state: UIState, action: str = "user_action", 
                     context: Dict[str, Any] = None, user_id: Optional[str] = None) -> bool:
        """
        Transition to a new state
        
        Args:
            to_state: Target state
            action: Action that triggered the transition
            context: Additional context for the transition
            user_id: User identifier
            
        Returns:
            True if transition was successful, False otherwise
        """
        if not self.can_transition(self.current_state, to_state):
            logger.warning(f"Invalid transition: {self.current_state.value} -> {to_state.value}")
            return False
        
        # Create transition record
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            action=action,
            context=context or {},
            timestamp=datetime.now(),
            user_id=user_id
        )
        
        # Update state
        self.current_state = to_state
        
        # Store transition in history
        self.state_history.append(transition)
        
        # Maintain history size limit
        if len(self.state_history) > self.max_history_size:
            self.state_history.pop(0)
        
        # Update state context
        if context:
            self.state_context[to_state].update(context)
        
        logger.info(f"State transition: {transition.from_state.value} -> {transition.to_state.value} via {action}")
        return True
    
    def get_current_state(self) -> UIState:
        """Get current state"""
        return self.current_state
    
    def get_state_context(self, state: UIState) -> Dict[str, Any]:
        """Get context for a specific state"""
        return self.state_context.get(state, {}).copy()
    
    def get_state_history(self, limit: int = None) -> List[StateTransition]:
        """Get state transition history"""
        if limit is None:
            return self.state_history.copy()
        return self.state_history[-limit:].copy()
    
    def get_available_transitions(self) -> Set[UIState]:
        """Get available transitions from current state"""
        return self.valid_transitions.get(self.current_state, set()).copy()
    
    def rollback_to_previous(self) -> bool:
        """Rollback to previous state"""
        if len(self.state_history) < 2:
            logger.warning("Cannot rollback: insufficient history")
            return False
        
        # Get the previous transition (second to last)
        previous_transition = self.state_history[-2]
        
        # Create rollback transition
        rollback_transition = StateTransition(
            from_state=self.current_state,
            to_state=previous_transition.from_state,
            action="rollback",
            context={"rollback_from": self.current_state.value},
            timestamp=datetime.now(),
            user_id=previous_transition.user_id
        )
        
        # Update state
        self.current_state = previous_transition.from_state
        self.state_history.append(rollback_transition)
        
        logger.info(f"Rollback: {rollback_transition.from_state.value} -> {rollback_transition.to_state.value}")
        return True
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get comprehensive state information"""
        return {
            "current_state": self.current_state.value,
            "available_transitions": [state.value for state in self.get_available_transitions()],
            "history_size": len(self.state_history),
            "recent_transitions": [
                {
                    "from": t.from_state.value,
                    "to": t.to_state.value,
                    "action": t.action,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in self.state_history[-5:]  # Last 5 transitions
            ]
        }
    
    def clear_state_context(self, state: UIState):
        """Clear context for a specific state"""
        self.state_context[state] = {}
        logger.info(f"Cleared context for state: {state.value}")
    
    def clear_all_contexts(self):
        """Clear all state contexts"""
        self._initialize_state_contexts()
        logger.info("Cleared all state contexts")