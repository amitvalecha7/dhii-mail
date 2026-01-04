import subprocess

updates = [
    {
        "id": "1",
        "comment": """### Verification Update
**Status: Not Fixed**
Analysis shows that `auth_api.py` (lines 38-73) implements its own JWT logic (`jwt.encode`, `SECRET_KEY`) and mocks a user database (`users_db = {}`), completely bypassing the robust `AuthManager` in `auth.py` and the real database.

**Recommendation:**
1. Refactor `auth_api.py` to import `auth_manager` from `main.py` (or `auth.py`).
2. Replace `api_signup` logic to use `auth_manager.create_user`.
3. Remove local `SECRET_KEY` and `users_db` from `auth_api.py`.
"""
    },
    {
        "id": "2",
        "comment": """### Verification Update
**Status: Not Fixed**
`a2ui_router_updated.py` (lines 38-56) performs manual adaptation of `orchestrator` output, which implies the `A2UIOrchestrator` is not returning the canonical schema expected by the router.

**Recommendation:**
Define a shared Pydantic model for `Component` and `Page` in a common file (e.g., `a2ui_models.py`) and ensure both Orchestrator and Router import it, eliminating the need for ad-hoc dict conversion.
"""
    },
    {
        "id": "14",
        "comment": """### Verification Update
**Status: Not Fixed**
`main.py` (line 120) explicitly sets `allow_origins=["*"]`. This contradicts production security best practices.

**Recommendation:**
1. Introduce an environment variable `CORS_ORIGINS`.
2. Update `main.py` to load this variable, defaulting to `["http://localhost:3000"]` (or similar) in dev, but enforcing strict origins in production.
"""
    }
]

def update_issue(issue_id, comment):
    print(f"Updating Issue #{issue_id}...")
    try:
        # Add 'to do' label
        subprocess.run(["gh", "issue", "edit", issue_id, "--add-label", "to do"], check=True)
        
        # Add verification comment
        subprocess.run(["gh", "issue", "comment", issue_id, "--body", comment], check=True)
        print(f"Issue #{issue_id} updated.")
    except Exception as e:
        print(f"Error updating #{issue_id}: {e}")

if __name__ == "__main__":
    for update in updates:
        update_issue(update["id"], update["comment"])
