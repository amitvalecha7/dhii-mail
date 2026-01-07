# Plugin Framework 2.0 Architecture Specification

> **Goal**: Establish a production-grade, async-native, strongly-typed plugin system for Dhii-Mail, enabling safe and scalable extension.

## 1. Core Principles
1.  **Async-First**: All I/O operations must be non-blocking `async/await`.
2.  **Type Safety**: Use Pydantic for all input/output schemas (Design-by-Contract).
3.  **Resilience**: Built-in retries, circuit breakers, and error handling.
4.  **Observability**: Telemetry and health checks are first-class citizens.
5.  **Safety**: Strict resource limits and sandboxing.

---

## 2. Core Abstractions

### 2.1 The Plugin Contract (`a2ui_integration.core.plugin_contract`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from dataclasses import dataclass, field
import asyncio

@dataclass
class ExecutionContext:
    request_id: str
    user_id: Optional[str]
    timeout: float = 30.0
    cancellation_token: asyncio.Event = field(default_factory=asyncio.Event)

class PluginInterface(ABC):
    """The Protocol all plugins must implement."""

    # --- Lifecycle ---
    async def on_load(self, config: Dict[str, Any]): ...
    async def on_ready(self): ...
    async def on_unload(self): ...
    async def health_check(self) -> 'HealthStatus': ...

    # --- Capabilities ---
    @property
    @abstractmethod
    def capabilities(self) -> List['PluginCapability']: ...

    # --- Execution ---
    @abstractmethod
    async def execute_capability(
        self, 
        capability_id: str, 
        params: Dict[str, Any],
        context: Optional[ExecutionContext] = None
    ) -> Any: ...
```

### 2.2 Capability Definition (Pydantic-Powered)

```python
from typing import Type, Generic, TypeVar
T = TypeVar('T', bound=BaseModel)
U = TypeVar('U', bound=BaseModel)

class PluginCapability(BaseModel, Generic[T, U]):
    id: str
    name: str
    description: str
    input_model: Type[T]
    output_model: Type[U]
    
    # Metadata
    tags: List[str] = []
    requires_auth: bool = True
    rate_limit: int = 100 # RPM

    @property
    def input_schema(self) -> Dict[str, Any]:
        return self.input_model.model_json_schema()
```

### 2.3 Error Taxonomy (`a2ui_integration.core.exceptions`)
*   `PluginError` (Base)
    *   `PluginConfigurationError` (Fatal)
    *   `PluginAuthenticationError` (User Action)
    *   `PluginNetworkError` (Retryable)
    *   `PluginValidationError` (Bad Request)

---

## 3. Kernel Services Enhancement

### 3.1 Plugin Manager
*   **Discovery**: Scan `plugins/` directory for `manifest.json`.
*   **Dependency Resolution**: Ensure `imports` are met.
*   **Sandboxing**: Load modules with restricted `sys.modules` access.
*   **Lifecycle**: Call `on_load` -> `on_ready`.

### 3.2 Telemetry Wrapper
All plugins are wrapped in an `InstrumentedPlugin` proxy that:
1.  Starts an OpenTelemetry span.
2.  Records duration and success/failure metrics.
3.  Logs execution context.

### 3.3 Retry & Circuit Breaker
*   Kernel applies `RetryPolicy` (Exponential Backoff) for `PluginNetworkError`.
*   Kernel tracks failure rates; if specific plugin > 50% fails, open circuit (fail fast).

---

## 4. Developer Experience (DX)

### 4.1 CLI Tools
*   `dhii plugin create <name>`: Scaffolds a new plugin from template.
*   `dhii plugin validate <path>`: static checks for manifest and contract compliance.
*   `dhii plugin bundle <path>`: Packs plugin for registry.

### 4.2 Template
Standard template includes:
- `plugin.py` (Implementation)
- `manifest.json` (Metadata)
- `requirements.txt` (Dependencies)
- `README.md` (Docs)

---

## 5. Migration Strategy
1.  **Phase 1**: Implement Core Core (Contract, Exceptions, Types).
2.  **Phase 2**: Update Kernel PluginManager to support v2 interface.
3.  **Phase 3**: Create `LegacyAdapter` to run existing plugins inside v2.
4.  **Phase 4**: Refactor `Email` and `Calendar` to native v2.
