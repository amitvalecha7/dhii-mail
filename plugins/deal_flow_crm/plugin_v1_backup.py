"""
Deal-Flow CRM Plugin for dhii Mail
Implements comprehensive deal and pipeline management capabilities
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal

from a2ui_integration.core.plugins import BasePlugin
from a2ui_integration.core.types import PluginType, Capability, PluginStatus
from a2ui_integration.core.shared_services import get_shared_services
from .ui_components import DealFlowCRMUIRenderer

logger = logging.getLogger(__name__)

@dataclass
class Deal:
    """Represents a sales deal"""
    id: str
    title: str
    description: str
    value: Decimal
    currency: str
    stage: str
    probability: int  # 0-100
    contact_id: Optional[str] = None
    company_id: Optional[str] = None
    owner_id: str = "system"
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

@dataclass
class Pipeline:
    """Represents a sales pipeline"""
    id: str
    name: str
    description: str
    stages: List[str]
    is_default: bool = False
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class PipelineMetrics:
    """Pipeline analytics and metrics"""
    pipeline_id: str
    total_deals: int
    total_value: Decimal
    deals_by_stage: Dict[str, int]
    value_by_stage: Dict[str, Decimal]
    conversion_rates: Dict[str, float]
    avg_deal_size: Decimal
    avg_sales_cycle: int  # days

class DealFlowCRMPlugin(BasePlugin):
    """Deal-Flow CRM Plugin for comprehensive sales pipeline management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            plugin_id="deal_flow_crm",
            name="Deal-Flow CRM",
            version="1.0.0",
            description="Comprehensive deal flow and pipeline management for sales teams",
            plugin_type=PluginType.CUSTOM
        )
        # Initialize configuration with defaults
        self.config = config or {}
        # Get database path from configuration or use default
        self.db_path = self.config.get("database_path", "/tmp/dealflow_crm.db")
        self.shared_services = get_shared_services()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for CRM data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create deals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deals (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    value REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    stage TEXT NOT NULL,
                    probability INTEGER DEFAULT 0,
                    contact_id TEXT,
                    company_id TEXT,
                    owner_id TEXT DEFAULT 'system',
                    expected_close_date TEXT,
                    actual_close_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create pipelines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipelines (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    stages TEXT NOT NULL,  -- JSON array
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create default pipeline if none exists
            cursor.execute('SELECT COUNT(*) FROM pipelines WHERE is_default = TRUE')
            if cursor.fetchone()[0] == 0:
                default_stages = json.dumps([
                    "Prospecting", "Qualification", "Proposal", 
                    "Negotiation", "Closed Won", "Closed Lost"
                ])
                cursor.execute('''
                    INSERT INTO pipelines (id, name, description, stages, is_default, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    "default_pipeline",
                    "Default Sales Pipeline",
                    "Standard sales pipeline with 6 stages",
                    default_stages,
                    True,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            logger.info("Deal-Flow CRM database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CRM database: {e}")
            raise
    
    def _register_capabilities(self):
        """Register CRM-related capabilities"""
        capabilities = [
            # Deal management capabilities
            Capability(
                id="deal.create",
                domain="crm",
                name="Create Deal",
                description="Create a new sales deal",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "minLength": 1},
                        "description": {"type": "string"},
                        "value": {"type": "number", "minimum": 0},
                        "currency": {"type": "string", "default": "USD"},
                        "stage": {"type": "string"},
                        "contact_id": {"type": "string"},
                        "company_id": {"type": "string"},
                        "owner_id": {"type": "string"},
                        "expected_close_date": {"type": "string", "format": "date-time"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["title", "value"]
                },
                output_schema={"type": "object", "properties": {"deal_id": {"type": "string"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            
            Capability(
                id="deal.update",
                domain="crm",
                name="Update Deal",
                description="Update an existing deal",
                input_schema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "value": {"type": "number", "minimum": 0},
                        "stage": {"type": "string"},
                        "probability": {"type": "integer", "minimum": 0, "maximum": 100},
                        "contact_id": {"type": "string"},
                        "company_id": {"type": "string"},
                        "expected_close_date": {"type": "string", "format": "date-time"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["deal_id"]
                },
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            
            Capability(
                id="deal.delete",
                domain="crm",
                name="Delete Deal",
                description="Delete a deal",
                input_schema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string"}
                    },
                    "required": ["deal_id"]
                },
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
                side_effects=["delete"],
                requires_auth=True
            ),
            
            Capability(
                id="deal.get",
                domain="crm",
                name="Get Deal",
                description="Retrieve a specific deal",
                input_schema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string"}
                    },
                    "required": ["deal_id"]
                },
                output_schema={"type": "object"},
                side_effects=["read"]
            ),
            
            Capability(
                id="deal.list",
                domain="crm",
                name="List Deals",
                description="List deals with filtering and pagination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string"},
                        "stage": {"type": "string"},
                        "owner_id": {"type": "string"},
                        "contact_id": {"type": "string"},
                        "company_id": {"type": "string"},
                        "limit": {"type": "integer", "default": 50, "maximum": 500},
                        "offset": {"type": "integer", "default": 0},
                        "include_closed": {"type": "boolean", "default": False}
                    }
                },
                output_schema={"type": "object", "properties": {"deals": {"type": "array"}, "total": {"type": "integer"}}},
                side_effects=["read"]
            ),
            
            Capability(
                id="deal.move_stage",
                domain="crm",
                name="Move Deal Stage",
                description="Move a deal to a different pipeline stage",
                input_schema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string"},
                        "new_stage": {"type": "string"},
                        "reason": {"type": "string"}
                    },
                    "required": ["deal_id", "new_stage"]
                },
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            
            # Pipeline management capabilities
            Capability(
                id="pipeline.create",
                domain="crm",
                name="Create Pipeline",
                description="Create a new sales pipeline",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "description": {"type": "string"},
                        "stages": {"type": "array", "items": {"type": "string"}, "minItems": 2}
                    },
                    "required": ["name", "stages"]
                },
                output_schema={"type": "object", "properties": {"pipeline_id": {"type": "string"}}},
                side_effects=["write"],
                requires_auth=True
            ),
            
            Capability(
                id="pipeline.list",
                domain="crm",
                name="List Pipelines",
                description="List all available pipelines",
                input_schema={"type": "object"},
                output_schema={"type": "object", "properties": {"pipelines": {"type": "array"}}},
                side_effects=["read"]
            ),
            
            # Analytics capabilities
            Capability(
                id="analytics.pipeline_metrics",
                domain="crm",
                name="Pipeline Metrics",
                description="Get pipeline analytics and metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string"},
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start_date": {"type": "string", "format": "date-time"},
                                "end_date": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                },
                output_schema={"type": "object"},
                side_effects=["read"]
            ),
            
            Capability(
                id="analytics.deal_forecast",
                domain="crm",
                name="Deal Forecast",
                description="Generate deal forecast based on current pipeline",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string"},
                        "forecast_period": {"type": "integer", "default": 90, "description": "Days ahead to forecast"}
                    }
                },
                output_schema={"type": "object"},
                side_effects=["read"]
            ),
            
            # UI capabilities
            Capability(
                id="ui.dashboard",
                domain="crm",
                name="Deal Dashboard UI",
                description="Render the deal dashboard UI",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "default": "default_pipeline"}
                    }
                },
                output_schema={"type": "object", "properties": {"ui_operations": {"type": "array"}}},
                side_effects=["read"]
            ),
            
            Capability(
                id="ui.pipeline_view",
                domain="crm",
                name="Pipeline View UI",
                description="Render the pipeline view UI",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "default": "default_pipeline"}
                    }
                },
                output_schema={"type": "object", "properties": {"ui_operations": {"type": "array"}}},
                side_effects=["read"]
            ),
            
            Capability(
                id="ui.deal_form",
                domain="crm",
                name="Deal Form UI",
                description="Render the deal form UI",
                input_schema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string"},
                        "pipeline_id": {"type": "string", "default": "default_pipeline"}
                    }
                },
                output_schema={"type": "object", "properties": {"ui_operations": {"type": "array"}}},
                side_effects=["read"]
            ),
            
            Capability(
                id="ui.deal_list",
                domain="crm",
                name="Deal List UI",
                description="Render the deal list UI",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "default": "default_pipeline"},
                        "include_closed": {"type": "boolean", "default": False},
                        "limit": {"type": "integer", "default": 50, "maximum": 500},
                        "offset": {"type": "integer", "default": 0}
                    }
                },
                output_schema={"type": "object", "properties": {"ui_operations": {"type": "array"}}},
                side_effects=["read"]
            )
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    async def _initialize_plugin(self):
        """Initialize the CRM plugin"""
        logger.info("Deal-Flow CRM plugin initialized")
    
    async def _shutdown_plugin(self):
        """Shutdown the CRM plugin"""
        logger.info("Deal-Flow CRM plugin shut down")
    
    async def _execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific CRM capability"""
        if capability_id.startswith("deal."):
            return await self._execute_deal_capability(capability_id, params)
        elif capability_id.startswith("pipeline."):
            return await self._execute_pipeline_capability(capability_id, params)
        elif capability_id.startswith("analytics."):
            return await self._execute_analytics_capability(capability_id, params)
        elif capability_id.startswith("ui."):
            return await self._execute_ui_capability(capability_id, params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    async def _execute_deal_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deal-related capabilities"""
        if capability_id == "deal.create":
            return await self._create_deal(params)
        elif capability_id == "deal.update":
            return await self._update_deal(params)
        elif capability_id == "deal.delete":
            return await self._delete_deal(params)
        elif capability_id == "deal.get":
            return await self._get_deal(params)
        elif capability_id == "deal.list":
            return await self._list_deals(params)
        elif capability_id == "deal.move_stage":
            return await self._move_deal_stage(params)
        else:
            raise ValueError(f"Unknown deal capability: {capability_id}")
    
    async def _execute_pipeline_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline-related capabilities"""
        if capability_id == "pipeline.create":
            return await self._create_pipeline(params)
        elif capability_id == "pipeline.list":
            return await self._list_pipelines(params)
        else:
            raise ValueError(f"Unknown pipeline capability: {capability_id}")
    
    async def _execute_analytics_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics-related capabilities"""
        if capability_id == "analytics.pipeline_metrics":
            return await self._get_pipeline_metrics(params)
        elif capability_id == "analytics.deal_forecast":
            return await self._get_deal_forecast(params)
        else:
            raise ValueError(f"Unknown analytics capability: {capability_id}")
    
    async def _execute_ui_capability(self, capability_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UI-related capabilities"""
        if capability_id == "ui.dashboard":
            return await self._render_dashboard_ui(params)
        elif capability_id == "ui.pipeline_view":
            return await self._render_pipeline_ui(params)
        elif capability_id == "ui.deal_form":
            return await self._render_deal_form_ui(params)
        elif capability_id == "ui.deal_list":
            return await self._render_deal_list_ui(params)
        else:
            raise ValueError(f"Unknown UI capability: {capability_id}")
    
    async def _create_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal"""
        deal_id = f"deal_{datetime.now().timestamp()}"
        now = datetime.now().isoformat()
        
        # Get default pipeline if none specified
        if "pipeline_id" not in params:
            params["pipeline_id"] = "default_pipeline"
        
        # Get first stage of pipeline if none specified
        if "stage" not in params:
            pipeline = await self._get_pipeline({"pipeline_id": params["pipeline_id"]})
            if pipeline["pipelines"]:
                params["stage"] = pipeline["pipelines"][0]["stages"][0]
        
        # Calculate probability based on stage if not provided
        if "probability" not in params and params.get("stage"):
            default_probs = {
                "Prospecting": 10, "Qualification": 25, "Proposal": 50,
                "Negotiation": 75, "Closed Won": 100, "Closed Lost": 0
            }
            params["probability"] = default_probs.get(params["stage"], 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deals (
                id, title, description, value, currency, stage, probability,
                contact_id, company_id, owner_id, expected_close_date,
                created_at, updated_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_id,
            params["title"],
            params.get("description", ""),
            float(params["value"]),
            params.get("currency", "USD"),
            params["stage"],
            params.get("probability", 50),
            params.get("contact_id"),
            params.get("company_id"),
            params.get("owner_id", "system"),
            params.get("expected_close_date"),
            now,
            now,
            json.dumps(params.get("metadata", {}))
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created deal {deal_id}: {params['title']}")
        return {"deal_id": deal_id}
    
    async def _update_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal"""
        deal_id = params["deal_id"]
        now = datetime.now().isoformat()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field in ["title", "description", "value", "stage", "probability", 
                     "contact_id", "company_id", "expected_close_date"]:
            if field in params:
                update_fields.append(f"{field} = ?")
                if field == "value":
                    values.append(float(params[field]))
                else:
                    values.append(params[field])
        
        if "metadata" in params:
            update_fields.append("metadata = ?")
            values.append(json.dumps(params["metadata"]))
        
        if not update_fields:
            return {"success": False, "error": "No fields to update"}
        
        update_fields.append("updated_at = ?")
        values.append(now)
        values.append(deal_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            UPDATE deals SET {', '.join(update_fields)} WHERE id = ?
        ''', values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Updated deal {deal_id}")
        
        return {"success": success}
    
    async def _delete_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a deal"""
        deal_id = params["deal_id"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM deals WHERE id = ?", (deal_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Deleted deal {deal_id}")
        
        return {"success": success}
    
    async def _get_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific deal"""
        deal_id = params["deal_id"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, value, currency, stage, probability,
                   contact_id, company_id, owner_id, expected_close_date,
                   actual_close_date, created_at, updated_at, metadata
            FROM deals WHERE id = ?
        ''', (deal_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"deal": None}
        
        deal = self._row_to_deal(row)
        return {"deal": asdict(deal)}
    
    async def _list_deals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List deals with filtering"""
        filters = []
        values = []
        
        # Build WHERE clause
        if "stage" in params:
            filters.append("stage = ?")
            values.append(params["stage"])
        
        if "owner_id" in params:
            filters.append("owner_id = ?")
            values.append(params["owner_id"])
        
        if "contact_id" in params:
            filters.append("contact_id = ?")
            values.append(params["contact_id"])
        
        if "company_id" in params:
            filters.append("company_id = ?")
            values.append(params["company_id"])
        
        if not params.get("include_closed", False):
            filters.append("stage NOT IN ('Closed Won', 'Closed Lost')")
        
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        
        # Add pagination
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM deals {where_clause}", values)
        total = cursor.fetchone()[0]
        
        # Get deals
        cursor.execute(f'''
            SELECT id, title, description, value, currency, stage, probability,
                   contact_id, company_id, owner_id, expected_close_date,
                   actual_close_date, created_at, updated_at, metadata
            FROM deals {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', values + [limit, offset])
        
        rows = cursor.fetchall()
        conn.close()
        
        deals = [asdict(self._row_to_deal(row)) for row in rows]
        return {"deals": deals, "total": total}
    
    async def _move_deal_stage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move deal to different stage"""
        deal_id = params["deal_id"]
        new_stage = params["new_stage"]
        
        # Get current deal info
        deal_result = await self._get_deal({"deal_id": deal_id})
        if not deal_result["deal"]:
            return {"success": False, "error": "Deal not found"}
        
        current_stage = deal_result["deal"]["stage"]
        
        # Update stage and probability
        update_params = {
            "deal_id": deal_id,
            "stage": new_stage,
            "probability": self._get_stage_probability(new_stage)
        }
        
        # Handle closed stages
        if new_stage in ["Closed Won", "Closed Lost"]:
            update_params["actual_close_date"] = datetime.now().isoformat()
        
        return await self._update_deal(update_params)
    
    def _get_stage_probability(self, stage: str) -> int:
        """Get default probability for a stage"""
        default_probs = {
            "Prospecting": 10, "Qualification": 25, "Proposal": 50,
            "Negotiation": 75, "Closed Won": 100, "Closed Lost": 0
        }
        return default_probs.get(stage, 50)
    
    def _row_to_deal(self, row: tuple) -> Deal:
        """Convert database row to Deal object"""
        return Deal(
            id=row[0],
            title=row[1],
            description=row[2] or "",
            value=Decimal(str(row[3])),
            currency=row[4],
            stage=row[5],
            probability=row[6],
            contact_id=row[7],
            company_id=row[8],
            owner_id=row[9],
            expected_close_date=datetime.fromisoformat(row[10]) if row[10] else None,
            actual_close_date=datetime.fromisoformat(row[11]) if row[11] else None,
            created_at=datetime.fromisoformat(row[12]),
            updated_at=datetime.fromisoformat(row[13]),
            metadata=json.loads(row[14]) if row[14] else {}
        )
    
    async def _create_pipeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new pipeline"""
        pipeline_id = f"pipeline_{datetime.now().timestamp()}"
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pipelines (id, name, description, stages, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            pipeline_id,
            params["name"],
            params.get("description", ""),
            json.dumps(params["stages"]),
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created pipeline {pipeline_id}: {params['name']}")
        return {"pipeline_id": pipeline_id}
    
    async def _list_pipelines(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all pipelines"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, stages, is_default, created_at, updated_at
            FROM pipelines
            ORDER BY is_default DESC, name ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        pipelines = []
        for row in rows:
            pipelines.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "stages": json.loads(row[3]),
                "is_default": bool(row[4]),
                "created_at": row[5],
                "updated_at": row[6]
            })
        
        return {"pipelines": pipelines}
    
    async def _get_pipeline_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pipeline analytics and metrics"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        
        # Get all deals for the pipeline
        deals_result = await self._list_deals({
            "pipeline_id": pipeline_id,
            "include_closed": True,
            "limit": 1000
        })
        
        deals = deals_result["deals"]
        
        # Calculate metrics
        total_deals = len(deals)
        total_value = sum(Decimal(str(deal["value"])) for deal in deals)
        
        deals_by_stage = {}
        value_by_stage = {}
        
        for deal in deals:
            stage = deal["stage"]
            deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1
            value_by_stage[stage] = value_by_stage.get(stage, Decimal(0)) + Decimal(str(deal["value"]))
        
        # Calculate conversion rates (simplified)
        conversion_rates = {}
        if total_deals > 0:
            closed_won = deals_by_stage.get("Closed Won", 0)
            conversion_rates["overall"] = (closed_won / total_deals) * 100
        
        # Calculate average deal size
        avg_deal_size = total_value / total_deals if total_deals > 0 else Decimal(0)
        
        # Calculate average sales cycle (simplified)
        avg_sales_cycle = 45  # Default, would calculate from actual data
        
        return {
            "pipeline_id": pipeline_id,
            "total_deals": total_deals,
            "total_value": float(total_value),
            "deals_by_stage": deals_by_stage,
            "value_by_stage": {k: float(v) for k, v in value_by_stage.items()},
            "conversion_rates": conversion_rates,
            "avg_deal_size": float(avg_deal_size),
            "avg_sales_cycle": avg_sales_cycle
        }
    
    async def _get_deal_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deal forecast"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        forecast_period = params.get("forecast_period", 90)
        
        # Get active deals (not closed)
        deals_result = await self._list_deals({
            "pipeline_id": pipeline_id,
            "include_closed": False,
            "limit": 500
        })
        
        deals = deals_result["deals"]
        
        # Calculate forecast based on deal probabilities and expected close dates
        forecast_value = Decimal(0)
        forecast_by_month = {}
        
        for deal in deals:
            probability = deal["probability"] / 100
            weighted_value = Decimal(str(deal["value"])) * Decimal(str(probability))
            forecast_value += weighted_value
            
            # Group by expected close month
            if deal.get("expected_close_date"):
                close_date = datetime.fromisoformat(deal["expected_close_date"])
                month_key = close_date.strftime("%Y-%m")
                forecast_by_month[month_key] = forecast_by_month.get(month_key, Decimal(0)) + weighted_value
        
        return {
            "pipeline_id": pipeline_id,
            "forecast_period": forecast_period,
            "total_forecast": float(forecast_value),
            "forecast_by_month": {k: float(v) for k, v in forecast_by_month.items()},
            "active_deals": len(deals),
            "generated_at": datetime.now().isoformat()
        }
    
    # UI Capabilities
    async def _render_dashboard_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render the deal dashboard UI"""
        try:
            # Get deals and metrics
            deals_result = await self._list_deals({
                "pipeline_id": params.get("pipeline_id", "default_pipeline"),
                "include_closed": False,
                "limit": 50
            })
            
            metrics_result = await self._get_pipeline_metrics({
                "pipeline_id": params.get("pipeline_id", "default_pipeline")
            })
            
            # Render dashboard
            operations = DealFlowCRMUIRenderer.render_dashboard(
                deals_result["deals"],
                metrics_result
            )
            
            return {
                "ui_operations": operations,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error rendering dashboard UI: {e}")
            return {
                "ui_operations": [],
                "status": "error",
                "error": str(e)
            }
    
    async def _render_pipeline_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render the pipeline view UI"""
        try:
            # Get deals and pipelines
            deals_result = await self._list_deals({
                "pipeline_id": params.get("pipeline_id", "default_pipeline"),
                "include_closed": False,
                "limit": 100
            })
            
            pipelines_result = await self._list_pipelines({})
            
            # Render pipeline view
            operations = DealFlowCRMUIRenderer.render_pipeline_view(
                deals_result["deals"],
                pipelines_result["pipelines"]
            )
            
            return {
                "ui_operations": operations,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error rendering pipeline UI: {e}")
            return {
                "ui_operations": [],
                "status": "error",
                "error": str(e)
            }
    
    async def _render_deal_form_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render the deal form UI"""
        try:
            deal = None
            if "deal_id" in params:
                deal_result = await self._get_deal({"deal_id": params["deal_id"]})
                deal = deal_result["deal"]
            
            pipelines_result = await self._list_pipelines({})
            
            # Render deal form
            operations = DealFlowCRMUIRenderer.render_deal_form(
                deal,
                pipelines_result["pipelines"]
            )
            
            return {
                "ui_operations": operations,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error rendering deal form UI: {e}")
            return {
                "ui_operations": [],
                "status": "error",
                "error": str(e)
            }
    
    async def _render_deal_list_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render the deal list UI"""
        try:
            # Get deals
            deals_result = await self._list_deals({
                "pipeline_id": params.get("pipeline_id", "default_pipeline"),
                "include_closed": params.get("include_closed", False),
                "limit": params.get("limit", 50),
                "offset": params.get("offset", 0)
            })
            
            # Render deal list
            operations = DealFlowCRMUIRenderer.render_deal_list(deals_result["deals"])
            
            return {
                "ui_operations": operations,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error rendering deal list UI: {e}")
            return {
                "ui_operations": [],
                "status": "error",
                "error": str(e)
            }