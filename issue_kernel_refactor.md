### Summary
The current `kernel_plugin_integration.py` performs eager loading of all plugins, which causes the entire kernel to crash if a single dependency is missing (as seen with `aiohttp`). It also hardcodes plugin registration, violating the "Plug-and-Play" vision.

### Drivers
- **Product Feedback Report**: `docs/architecture/PRODUCT_FEEDBACK_REPORT.md`
- **Severity**: High (Stability & Extensibility)

### Scope
1.  **Lazy Loading**: Change `_register_x_plugin` to import dependencies *inside* the method or use `importlib`. Wrap in `try/except` to prevent Kernel crashes.
2.  **Dynamic Discovery**: Implement a filesystem scanner that looks for `manifest.json` in `plugins/*`.
3.  **UI Integration**: Parse `ui_routes` from the manifest and register them with the AppShell.

### Deliverables
- [ ] Refactored `KernelPluginIntegration` class.
- [ ] `test_lazy_loading.py` to verify resilience.

### Assignee
- **Core Architect (Agent A)**
