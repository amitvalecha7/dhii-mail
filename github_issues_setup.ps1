# Creates labels and key project issues for dhii-mail

# --- Optional: create labels (skip if they already exist) ---
# Comment out this block if you don't want to recreate labels.
try {
  gh label create "type/bug" --color "d73a4a" --description "Bug or incorrect behaviour" 2>$null
  gh label create "type/feature" --color "a2eeef" --description "New feature" 2>$null
  gh label create "type/refactor" --color "cfd3d7" --description "Internal refactor" 2>$null
  gh label create "type/docs" --color "0075ca" --description "Documentation" 2>$null
  gh label create "type/chore" --color "ffffff" --description "Maintenance / chore" 2>$null

  gh label create "area/shell" --color "5319e7" --description "AppShell and top-level layout" 2>$null
  gh label create "area/domain-mail" --color "0e8a16" --description "Mail domain" 2>$null
  gh label create "area/domain-meetings" --color "fbca04" --description "Meetings domain" 2>$null
  gh label create "area/domain-tasks" --color "fef2c0" --description "Tasks domain" 2>$null
  gh label create "area/design-system" --color "1d76db" --description "Design tokens and theming" 2>$null
  gh label create "area/component-catalog" --color "0052cc" --description "Shared UI components" 2>$null
  gh label create "area/a2ui-router" --color "5319e7" --description "A2UI router & orchestrator" 2>$null
  gh label create "area/security" --color "b60205" --description "Security & CORS" 2>$null
  gh label create "area/state-machine" --color "5319e7" --description "State machine & autonomy" 2>$null

  gh label create "phase/19" --color "f9d0c4" --description "AppShell & layout" 2>$null
  gh label create "phase/20" --color "f9d0c4" --description "Component catalog" 2>$null
  gh label create "phase/21" --color "f9d0c4" --description "Domain experiences" 2>$null
  gh label create "phase/22" --color "f9d0c4" --description "Responsive system" 2>$null
  gh label create "phase/23" --color "f9d0c4" --description "Command palette" 2>$null
  gh label create "phase/24" --color "f9d0c4" --description "Advanced interactions" 2>$null
  gh label create "phase/25" --color "f9d0c4" --description "State machine & autonomy" 2>$null

  gh label create "priority/p0" --color "b60205" --description "Blocking" 2>$null
  gh label create "priority/p1" --color "d93f0b" --description "High priority" 2>$null
  gh label create "priority/p2" --color "fbca04" --description "Normal priority" 2>$null
  gh label create "priority/p3" --color "0e8a16" --description "Low priority" 2>$null
} catch {
  Write-Host "Label creation step encountered errors (likely labels already exist). Continuing..." -ForegroundColor Yellow
}

# Helper to avoid failing the whole script if one issue creation fails
function New-DhiiIssue {
  param(
    [string]$Title,
    [string[]]$Labels,
    [string]$Body
  )

  $labelArgs = @()
  foreach ($l in $Labels) {
    $labelArgs += @('--label', $l)
  }

  Write-Host "Creating issue: $Title" -ForegroundColor Cyan
  $tempFile = [System.IO.Path]::GetTempFileName()
  Set-Content -Path $tempFile -Value $Body -Encoding UTF8
  gh issue create --title $Title @labelArgs --body-file $tempFile
  Remove-Item $tempFile -ErrorAction SilentlyContinue
}

# 1. Auth mismatch main.py / auth.py
New-DhiiIssue -Title "Unify AuthManager usage and token handling between main.py and auth.py" -Labels @("type/refactor","area/security","priority/p1") -Body @'
Problem
The authentication token management logic is duplicated and inconsistent between main.py and auth.py. This can lead to divergent behavior, harder maintenance, and subtle auth bugs.

Scope / details
- main.py and auth.py both implement or reference token / session handling in slightly different ways.
- There is no single canonical AuthManager/auth service that all entry points use.
- This makes it difficult to reason about refresh, expiry, and error handling consistently.

Impact
- Higher risk of auth bugs (e.g., tokens not refreshed, inconsistent error responses).
- Harder to extend or replace auth (OIDC, SSO, etc.) because logic is scattered.

Proposed direction
- Introduce a single AuthManager (or reuse the existing one) as the canonical source of auth behavior.
- Refactor main.py and auth.py to depend on this shared component only.
- Add unit tests covering:
  - Token creation and refresh paths.
  - Error handling for invalid/expired tokens.
  - Any public functions used by the rest of the app.

Acceptance criteria
- Auth logic lives in one place, imported everywhere else.
- main.py and auth.py no longer contain bespoke token logic.
- Tests cover happy path + expired/invalid token cases.
'@

# 2. A2UI router vs orchestrator schema
New-DhiiIssue -Title "Align A2UI router response shape with orchestrator contract in a2ui_router_updated.py" -Labels @("type/bug","area/a2ui-router","priority/p1") -Body @'
Problem
a2ui_router_updated.py expects/produces a response shape that does not match the orchestrator’s contract. This mismatch can cause runtime errors or missing UI data.

Scope / details
- The A2UI router is the boundary between the orchestrator and UI, but the current schema is inconsistent with the orchestrator’s documented/expected output.
- Some fields are missing, renamed, or structured differently (e.g., nested vs flat objects).

Impact
- UI components may receive incomplete or malformed data.
- Harder to evolve the orchestrator or router because implicit schema differences are not documented or validated.

Proposed direction
- Document the canonical orchestrator response schema (types or JSON examples).
- Update a2ui_router_updated.py to:
  - Validate incoming orchestrator responses.
  - Transform them into a clearly defined A2UI response format used by the frontend.
- Add tests using sample orchestrator responses to verify router output.

Acceptance criteria
- Single, documented schema for orchestrator → A2UI responses.
- a2ui_router_updated.py conforms to it and is covered by tests.
- No ad-hoc field renames or missing fields at call sites.
'@

# 3. CORS / SECURITY mismatch
New-DhiiIssue -Title "Align CORS and security configuration with SECURITY/README" -Labels @("type/bug","area/security","priority/p1") -Body @'
Problem
The current CORS and security configuration does not match what is promised in SECURITY/README. There is a gap between documented guarantees and actual behavior.

Scope / details
- Security docs describe specific CORS origins/headers and protections.
- Implementation leaves some of these out or configures them differently.
- There may be additional headers or middleware implied by docs that are not configured.

Impact
- Potential security exposure (over-permissive CORS) or broken integrations (over-restrictive CORS).
- Confusion for developers and auditors reading the docs vs the implementation.

Proposed direction
- Audit current CORS/security settings in code and infrastructure config.
- Compare line-by-line with SECURITY/README.
- Update either:
  - the implementation to match the docs, or
  - the docs to truthfully describe current behavior, if the current behavior is correct.
- Add automated tests or checks (where possible) to lock in the agreed CORS policy.

Acceptance criteria
- No material discrepancies between SECURITY/README and the effective CORS/security configuration.
- Test coverage or static checks validate critical CORS rules.
'@

# 4. AppShell integration (Phase 19)
New-DhiiIssue -Title "Complete AppShell integration and cross-view layout behavior (Phase 19)" -Labels @("type/refactor","area/shell","phase/19","priority/p2") -Body @'
Problem
The AppShell is present and partially integrated, but its role and behavior across views is incomplete. Layout and shell responsibilities are not consistently applied.

Scope / details
- Some pages/screens bypass AppShell or embed layout logic directly.
- Shared elements (nav, header, sidebars, status surfaces) are not handled uniformly.
- Resize behavior and inter-pane relationships are only partially implemented.

Impact
- Inconsistent UX across different views.
- Harder to evolve layout because shell responsibilities are not clearly centralized.

Proposed direction
- Define AppShell’s responsibilities (what it owns vs what pages own).
- Ensure all primary experiences (mail/meetings/tasks) are rendered within AppShell.
- Move duplicated layout/frame logic from individual pages into AppShell.
- Add tests or stories to validate that all main routes use the shell correctly.

Acceptance criteria
- All main routes render under a single AppShell.
- Shared UI (navigation, headers, status) is defined once in the shell.
- No page implements its own top-level frame that duplicates shell behavior.
'@

# 5. Resizable panes & breakpoints (19/22)
New-DhiiIssue -Title "Implement resizable panes and breakpoint-aware AppShell layout (Phase 19/22)" -Labels @("type/feature","area/shell","phase/22","priority/p2") -Body @'
Problem
Pane resizing and breakpoint-aware layout behavior are not implemented or are only stubbed. The UI does not react properly to window size changes or user resizing.

Scope / details
- Split views (e.g., list + detail) are fixed or only loosely adjustable.
- No consistent rules for min/max pane sizes.
- Layout does not switch/adjust at defined breakpoints.

Impact
- Poor UX on small or large screens.
- Layout can break or feel cramped with no user control.

Proposed direction
- Introduce a resizable pane system with:
  - Min/max constraints.
  - Persisted user preferences where appropriate.
- Wire AppShell to respond to breakpoint changes (e.g., collapse sidebars below a threshold).
- Add visual tests or stories for key breakpoint + pane configurations.

Acceptance criteria
- Users can resize key panes within safe limits.
- Layout behaves predictably across at least 2–3 breakpoints.
- No overlapping or unusable regions at common window sizes.
'@

# 6. Advanced components in catalog (Phase 20)
New-DhiiIssue -Title "Complete advanced components in UI catalog (Phase 20)" -Labels @("type/feature","area/component-catalog","phase/20","priority/p2") -Body @'
Problem
The rich component catalog is largely implemented, but several advanced or named components from the spec are still missing.

Scope / details
- Some complex components (e.g., composite lists, multi-pane controls, advanced filters) are not present or only partially implemented.
- Story/docs coverage may exist only for basic components.

Impact
- Teams cannot rely on the catalog for end-to-end UI composition.
- More one-off components proliferate, increasing maintenance cost.

Proposed direction
- Review the spec/list of intended advanced components.
- Implement missing components in the shared catalog, with:
  - Clear props API.
  - Composability in mind (headless/slots, if appropriate).
- Add stories/docs and basic visual regression tests.

Acceptance criteria
- All advanced components called out in the spec are implemented or explicitly descoped.
- Each advanced component has stories/docs and can be used across domain experiences.
- New screens do not ship custom copies of catalog functionality.
'@

# 7. De-duplicate ad-hoc components
New-DhiiIssue -Title "Audit and de-duplicate ad-hoc UI components in favor of catalog usage" -Labels @("type/refactor","area/component-catalog","priority/p2") -Body @'
Problem
There are likely one-off UI components that duplicate catalog behavior instead of using shared primitives, increasing inconsistency and maintenance cost.

Scope / details
- Screens or flows re-implement buttons, lists, filters, etc. that already exist in the catalog.
- Some styling or behavior drifts from the design system.

Impact
- Inconsistent UX and visual style.
- Tougher refactors because changes must be applied in multiple places.

Proposed direction
- Audit domain experiences for components that should be replaced by catalog counterparts.
- Replace ad-hoc implementations with catalog usage where possible.
- If a pattern is broadly useful but missing from the catalog, promote it into the catalog.

Acceptance criteria
- Clear mapping between domain UI and catalog components.
- Reduced number of bespoke components implementing generic patterns.
- Documented list of exceptions (legitimate one-offs).
'@

# 8. Shell vs domain responsibilities (Phase 21)
New-DhiiIssue -Title "Normalize shell vs domain responsibilities across email/meetings/tasks (Phase 21)" -Labels @("type/refactor","area/shell","phase/21","priority/p2") -Body @'
Problem
Domain experiences (email/meetings/tasks) exist, but the separation between shell-level concerns and domain-specific UI is only partially realized.

Scope / details
- Each domain may define its own navigation, chrome, or layout elements that should belong to the shell.
- Shared patterns (list/detail, filtering, selection) are implemented differently per domain.

Impact
- Inconsistent UX and harder code reuse.
- Changes to global layout or patterns require touching multiple domain implementations.

Proposed direction
- Define a clear contract between AppShell and each domain experience (props, slots, shared services).
- Refactor domains to:
  - Use shell-provided layout slots.
  - Reuse catalog components for lists, detail panes, filters, etc.
- Remove duplicate shell-like constructs from domain code.

Acceptance criteria
- Each domain implements only its domain-specific screens and logic.
- Shell-level concerns are handled centrally.
- Domain code size and duplication are reduced where possible.
'@

# 9. Responsive tokens & breakpoints (Phase 22)
New-DhiiIssue -Title "Define responsive design tokens and breakpoint system (Phase 22)" -Labels @("type/feature","area/design-system","phase/22","priority/p2") -Body @'
Problem
There is no canonical definition of breakpoints, spacing/typography scales per breakpoint, or responsive tokens. Implementations guess behavior ad-hoc.

Scope / details
- Breakpoints are not centrally defined in a design tokens or theme layer.
- Components and layouts use hard-coded magic numbers.
- No docs describing how responsiveness should work.

Impact
- Inconsistent responsive behavior across components.
- Hard to adjust the design system globally for new form factors.

Proposed direction
- Define primary breakpoints and any derived tokens (spacing, font sizes, layout constraints).
- Add them to the design token/theming system.
- Document how to consume these tokens in components and layouts.

Acceptance criteria
- Single source of truth for breakpoints and key responsive design tokens.
- Docs/examples show how to use them.
- New UI work does not introduce new magic breakpoint values.
'@

# 10. Apply responsive system to key layouts
New-DhiiIssue -Title "Apply responsive system to primary layouts (Phase 22 rollout)" -Labels @("type/feature","area/shell","phase/22","priority/p2") -Body @'
Problem
Even after defining a responsive system, primary layouts (shell + domain experiences) do not fully adopt it, leaving behavior inconsistent.

Scope / details
- AppShell, list/detail views, and key dialogs/overlays may still use fixed dimensions.
- Some components ignore responsive tokens or breakpoints.

Impact
- Users experience partial or broken responsiveness.
- Design system value is not realized.

Proposed direction
- Prioritize a set of primary screens (e.g., main mail view, meeting schedule, task list).
- Update layouts and components on those screens to use the responsive tokens and breakpoints.
- Verify behavior manually (and via visual tests if available).

Acceptance criteria
- Primary flows look correct across defined breakpoints.
- Code on those screens uses responsive tokens, not magic numbers.
- Any remaining non-responsive screens are listed as follow-ups.
'@

# 11. Advanced interaction layer (kbd / DnD / gestures)
New-DhiiIssue -Title "Implement advanced interaction layer (keyboard navigation, drag & drop, gestures)" -Labels @("type/feature","area/design-system","phase/24","priority/p2") -Body @'
Problem
Advanced interactions such as keyboard navigation, drag & drop, and gestures are mostly not implemented, despite being part of the project goals.

Scope / details
- Keyboard navigation across key views and components is incomplete or missing.
- Drag & drop flows (if specified in UX) are not wired.
- Gestures (if applicable for touch devices) are not implemented.

Impact
- Accessibility suffers due to lack of keyboard support.
- UX does not meet expectations for power users or complex flows.
- Some UX specs from the documentation are effectively 'dead letters'.

Proposed direction
- Prioritize a minimal set of advanced interactions:
  - Keyboard focus order and shortcuts for primary workflows.
  - Drag & drop for key items (e.g., moving items, reordering).
  - Any critical gestures required by spec.
- Implement these on top of a reusable interaction layer (not per-screen hacks).
- Add tests where feasible and update docs accordingly.

Acceptance criteria
- Users can complete primary workflows via keyboard alone.
- Any promised drag & drop flows work and are tested.
- New UI work can hook into the same interaction primitives.
'@

# 12. Autonomy model integration (Phase 25)
New-DhiiIssue -Title "Complete autonomy model integration for existing state machine (Phase 25)" -Labels @("type/feature","area/state-machine","phase/25","priority/p2") -Body @'
Problem
The state machine is implemented and tested, but the autonomy model described for Phase 25 is not integrated. The system lacks the higher-level autonomous behavior originally planned.

Scope / details
- Core state machine exists and is covered by tests.
- Autonomy logic (policies, triggers, long-running behaviors) is not wired into the state machine or is only partially present.
- There may be missing hooks for observability and control (e.g., pause/override).

Impact
- Features that depend on autonomous operation are missing or degraded.
- Harder to validate system-level behavior because autonomy is not formalized.

Proposed direction
- Revisit Phase 25 autonomy design (specs + docs).
- Define the minimal viable autonomy model that can be implemented on top of the current state machine.
- Implement:
  - Policy representation.
  - Decision hooks in the state machine.
  - Safety/override controls.
- Add targeted tests/simulations for autonomous flows.

Acceptance criteria
- Autonomy model integrated with the state machine according to a documented spec.
- Tests cover core autonomous workflows and safety paths.
- Clear knobs to enable/disable or tune autonomy.
'@
