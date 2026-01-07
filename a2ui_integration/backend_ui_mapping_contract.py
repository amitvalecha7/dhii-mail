"""
Backend→UI Intent Mapping Contract
Implementation of New Design Spec v1.2 mapping principles
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class IntentType(Enum):
    """Backend orchestrator intent types"""
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    REASON = "reason"
    CLARIFY = "clarify"
    OVERVIEW = "overview"
    STATUS = "status"
    INSIGHTS = "insights"
    PRIORITIES = "priorities"
    LIST = "list"
    SHOW = "show"
    BROWSE = "browse"
    COMPARE = "compare"
    ACTION = "action"
    CONFIRM = "confirm"
    INPUT = "input"
    ERROR = "error"

class ChunkType(Enum):
    """Allowed UI chunk types"""
    TEXT_BLOCK = "TextBlock"
    AGGREGATED_CARD = "AggregatedCard"
    DATA_TABLE = "DataTable"
    LIST_CARD = "ListCard"
    ACTION_CARD = "ActionCard"
    FORM_CARD = "FormCard"
    ERROR_CARD = "ErrorCard"

class ToneType(Enum):
    """TextBlock tone types"""
    NEUTRAL = "neutral"
    ADVISORY = "advisory"
    WARNING = "warning"

class OrchestratorOutput(BaseModel):
    """Mandatory orchestrator output envelope"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    user_id: str
    state: str = Field(regex="^(STREAMING|WAITING_FOR_CONFIRMATION|COMPLETED|ERROR)$")
    explanation: Optional[str] = None
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class IntentMappingRule(BaseModel):
    """Mapping rule from backend intent to UI chunk"""
    intent_type: IntentType
    description: str
    chunk_type: ChunkType
    required_fields: List[str]
    optional_fields: List[str]
    ui_behavior: str
    validation_rules: List[str] = Field(default_factory=list)

class BackendUIMappingContract:
    """Contract that defines backend→UI intent mapping (New Design Spec v1.2)"""
    
    def __init__(self):
        self.mapping_rules = self._build_mapping_rules()
        self.validate_contract()
    
    def _build_mapping_rules(self) -> Dict[IntentType, IntentMappingRule]:
        """Build the complete mapping ruleset"""
        return {
            # Informational Reasoning
            IntentType.EXPLAIN: IntentMappingRule(
                intent_type=IntentType.EXPLAIN,
                description="Explain concepts or provide reasoning",
                chunk_type=ChunkType.TEXT_BLOCK,
                required_fields=["content", "tone"],
                optional_fields=["completed", "collapsible"],
                ui_behavior="Render as conversational text, collapsible after completion, no actions allowed",
                validation_rules=["tone must be neutral|advisory|warning", "content must be non-empty"]
            ),
            IntentType.SUMMARIZE: IntentMappingRule(
                intent_type=IntentType.SUMMARIZE,
                description="Summarize information or content",
                chunk_type=ChunkType.TEXT_BLOCK,
                required_fields=["content", "tone"],
                optional_fields=["completed", "collapsible"],
                ui_behavior="Render as conversational text, collapsible after completion",
                validation_rules=["tone must be neutral|advisory|warning", "content must be non-empty"]
            ),
            IntentType.REASON: IntentMappingRule(
                intent_type=IntentType.REASON,
                description="Provide reasoning or analysis",
                chunk_type=ChunkType.TEXT_BLOCK,
                required_fields=["content", "tone"],
                optional_fields=["completed", "collapsible"],
                ui_behavior="Render as conversational text, collapsible after completion",
                validation_rules=["tone must be neutral|advisory|warning", "content must be non-empty"]
            ),
            IntentType.CLARIFY: IntentMappingRule(
                intent_type=IntentType.CLARIFY,
                description="Clarify concepts or information",
                chunk_type=ChunkType.TEXT_BLOCK,
                required_fields=["content", "tone"],
                optional_fields=["completed", "collapsible"],
                ui_behavior="Render as conversational text, collapsible after completion",
                validation_rules=["tone must be neutral|advisory|warning", "content must be non-empty"]
            ),
            
            # Aggregated Insights (Dashboard Replacement)
            IntentType.OVERVIEW: IntentMappingRule(
                intent_type=IntentType.OVERVIEW,
                description="Provide overview or summary",
                chunk_type=ChunkType.AGGREGATED_CARD,
                required_fields=["title", "sources", "items"],
                optional_fields=["multiple_sources", "partial_rendering", "importance_based_layout"],
                ui_behavior="Replaces dashboards, renders as single card, supports partial rendering if sources fail",
                validation_rules=["sources must be non-empty list", "items must be non-empty list", "each item must have label and value"]
            ),
            IntentType.STATUS: IntentMappingRule(
                intent_type=IntentType.STATUS,
                description="Show current status or state",
                chunk_type=ChunkType.AGGREGATED_CARD,
                required_fields=["title", "sources", "items"],
                optional_fields=["multiple_sources", "partial_rendering", "importance_based_layout"],
                ui_behavior="Replaces dashboards, renders as single card",
                validation_rules=["sources must be non-empty list", "items must be non-empty list", "each item must have label and value"]
            ),
            IntentType.INSIGHTS: IntentMappingRule(
                intent_type=IntentType.INSIGHTS,
                description="Provide insights or analysis",
                chunk_type=ChunkType.AGGREGATED_CARD,
                required_fields=["title", "sources", "items"],
                optional_fields=["multiple_sources", "partial_rendering", "importance_based_layout"],
                ui_behavior="Replaces dashboards, renders as single card",
                validation_rules=["sources must be non-empty list", "items must be non-empty list", "each item must have label and value"]
            ),
            IntentType.PRIORITIES: IntentMappingRule(
                intent_type=IntentType.PRIORITIES,
                description="Show priorities or focus areas",
                chunk_type=ChunkType.AGGREGATED_CARD,
                required_fields=["title", "sources", "items"],
                optional_fields=["multiple_sources", "partial_rendering", "importance_based_layout"],
                ui_behavior="Replaces dashboards, renders as single card",
                validation_rules=["sources must be non-empty list", "items must be non-empty list", "each item must have label and value"]
            ),
            
            # Data Presentation
            IntentType.LIST: IntentMappingRule(
                intent_type=IntentType.LIST,
                description="Display data as a list",
                chunk_type=ChunkType.LIST_CARD,
                required_fields=["items"],
                optional_fields=["title", "columns"],
                ui_behavior="Read-only by default, supports sorting and filtering",
                validation_rules=["items must be non-empty list"]
            ),
            IntentType.SHOW: IntentMappingRule(
                intent_type=IntentType.SHOW,
                description="Show specific data or information",
                chunk_type=ChunkType.DATA_TABLE,
                required_fields=["columns", "rows"],
                optional_fields=["title", "sortable", "searchable"],
                ui_behavior="Read-only by default, supports sorting and filtering",
                validation_rules=["columns must be non-empty list", "rows must be non-empty list"]
            ),
            IntentType.BROWSE: IntentMappingRule(
                intent_type=IntentType.BROWSE,
                description="Allow browsing through data",
                chunk_type=ChunkType.LIST_CARD,
                required_fields=["items"],
                optional_fields=["title", "columns", "pagination"],
                ui_behavior="Supports navigation and pagination",
                validation_rules=["items must be non-empty list"]
            ),
            IntentType.COMPARE: IntentMappingRule(
                intent_type=IntentType.COMPARE,
                description="Compare data or items",
                chunk_type=ChunkType.DATA_TABLE,
                required_fields=["columns", "rows"],
                optional_fields=["title", "sortable", "comparison_mode"],
                ui_behavior="Read-only by default, supports comparison features",
                validation_rules=["columns must be non-empty list", "rows must be non-empty list"]
            )
        }
    
    def validate_orchestrator_output(self, output: OrchestratorOutput) -> bool:
        """Validate orchestrator output against the contract"""
        if not output.chunks:
            return True  # Empty chunks is valid
        
        for chunk in output.chunks:
            if not self.validate_chunk(chunk):
                return False
        
        return True
    
    def validate_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Validate a single chunk against the mapping rules"""
        chunk_type = chunk.get("type")
        if not chunk_type:
            return False
        
        # Find the mapping rule for this chunk type
        for rule in self.mapping_rules.values():
            if rule.chunk_type.value == chunk_type:
                return self._validate_chunk_against_rule(chunk, rule)
        
        # Unknown chunk type
        return False
    
    def _validate_chunk_against_rule(self, chunk: Dict[str, Any], rule: IntentMappingRule) -> bool:
        """Validate chunk against specific mapping rule"""
        # Check required fields
        for field in rule.required_fields:
            if field not in chunk:
                return False
        
        # Apply validation rules
        for validation_rule in rule.validation_rules:
            if not self._apply_validation_rule(chunk, validation_rule):
                return False
        
        return True
    
    def _apply_validation_rule(self, chunk: Dict[str, Any], rule: str) -> bool:
        """Apply a specific validation rule"""
        if rule.startswith("tone must be"):
            tone = chunk.get("tone", "neutral")
            allowed_tones = rule.split("must be ")[1].split("|")
            return tone in allowed_tones
        
        elif rule == "content must be non-empty":
            content = chunk.get("content", "")
            return bool(content and content.strip())
        
        elif rule == "sources must be non-empty list":
            sources = chunk.get("sources", [])
            return isinstance(sources, list) and len(sources) > 0
        
        elif rule == "items must be non-empty list":
            items = chunk.get("items", [])
            return isinstance(items, list) and len(items) > 0
        
        elif rule == "columns must be non-empty list":
            columns = chunk.get("columns", [])
            return isinstance(columns, list) and len(columns) > 0
        
        elif rule == "rows must be non-empty list":
            rows = chunk.get("rows", [])
            return isinstance(rows, list) and len(rows) > 0
        
        elif rule == "each item must have label and value":
            items = chunk.get("items", [])
            for item in items:
                if not isinstance(item, dict):
                    return False
                if "label" not in item or "value" not in item:
                    return False
            return True
        
        return True  # Unknown rule, assume valid
    
    def get_chunk_type_for_intent(self, intent_type: IntentType) -> Optional[ChunkType]:
        """Get the expected chunk type for a given intent"""
        rule = self.mapping_rules.get(intent_type)
        return rule.chunk_type if rule else None
    
    def validate_contract(self):
        """Validate that the contract is complete and consistent"""
        # Ensure all intent types have mapping rules
        for intent_type in IntentType:
            if intent_type not in self.mapping_rules:
                raise ValueError(f"Missing mapping rule for intent type: {intent_type}")
        
        # Ensure all chunk types are covered
        covered_chunk_types = {rule.chunk_type for rule in self.mapping_rules.values()}
        for chunk_type in ChunkType:
            if chunk_type not in covered_chunk_types:
                # This is acceptable - not all chunk types need to be mapped initially
                pass
    
    def get_contract_summary(self) -> Dict[str, Any]:
        """Get a summary of the mapping contract"""
        return {
            "total_intent_types": len(self.mapping_rules),
            "total_chunk_types": len(ChunkType),
            "mapped_chunk_types": len({rule.chunk_type for rule in self.mapping_rules.values()}),
            "principles": [
                "Backend emits meaning",
                "UI renders meaning", 
                "Humans decide meaning",
                "This mapping is the contract that makes Dhii scalable"
            ],
            "core_rules": [
                "Backend never sends UI directly",
                "Backend sends structured intent-aligned output",
                "UI renders as protocol-defined chunks",
                "Unknown chunk types → render error card",
                "Chunks order is authoritative",
                "UI must render in order",
                "UI must not reorder, merge, or drop chunks"
            ]
        }

# Global contract instance
backend_ui_mapping_contract = BackendUIMappingContract()