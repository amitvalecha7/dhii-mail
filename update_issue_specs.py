import subprocess
import json

# Standard Tech Spec Addendum
tech_spec_addendum = """

---
### 🛠️ Technical Implementation Specs (Architect Update)

**Standard**: All UI components MUST adhere to the [A2UI Schema Contract](docs/architecture/A2UI_SCHEMA.md).
**Factory**: Use the [Agentic Component Factory](docs/architecture/AGENTIC_COMPONENT_FACTORY.md) to generate initial scaffolding.
**Router**: Register all routes via the `A2UIOrchestrator` using `AppShell` types.

#### Reference Files:
- Schema: `docs/architecture/A2UI_SCHEMA.md`
- Factory: `tools/component_factory.py`
- Registry: `docs/architecture/A2UI_CUSTOM_COMPONENT_REGISTRY.md`
"""

# Issues to update (Plugins & Architecture)
target_issues = [
    "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", # Plugins
    "53", "54" # Architecture
]

for issue_id in target_issues:
    try:
        # Get current body
        cmd_get = ["gh", "issue", "view", issue_id, "--json", "body"]
        result = subprocess.run(cmd_get, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        if data is None:
             print(f"⚠️ data is None for #{issue_id}")
             continue
             
        current_body = data.get("body")
        if current_body is None:
            current_body = ""
        
        # Check if already updated
        if "Technical Implementation Specs" in current_body:
            print(f"Skipping #{issue_id} (Already updated)")
            continue

        # Append Spec
        new_body = current_body + tech_spec_addendum
        
        # Update Issue
        subprocess.run(["gh", "issue", "edit", issue_id, "--body", new_body], check=True)
        print(f"✅ Updated Spec for #{issue_id}")
        
    except Exception as e:
        print(f"⚠️ Failed to update #{issue_id}: {e}")
        # import traceback
        # traceback.print_exc()
