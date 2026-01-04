import subprocess
import os

body_content = """### Summary
Execute the major architecture refactor defined in `UNIFIED_PRODUCT_VISION_SPEC.md` and `implementation_plan.md`.
This involves converting the monolithic app into a **Kernel + Plugin** architecture and enforcing the **A2UI Adjacency List Standard**.

### Scope
1.  **Core Kernel**: Create `a2ui_integration/core` (Types, Kernel, PluginLoader).
2.  **Plugin Migration**: Move `email_manager`, `calendar_manager` to `/plugins/email`, `/plugins/calendar`.
3.  **Adjacency List**: Ensure all UI generation uses proper `Insert/Update` operations (Graph Model), replacing nested JSON.
4.  **Orchestrator**: Refactor `a2ui_orchestrator.py` to simply route to plugins.

### Impact
- Backend will be modular.
- API response format will change (BREAKING CHANGE).
- Frontend will need update (tracked in Issue #2).

### Deliverables
- [ ] `/plugins/` directory populated.
- [ ] `Kernel` class operational.
- [ ] `/api/a2ui/dashboard` returns Adjacency List operations.

---
### 🛠️ Agent Instructions
**When working on this issue, you must:**
1.  **Resolution:** Clearly comment the technical resolution details in this issue.
2.  **Code Update:** Update the git repository with the new code.
3.  **Review:** Tag this issue to be reviewed.
"""

def create_issue():
    print("Creating Grand Refactor Issue (File Mode)...")
    
    with open("grand_refactor_body.md", "w", encoding="utf-8") as f:
        f.write(body_content)
        
    cmd = [
        "gh", "issue", "create",
        "--title", "Major Refactor: Core Kernel and Plugin Migration",
        "--body-file", "grand_refactor_body.md",
        "--label", "type/refactor",
        "--label", "priority/p0",
        "--label", "area/core"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create issue: {e.stderr}")
    finally:
        if os.path.exists("grand_refactor_body.md"):
            os.remove("grand_refactor_body.md")

if __name__ == "__main__":
    create_issue()
