### Summary
Current endpoints wait for the full agent response before sending JSON. A2UI is designed for streaming partial updates (token-by-token or node-by-node) to improve perceived latency.

### Impact
Slower UX. Does not leverage GenAI streaming capabilities.

### Proposed direction
Update `a2ui_router.py` to use FastAPI `StreamingResponse`. modifying `agent_updated_v2.py` to yield partial A2UI operations.

### Affected files
- `a2ui_integration/a2ui_router.py`
- `a2ui_integration/agent/agent_updated_v2.py`


---
### 🛠️ Agent Instructions
**When working on this issue, you must:**
1.  **Resolution:** Clearly comment the technical resolution details in this issue.
2.  **Code Update:** Update the git repository with the new code.
3.  **Review:** Tag this issue to be reviewed (e.g., add a `status/needs-review` label or comment requesting review).
