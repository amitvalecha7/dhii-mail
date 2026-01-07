# Plugin Framework 2.0: Project Structure

> **Purpose**: Define the directory layout and file naming conventions for the V2 Architecture.

## 1. Directory Layout

```text
c:\DevAps\DeskAI\dhii-mail\
├── a2ui_integration\
│   ├── framework\                          # [NEW] The V2 Interface Definitions
│   │   ├── __init__.py
│   │   ├── contract.py                     # PluginInterface, ExecutionContext
│   │   ├── types.py                        # PluginCapability (Pydantic), HealthStatus
│   │   ├── exceptions.py                   # PluginError hierarchy
│   │   └── telemetry.py                    # OpenTelemetry instrumentation
│   │
│   ├── core\                               # The Kernel Runtime
│   │   ├── kernel.py                       # Existing Kernel (Main Entry)
│   │   ├── manager_v2.py                   # [NEW] PluginManager V2 implementation
│   │   └── sandbox.py                      # Existing Sandbox
│   │
│   └── cli\                                # [NEW] Developer Tools
│       ├── __init__.py
│       ├── main.py                         # Entry point for `python -m a2ui_integration.cli`
│       ├── commands.py                     # create, validate, bundle logic
│       └── templates\                      # Scaffolding templates
│           └── basic_plugin\
│               ├── plugin.py.j2
│               └── manifest.json.j2
│
└── plugins\                                # V2 Plugins Directory
    ├── email\                              # [MIGRATE] Email Plugin V2
    │   ├── manifest.json                   # Capability Definitions
    │   ├── plugin.py                       # The Implementation (Async)
    │   └── models.py                       # Pydantic Input/Output Schemas
    │
    └── custom_plugin\                      # Standard V2 Structure
        ├── manifest.json
        ├── plugin.py
        ├── models.py
        └── services.py                     # Optional: Logic separation
```

## 2. File Responsibilities

### `framework/contract.py`
*   **Must Have**: `PluginInterface` (ABC), `ExecutionContext` (Dataclass).
*   **Rule**: Minimal imports. Strictly abstracts.

### `framework/types.py`
*   **Must Have**: `PluginCapability` (Generic Pydantic Model), `HealthStatus`.
*   **Rule**: All schemas used by the Kernel to validate plugins go here.

### `core/manager_v2.py`
*   **Responsibility**: The logic that loads `plugins/`, creates `Sandbox`, validates `manifest.json` against `framework/types.py`, and manages the Lifecycle (`on_load`, `on_ready`).

### `plugins/<name>/plugin.py`
*   **Standard**: Must import from `a2ui_integration.framework`.
*   **Format**: `class <Name>Plugin(PluginInterface):`

## 3. Namespace Strategy
*   **Framework**: `a2ui_integration.framework` (The "SDK" for plugin devs).
*   **Runtime**: `a2ui_integration.core` (The "Server" code).
*   **CLI**: `a2ui_integration.cli` (The "Tooling").

## 4. Implementation Order (Issues)
1.  **#85**: Create `a2ui_integration/framework/*`
2.  **#86**: Create `a2ui_integration/core/manager_v2.py`
3.  **#87**: Create `a2ui_integration/cli/*`
4.  **#88**: Create `plugins/email/*` (Porting existing logic)
