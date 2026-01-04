import subprocess
import json

# The specific titles of the issues we just created
target_titles = [
    "Refactor A2UI Orchestrator to Adjacency List Model (A2UI Standard)",
    "Replace Custom Frontend Client with Official @a2ui/lit Renderer",
    "Implement Streaming Transport for A2UI",
    "Implement Tool Registry Pattern for Agent Extensibility",
    "Consolidate AI Agents (Deprecate ai_engine.py)",
    "Implement Database Persistence for Marketing Manager"
]

instruction_text = """

---
### 🛠️ Agent Instructions
**When working on this issue, you must:**
1.  **Resolution:** Clearly comment the technical resolution details in this issue.
2.  **Code Update:** Update the git repository with the new code.
3.  **Review:** Tag this issue to be reviewed (e.g., add a `status/needs-review` label or comment requesting review).
"""

def update_issues():
    print("Fetching issues...")
    # Get all open issues
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", "50", "--json", "number,title,body"],
            capture_output=True, text=True, check=True
        )
        issues = json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return

    for issue in issues:
        if issue['title'] in target_titles:
            print(f"Updating Issue #{issue['number']}: {issue['title']}")
            
            # Check if instruction is already present to avoid duplication
            if "Agent Instructions" in issue['body']:
                print(f"Skipping #{issue['number']} - Instructions already present.")
                continue

            new_body = issue['body'] + instruction_text
            
            # Write to temp file to handle special characters correctly
            with open("temp_update_body.md", "w", encoding="utf-8") as f:
                f.write(new_body)
            
            try:
                subprocess.run(
                    ["gh", "issue", "edit", str(issue['number']), "--body-file", "temp_update_body.md"],
                    capture_output=True, check=True
                )
                print(f"Successfully updated #{issue['number']}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to update #{issue['number']}: {e}")

if __name__ == "__main__":
    update_issues()
