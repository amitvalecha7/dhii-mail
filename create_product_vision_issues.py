import subprocess
import os

def create_issue(title, body, labels):
    print(f"Creating issue: {title}")
    
    # Create temp body file
    with open("temp_vision_body.md", "w", encoding="utf-8") as f:
        f.write(body)
    
    # Construct command
    cmd = ["gh", "issue", "create", "--title", title, "--body-file", "temp_vision_body.md"]
    for label in labels:
        cmd.extend(["--label", label])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue '{title}': {e.stderr}")

instruction_footer = """
---
### 🛠️ Agent Instructions
**When working on this issue, you must:**
1.  **Resolution:** Clearly comment the technical resolution details in this issue.
2.  **Code Update:** Update the git repository with the new code.
3.  **Review:** Tag this issue to be reviewed.
"""

issues = [
    {
        "title": "Implement 'Kernel + Plugin' Architecture",
        "labels": ["type/architecture", "area/core", "priority/p0"],
        "body": """### Summary
Transform `dhii-mail` into a Modular Kernel that loads extensions dynamically.
See **UNIFIED_PRODUCT_VISION_SPEC.md** strategies.

### Requirements
1.  **Plugin Loader**: Scan `/plugins` directory for `manifest.json`.
2.  **Manifest Parser**: Read capabilities, permissions, and intents.
3.  **Router**: Route user intents (e.g., "Book meeting") to the correct plugin (Calendar).
4.  Supersedes the simple 'Tool Registry' concept.

### Acceptance Criteria
- [ ] System starts up and discovers 'Email' and 'Calendar' as plugins.
- [ ] `PluginManager` class exists and manages lifecycle.
""" + instruction_footer
    },
    {
        "title": "Implement 'Liquid Glass' UI Theme & Layout",
        "labels": ["type/feature", "area/ui", "priority/p1"],
        "body": """### Summary
Implement the new "Liquid Glass" aesthetic and "Stream vs Canvas" layout defined in **UNIFIED_PRODUCT_VISION_SPEC.md**.

### Requirements
1.  **Visuals**: Glassmorphism 2.0 (backdrop-blur, dynamic lighting borders).
2.  **Layout**: 
    - Left: Chat Stream (Glass panel).
    - Right: Dynamic Canvas (Persistent A2UI Surface).
    - Bottom: Floating "Omni-Bar".
3.  **AppShell**: Refactor `AppShell` component to support this layout.

### Acceptance Criteria
- [ ] Application uses new layout structure.
- [ ] Visuals match "Aurora" & Glass description.
""" + instruction_footer
    },
    {
        "title": "Implement Generative 'Context Cards' Engine",
        "labels": ["type/feature", "area/ai", "priority/p1"],
        "body": """### Summary
Create the engine responsible for triggering and rendering "Context Cards" based on time/event, as described in **UNIFIED_PRODUCT_VISION_SPEC.md**.

### Requirements
1.  **Morning Brief**: Trigger card at 8 AM.
2.  **Prep Mode**: Trigger card 5 mins before meetings.
3.  **Generative Logic**: AI determines *what* to show in the card based on context.

### Acceptance Criteria
- [ ] `ContextEngine` service created.
- [ ] Can trigger a card push to the frontend independent of user input.
""" + instruction_footer
    },
    {
        "title": "Implement Universal Plugin Search",
        "labels": ["type/feature", "area/search", "priority/p2"],
        "body": """### Summary
Create a unified search interface that queries all enabled plugins.
See `UNIFIED_PRODUCT_VISION_SPEC.md` -> Feature 3.

### Requirements
1.  **Search API**: `Kernel.search(query)` delegates to `Plugin.search(query)`.
2.  **Aggregated Results**: Merge results from Email, Calendar, Jira, etc.
3.  **UI**: Display results in the "Omni-Bar" dropdown.

### Acceptance Criteria
- [ ] Searching "Project" returns mocks from multiple (simulated) plugins.
""" + instruction_footer
    },
    {
        "title": "Implement 'Skill Store' Interface",
        "labels": ["type/feature", "area/ui", "priority/p2"],
        "body": """### Summary
Create the UI for managing plugins (The "Skill Store").
See `UNIFIED_PRODUCT_VISION_SPEC.md` -> Feature C.

### Requirements
1.  **List View**: Show available plugins.
2.  **Toggle**: Enable/Disable plugins.
3.  **Config**: 'Connect Account' buttons for plugins requiring auth.

### Acceptance Criteria
- [ ] User can toggle a mock "Jira" plugin and see it active in the Kernel.
""" + instruction_footer
    }
]

for issue in issues:
    create_issue(issue["title"], issue["body"], issue["labels"])

if os.path.exists("temp_vision_body.md"):
    os.remove("temp_vision_body.md")
