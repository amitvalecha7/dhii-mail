"""
A2UI Components for Deal-Flow CRM Plugin
Implements UI components for deal management and pipeline visualization
"""

from typing import Dict, Any, List, Optional
from a2ui_integration.core.types import A2UIComponent, AdjacencyOperation
from a2ui_integration.data_structures import ComponentGraph

class DealFlowCRMComponents:
    """A2UI Components for Deal-Flow CRM"""
    
    @staticmethod
    def create_deal_dashboard(deals: List[Dict[str, Any]], metrics: Dict[str, Any]) -> A2UIComponent:
        """Create a comprehensive deal dashboard"""
        
        # Create metrics cards
        metrics_cards = [
            A2UIComponent(
                id="total-deals-card",
                type="Card",
                props={
                    "title": "Total Active Deals",
                    "value": str(metrics.get("total_deals", 0)),
                    "variant": "glass",
                    "accent": "blue"
                }
            ),
            A2UIComponent(
                id="pipeline-value-card",
                type="Card", 
                props={
                    "title": "Pipeline Value",
                    "value": f"${metrics.get('total_value', 0):,.0f}",
                    "variant": "glass",
                    "accent": "green"
                }
            ),
            A2UIComponent(
                id="avg-deal-size-card",
                type="Card",
                props={
                    "title": "Avg Deal Size",
                    "value": f"${metrics.get('avg_deal_size', 0):,.0f}",
                    "variant": "glass",
                    "accent": "purple"
                }
            ),
            A2UIComponent(
                id="conversion-rate-card",
                type="Card",
                props={
                    "title": "Conversion Rate",
                    "value": f"{metrics.get('conversion_rates', {}).get('overall', 0):.1f}%",
                    "variant": "glass",
                    "accent": "orange"
                }
            )
        ]
        
        # Create recent deals list
        recent_deals = deals[:5]  # Top 5 recent deals
        deal_items = []
        
        for deal in recent_deals:
            deal_items.append(
                A2UIComponent(
                    id=f"deal-item-{deal['id']}",
                    type="ListItem",
                    props={
                        "title": deal["title"],
                        "subtitle": f"{deal['stage']} • ${deal['value']:,.0f} • {deal['probability']}%",
                        "accent": DealFlowCRMComponents._get_stage_color(deal["stage"]),
                        "action": "view_deal",
                        "payload": {"deal_id": deal["id"]}
                    }
                )
            )
        
        recent_deals_list = A2UIComponent(
            id="recent-deals-list",
            type="List",
            props={
                "title": "Recent Deals",
                "items": deal_items,
                "variant": "glass"
            }
        )
        
        # Create main dashboard layout
        dashboard = A2UIComponent(
            id="deal-dashboard",
            type="Layout",
            props={
                "title": "Deal Flow Dashboard",
                "variant": "dashboard"
            },
            children=[
                A2UIComponent(
                    id="metrics-grid",
                    type="Grid",
                    props={"columns": 4, "gap": "md"},
                    children=metrics_cards
                ),
                A2UIComponent(
                    id="dashboard-content",
                    type="Container",
                    props={"layout": "split"},
                    children=[
                        recent_deals_list,
                        DealFlowCRMComponents._create_pipeline_chart(deals)
                    ]
                )
            ]
        )
        
        return dashboard
    
    @staticmethod
    def create_pipeline_view(deals: List[Dict[str, Any]], pipelines: List[Dict[str, Any]]) -> A2UIComponent:
        """Create a Kanban-style pipeline view"""
        
        # Group deals by stage
        deals_by_stage = {}
        for deal in deals:
            stage = deal["stage"]
            if stage not in deals_by_stage:
                deals_by_stage[stage] = []
            deals_by_stage[stage].append(deal)
        
        # Get stages from first pipeline (default)
        default_pipeline = next((p for p in pipelines if p.get("is_default", False)), pipelines[0])
        stages = default_pipeline["stages"]
        
        # Create stage columns
        stage_columns = []
        
        for stage in stages:
            stage_deals = deals_by_stage.get(stage, [])
            
            # Create deal cards for this stage
            deal_cards = []
            for deal in stage_deals:
                deal_cards.append(
                    A2UIComponent(
                        id=f"deal-card-{deal['id']}",
                        type="Card",
                        props={
                            "title": deal["title"],
                            "subtitle": f"${deal['value']:,.0f} • {deal['probability']}%",
                            "variant": "glass-outlined",
                            "accent": DealFlowCRMComponents._get_stage_color(stage),
                            "draggable": True,
                            "drag_payload": {
                                "deal_id": deal["id"],
                                "current_stage": stage,
                                "target_stage": None
                            }
                        },
                        children=[
                            A2UIComponent(
                                id=f"deal-value-{deal['id']}",
                                type="Text",
                                props={
                                    "content": f"Value: ${deal['value']:,.0f}",
                                    "size": "sm"
                                }
                            ),
                            A2UIComponent(
                                id=f"deal-contact-{deal['id']}",
                                type="Text",
                                props={
                                    "content": f"Contact: {deal.get('contact_id', 'N/A')}",
                                    "size": "sm"
                                }
                            ),
                            A2UIComponent(
                                id=f"deal-close-date-{deal['id']}",
                                type="Text",
                                props={
                                    "content": f"Close: {deal.get('expected_close_date', 'N/A')}",
                                    "size": "sm"
                                }
                            )
                        ]
                    )
                )
            
            # Create stage column
            stage_column = A2UIComponent(
                id=f"stage-column-{stage.lower().replace(' ', '-')}",
                type="Container",
                props={
                    "title": stage,
                    "variant": "column",
                    "accent": DealFlowCRMComponents._get_stage_color(stage),
                    "droppable": True,
                    "drop_action": "move_deal_stage",
                    "drop_payload": {"target_stage": stage}
                },
                children=deal_cards
            )
            
            stage_columns.append(stage_column)
        
        # Create pipeline view
        pipeline_view = A2UIComponent(
            id="pipeline-view",
            type="Container",
            props={
                "title": f"Pipeline: {default_pipeline['name']}",
                "variant": "pipeline",
                "layout": "horizontal-scroll"
            },
            children=stage_columns
        )
        
        return pipeline_view
    
    @staticmethod
    def create_deal_form(deal: Optional[Dict[str, Any]] = None, pipelines: List[Dict[str, Any]] = None) -> A2UIComponent:
        """Create a deal creation/edit form"""
        
        is_edit = deal is not None
        form_title = "Edit Deal" if is_edit else "Create New Deal"
        
        # Get default pipeline and stages
        if pipelines:
            default_pipeline = next((p for p in pipelines if p.get("is_default", False)), pipelines[0])
            stages = default_pipeline["stages"]
        else:
            stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
        
        # Form fields
        form_fields = [
            A2UIComponent(
                id="deal-title-field",
                type="TextField",
                props={
                    "label": "Deal Title",
                    "name": "title",
                    "required": True,
                    "value": deal["title"] if is_edit else "",
                    "placeholder": "Enter deal title..."
                }
            ),
            A2UIComponent(
                id="deal-description-field",
                type="TextArea",
                props={
                    "label": "Description",
                    "name": "description",
                    "value": deal["description"] if is_edit else "",
                    "placeholder": "Enter deal description...",
                    "rows": 3
                }
            ),
            A2UIComponent(
                id="deal-value-field",
                type="NumberField",
                props={
                    "label": "Deal Value",
                    "name": "value",
                    "required": True,
                    "value": deal["value"] if is_edit else 0,
                    "min": 0,
                    "step": 100,
                    "prefix": "$"
                }
            ),
            A2UIComponent(
                id="deal-stage-field",
                type="SelectField",
                props={
                    "label": "Stage",
                    "name": "stage",
                    "required": True,
                    "value": deal["stage"] if is_edit else stages[0],
                    "options": [{"value": stage, "label": stage} for stage in stages]
                }
            ),
            A2UIComponent(
                id="deal-probability-field",
                type="NumberField",
                props={
                    "label": "Probability (%)",
                    "name": "probability",
                    "value": deal["probability"] if is_edit else 50,
                    "min": 0,
                    "max": 100,
                    "step": 5
                }
            ),
            A2UIComponent(
                id="deal-close-date-field",
                type="DateField",
                props={
                    "label": "Expected Close Date",
                    "name": "expected_close_date",
                    "value": deal["expected_close_date"] if is_edit else "",
                    "min": "2024-01-01"
                }
            )
        ]
        
        # Create form
        deal_form = A2UIComponent(
            id="deal-form",
            type="Form",
            props={
                "title": form_title,
                "variant": "glass",
                "action": "save_deal",
                "method": "POST",
                "submit_label": "Save Deal" if is_edit else "Create Deal"
            },
            children=form_fields + [
                A2UIComponent(
                    id="deal-form-actions",
                    type="Container",
                    props={"layout": "horizontal", "gap": "sm"},
                    children=[
                        A2UIComponent(
                            id="save-deal-btn",
                            type="Button",
                            props={
                                "label": "Save Deal",
                                "variant": "primary",
                                "type": "submit"
                            }
                        ),
                        A2UIComponent(
                            id="cancel-deal-btn",
                            type="Button",
                            props={
                                "label": "Cancel",
                                "variant": "secondary",
                                "action": "cancel_deal_form"
                            }
                        )
                    ]
                )
            ]
        )
        
        return deal_form
    
    @staticmethod
    def create_deal_list_item(deal: Dict[str, Any]) -> A2UIComponent:
        """Create a list item for a deal"""
        return A2UIComponent(
            id=f"deal-list-item-{deal['id']}",
            type="ListItem",
            props={
                "title": deal["title"],
                "subtitle": f"{deal['stage']} • ${deal['value']:,.0f} • {deal['probability']}%",
                "accent": DealFlowCRMComponents._get_stage_color(deal["stage"]),
                "action": "view_deal",
                "payload": {"deal_id": deal["id"]},
                "metadata": {
                    "contact": deal.get("contact_id", "N/A"),
                    "company": deal.get("company_id", "N/A"),
                    "close_date": deal.get("expected_close_date", "N/A")
                }
            }
        )
    
    @staticmethod
    def _create_pipeline_chart(deals: List[Dict[str, Any]]) -> A2UIComponent:
        """Create a simple pipeline chart visualization"""
        # Group deals by stage for chart
        stage_data = {}
        for deal in deals:
            stage = deal["stage"]
            if stage not in stage_data:
                stage_data[stage] = {"count": 0, "value": 0}
            stage_data[stage]["count"] += 1
            stage_data[stage]["value"] += deal["value"]
        
        # Create chart data
        chart_data = {
            "labels": list(stage_data.keys()),
            "datasets": [
                {
                    "label": "Deal Count",
                    "data": [stage_data[stage]["count"] for stage in stage_data.keys()],
                    "backgroundColor": [DealFlowCRMComponents._get_stage_color(stage) for stage in stage_data.keys()]
                }
            ]
        }
        
        return A2UIComponent(
            id="pipeline-chart",
            type="Chart",
            props={
                "title": "Pipeline Overview",
                "type": "bar",
                "data": chart_data,
                "variant": "glass",
                "height": 300
            }
        )
    
    @staticmethod
    def _get_stage_color(stage: str) -> str:
        """Get color for a pipeline stage"""
        colors = {
            "Prospecting": "blue",
            "Qualification": "cyan",
            "Proposal": "yellow",
            "Negotiation": "orange",
            "Closed Won": "green",
            "Closed Lost": "red"
        }
        return colors.get(stage, "gray")

class DealFlowCRMUIRenderer:
    """UI Renderer for Deal-Flow CRM operations"""
    
    @staticmethod
    def render_dashboard(deals: List[Dict[str, Any]], metrics: Dict[str, Any]) -> List[AdjacencyOperation]:
        """Render the deal dashboard"""
        dashboard = DealFlowCRMComponents.create_deal_dashboard(deals, metrics)
        
        return [
            AdjacencyOperation(
                operation="replace",
                node_id="main-content",
                node_type="div",
                parent_id="main-content",
                properties={"component": dashboard}
            )
        ]
    
    @staticmethod
    def render_pipeline_view(deals: List[Dict[str, Any]], pipelines: List[Dict[str, Any]]) -> List[AdjacencyOperation]:
        """Render the pipeline view"""
        pipeline_view = DealFlowCRMComponents.create_pipeline_view(deals, pipelines)
        
        return [
            AdjacencyOperation(
                operation="replace",
                node_id="main-content",
                node_type="div",
                parent_id="main-content",
                properties={"component": pipeline_view}
            )
        ]
    
    @staticmethod
    def render_deal_form(deal: Optional[Dict[str, Any]] = None, pipelines: List[Dict[str, Any]] = None) -> List[AdjacencyOperation]:
        """Render the deal form"""
        deal_form = DealFlowCRMComponents.create_deal_form(deal, pipelines)
        
        return [
            AdjacencyOperation(
                operation="replace",
                node_id="main-content",
                node_type="div",
                parent_id="main-content",
                properties={"component": deal_form}
            )
        ]
    
    @staticmethod
    def render_deal_list(deals: List[Dict[str, Any]]) -> List[AdjacencyOperation]:
        """Render a list of deals"""
        deal_items = [DealFlowCRMComponents.create_deal_list_item(deal) for deal in deals]
        
        deal_list = A2UIComponent(
            id="deal-list",
            type="List",
            props={
                "title": "Deals",
                "items": deal_items,
                "variant": "glass"
            }
        )
        
        return [
            AdjacencyOperation(
                operation="replace",
                node_id="main-content",
                node_type="div",
                parent_id="main-content",
                properties={"component": deal_list}
            )
        ]