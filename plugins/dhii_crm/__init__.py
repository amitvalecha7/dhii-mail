# Deal-Flow CRM Plugin
# Manages sales pipeline

# Mock Data Store
_DEALS = [
    {"id": "1", "title": "Acme Corp Contract", "value": 50000, "stage": "Proposal"},
    {"id": "2", "title": "Globex Licensing", "value": 12000, "stage": "Lead"}
]

def register(kernel):
    kernel["log"]("Deal-Flow CRM loading...")

    def get_pipeline(params):
        """
        Fetches deals grouped by stage (simplified list for MVP).
        """
        items = []
        for d in _DEALS:
            items.append({
                "id": d["id"],
                "title": f"{d['title']} (${d['value']})",
                "subtitle": f"Stage: {d['stage']}",
                "action": {
                    "type": "run_capability",
                    "capability_id": "update_stage",
                    "params": {"deal_id": d["id"], "new_stage": "Closed Won"}
                }
            })
        
        return {
            "type": "card",
            "id": "crm-pipeline",
            "title": "Sales Pipeline",
            "children": [
                {
                    "type": "list",
                    "items": items
                }
            ]
        }

    def add_deal(params):
        """
        Adds a new deal.
        """
        title = params.get("title")
        value = params.get("value")
        stage = params.get("stage", "Lead")
        
        if not title or not value:
             return {
                "type": "card",
                "title": "Error",
                "children": [{"type": "text", "content": "Missing title or value."}]
            }

        new_id = str(len(_DEALS) + 1)
        _DEALS.append({
            "id": new_id,
            "title": title,
            "value": value,
            "stage": stage
        })
        
        return {
            "type": "card",
            "title": "Deal Added",
            "children": [
                {
                    "type": "text",
                    "content": f"Added {title} to {stage}"
                }
            ]
        }
    
    def update_stage(params):
        """
        Updates a deal's stage.
        """
        deal_id = params.get("deal_id")
        new_stage = params.get("new_stage")
        
        if not deal_id or not new_stage:
            return {"type": "card", "title": "Error", "children": [{"type": "text", "content": "Missing parameters."}]}

        for d in _DEALS:
            if d["id"] == deal_id:
                old_stage = d["stage"]
                d["stage"] = new_stage
                return {
                    "type": "card",
                    "title": "Deal Updated",
                    "children": [{"type": "text", "content": f"Moved {d['title']} from {old_stage} to {new_stage}"}]
                }
        
        return {"type": "card", "title": "Error", "children": [{"type": "text", "content": "Deal not found."}]}

    kernel["register_capability"]("get_pipeline", get_pipeline)
    kernel["register_capability"]("add_deal", add_deal)
    kernel["register_capability"]("update_stage", update_stage)
