import subprocess
import os

def create_issue(title, body, labels):
    print(f"Creating issue: {title}")
    
    # Create temp body file
    with open("temp_body.md", "w", encoding="utf-8") as f:
        f.write(body)
    
    # Construct command
    cmd = ["gh", "issue", "create", "--title", title, "--body-file", "temp_body.md"]
    for label in labels:
        cmd.extend(["--label", label])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue '{title}': {e.stderr}")

issues = [
    {
        "title": "Refactor A2UI Orchestrator to Adjacency List Model (A2UI Standard)",
        "labels": ["type/refactor", "area/a2ui-router", "priority/p0"],
        "body": """### Summary
The current `a2ui_orchestrator.py` generates full nested JSON trees for UI updates. The official A2UI spec requires an 'Adjacency List' model where components are nodes in a graph, supporting Insert/Update/Remove operations.

### Impact
Incompatible with official A2UI tools and renderers. High bandwidth usage for small updates (sending full tree vs diffs).

### Proposed direction
Rewrite `a2ui_orchestrator.py` to manage a graph of components. Implement `create_operation(type, node)` methods to generate A2UI-compliant JSON.

### Affected files
- `a2ui_integration/a2ui_orchestrator.py`
- `a2ui_integration/a2ui_components_extended.py`
"""
    },
    {
        "title": "Replace Custom Frontend Client with Official @a2ui/lit Renderer",
        "labels": ["type/feature", "area/shell", "priority/p0"],
        "body": """### Summary
The frontend (`client/main.js`) uses a custom parser to render the non-standard JSON. To use the A2UI ecosystem, we must use the official standard renderer.

### Impact
Cannot use standard A2UI components or agents. Maintenance burden of custom renderer.

### Proposed direction
Update `package.json` to include `@a2ui/lit` (if not already properly used) and replace `main.js` logic to instantiate the official `<a2ui-renderer>` component.

### Affected files
- `a2ui_integration/client/main.js`
- `a2ui_integration/client/package.json`
- `a2ui_integration/client/index.html`
"""
    },
    {
        "title": "Implement Streaming Transport for A2UI",
        "labels": ["type/feature", "area/a2ui-router", "priority/p1"],
        "body": """### Summary
Current endpoints wait for the full agent response before sending JSON. A2UI is designed for streaming partial updates (token-by-token or node-by-node) to improve perceived latency.

### Impact
Slower UX. Does not leverage GenAI streaming capabilities.

### Proposed direction
Update `a2ui_router.py` to use FastAPI `StreamingResponse`. modifying `agent_updated_v2.py` to yield partial A2UI operations.

### Affected files
- `a2ui_integration/a2ui_router.py`
- `a2ui_integration/agent/agent_updated_v2.py`
"""
    },
    {
        "title": "Implement Tool Registry Pattern for Agent Extensibility",
        "labels": ["type/refactor", "area/state-machine", "priority/p2"],
        "body": """### Summary
Agent tools are hardcoded in `agent_updated_v2.py` (`tools=[...]`). Adding a new module (e.g., CRM) requires modifying core agent code.

### Impact
Poor extensibility. Violates Open/Closed principle.

### Proposed direction
Create a `ToolRegistry` singleton. Allow other modules (`email_manager`, `calendar_manager`) to register their tools at startup. Agent loads tools from Registry.

### Affected files
- `a2ui_integration/agent/agent_updated_v2.py`
- `a2ui_integration/tool_registry.py`
"""
    },
    {
        "title": "Consolidate AI Agents (Deprecate ai_engine.py)",
        "labels": ["type/refactor", "area/a2ui-router", "priority/p2"],
        "body": """### Summary
Two agent implementations exist: `ai_engine.py` (legacy/hardcoded) and `agent_updated_v2.py` (ADK-based). Logic is split.

### Impact
Confusion, code duplication, two places to maintain.

### Proposed direction
Migrate any unique logic from `ai_engine.py` to `agent_updated_v2.py`. Deprecate and remove `ai_engine.py`. Ensure `agent_updated_v2` powers the main chat.

### Affected files
- `ai_engine.py`
- `a2ui_integration/agent/agent_updated_v2.py`
"""
    },
    {
        "title": "Implement Database Persistence for Marketing Manager",
        "labels": ["type/bug", "area/domain-mail", "priority/p1"],
        "body": """### Summary
`MarketingManager` stores campaigns in an in-memory dictionary. Data is lost on server restart.

### Impact
Critical data loss. Feature is not production-ready.

### Proposed direction
Add `marketing_campaigns` table to `database.py`. Update `MarketingManager` to use SQLite/SQLAlchemy for CRUD operations.

### Affected files
- `marketing_manager.py`
- `database.py`
"""
    }
]

for issue in issues:
    create_issue(issue["title"], issue["body"], issue["labels"])

if os.path.exists("temp_body.md"):
    os.remove("temp_body.md")
