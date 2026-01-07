"""
Deal-Flow CRM Plugin for dhii Mail - Framework 2.0
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
            version="2.0.0",
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
        if "probability" not in params:
            stage_probabilities = {
                "Prospecting": 10,
                "Qualification": 25,
                "Proposal": 50,
                "Negotiation": 75,
                "Closed Won": 100,
                "Closed Lost": 0
            }
            params["probability"] = stage_probabilities.get(params.get("stage", ""), 50)
        
        # Set default values
        params.setdefault("currency", "USD")
        params.setdefault("owner_id", "system")
        params.setdefault("created_at", now)
        params.setdefault("updated_at", now)
        
        # Convert metadata to JSON
        metadata_json = json.dumps(params.get("metadata", {}))
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO deals (
                    id, title, description, value, currency, stage, probability,
                    contact_id, company_id, owner_id, expected_close_date,
                    actual_close_date, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deal_id, params["title"], params.get("description", ""),
                float(params["value"]), params["currency"], params["stage"],
                params["probability"], params.get("contact_id"), params.get("company_id"),
                params["owner_id"], params.get("expected_close_date"),
                params.get("actual_close_date"), params["created_at"],
                params["updated_at"], metadata_json
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deal created successfully: {deal_id}")
            return {"deal_id": deal_id, "success": True}
            
        except Exception as e:
            logger.error(f"Failed to create deal: {e}")
            raise
    
    async def _update_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal"""
        deal_id = params["deal_id"]
        now = datetime.now().isoformat()
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        for field in ["title", "description", "value", "currency", "stage", 
                     "probability", "contact_id", "company_id", "expected_close_date"]:
            if field in params:
                update_fields.append(f"{field} = ?")
                update_values.append(params[field])
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = ?")
        update_values.append(now)
        
        # Handle metadata separately
        if "metadata" in params:
            update_fields.append("metadata = ?")
            update_values.append(json.dumps(params["metadata"]))
        
        update_values.append(deal_id)  # Add deal_id for WHERE clause
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                UPDATE deals 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deal updated successfully: {deal_id}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to update deal: {e}")
            raise
    
    async def _delete_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a deal"""
        deal_id = params["deal_id"]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM deals WHERE id = ?', (deal_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deal deleted successfully: {deal_id}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to delete deal: {e}")
            raise
    
    async def _get_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific deal"""
        deal_id = params["deal_id"]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM deals WHERE id = ?', (deal_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                deal_data = dict(zip(columns, row))
                
                # Convert JSON fields
                deal_data["metadata"] = json.loads(deal_data.get("metadata", "{}"))
                
                # Convert numeric fields
                deal_data["value"] = float(deal_data["value"])
                deal_data["probability"] = int(deal_data["probability"])
                
                return {"deal": deal_data}
            else:
                return {"deal": None}
                
        except Exception as e:
            logger.error(f"Failed to get deal: {e}")
            raise
    
    async def _list_deals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List deals with filtering"""
        query = "SELECT * FROM deals WHERE 1=1"
        query_values = []
        
        # Apply filters
        if "stage" in params:
            query += " AND stage = ?"
            query_values.append(params["stage"])
        
        if "owner_id" in params:
            query += " AND owner_id = ?"
            query_values.append(params["owner_id"])
        
        if "contact_id" in params:
            query += " AND contact_id = ?"
            query_values.append(params["contact_id"])
        
        if "company_id" in params:
            query += " AND company_id = ?"
            query_values.append(params["company_id"])
        
        # Exclude closed deals if not requested
        if not params.get("include_closed", False):
            closed_stages = ["Closed Won", "Closed Lost"]
            placeholders = ",".join(["?"] * len(closed_stages))
            query += f" AND stage NOT IN ({placeholders})"
            query_values.extend(closed_stages)
        
        # Add pagination
        limit = min(params.get("limit", 50), 500)  # Cap at 500
        offset = params.get("offset", 0)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        query_values.extend([limit, offset])
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(query, query_values)
            rows = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM deals WHERE 1=1"
            count_values = query_values[:-2]  # Remove LIMIT and OFFSET values
            
            if not params.get("include_closed", False):
                closed_stages = ["Closed Won", "Closed Lost"]
                placeholders = ",".join(["?"] * len(closed_stages))
                count_query += f" AND stage NOT IN ({placeholders})"
                count_values.extend(closed_stages)
            
            cursor.execute(count_query, count_values)
            total = cursor.fetchone()[0]
            
            conn.close()
            
            # Convert rows to deals
            deals = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in rows:
                deal_data = dict(zip(columns, row))
                deal_data["metadata"] = json.loads(deal_data.get("metadata", "{}"))
                deal_data["value"] = float(deal_data["value"])
                deal_data["probability"] = int(deal_data["probability"])
                deals.append(deal_data)
            
            return {"deals": deals, "total": total}
            
        except Exception as e:
            logger.error(f"Failed to list deals: {e}")
            raise
    
    async def _move_deal_stage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move a deal to a different stage"""
        deal_id = params["deal_id"]
        new_stage = params["new_stage"]
        reason = params.get("reason", "")
        
        # Get current deal
        current_deal = await self._get_deal({"deal_id": deal_id})
        if not current_deal["deal"]:
            return {"success": False, "error": "Deal not found"}
        
        current_stage = current_deal["deal"]["stage"]
        
        # Update the deal stage
        update_params = {
            "deal_id": deal_id,
            "stage": new_stage,
            "reason": reason
        }
        
        # Update probability based on new stage
        stage_probabilities = {
            "Prospecting": 10,
            "Qualification": 25,
            "Proposal": 50,
            "Negotiation": 75,
            "Closed Won": 100,
            "Closed Lost": 0
        }
        
        if new_stage in stage_probabilities:
            update_params["probability"] = stage_probabilities[new_stage]
        
        result = await self._update_deal(update_params)
        
        # Log the stage change
        logger.info(f"Deal {deal_id} moved from {current_stage} to {new_stage}: {reason}")
        
        return result
    
    async def _create_pipeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new pipeline"""
        pipeline_id = f"pipeline_{datetime.now().timestamp()}"
        now = datetime.now().isoformat()
        
        params.setdefault("created_at", now)
        params.setdefault("updated_at", now)
        
        # Convert stages to JSON
        stages_json = json.dumps(params["stages"])
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pipelines (id, name, description, stages, is_default, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pipeline_id, params["name"], params.get("description", ""),
                stages_json, params.get("is_default", False), params["created_at"], params["updated_at"]
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Pipeline created successfully: {pipeline_id}")
            return {"pipeline_id": pipeline_id}
            
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            raise
    
    async def _list_pipelines(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all pipelines"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM pipelines ORDER BY created_at')
            rows = cursor.fetchall()
            
            conn.close()
            
            pipelines = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in rows:
                pipeline_data = dict(zip(columns, row))
                pipeline_data["stages"] = json.loads(pipeline_data["stages"])
                pipelines.append(pipeline_data)
            
            return {"pipelines": pipelines}
            
        except Exception as e:
            logger.error(f"Failed to list pipelines: {e}")
            raise
    
    async def _get_pipeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific pipeline"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM pipelines WHERE id = ?', (pipeline_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                pipeline_data = dict(zip(columns, row))
                pipeline_data["stages"] = json.loads(pipeline_data["stages"])
                return {"pipelines": [pipeline_data]}
            else:
                return {"pipelines": []}
                
        except Exception as e:
            logger.error(f"Failed to get pipeline: {e}")
            raise
    
    async def _get_pipeline_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pipeline metrics and analytics"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        
        try:
            # Get all deals for the pipeline
            deals_result = await self._list_deals({"pipeline_id": pipeline_id, "include_closed": True})
            deals = deals_result["deals"]
            
            if not deals:
                return {
                    "pipeline_id": pipeline_id,
                    "total_deals": 0,
                    "total_value": 0,
                    "deals_by_stage": {},
                    "value_by_stage": {},
                    "conversion_rates": {},
                    "avg_deal_size": 0,
                    "avg_sales_cycle": 0
                }
            
            # Calculate metrics
            total_deals = len(deals)
            total_value = sum(deal["value"] for deal in deals)
            
            # Group by stage
            deals_by_stage = {}
            value_by_stage = {}
            
            for deal in deals:
                stage = deal["stage"]
                deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1
                value_by_stage[stage] = value_by_stage.get(stage, 0) + deal["value"]
            
            # Calculate conversion rates
            conversion_rates = {}
            stage_order = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won"]
            
            for i, stage in enumerate(stage_order[:-1]):
                current_count = deals_by_stage.get(stage, 0)
                next_count = deals_by_stage.get(stage_order[i+1], 0)
                if current_count > 0:
                    conversion_rates[stage] = (next_count / current_count) * 100
                else:
                    conversion_rates[stage] = 0
            
            # Calculate averages
            avg_deal_size = total_value / total_deals if total_deals > 0 else 0
            
            # Calculate average sales cycle (simplified)
            avg_sales_cycle = 45  # Default assumption
            
            return {
                "pipeline_id": pipeline_id,
                "total_deals": total_deals,
                "total_value": float(total_value),
                "deals_by_stage": deals_by_stage,
                "value_by_stage": {stage: float(value) for stage, value in value_by_stage.items()},
                "conversion_rates": conversion_rates,
                "avg_deal_size": float(avg_deal_size),
                "avg_sales_cycle": avg_sales_cycle
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline metrics: {e}")
            raise
    
    async def _get_deal_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deal forecast"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        forecast_period = params.get("forecast_period", 90)
        
        try:
            # Get active deals (not closed)
            deals_result = await self._list_deals({"pipeline_id": pipeline_id, "include_closed": False})
            active_deals = deals_result["deals"]
            
            # Calculate weighted forecast
            total_forecast = 0
            deals_by_stage = {}
            
            for deal in active_deals:
                weighted_value = deal["value"] * (deal["probability"] / 100)
                total_forecast += weighted_value
                
                stage = deal["stage"]
                if stage not in deals_by_stage:
                    deals_by_stage[stage] = {"count": 0, "value": 0, "weighted_value": 0}
                
                deals_by_stage[stage]["count"] += 1
                deals_by_stage[stage]["value"] += deal["value"]
                deals_by_stage[stage]["weighted_value"] += weighted_value
            
            # Calculate confidence intervals (simplified)
            low_forecast = total_forecast * 0.7
            high_forecast = total_forecast * 1.2
            
            return {
                "pipeline_id": pipeline_id,
                "forecast_period_days": forecast_period,
                "total_forecast": float(total_forecast),
                "low_forecast": float(low_forecast),
                "high_forecast": float(high_forecast),
                "active_deals": len(active_deals),
                "forecast_by_stage": {
                    stage: {
                        "deal_count": data["count"],
                        "total_value": float(data["value"]),
                        "weighted_value": float(data["weighted_value"])
                    }
                    for stage, data in deals_by_stage.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate deal forecast: {e}")
            raise
    
    async def _render_dashboard_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render dashboard UI"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        
        # Get pipeline metrics
        metrics = await self._get_pipeline_metrics({"pipeline_id": pipeline_id})
        
        # Get recent deals
        recent_deals = await self._list_deals({"pipeline_id": pipeline_id, "limit": 10})
        
        # Render UI components
        renderer = DealFlowCRMUIRenderer()
        ui_operations = renderer.render_dashboard(metrics, recent_deals)
        
        return {"ui_operations": ui_operations}
    
    async def _render_pipeline_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render pipeline view UI"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        
        # Get pipeline data
        pipeline_data = await self._get_pipeline({"pipeline_id": pipeline_id})
        deals = await self._list_deals({"pipeline_id": pipeline_id, "include_closed": False})
        
        # Render UI components
        renderer = DealFlowCRMUIRenderer()
        ui_operations = renderer.render_pipeline_view(pipeline_data, deals)
        
        return {"ui_operations": ui_operations}
    
    async def _render_deal_form_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render deal form UI"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        deal_id = params.get("deal_id")
        
        # Get pipeline data
        pipeline_data = await self._get_pipeline({"pipeline_id": pipeline_id})
        
        # Get deal data if editing
        deal_data = None
        if deal_id:
            deal_result = await self._get_deal({"deal_id": deal_id})
            deal_data = deal_result.get("deal")
        
        # Render UI components
        renderer = DealFlowCRMUIRenderer()
        ui_operations = renderer.render_deal_form(pipeline_data, deal_data)
        
        return {"ui_operations": ui_operations}
    
    async def _render_deal_list_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render deal list UI"""
        pipeline_id = params.get("pipeline_id", "default_pipeline")
        
        # Get deals
        deals = await self._list_deals({
            "pipeline_id": pipeline_id,
            "include_closed": params.get("include_closed", False),
            "limit": params.get("limit", 50),
            "offset": params.get("offset", 0)
        })
        
        # Render UI components
        renderer = DealFlowCRMUIRenderer()
        ui_operations = renderer.render_deal_list(deals)
        
        return {"ui_operations": ui_operations}

# Framework 2.0 registration function
def register(kernel_api: Dict[str, Any]) -> DealFlowCRMPlugin:
    """Register the Deal-Flow CRM plugin with Framework 2.0"""
    plugin = DealFlowCRMPlugin()
    plugin.initialize(kernel_api)
    return plugin