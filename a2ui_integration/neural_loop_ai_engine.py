"""
Enhanced Neural Loop AI Engine for A2UI
Provides advanced intent resolution, ambiguity handling, and reasoning capabilities
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Enhanced intent types for better classification"""
    DASHBOARD = "dashboard"
    EMAIL_COMPOSE = "email_compose"
    EMAIL_READ = "email_read"
    EMAIL_SEND = "email_send"
    CALENDAR_VIEW = "calendar_view"
    MEETING_SCHEDULE = "meeting_schedule"
    MEETING_CANCEL = "meeting_cancel"
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    CONTACT_SEARCH = "contact_search"
    CONTACT_ADD = "contact_add"
    ANALYTICS_VIEW = "analytics_view"
    SETTINGS_UPDATE = "settings_update"
    HELP_REQUEST = "help_request"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"

class AmbiguityType(Enum):
    """Types of ambiguity that require resolution"""
    MULTIPLE_INTENTS = "multiple_intents"
    MISSING_ENTITIES = "missing_entities"
    UNCLEAR_ACTION = "unclear_action"
    VAGUE_REFERENCES = "vague_references"
    CONFLICTING_PARAMETERS = "conflicting_parameters"

@dataclass
class Entity:
    """Represents extracted entities from user input"""
    entity_type: str
    value: str
    confidence: float
    position: Tuple[int, int]
    metadata: Dict[str, Any] = None

@dataclass
class IntentCandidate:
    """Represents a candidate intent with confidence scoring"""
    intent_type: IntentType
    confidence: float
    entities: List[Entity]
    missing_entities: List[str]
    ambiguity_type: Optional[AmbiguityType] = None
    clarification_needed: bool = False
    reasoning: str = ""

@dataclass
class NeuralLoopContext:
    """Enhanced context for Neural Loop processing"""
    user_input: str
    session_history: List[Dict[str, Any]]
    user_profile: Dict[str, Any]
    tenant_context: Dict[str, Any]
    timestamp: datetime
    intent_candidates: List[IntentCandidate]
    selected_intent: Optional[IntentCandidate] = None
    clarification_questions: List[str] = None
    reasoning_chain: List[str] = None

class EnhancedNeuralLoopEngine:
    """Enhanced AI engine for sophisticated intent resolution"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.entity_patterns = self._initialize_entity_patterns()
        self.clarification_templates = self._initialize_clarification_templates()
        self.reasoning_templates = self._initialize_reasoning_templates()
        
    def _initialize_intent_patterns(self) -> Dict[IntentType, List[Dict[str, Any]]]:
        """Initialize comprehensive intent detection patterns"""
        return {
            IntentType.DASHBOARD: [
                {"patterns": [r"show.*dashboard", r"go.*home", r"main.*page", r"overview"], "confidence": 0.9},
                {"patterns": [r"dashboard", r"home", r"start"], "confidence": 0.8}
            ],
            IntentType.EMAIL_COMPOSE: [
                {"patterns": [r"write.*email", r"compose.*email", r"new.*email", r"draft.*email"], "confidence": 0.95},
                {"patterns": [r"send.*email", r"email.*to", r"message.*to"], "confidence": 0.85},
                {"patterns": [r"compose", r"write", r"draft"], "confidence": 0.7}
            ],
            IntentType.EMAIL_READ: [
                {"patterns": [r"read.*email", r"check.*email", r"view.*email", r"inbox"], "confidence": 0.9},
                {"patterns": [r"emails", r"messages"], "confidence": 0.8}
            ],
            IntentType.CALENDAR_VIEW: [
                {"patterns": [r"show.*calendar", r"view.*calendar", r"check.*calendar", r"schedule"], "confidence": 0.9},
                {"patterns": [r"calendar", r"events", r"appointments"], "confidence": 0.8}
            ],
            IntentType.MEETING_SCHEDULE: [
                {"patterns": [r"schedule.*meeting", r"book.*meeting", r"set.*meeting", r"arrange.*meeting"], "confidence": 0.95},
                {"patterns": [r"meeting.*with", r"meet.*with", r"call.*with"], "confidence": 0.85},
                {"patterns": [r"meeting", r"meet"], "confidence": 0.7}
            ],
            IntentType.TASK_CREATE: [
                {"patterns": [r"create.*task", r"add.*task", r"new.*task", r"make.*task"], "confidence": 0.9},
                {"patterns": [r"task.*to.*do", r"todo"], "confidence": 0.8},
                {"patterns": [r"task"], "confidence": 0.6}
            ],
            IntentType.ANALYTICS_VIEW: [
                {"patterns": [r"show.*analytics", r"view.*analytics", r"reports", r"insights", r"statistics"], "confidence": 0.9},
                {"patterns": [r"analytics", r"data", r"metrics"], "confidence": 0.8}
            ],
            IntentType.HELP_REQUEST: [
                {"patterns": [r"help", r"assist", r"guide", r"what.*can.*you.*do", r"how.*to"], "confidence": 0.9},
                {"patterns": [r"support", r"instructions"], "confidence": 0.8}
            ],
            IntentType.GREETING: [
                {"patterns": [r"hello", r"hi", r"hey", r"good.*morning", r"good.*afternoon", r"good.*evening"], "confidence": 0.9}
            ],
            IntentType.GOODBYE: [
                {"patterns": [r"bye", r"goodbye", r"see.*you", r"talk.*later", r"done", r"finish"], "confidence": 0.9}
            ]
        }
    
    def _initialize_entity_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize entity extraction patterns"""
        return {
            "email": [
                {"pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "type": "email", "confidence": 0.95}
            ],
            "phone": [
                {"pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "type": "phone", "confidence": 0.9}
            ],
            "date": [
                {"pattern": r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", "type": "day", "confidence": 0.9},
                {"pattern": r"\b(?:tomorrow|today|yesterday)\b", "type": "relative_date", "confidence": 0.95},
                {"pattern": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "type": "date", "confidence": 0.9},
                {"pattern": r"\b(?:next|this|last)\s+(?:week|month|year)\b", "type": "relative_date", "confidence": 0.85}
            ],
            "time": [
                {"pattern": r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b", "type": "time", "confidence": 0.95},
                {"pattern": r"\b\d{1,2}\s*(?:am|pm)\b", "type": "time", "confidence": 0.9}
            ],
            "contact": [
                {"pattern": r"\b(?:contact|person|user)\s+(\w+)\b", "type": "contact_name", "confidence": 0.8},
                {"pattern": r"\b(?:to|with|from)\s+(\w+)\b", "type": "recipient", "confidence": 0.85}
            ],
            "priority": [
                {"pattern": r"\b(?:urgent|important|high.*priority)\b", "type": "high_priority", "confidence": 0.9},
                {"pattern": r"\b(?:low.*priority|not.*important)\b", "type": "low_priority", "confidence": 0.9}
            ]
        }
    
    def _initialize_clarification_templates(self) -> Dict[AmbiguityType, List[str]]:
        """Initialize clarification question templates"""
        return {
            AmbiguityType.MULTIPLE_INTENTS: [
                "I noticed you mentioned several things. Could you clarify what you'd like to focus on first?",
                "It sounds like you have multiple requests. Which one would you like me to help with first?",
                "I can help with a few different things you mentioned. What should we start with?"
            ],
            AmbiguityType.MISSING_ENTITIES: [
                "I'd be happy to help you {intent}. Could you provide more details about {missing_info}?",
                "To {intent}, I'll need some additional information: {missing_info}",
                "I can help with that! I'm missing some details though: {missing_info}"
            ],
            AmbiguityType.UNCLEAR_ACTION: [
                "I'm not sure what specific action you'd like to take. Could you clarify?",
                "What would you like me to do exactly?",
                "Could you be more specific about what you want to accomplish?"
            ],
            AmbiguityType.VAGUE_REFERENCES: [
                "Could you be more specific about what/who you're referring to?",
                "I'm not sure which {entity_type} you mean. Could you clarify?",
                "There might be multiple options. Which one are you referring to?"
            ]
        }
    
    def _initialize_reasoning_templates(self) -> Dict[str, List[str]]:
        """Initialize reasoning chain templates"""
        return {
            "intent_selection": [
                "User mentioned '{keyword}' which strongly suggests {intent_type}",
                "Pattern '{pattern}' matches {intent_type} with {confidence}% confidence",
                "Based on context and keywords, {intent_type} is the most likely intent"
            ],
            "ambiguity_detection": [
                "Multiple intent patterns detected: {intents}",
                "Missing required entities for {intent_type}: {entities}",
                "Conflicting parameters found: {conflicts}"
            ],
            "entity_extraction": [
                "Found {entity_type}: '{value}' at position {position}",
                "Extracted {count} entities of type {entity_type}",
                "Entity '{value}' has {confidence}% confidence"
            ]
        }
    
    def process_user_input(self, user_input: str, context: NeuralLoopContext) -> Dict[str, Any]:
        """Main processing method for enhanced Neural Loop"""
        try:
            logger.info(f"Processing user input: {user_input}")
            
            # Update context
            context.user_input = user_input
            context.timestamp = datetime.now()
            
            # Step 1: Extract entities
            entities = self._extract_entities(user_input)
            
            # Step 2: Detect intent candidates
            intent_candidates = self._detect_intent_candidates(user_input, entities, context)
            
            # Step 3: Rank and select best intent
            selected_intent = self._select_best_intent(intent_candidates, context)
            
            # Step 4: Handle ambiguity if needed
            if selected_intent.clarification_needed:
                clarification_questions = self._generate_clarification_questions(selected_intent, context)
                return {
                    "type": "clarification_required",
                    "selected_intent": selected_intent,
                    "clarification_questions": clarification_questions,
                    "reasoning": selected_intent.reasoning,
                    "confidence": selected_intent.confidence
                }
            
            # Step 5: Generate response
            response = self._generate_response(selected_intent, context)
            
            return {
                "type": "intent_resolved",
                "selected_intent": selected_intent,
                "response": response,
                "confidence": selected_intent.confidence,
                "reasoning": selected_intent.reasoning
            }
            
        except Exception as e:
            logger.error(f"Error in Neural Loop processing: {e}")
            return {
                "type": "error",
                "error": str(e),
                "fallback_intent": IntentCandidate(
                    intent_type=IntentType.UNKNOWN,
                    confidence=0.1,
                    entities=[],
                    missing_entities=[],
                    reasoning="Error occurred during processing"
                )
            }
    
    def _extract_entities(self, user_input: str) -> List[Entity]:
        """Extract entities from user input using advanced patterns"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern_config in patterns:
                pattern = pattern_config["pattern"]
                entity_type_name = pattern_config["type"]
                confidence = pattern_config["confidence"]
                
                matches = re.finditer(pattern, user_input, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        entity_type=entity_type_name,
                        value=match.group(),
                        confidence=confidence,
                        position=(match.start(), match.end()),
                        metadata={"pattern": pattern}
                    )
                    entities.append(entity)
        
        # Remove duplicate entities (same value and type)
        unique_entities = []
        seen = set()
        for entity in entities:
            key = (entity.entity_type, entity.value.lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _detect_intent_candidates(self, user_input: str, entities: List[Entity], context: NeuralLoopContext) -> List[IntentCandidate]:
        """Detect multiple intent candidates with confidence scoring"""
        candidates = []
        
        for intent_type, pattern_configs in self.intent_patterns.items():
            max_confidence = 0
            matched_patterns = []
            
            for pattern_config in pattern_configs:
                pattern = pattern_config["pattern"]
                confidence = pattern_config["confidence"]
                
                if re.search(pattern, user_input, re.IGNORECASE):
                    if confidence > max_confidence:
                        max_confidence = confidence
                    matched_patterns.append(pattern)
            
            if max_confidence > 0:
                # Analyze entities for this intent
                relevant_entities = self._get_relevant_entities(intent_type, entities)
                missing_entities = self._get_missing_entities(intent_type, relevant_entities)
                
                # Determine if clarification is needed
                clarification_needed = len(missing_entities) > 0 or max_confidence < 0.7
                
                # Generate reasoning
                reasoning = self._generate_intent_reasoning(intent_type, max_confidence, matched_patterns, entities)
                
                candidate = IntentCandidate(
                    intent_type=intent_type,
                    confidence=max_confidence,
                    entities=relevant_entities,
                    missing_entities=missing_entities,
                    clarification_needed=clarification_needed,
                    reasoning=reasoning
                )
                candidates.append(candidate)
        
        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        # If no clear intent found, add UNKNOWN with low confidence
        if not candidates or (candidates and candidates[0].confidence < 0.5):
            unknown_reasoning = "No clear intent patterns matched user input"
            if candidates:
                unknown_reasoning += f". Best match was {candidates[0].intent_type.value} with {candidates[0].confidence:.2f} confidence"
            
            unknown_candidate = IntentCandidate(
                intent_type=IntentType.UNKNOWN,
                confidence=0.3 if candidates else 0.1,
                entities=entities,
                missing_entities=[],
                clarification_needed=True,
                reasoning=unknown_reasoning
            )
            candidates.insert(0, unknown_candidate)
        
        return candidates
    
    def _get_relevant_entities(self, intent_type: IntentType, entities: List[Entity]) -> List[Entity]:
        """Get entities relevant to specific intent type"""
        relevant = []
        
        intent_entity_mapping = {
            IntentType.EMAIL_COMPOSE: ["email", "contact", "recipient"],
            IntentType.EMAIL_READ: ["email", "contact"],
            IntentType.MEETING_SCHEDULE: ["date", "time", "contact", "day"],
            IntentType.CALENDAR_VIEW: ["date", "day", "time"],
            IntentType.TASK_CREATE: ["priority", "date", "time"]
        }
        
        relevant_types = intent_entity_mapping.get(intent_type, [])
        
        for entity in entities:
            if entity.entity_type in relevant_types:
                relevant.append(entity)
        
        return relevant
    
    def _get_missing_entities(self, intent_type: IntentType, relevant_entities: List[Entity]) -> List[str]:
        """Identify missing entities required for intent execution"""
        missing = []
        
        intent_requirements = {
            IntentType.EMAIL_COMPOSE: ["recipient"],
            IntentType.MEETING_SCHEDULE: ["contact"],
            IntentType.TASK_CREATE: []
        }
        
        required_types = intent_requirements.get(intent_type, [])
        
        present_types = {entity.entity_type for entity in relevant_entities}
        
        for required_type in required_types:
            if required_type not in present_types:
                missing.append(required_type)
        
        return missing
    
    def _select_best_intent(self, candidates: List[IntentCandidate], context: NeuralLoopContext) -> IntentCandidate:
        """Select the best intent using advanced reasoning"""
        if not candidates:
            return IntentCandidate(
                intent_type=IntentType.UNKNOWN,
                confidence=0.1,
                entities=[],
                missing_entities=[],
                clarification_needed=True,
                reasoning="No intent candidates found"
            )
        
        # If we have a high-confidence candidate, use it
        if candidates[0].confidence >= 0.8 and not candidates[0].clarification_needed:
            return candidates[0]
        
        # Apply context-based reasoning
        enhanced_candidate = self._apply_context_reasoning(candidates, context)
        
        return enhanced_candidate
    
    def _apply_context_reasoning(self, candidates: List[IntentCandidate], context: NeuralLoopContext) -> IntentCandidate:
        """Apply context-based reasoning to improve intent selection"""
        # Consider session history
        if context.session_history:
            last_intent = context.session_history[-1].get("intent")
            if last_intent:
                # Boost confidence for related intents
                for candidate in candidates:
                    if self._are_intents_related(candidate.intent_type, last_intent):
                        candidate.confidence += 0.1
                        candidate.reasoning += f" (boosted due to related previous intent: {last_intent})"
        
        # Consider user profile
        if context.user_profile:
            user_preferences = context.user_profile.get("preferences", {})
            # Apply user-specific reasoning
            
        # Consider tenant context
        if context.tenant_context:
            available_features = context.tenant_context.get("features", [])
            # Filter intents based on available features
            
        # Re-sort after context adjustments
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        return candidates[0]
    
    def _are_intents_related(self, intent1: IntentType, intent2: str) -> bool:
        """Check if two intents are related"""
        related_groups = [
            [IntentType.EMAIL_COMPOSE, IntentType.EMAIL_READ, IntentType.EMAIL_SEND],
            [IntentType.CALENDAR_VIEW, IntentType.MEETING_SCHEDULE],
            [IntentType.TASK_CREATE, IntentType.TASK_UPDATE]
        ]
        
        for group in related_groups:
            if intent1 in group and intent2 in [i.value for i in group]:
                return True
        
        return False
    
    def _generate_intent_reasoning(self, intent_type: IntentType, confidence: float, matched_patterns: List[str], entities: List[Entity]) -> str:
        """Generate reasoning explanation for intent selection"""
        reasoning_parts = []
        
        if matched_patterns:
            reasoning_parts.append(f"Matched patterns: {', '.join(matched_patterns)}")
        
        if entities:
            entity_summary = ", ".join([f"{e.entity_type}:'{e.value}'" for e in entities[:3]])
            reasoning_parts.append(f"Found entities: {entity_summary}")
        
        reasoning_parts.append(f"Confidence: {confidence:.2f}")
        
        return "; ".join(reasoning_parts)
    
    def _generate_clarification_questions(self, intent: IntentCandidate, context: NeuralLoopContext) -> List[str]:
        """Generate clarification questions based on ambiguity type"""
        questions = []
        
        # Handle missing entities
        if intent.missing_entities:
            templates = self.clarification_templates.get(AmbiguityType.MISSING_ENTITIES, [])
            for template in templates:
                question = template.format(
                    intent=intent.intent_type.value.replace("_", " "),
                    missing_info=", ".join(intent.missing_entities)
                )
                questions.append(question)
        
        # Handle low confidence
        if intent.confidence < 0.6:
            questions.append("I'm not entirely sure what you'd like to do. Could you rephrase that?")
        
        # Handle unknown intent
        if intent.intent_type == IntentType.UNKNOWN:
            questions.append("I can help with email, calendar, meetings, and tasks. What would you like to do?")
        
        return questions[:2]  # Limit to 2 questions
    
    def _generate_response(self, intent: IntentCandidate, context: NeuralLoopContext) -> Dict[str, Any]:
        """Generate appropriate response based on resolved intent"""
        response_templates = {
            IntentType.DASHBOARD: {
                "message": "I'll show you your dashboard with an overview of your workspace.",
                "action": "navigate_dashboard",
                "ui_hint": "dashboard"
            },
            IntentType.EMAIL_COMPOSE: {
                "message": "I'll open the email composer for you.",
                "action": "open_email_composer",
                "ui_hint": "email_compose"
            },
            IntentType.EMAIL_READ: {
                "message": "I'll show you your email inbox.",
                "action": "show_email_inbox",
                "ui_hint": "email_inbox"
            },
            IntentType.CALENDAR_VIEW: {
                "message": "I'll display your calendar.",
                "action": "show_calendar",
                "ui_hint": "calendar"
            },
            IntentType.MEETING_SCHEDULE: {
                "message": "I'll help you schedule a meeting.",
                "action": "open_meeting_scheduler",
                "ui_hint": "meeting_schedule"
            },
            IntentType.TASK_CREATE: {
                "message": "I'll help you create a new task.",
                "action": "open_task_creator",
                "ui_hint": "task_create"
            },
            IntentType.ANALYTICS_VIEW: {
                "message": "I'll show you your analytics and insights.",
                "action": "show_analytics",
                "ui_hint": "analytics"
            },
            IntentType.HELP_REQUEST: {
                "message": "I can help you with email management, calendar scheduling, meetings, and tasks. What would you like to do?",
                "action": "show_help",
                "ui_hint": "help"
            },
            IntentType.GREETING: {
                "message": random.choice(["Hello! How can I help you today?", "Hi there! What can I do for you?", "Hello! I'm here to help with your email and calendar needs."]),
                "action": "greeting",
                "ui_hint": "greeting"
            },
            IntentType.GOODBYE: {
                "message": random.choice(["Goodbye! Have a great day!", "See you later! Feel free to reach out if you need anything.", "Take care! I'm here whenever you need help."]),
                "action": "goodbye",
                "ui_hint": "goodbye"
            }
        }
        
        # Get response template
        template = response_templates.get(intent.intent_type, {
            "message": "I'll help you with that.",
            "action": "unknown_action",
            "ui_hint": "general"
        })
        
        # Personalize based on user context
        if context.user_profile:
            user_name = context.user_profile.get("name", "User")
            if "{user}" in template["message"]:
                template["message"] = template["message"].format(user=user_name)
        
        return template

# Global enhanced Neural Loop engine instance
enhanced_neural_loop = EnhancedNeuralLoopEngine()