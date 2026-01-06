"""
Symphony Orchestrator - The Brain of Application Layer 3.0
Implements Neural Loops, Optimistic Execution, and Intent-driven UI composition
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

from .a2ui_components_extended import A2UIComponents
from .a2ui_state_machine import UIState
from .data_structures import ComponentGraph

logger = logging.getLogger(__name__)

class OrchestratorState(Enum):
    """Symphony Orchestrator states for Neural Loop processing"""
    IDLE = "idle"
    INTENT_PROCESSING = "intent_processing"
    AMBIGUITY_RESOLUTION = "ambiguity_resolution"
    OPTIMISTIC_EXECUTION = "optimistic_execution"
    COMPOSITION = "composition"
    ERROR_RECOVERY = "error_recovery"

@dataclass
class NeuralLoopContext:
    """Context for Neural Loop processing"""
    user_intent: str
    raw_input: str
    detected_intent: Optional[Dict[str, Any]] = None
    missing_parameters: List[str] = None
    clarification_questions: List[str] = None
    plugin_capabilities: List[Dict[str, Any]] = None
    execution_results: Dict[str, Any] = None
    ui_skeleton: Optional[Dict[str, Any]] = None
    error_context: Optional[Dict[str, Any]] = None

@dataclass  
class OptimisticExecutionResult:
    """Result of optimistic execution for latency hiding"""
    skeleton_component: Dict[str, Any]
    final_component: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0
    success: bool = True

class SymphonyOrchestrator:
    """
    Symphony Orchestrator - Core brain of Application Layer 3.0
    Implements Neural Loops, Optimistic Execution, and Intent-driven composition
    """
    
    def __init__(self, ai_engine=None, plugin_registry=None):
        self.state = OrchestratorState.IDLE
        self.components = A2UIComponents()
        self.current_loop: Optional[NeuralLoopContext] = None
        self.user_context = {}
        self.plugin_registry = plugin_registry
        self.ai_engine = ai_engine
        
        # Neural Loop handlers
        self.loop_handlers = {
            OrchestratorState.INTENT_PROCESSING: self._handle_intent_processing,
            OrchestratorState.AMBIGUITY_RESOLUTION: self._handle_ambiguity_resolution,
            OrchestratorState.OPTIMISTIC_EXECUTION: self._handle_optimistic_execution,
            OrchestratorState.COMPOSITION: self._handle_composition,
            OrchestratorState.ERROR_RECOVERY: self._handle_error_recovery
        }
    
    async def process_dashboard_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Special handler for dashboard requests - bypass Neural Loop ambiguity"""
        self.user_context = context
        self.current_loop = NeuralLoopContext(
            user_intent="dashboard",
            raw_input="show dashboard",
            missing_parameters=[],
            clarification_questions=[],
            plugin_capabilities=[]
        )
        
        # Create dashboard UI directly
        graph = ComponentGraph()
        
        # Main dashboard card
        dashboard_card = graph.add_node("Card", {
            "title": "📊 Dashboard",
            "content": f"Welcome back, {context.get('name', 'User')}!",
            "variant": "primary"
        })
        
        # Stats section
        stats_data = context.get('stats', {})
        stats_card = graph.add_node("Card", {
            "title": "📈 Quick Stats",
            "content": f"Meetings: {stats_data.get('meetings', 0)} | Emails: {stats_data.get('pendingEmails', 0)} | Video: {stats_data.get('activeVideo', 0)} | Campaigns: {stats_data.get('campaigns', 0)}",
            "variant": "info"
        })
        
        # Recent activity
        recent_activity = context.get('recent_activity', [])
        if recent_activity:
            activity_content = "Recent Activity:\n" + "\n".join(f"• {activity}" for activity in recent_activity)
            activity_card = graph.add_node("Card", {
                "title": "📝 Recent Activity",
                "content": activity_content,
                "variant": "secondary"
            })
            graph.add_child(dashboard_card, activity_card)
        
        # Upcoming events
        upcoming_events = context.get('upcoming_events', [])
        if upcoming_events:
            events_content = "Upcoming:\n" + "\n".join(f"• {event}" for event in upcoming_events)
            events_card = graph.add_node("Card", {
                "title": "📅 Upcoming Events",
                "content": events_content,
                "variant": "secondary"
            })
            graph.add_child(dashboard_card, events_card)
        
        graph.add_child(dashboard_card, stats_card)
        
        return {
            'type': 'final_response',
            'ui': graph.to_json(),
            'timestamp': datetime.now().isoformat(),
            'intent': 'dashboard'
        }
    
    async def process_user_intent(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Neural Loop processing
        Intent -> Clarification -> Composition -> Feedback -> Learning
        """
        self.user_context = context
        self.current_loop = NeuralLoopContext(
            user_intent=user_input,
            raw_input=user_input,
            missing_parameters=[],
            clarification_questions=[],
            plugin_capabilities=[]
        )
        
        # Start Neural Loop
        self.state = OrchestratorState.INTENT_PROCESSING
        
        # Execute the complete Neural Loop
        result = await self._execute_neural_loop()
        
        # Reset state
        self.state = OrchestratorState.IDLE
        
        return result
    
    async def _execute_neural_loop(self) -> Dict[str, Any]:
        """Execute the complete Neural Loop sequence"""
        result = {}
        
        try:
            # Process through all Neural Loop states
            for state in [
                OrchestratorState.INTENT_PROCESSING,
                OrchestratorState.AMBIGUITY_RESOLUTION,
                OrchestratorState.OPTIMISTIC_EXECUTION,
                OrchestratorState.COMPOSITION
            ]:
                self.state = state
                result = await self.loop_handlers[state]()
                
                # If we need to pause for clarification, return intermediate result
                if state == OrchestratorState.AMBIGUITY_RESOLUTION and \
                   self.current_loop.clarification_questions:
                    return self._create_clarification_response()
        
        except Exception as e:
            logger.error(f"Neural Loop error: {e}")
            self.state = OrchestratorState.ERROR_RECOVERY
            result = await self._handle_error_recovery(e)
        
        return result
    
    async def _handle_intent_processing(self) -> Dict[str, Any]:
        """Phase 1: Intent processing and capability discovery"""
        logger.info(f"Processing intent: {self.current_loop.raw_input}")
        
        # Use AI engine for intent detection (if available)
        if self.ai_engine:
            try:
                intent = await self.ai_engine.detect_intent(self.current_loop.raw_input)
                self.current_loop.detected_intent = {
                    'type': intent.intent,
                    'confidence': intent.confidence,
                    'entities': intent.entities
                }
            except Exception as e:
                logger.warning(f"AI intent detection failed: {e}")
                # Fallback to basic intent detection
                self.current_loop.detected_intent = self._fallback_intent_detection()
        else:
            self.current_loop.detected_intent = self._fallback_intent_detection()
        
        # Discover plugin capabilities for this intent
        if self.plugin_registry:
            self.current_loop.plugin_capabilities = await self.plugin_registry.discover_capabilities(
                self.current_loop.detected_intent['type']
            )
        
        # Check for missing parameters
        self._identify_missing_parameters()
        
        return {}
    
    async def _handle_ambiguity_resolution(self) -> Dict[str, Any]:
        """Phase 2: Ambiguity resolution with Interactive Clarification Blocks"""
        if not self.current_loop.missing_parameters:
            return {}  # No ambiguity to resolve
        
        # Generate clarification questions for missing parameters
        self.current_loop.clarification_questions = [
            self._generate_clarification_question(param)
            for param in self.current_loop.missing_parameters
        ]
        
        # If we have questions, pause execution and return clarification UI
        if self.current_loop.clarification_questions:
            return self._create_clarification_response()
        
        return {}
    
    async def _handle_optimistic_execution(self) -> Dict[str, Any]:
        """Phase 3: Optimistic Execution with Predictive Skeleton Streaming"""
        logger.info("Starting optimistic execution with skeleton streaming")
        
        # Generate predictive skeleton immediately (<200ms perceived latency)
        skeleton = self._generate_predictive_skeleton()
        self.current_loop.ui_skeleton = skeleton
        
        # Start async execution of actual plugin capabilities
        execution_task = asyncio.create_task(self._execute_plugin_capabilities())
        
        # Return skeleton immediately while execution continues in background
        return {
            'type': 'optimistic_response',
            'skeleton': skeleton,
            'execution_id': id(execution_task),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_composition(self) -> Dict[str, Any]:
        """Phase 4: Final composition with actual execution results"""
        if not self.current_loop.execution_results:
            # Wait for execution to complete if not already done
            await self._execute_plugin_capabilities()
        
        # Compose final UI with actual data
        final_ui = self._compose_final_ui()
        
        return {
            'type': 'final_response',
            'ui': final_ui,
            'execution_results': self.current_loop.execution_results,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_error_recovery(self, error: Exception) -> Dict[str, Any]:
        """Phase 5: Error recovery with Self-Healing UI"""
        logger.error(f"Error recovery triggered: {error}")
        
        # Create error boundary component
        error_ui = self._create_error_boundary(error)
        
        return {
            'type': 'error_response',
            'ui': error_ui,
            'error': str(error),
            'recovery_options': ['retry', 'fallback', 'cancel']
        }
    
    def _fallback_intent_detection(self) -> Dict[str, Any]:
        """Basic intent detection fallback when AI engine is unavailable"""
        input_text = self.current_loop.raw_input.lower()
        
        if any(word in input_text for word in ['email', 'send', 'message']):
            return {'type': 'send_email', 'confidence': 0.8, 'entities': {}}
        elif any(word in input_text for word in ['meeting', 'schedule', 'calendar']):
            return {'type': 'schedule_meeting', 'confidence': 0.8, 'entities': {}}
        elif any(word in input_text for word in ['show', 'view', 'list']):
            return {'type': 'view_content', 'confidence': 0.7, 'entities': {}}
        else:
            return {'type': 'general_chat', 'confidence': 0.5, 'entities': {}}
    
    def _identify_missing_parameters(self):
        """Identify missing parameters for the detected intent"""
        intent_type = self.current_loop.detected_intent['type']
        
        # Define required parameters for each intent type
        required_params = {
            'send_email': ['recipient', 'subject', 'body'],
            'schedule_meeting': ['title', 'participants', 'time'],
            'view_content': ['content_type']
        }
        
        self.current_loop.missing_parameters = required_params.get(intent_type, [])
    
    def _generate_clarification_question(self, parameter: str) -> str:
        """Generate clarification question for missing parameter"""
        questions = {
            'recipient': "Who would you like to send this email to?",
            'subject': "What should the subject of this email be?",
            'body': "What would you like to say in this email?",
            'title': "What should we title this meeting?",
            'participants': "Who should be invited to this meeting?",
            'time': "When would you like to schedule this meeting?",
            'content_type': "What would you like to view? (emails, meetings, tasks)"
        }
        
        return questions.get(parameter, f"Please provide {parameter}")
    
    def _create_clarification_response(self) -> Dict[str, Any]:
        """Create UI response for ambiguity resolution"""
        graph = ComponentGraph()
        
        # Create clarification card
        clarification_card = graph.add_node("Card", {
            "title": "🤔 Let's clarify",
            "content": "I need a bit more information to help you:",
            "variant": "info"
        })
        
        # Add clarification questions as form
        form_fields = []
        for i, question in enumerate(self.current_loop.clarification_questions):
            form_fields.append({
                "type": "text",
                "name": f"param_{i}",
                "label": question,
                "required": True
            })
        
        clarification_form = graph.add_node("Form", {
            "title": "Additional Information",
            "fields": form_fields,
            "actions": [
                {
                    "label": "Submit",
                    "action": "resolve_ambiguity",
                    "params": {
                        "intent": self.current_loop.detected_intent,
                        "missing_params": self.current_loop.missing_parameters
                    }
                }
            ]
        })
        
        graph.add_child(clarification_card, clarification_form)
        
        return {
            'type': 'clarification_response',
            'ui': graph.to_json(),
            'requires_user_input': True,
            'clarification_questions': self.current_loop.clarification_questions
        }
    
    def _generate_predictive_skeleton(self) -> Dict[str, Any]:
        """Generate predictive skeleton UI for optimistic execution"""
        intent_type = self.current_loop.detected_intent['type']
        
        # Skeleton templates for different intent types
        skeletons = {
            'send_email': self._create_email_skeleton,
            'schedule_meeting': self._create_meeting_skeleton,
            'view_content': self._create_content_skeleton,
            'general_chat': self._create_chat_skeleton
        }
        
        skeleton_generator = skeletons.get(intent_type, self._create_general_skeleton)
        return skeleton_generator()
    
    def _create_email_skeleton(self) -> Dict[str, Any]:
        """Create skeleton for email composition"""
        graph = ComponentGraph()
        
        email_card = graph.add_node("Card", {
            "title": "✉️ Composing Email...",
            "content": "Preparing your email",
            "variant": "info",
            "skeleton": True
        })
        
        return graph.to_json()
    
    def _create_meeting_skeleton(self) -> Dict[str, Any]:
        """Create skeleton for meeting scheduling"""
        graph = ComponentGraph()
        
        meeting_card = graph.add_node("Card", {
            "title": "📅 Scheduling Meeting...",
            "content": "Finding the perfect time",
            "variant": "info",
            "skeleton": True
        })
        
        return graph.to_json()
    
    async def _execute_plugin_capabilities(self) -> Dict[str, Any]:
        """Execute plugin capabilities for the detected intent"""
        if not self.plugin_registry or not self.current_loop.plugin_capabilities:
            return {}
        
        results = {}
        
        try:
            # Execute each plugin capability
            for capability in self.current_loop.plugin_capabilities:
                plugin_name = capability['plugin']
                method_name = capability['method']
                
                # Execute the capability
                result = await self.plugin_registry.execute_capability(
                    plugin_name, method_name, self.current_loop.detected_intent['entities']
                )
                
                results[f"{plugin_name}.{method_name}"] = result
        
        except Exception as e:
            logger.error(f"Plugin execution failed: {e}")
            results['error'] = str(e)
        
        self.current_loop.execution_results = results
        return results
    
    def _compose_final_ui(self) -> Dict[str, Any]:
        """Compose final UI with execution results"""
        graph = ComponentGraph()
        
        if not self.current_loop.execution_results or 'error' in self.current_loop.execution_results:
            # Return error UI if execution failed
            return self._create_error_boundary(
                Exception(self.current_loop.execution_results.get('error', 'Unknown error'))
            )
        
        # Create success UI based on intent type
        intent_type = self.current_loop.detected_intent['type']
        
        if intent_type == 'send_email':
            success_card = graph.add_node("Card", {
                "title": "✅ Email Sent",
                "content": "Your email has been sent successfully!",
                "variant": "success"
            })
        elif intent_type == 'schedule_meeting':
            success_card = graph.add_node("Card", {
                "title": "✅ Meeting Scheduled", 
                "content": "Your meeting has been scheduled successfully!",
                "variant": "success"
            })
        else:
            success_card = graph.add_node("Card", {
                "title": "✅ Completed",
                "content": "Your request has been processed successfully!",
                "variant": "success"
            })
        
        return graph.to_json()
    
    def _create_error_boundary(self, error: Exception) -> Dict[str, Any]:
        """Create self-healing error boundary UI"""
        graph = ComponentGraph()
        
        error_card = graph.add_node("Card", {
            "title": "⚠️ Something went wrong",
            "content": f"Error: {str(error)}",
            "variant": "error"
        })
        
        # Add recovery actions
        recovery_actions = graph.add_node("Actions", {
            "actions": [
                {
                    "label": "🔄 Retry",
                    "action": "retry_execution",
                    "variant": "primary"
                },
                {
                    "label": "🔀 Use Fallback",
                    "action": "use_fallback",
                    "variant": "secondary"
                },
                {
                    "label": "❌ Cancel",
                    "action": "cancel_operation",
                    "variant": "danger"
                }
            ]
        })
        
        graph.add_child(error_card, recovery_actions)
        
        return graph.to_json()
    
    def _create_content_skeleton(self) -> Dict[str, Any]:
        """Create skeleton for content viewing"""
        graph = ComponentGraph()
        
        content_card = graph.add_node("Card", {
            "title": "📊 Loading Content...",
            "content": "Gathering your information",
            "variant": "info",
            "skeleton": True
        })
        
        return graph.to_json()
    
    def _create_chat_skeleton(self) -> Dict[str, Any]:
        """Create skeleton for chat responses"""
        graph = ComponentGraph()
        
        chat_card = graph.add_node("Card", {
            "title": "💭 Thinking...",
            "content": "Processing your message",
            "variant": "info", 
            "skeleton": True
        })
        
        return graph.to_json()
    
    def _create_general_skeleton(self) -> Dict[str, Any]:
        """Create general purpose skeleton"""
        graph = ComponentGraph()
        
        general_card = graph.add_node("Card", {
            "title": "⚡ Processing...",
            "content": "Working on your request",
            "variant": "info",
            "skeleton": True
        })
        
        return graph.to_json()