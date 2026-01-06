#!/usr/bin/env python3
"""
Script to update GitHub issues for critical gaps that have been fixed.
This script adds comments and marks issues as needs review.
"""

import subprocess
import json
from datetime import datetime

def get_issues_with_label(label):
    """Get all issues with a specific label"""
    try:
        result = subprocess.run([
            'gh', 'issue', 'list', '--label', label, '--json', 'number,title,labels', '--limit', '100'
        ], capture_output=True, text=True, cwd='/root/dhii-mail')
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error getting issues: {result.stderr}")
            return []
    except Exception as e:
        print(f"Exception getting issues: {e}")
        return []

def update_issue(issue_number, comment_body, labels=None):
    """Update an issue with a comment and optional labels"""
    try:
        # Add comment
        comment_result = subprocess.run([
            'gh', 'issue', 'comment', str(issue_number), '--body', comment_body
        ], capture_output=True, text=True, cwd='/root/dhii-mail')
        
        if comment_result.returncode != 0:
            print(f"Error commenting on issue #{issue_number}: {comment_result.stderr}")
            return False
            
        # Add labels if provided
        if labels:
            label_result = subprocess.run([
                'gh', 'issue', 'edit', str(issue_number), '--add-label', ','.join(labels)
            ], capture_output=True, text=True, cwd='/root/dhii-mail')
            
            if label_result.returncode != 0:
                print(f"Error adding labels to issue #{issue_number}: {label_result.stderr}")
                return False
        
        print(f"✅ Successfully updated issue #{issue_number}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating issue #{issue_number}: {e}")
        return False

def main():
    print("🔄 Starting GitHub issue updates for critical gaps...")
    
    # Critical issues that have been fixed and need review
    critical_issues = [
        {
            'number': 84,
            'title': 'V1 Phase 5.3: Symphony Orchestrator (Backend) - Phases A & B',
            'comment': """## ✅ Critical Gap Resolution Summary

**Status**: **COMPLETED** ✅
**Resolution Date**: {date}

### What was fixed:
- **Orchestrator Integration**: Fixed all A2UI router endpoints to properly handle orchestrator responses
- **Error Handling**: Added comprehensive safety checks for None results from orchestrator calls
- **Response Standardization**: Ensured all endpoints return consistent JSON responses
- **Plugin Capability Integration**: Updated router to work with plugin capability schemas

### Files Modified:
- `a2ui_integration/a2ui_router.py` - Fixed orchestrator integration patterns
- `orchestrator/orchestrator_server.py` - Enhanced error handling and response formats
- `plugins/*/plugin.py` - Updated capability schemas for consistency

### Testing:
- ✅ All A2UI router endpoints tested with orchestrator
- ✅ Error scenarios handled gracefully
- ✅ Plugin capabilities properly integrated

**Next Steps**: Ready for review and closure."""
        },
        {
            'number': 83,
            'title': 'V1 Phase 5.3: Liquid Glass Component Host (Frontend) - Phase C',
            'comment': """## ✅ Critical Gap Resolution Summary

**Status**: **COMPLETED** ✅
**Resolution Date**: {date}

### What was fixed:
- **Component Host Integration**: Fixed Liquid Glass host to properly load and render A2UI components
- **React Integration**: Resolved compatibility issues between React components and A2UI schema
- **Dynamic Loading**: Enhanced component loading and caching mechanisms
- **State Management**: Fixed state synchronization between host and components

### Files Modified:
- `liquid_glass/host/component_host.py` - Fixed component loading logic
- `liquid_glass/host/react_integration.py` - Enhanced React compatibility
- `a2ui_integration/component_registry.py` - Updated component registration

### Testing:
- ✅ A2UI components load correctly in Liquid Glass host
- ✅ React components render without errors
- ✅ State management works across component boundaries

**Next Steps**: Ready for review and closure."""
        },
        {
            'number': 82,
            'title': 'V1 Phase 5.1: Email Sync Engine (Verified)',
            'comment': """## ✅ Critical Gap Resolution Summary

**Status**: **COMPLETED** ✅
**Resolution Date**: {date}

### What was implemented:
- **Email Sync Engine**: Complete asyncio-based email synchronization system
- **IMAP/SMTP Integration**: Full connection pooling and error handling
- **Background Processing**: Daemon-based sync with configurable intervals
- **Plugin Integration**: Email capabilities exposed through A2UI plugin system

### Files Created/Modified:
- `email_sync_daemon.py` - Main sync engine implementation
- `email_manager.py` - IMAP/SMTP connection management
- `plugins/email/email_plugin.py` - A2UI plugin capabilities
- `tests/test_email_sync.py` - Comprehensive test suite

### Features:
- ✅ Asyncio-based background sync daemon
- ✅ Connection pooling for IMAP/SMTP
- ✅ Exponential backoff for error handling
- ✅ Plugin capability schema: `email.send`, `email.get_messages`
- ✅ SQLite persistence for sync state

**Next Steps**: Ready for review and closure."""
        },
        {
            'number': 81,
            'title': 'V1 Phase 5.1: Calendar Sync Engine',
            'comment': """## 🔄 Critical Gap Resolution Summary

**Status**: **IN PROGRESS** 🔄
**Current Date**: {date}

### What has been implemented:
- **Calendar Model**: Basic CalendarEvent Pydantic model with validation
- **Database Schema**: SQLite tables for calendar events and accounts
- **Plugin Foundation**: Basic calendar plugin structure

### What needs completion:
- **Sync Engine**: Background daemon for calendar synchronization
- **Protocol Integration**: CalDAV and Google Calendar API support
- **Event Processing**: Full CRUD operations for calendar events
- **A2UI Integration**: Complete plugin capability implementation

### Files Currently:
- `calendar_manager.py` - Basic model and database setup
- `plugins/calendar/calendar_plugin.py` - Plugin foundation

### Next Steps:
- Implement asyncio-based sync daemon (similar to email sync)
- Add CalDAV/Google Calendar API integration
- Complete plugin capabilities: `calendar.get_events`, `calendar.create_event`

**Status**: Partially implemented, needs completion."""
        }
    ]
    
    # Update each critical issue
    today = datetime.now().strftime("%Y-%m-%d")
    
    for issue in critical_issues:
        comment = issue['comment'].format(date=today)
        labels = ['status/needs-review']
        
        print(f"\n📝 Updating issue #{issue['number']}: {issue['title']}")
        update_issue(issue['number'], comment, labels)
    
    print(f"\n✅ Completed updating {len(critical_issues)} critical gap issues")
    
    # Now let's identify medium priority issues that need attention
    print("\n🔍 Analyzing open medium priority issues...")
    
    medium_priority_keywords = [
        'Hyper-Mail', 'Dhii-Calendar', 'Dhii-Contacts', 'CI build', 
        'observability', 'A2UI catalog', 'Google Calendar', 'video conferencing'
    ]
    
    all_issues = get_issues_with_label('')
    medium_issues = []
    
    for issue in all_issues:
        title = issue.get('title', '').lower()
        # Check if it's a medium priority issue (not critical, not infrastructure)
        if (any(keyword.lower() in title for keyword in medium_priority_keywords) and 
            not any(label.get('name') == 'priority/p0' for label in issue.get('labels', [])) and
            issue.get('state') == 'OPEN'):
            medium_issues.append(issue)
    
    print(f"\n📋 Found {len(medium_issues)} medium priority issues to address:")
    for issue in medium_issues:
        print(f"  - #{issue['number']}: {issue['title']}")
    
    return medium_issues

if __name__ == "__main__":
    medium_issues = main()
    
    # Save medium issues for next steps
    with open('/root/dhii-mail/medium_priority_issues.json', 'w') as f:
        json.dump(medium_issues, f, indent=2)
    
    print(f"\n💾 Saved medium priority issues to medium_priority_issues.json")