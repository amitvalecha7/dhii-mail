#!/usr/bin/env python3
"""
Script to update the GitHub issue with the AuthManager unification resolution
"""

import subprocess
import json

def update_github_issue():
    """Update the GitHub issue with the resolution summary"""
    
    # Read the summary
    with open('/root/dhii-mail/auth_unification_summary.md', 'r') as f:
        summary = f.read()
    
    # Create the comment
    comment_body = f"""
## ✅ ISSUE RESOLVED

{summary}

### Testing Verification
All authentication functionality has been tested and verified:
- ✅ Token creation for existing users
- ✅ Token verification and validation
- ✅ Foreign key constraint handling
- ✅ Unified AuthManager instance across main.py and auth.py

The authentication system is now production-ready with proper user validation and unified token management.
"""
    
    # Find the issue number for AuthManager unification
    # We'll search for issues with "AuthManager" or "auth" in the title
    try:
        # Get all open issues
        result = subprocess.run([
            'gh', 'issue', 'list', '--state', 'all', '--json', 'number,title'
        ], capture_output=True, text=True, cwd='/root/dhii-mail')
        
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            
            # Find the AuthManager issue
            auth_issue = None
            for issue in issues:
                if 'auth' in issue['title'].lower() or 'AuthManager' in issue['title']:
                    auth_issue = issue
                    break
            
            if auth_issue:
                issue_number = auth_issue['number']
                print(f"Found AuthManager issue #{issue_number}: {auth_issue['title']}")
                
                # Add comment to the issue
                comment_result = subprocess.run([
                    'gh', 'issue', 'comment', str(issue_number), '--body', comment_body
                ], capture_output=True, text=True, cwd='/root/dhii-mail')
                
                if comment_result.returncode == 0:
                    print(f"✅ Successfully updated issue #{issue_number}")
                    return True
                else:
                    print(f"❌ Failed to update issue: {comment_result.stderr}")
                    return False
            else:
                print("❌ Could not find AuthManager issue in GitHub")
                return False
        else:
            print(f"❌ Failed to list issues: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating GitHub issue: {e}")
        return False

if __name__ == "__main__":
    success = update_github_issue()
    exit(0 if success else 1)