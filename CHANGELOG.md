# Changelog

## [Unreleased] - 2025-01-04

### Security Fixes (P1 Priority)
- **Issue #1**: Unified AuthManager instances and JWT secret configuration
  - Consolidated authentication across auth_api.py and main auth system
  - Removed duplicate JWT configuration
  - Fixed hardcoded fallback JWT secret
  - All authentication flows now use unified PASETO token system

- **Issue #2**: Standardized A2UI router response to AppShell orchestrator shape
  - Updated all 12 render functions to return unified AppShell format
  - Created comprehensive test suite validating all UI states
  - Ensured consistent response format across all components

- **Issue #11**: Fixed EmailManager._save_sent_message foreign key integrity
  - Updated function signatures to accept user_id parameter
  - Modified database operations to use proper user_id foreign key
  - Resolved data integrity issues in email_messages table

- **Issue #14**: Unified auth_api.py SECRET_KEY with main auth configuration
  - Removed duplicate JWT configuration
  - Updated token creation/verification to use AuthManager

### Bug Fixes
- **Issue #10**: Fixed missing sqlite3 import in main.py email send endpoint
- **Issue #12**: Made security_audit.py paths project-relative instead of hardcoded

### Features Implemented
- **Issue #4**: Complete Phase 19 - AppShell with resizable panes and BottomBar
- **Issue #5**: Complete Phase 20 - Advanced A2UI component catalog
- **Issue #6**: Complete Phase 21 - Domain shell components and meeting scheduler
- **Issue #7**: Complete Phase 22 - Responsive A2UI design system
- **Issue #8**: Complete Phase 24 - Advanced interactions (keyboard, DnD, gestures)
- **Issue #9**: Complete Phase 25 - Autonomy levels and safety/audit framework

### New Issues Created
- **Issue #16**: Implement Tool Registry Pattern for Agent Extensibility
- **Issue #17**: Consolidate AI Agents (Deprecate ai_engine.py)
- **Issue #18**: Implement Database Persistence for Marketing Manager
- **Issue #19**: Implement 'Liquid Glass' UI Theme & Layout
- **Issue #20**: Implement Generative 'Context Cards' Engine
- **Issue #21**: Implement Universal Plugin Search
- **Issue #22**: Implement 'Skill Store' Interface
- **Issue #23**: Major Refactor: Core Kernel and Plugin Migration
- **Issue #24**: Implement Shared Kernel Services (DB, Auth, EventBus)

### Testing
- Created comprehensive test suite for A2UI orchestrator format validation
- Added tests for email user_id fix validation
- All existing tests passing

### Code Quality
- Improved code organization and modular architecture
- Enhanced security practices
- Better separation of concerns

## Previous Releases

### [v0.1.0] - 2024-12-XX
- Initial A2UI framework implementation
- Basic AppShell architecture
- Email management system
- Authentication system
- State machine implementation