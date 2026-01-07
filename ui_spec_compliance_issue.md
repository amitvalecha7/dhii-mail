# UI Spec Compliance Issue - New Design Spec v1.2 Implementation

## Issue Summary
The current UI implementation needs to be aligned with the New Design Spec v1.2 to ensure proper component taxonomy and UI standardization.

## Current Status
✅ **COMPLETED:**
- Multi-tenant isolation (foundation)
- Neural Loop AI processing (core functionality)

🔄 **IN PROGRESS:**
- Framework 2.0 migration
- UI spec compliance alignment

## Critical Gaps Identified

### 1. Component Taxonomy Misalignment
**Current Issue:** Custom card components vs. New Design Spec components
- **Current:** Custom `Card` components with literal strings
- **Required:** `TextBlock` and `AggregatedCard` components per New Design Spec v1.2

**Files Affected:**
- `/root/dhii-mail/a2ui_integration/a2ui_orchestrator.py` - Multiple Card component usages
- `/root/dhii-mail/a2ui_integration/a2ui_components_extended.py` - Component definitions

### 2. UI State Adjacency List Compliance
**Current Issue:** ComponentGraph adjacency list structure needs verification
- **Required:** Ensure all UI states follow proper adjacency patterns per Issue #25

**Files Affected:**
- `/root/dhii-mail/a2ui_integration/a2ui_orchestrator.py` - ComponentGraph usage
- `/root/dhii-mail/a2ui_integration/data_structures.py` - Adjacency list implementation

### 3. Tenant-Scoped User-Verse Boundaries
**Current Issue:** Security layer for user-verse isolation within tenants
- **Required:** Implement user-verse boundaries to prevent cross-user data access

**Files Affected:**
- `/root/dhii-mail/a2ui_integration/tenant_manager.py` - User context management
- `/root/dhii-mail/a2ui_integration/a2ui_orchestrator.py` - User context filtering

### 4. Backend→UI Intent Mapping
**Current Issue:** Protocol refinement for intent communication
- **Required:** Standardize backend intent mapping to UI component rendering

**Files Affected:**
- `/root/dhii-mail/a2ui_integration/neural_loop_ai_engine.py` - Intent processing
- `/root/dhii-mail/a2ui_integration/a2ui_orchestrator.py` - Intent-to-UI mapping

## Implementation Action Items

### Phase 1: Component Taxonomy Standardization
- [ ] Replace all custom `Card` components with `TextBlock` components
- [ ] Replace dashboard cards with `AggregatedCard` components  
- [ ] Update component schemas to match New Design Spec v1.2
- [ ] Implement proper component hierarchy per spec

### Phase 2: UI State Compliance
- [ ] Verify ComponentGraph adjacency list for all UI states
- [ ] Ensure proper state transitions per Issue #25 requirements
- [ ] Test adjacency compliance for dashboard, email, calendar, meeting states
- [ ] Document state machine transitions

### Phase 3: Security Layer Implementation
- [ ] Implement user-verse boundary checks in tenant manager
- [ ] Add user context filtering to all data retrieval methods
- [ ] Create user-scoped component rendering
- [ ] Test cross-user data isolation

### Phase 4: Intent Mapping Protocol
- [ ] Standardize intent-to-component mapping schema
- [ ] Update Neural Loop engine output format
- [ ] Implement consistent intent handling across all UI states
- [ ] Create intent mapping documentation

### Phase 5: Framework 2.0 Migration
- [ ] Complete plugin interface migration
- [ ] Update all plugin manifests to Framework 2.0 format
- [ ] Test plugin loading and execution
- [ ] Document migration guide

## Files to be Modified

### Primary Files:
1. `/root/dhii-mail/a2ui_integration/a2ui_orchestrator.py` - Main orchestrator logic
2. `/root/dhii-mail/a2ui_integration/a2ui_components_extended.py` - Component definitions
3. `/root/dhii-mail/a2ui_integration/data_structures.py` - Adjacency list structures
4. `/root/dhii-mail/a2ui_integration/tenant_manager.py` - Tenant/user management

### Secondary Files:
1. `/root/dhii-mail/a2ui_integration/neural_loop_ai_engine.py` - Intent processing
2. `/root/dhii-mail/a2ui_integration/a2ui_state_machine.py` - State transitions
3. `/root/dhii-mail/plugins/*` - Plugin implementations

## Testing Requirements

### Unit Tests:
- Component taxonomy compliance tests
- Adjacency list validation tests
- User-verse boundary tests
- Intent mapping accuracy tests

### Integration Tests:
- End-to-end UI spec compliance
- Multi-tenant isolation verification
- Plugin Framework 2.0 compatibility
- Neural Loop integration tests

## Definition of Done

✅ **UI Spec Compliance Achieved When:**
- All components use TextBlock/AggregatedCard per New Design Spec v1.2
- ComponentGraph adjacency list passes all compliance checks
- User-verse boundaries prevent cross-user data access
- Intent mapping follows standardized protocol
- Framework 2.0 migration is complete
- All tests pass for spec compliance

## Priority Order
1. **HIGH:** Component taxonomy standardization (blocks UI rendering)
2. **HIGH:** User-verse boundaries (security compliance)
3. **MEDIUM:** UI state adjacency compliance
4. **MEDIUM:** Intent mapping protocol
5. **LOW:** Framework 2.0 migration completion

## References
- New Design Spec v1.2: `/root/dhii-mail/New Design Spec.md`
- Issue #25: A2UI Orchestrator adjacency list compliance
- Issue #23: Kernel-plugin integration validation
- Framework 2.0 specification