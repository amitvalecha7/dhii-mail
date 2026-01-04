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

# High priority issues from Project Review
issues = [
    {
        "title": "Unify AuthManager usage and token handling between main.py and auth.py",
        "labels": ["type/bug", "area/security", "priority/p0"],
        "body": """### Problem
The authentication token management logic is duplicated and inconsistent between main.py and auth.py. This can lead to divergent behavior, harder maintenance, and subtle auth bugs.

### Details
- `main.py` creates an `AuthManager` instance with a secret key derived from `JWT_SECRET_KEY`
- `auth.py` defines a separate global `auth_manager` with a hard-coded development secret
- Tokens created via the `auth_manager` in `main.py` may fail verification in `get_current_user` if `JWT_SECRET_KEY` is different

### Impact
- Higher risk of auth bugs (e.g., tokens not refreshed, inconsistent error responses)
- Code duplication and maintenance burden
- Potential security vulnerabilities

### Suggested Fix
- Ensure that only one `AuthManager` instance is used across the app
- Either import a single global `auth_manager` from `auth.py` into `main.py`, or
- Refactor `get_current_user` to rely on the `auth_manager` instantiated in `main.py`
- Remove the hard-coded dev secret from `auth.py` in favor of environment-based configuration

### Affected Files
- `main.py` (lines with AuthManager instantiation)
- `auth.py` (global auth_manager and get_current_user function)
"""
    },
    {
        "title": "Align A2UI router response shape with orchestrator contract in a2ui_router_updated.py",
        "labels": ["type/bug", "area/a2ui-router", "priority/p0"],
        "body": """### Problem
A2UI router endpoints are mixed between old and new response shapes, causing KeyError exceptions when accessing expected keys.

### Details
- `/dashboard` and `/email/inbox` use `create_ui_response_from_orchestrator(ui_data)` which wraps AppShell structure correctly
- Other routes (e.g., `/email/compose`, `/calendar`, `/meetings`, `/tasks`, `/analytics`) still assume old structure with keys like `ui_type`, `layout`, `navigation`, `chat_component`
- Orchestrator now returns AppShell layout rather than old flat schema

### Impact
- Endpoints that still assume old structure will raise `KeyError` when accessing `ui_data["ui_type"]`, `ui_data["layout"]` etc.
- Several UI endpoints are currently broken

### Suggested Fix
- Standardize orchestrator output and router expectations
- Decide on single canonical A2UI response shape (AppShell-centric)
- Update ALL routes in `a2ui_router_updated.py` to use `create_ui_response_from_orchestrator(ui_data)`
- Delete/adapt remaining code that assumes legacy `{ui_type, layout, navigation, chat_component}` keys

### Affected Files
- `a2ui_integration/a2ui_router_updated.py` (multiple route handlers)
- `a2ui_integration/a2ui_orchestrator.py` (response shape)
"""
    },
    {
        "title": "Align CORS and security configuration with SECURITY/README",
        "labels": ["type/bug", "area/security", "priority/p1"],
        "body": """### Problem
CORS configuration in main.py is completely open and doesn't match the security documentation.

### Details
- `main.py` configures CORS as completely open: `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`
- `SECURITY.md` and README describe stricter production posture (specific origins, tuned rate limits)
- `backend/core/middleware.py` correctly adds basic security headers and IP-based rate limiter

### Impact
- Security configuration doesn't match documentation for hardened production deployment
- Potential security vulnerabilities in production

### Suggested Fix
- For production profiles, restrict CORS to known front-end origins
- Expose CORS config via environment for easier dev/prod switching
- Ensure configuration matches SECURITY.md specifications

### Affected Files
- `main.py` (CORS configuration)
- `SECURITY.md` (security requirements)
- `backend/core/middleware.py` (security middleware)
"""
    }
]

for issue in issues:
    create_issue(issue["title"], issue["body"], issue["labels"])

if os.path.exists("temp_body.md"):
    os.remove("temp_body.md")