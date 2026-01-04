import subprocess
import os

body_content = """### Summary
Implement the **Shared Services Layer** of the Kernel as defined in `SHARED_KERNEL_SERVICES_DESIGN.md`.
This provides the common infrastructure for all plugins to prevent code duplication.

### Parent Issue
- Part of Major Refactor: #23

### Scope
1.  **Database Service**:
    - Centralized `SQLAlchemy` engine.
    - `register_models()` functionality for plugins.
    - Shared Session management for cross-plugin JOINs.
2.  **Identity Service**:
    - `Vault` for storing/retrieving OAuth tokens securely.
    - User Context injection.
3.  **Event Bus**:
    - Simple Pub/Sub mechanism (`kernel.bus.publish`, `kernel.bus.subscribe`).
4.  **Component Factory**:
    - Centralized A2UI Component classes to enforce "Liquid Glass" theme.
5.  **Memory Service**:
    - Placeholder for Vector DB integration.

### Deliverables
- [ ] `a2ui_integration/core/services/database.py`
- [ ] `a2ui_integration/core/services/identity.py`
- [ ] `a2ui_integration/core/services/events.py`
- [ ] Updated `Kernel` to initialize these services.

---
### 🛠️ Agent Instructions
**When working on this issue, you must:**
1.  **Resolution:** Clearly comment the technical resolution details in this issue.
2.  **Code Update:** Update the git repository with the new code.
3.  **Review:** Tag this issue to be reviewed.
"""

def create_issue():
    print("Creating Shared Kernel Services Issue...")
    
    with open("kernel_services_body.md", "w", encoding="utf-8") as f:
        f.write(body_content)
        
    cmd = [
        "gh", "issue", "create",
        "--title", "Implement Shared Kernel Services (DB, Auth, EventBus)",
        "--body-file", "kernel_services_body.md",
        "--label", "type/feature",
        "--label", "priority/p0",
        "--label", "area/core"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success: {result.stdout.strip()}")
        
        # Extract new issue URL/Number from stdout (format: https://github.com/.../issues/24)
        output = result.stdout.strip()
        print(f"Created Issue: {output}")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to create issue: {e.stderr}")
    finally:
        if os.path.exists("kernel_services_body.md"):
            os.remove("kernel_services_body.md")

if __name__ == "__main__":
    create_issue()
