# Script to create issues from Vision/Reality Gap and A2UI Comparison Analysis
# Requires github_issues_templates_v2.ps1 in the same directory

Import-Module -Name ".\github_issues_templates_v2.ps1" -Force

# 1. Refactor A2UI Orchestrator to Adjacency List Model
New-DhiiCodeIssue `
    -Title "Refactor A2UI Orchestrator to use Adjacency List Model (A2UI Standard)" `
    -Labels @("type/refactor", "area/a2ui-router", "priority/p0") `
    -Problem "The current `a2ui_orchestrator.py` generates full nested JSON trees for UI updates. The official A2UI spec requires an 'Adjacency List' model where components are nodes in a graph, supporting Insert/Update/Remove operations." `
    -Impact "Incompatible with official A2UI tools and renderers. High bandwidth usage for small updates (sending full tree vs diffs)." `
    -ProposedFix "Rewrite `a2ui_orchestrator.py` to manage a graph of components. Implement `create_operation(type, node)` methods to generate A2UI-compliant JSON." `
    -AffectedFiles @("a2ui_integration/a2ui_orchestrator.py", "a2ui_integration/a2ui_components_extended.py") `
    -Tasks @("Study A2UI Adjacency List Spec", "Refactor internal component representation to Node/Graph", "Implement Operation generation (Insert/Update/Remove)")

# 2. Replace Frontend Client with Official Renderer
New-DhiiCodeIssue `
    -Title "Replace Custom Frontend Client with Official @a2ui/lit Renderer" `
    -Labels @("type/feature", "area/shell", "priority/p0") `
    -Problem "The frontend (`client/main.js`) uses a custom parser to render the non-standard JSON. To use the A2UI ecosystem, we must use the official standard renderer." `
    -Impact "Cannot use standard A2UI components or agents. Maintenance burden of custom renderer." `
    -ProposedFix "Update `package.json` to include `@a2ui/lit` (if not already properly used) and replace `main.js` logic to instantiate the official `<a2ui-renderer>` component." `
    -AffectedFiles @("a2ui_integration/client/main.js", "a2ui_integration/client/package.json", "a2ui_integration/client/index.html") `
    -Tasks @("Install official A2UI client libraries", "Replace main.js rendering logic", "Verify connectivity with new Orchestrator format")

# 3. Implement Streaming Transport
New-DhiiCodeIssue `
    -Title "Implement Streaming Transport for A2UI" `
    -Labels @("type/feature", "area/a2ui-router", "priority/p1") `
    -Problem "Current endpoints wait for the full agent response before sending JSON. A2UI is designed for streaming partial updates (token-by-token or node-by-node) to improve perceived latency." `
    -Impact "Slower UX. Does not leverage GenAI streaming capabilities." `
    -ProposedFix "Update `a2ui_router.py` to use FastAPI `StreamingResponse`. modifying `agent_updated_v2.py` to yield partial A2UI operations." `
    -AffectedFiles @("a2ui_integration/a2ui_router.py", "a2ui_integration/agent/agent_updated_v2.py") `
    -Tasks @("Implement generator in Agent", "Switch Router to StreamingResponse", "Ensure Client handles stream")

# 4. Tool Registry Pattern for Extensibility
New-DhiiCodeIssue `
    -Title "Implement Tool Registry Pattern for Agent Extensibility" `
    -Labels @("type/refactor", "area/state-machine", "priority/p2") `
    -Problem "Agent tools are hardcoded in `agent_updated_v2.py` (`tools=[...]`). Adding a new module (e.g., CRM) requires modifying core agent code." `
    -Impact "Poor extensibility. Violates Open/Closed principle." `
    -ProposedFix "Create a `ToolRegistry` singleton. Allow other modules (`email_manager`, `calendar_manager`) to register their tools at startup. Agent loads tools from Registry." `
    -AffectedFiles @("a2ui_integration/agent/agent_updated_v2.py", "a2ui_integration/tool_registry.py") `
    -Tasks @("Create ToolRegistry class", "Update Managers to register tools", "Update Agent to consume Registry")

# 5. Consolidate AI Agents
New-DhiiCodeIssue `
    -Title "Consolidate AI Agents (Deprecate ai_engine.py)" `
    -Labels @("type/refactor", "area/a2ui-router", "priority/p2") `
    -Problem "Two agent implementations exist: `ai_engine.py` (legacy/hardcoded) and `agent_updated_v2.py` (ADK-based). Logic is split." `
    -Impact "Confusion, code duplication, two places to maintain." `
    -ProposedFix "Migrate any unique logic from `ai_engine.py` to `agent_updated_v2.py`. Deprecate and remove `ai_engine.py`. Ensure `agent_updated_v2` powers the main chat." `
    -AffectedFiles @("ai_engine.py", "a2ui_integration/agent/agent_updated_v2.py") `
    -Tasks @("Audit ai_engine.py features", "Port to agent_updated_v2", "Switch main.py to use agent_updated_v2", "Delete ai_engine.py")

# 6. Marketing Data Persistence
New-DhiiCodeIssue `
    -Title "Implement Database Persistence for Marketing Manager" `
    -Labels @("type/bug", "area/domain-mail", "priority/p1") `
    -Problem "`MarketingManager` stores campaigns in an in-memory dictionary. Data is lost on server restart." `
    -Impact "Critical data loss. Feature is not production-ready." `
    -ProposedFix "Add `marketing_campaigns` table to `database.py`. Update `MarketingManager` to use SQLite/SQLAlchemy for CRUD operations." `
    -AffectedFiles @("marketing_manager.py", "database.py") `
    -Tasks @("Define Schema", "Update MarketingManager methods", "Add migration if needed")

Write-Host "Gap Analysis Issues Created!" -ForegroundColor Green
