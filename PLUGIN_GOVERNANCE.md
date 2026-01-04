# Plugin SDK Governance & Security Model (Issue #52)

**Status**: DRAFT  
**Version**: 1.0.0  
**Last Updated**: 2026-01-04

---

## 1. Philosophy: "Trust, but Verify"

The Dhii-Mail Kernel is designed to run code from third-party developers. To ensure user privacy and system stability, plugins operate within a **Capability-Based Security Model**. A plugin cannot do *anything* unless it has been explicitly granted the capability to do so by the user.

## 2. The Sandbox Model

We will transition from the current "Trusted Import" model to a "Restricted Execution" model.

### Phase 1: Trusted Imports (Current)
*   Plugins are Python modules loaded via `importlib`.
*   They share the same process memory as the Kernel.
*   **Risk**: High. A malicious plugin can access global variables or block the event loop.

### Phase 2: Restricted Execution (Target State)
*   **Isolation**: Plugins run in separate processes (or sub-interpreters).
*   **Communication**: IPC (Inter-Process Communication) via the Kernel Bridge.
*   **FileSystem**: Read-only access to their own directory. No access to `/root` or `/etc`.
*   **Network**: No direct `socket` or `requests` access. All network calls must go through `kernel.http_client`.

## 3. Capability Manifest (`manifest.json`)

Every plugin MUST define its required capabilities in `manifest.json`. If a capability is not requested here, the Kernel will block the action at runtime.

```json
{
  "id": "com.dhiimail.marketing",
  "name": "Marketing Genius",
  "version": "1.0.0",
  "permissions": [
    "email.read",
    "email.send",
    "network.dhiiai.com" 
  ]
}
```

## 4. API Surface Area

Plugins interact with the world ONLY through the **Plugin SDK**.

### Allowed Imports (Allowlist)
*   `datetime`, `json`, `math`, `re` (Standard Library utilities)
*   `dhii_sdk.*` (The official SDK)

### Banned Imports (Blocklist)
*   `os`, `sys`, `subprocess` (System access)
*   `socket`, `http` (Direct networking)
*   `threading`, `multiprocessing` (Concurrency management)

## 5. Resource Limits (Quotas)

To prevent a plugin from freezing the UI ("The Chrome Tab Problem"):

| Metric | Limit (Per Plugin) | Action on Breach |
| :--- | :--- | :--- |
| **Execution Time** | 200ms per Capability Call | `TimeoutError` thrown to UI |
| **Memory** | 50MB Heap | Process Kill & Restart |
| **Storage** | 100MB (Local DB) | `QuotaExceededError` |
| **Network** | 50 Requests / Minute | Rate Limited |

## 6. Data Privacy Contracts

1.  **Local-First**: Plugins process data locally by default.
2.  **Exfiltration Check**: Sending data to an external API requires a specific `network.host` permission that is highlighted to the user during installation.
    *   *Example Warning*: "This plugin wants to send your emails to `api.marketing-tool.com`. Allow?"

## 7. Review Process

Before a plugin is listed in the **Skill Store**:
1.  **Static Analysis**: Automated scan for banned imports.
2.  **Manifest Verification**: Checking that requested permissions match code usage.
3.  **Manual Review**: For "Verified" badges.
