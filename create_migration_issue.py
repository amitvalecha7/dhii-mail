import os
import requests
import json

# Configuration
REPO_OWNER = "amitvalecha7"
REPO_NAME = "dhii-mail"
TOKEN = os.environ.get("GITHUB_TOKEN")

def create_issue():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    body_markdown = """
# 🎨 Phase 2: React Frontend Integration (Liquid Glass)

## Context
We have replaced the prototype `Lit` client with a high-fidelity **React + Tailwind** application (`dhii-conversational-dashboard`). The files are now in `a2ui_integration/client`.

## Objectives
Connect this new UI to the Python Kernel (`/api/a2ui`) to enable the full Agentic Loop.

## Integration Steps (Checklist)

### 1. 🔌 The Neural Link (API Bridge)
- [ ] Create `services/kernelBridge.ts` to replace `geminiService.ts`.
- [ ] Implement `fetchState(route)`: fetches JSON from `/api/a2ui/{route}`.
- [ ] Implement `sendAction(action)`: POSTs to `/api/a2ui/ui/action`.
- [ ] Ensure `vite.config.ts` proxies `/api` and `/ws` to `http://kernel:8005`.

### 2. 🧠 Data Binding
- [ ] **Dashboard**: In `DashboardScreen.tsx`, replace mock data with `useEffect(() => kernelBridge.fetchState('dashboard'), [])`.
- [ ] **Chat**: In `WorkspaceShell.tsx`, route user messages to `kernelBridge.sendMessage(text)` instead of standard Gemini API.

### 3. 🛡️ Verification
- [ ] Verify that clicking "Inbox" fetches real email data from the Kernel.
- [ ] Verify that the "Liquid Glass" styling renders correctly in the Docker container.

## Resources
- **Design System**: Already implemented in `index.css` and Tailwind config.
- **Protocol**: See `A2UI_SCHEMA.md` for the JSON structure expected from the Kernel.
"""

    payload = {
        "title": "Refactor: Integrate 'Liquid Glass' React Frontend with Kernel",
        "body": body_markdown,
        "labels": ["enhancement", "frontend", "a2ui"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        issue = response.json()
        print(f"Successfully created Issue #{issue['number']}: {issue['title']}")
    except Exception as e:
        print(f"Failed to create issue: {e}")
        if 'response' in locals():
            print(response.text)

if __name__ == "__main__":
    create_issue()
