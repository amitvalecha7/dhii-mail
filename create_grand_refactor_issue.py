import subprocess

issue_body = """### Summary
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
    print("Creating Grand Refactor Issue...")
    cmd = [
        "gh", "issue", "create",
        "--title", "Major Refactor: Core Kernel and Plugin Migration",
        "--body", issue_body,
        "--label", "type/refactor",
        "--label", "priority/p0",
        "--label", "area/core"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Issue created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create issue: {e}")

if __name__ == "__main__":
    create_issue()
