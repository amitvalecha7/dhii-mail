# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Kernel and Shared Services integration in main.py
- Plugin architecture foundation with complete API endpoints
- Kernel management endpoints: `/kernel/plugins`, `/kernel/plugins/install`, `/kernel/status`
- Enhanced kernel with proper shared services integration
- Database schema for plugins, capabilities, and dependencies
- Async plugin registration and management functionality
- Status reporting functionality for kernel monitoring
- **Issue #34**: Dynamic plugin discovery via manifest.json files in plugins/* directories
- **Issue #34**: Lazy loading implementation to prevent kernel crashes from missing plugin dependencies
- **Issue #34**: UI route registration from plugin manifests for automatic AppShell integration
- **Issue #34**: Comprehensive test suite (`test_lazy_loading.py`) with 10 test cases covering plugin discovery, dependency checking, and error resilience

### Changed
- Updated main.py to initialize kernel and shared services on startup
- Enhanced kernel implementation with shared services database integration
- Improved error handling and event publishing for plugin operations

### Fixed
- Database schema issues with missing columns in plugins table
- Proper initialization of shared services for plugin architecture
- **Issue #34**: Kernel plugin integration fragility - implemented lazy loading and dynamic discovery to prevent crashes from missing dependencies

### Completed
- **Issue #24**: Structured Logging - Implemented foundation layer with correlation IDs, structured JSON logs, and request/response logging middleware.
- **Issue #25**: Health Monitoring - Implemented production-ready health monitoring with detailed checks for database, external services, and system resources. Added `/health` endpoint with degraded/unhealthy status reporting.
- **Issue #26**: Error Tracking - Implemented centralized error handling with `ErrorHandler` class, standardized `AppError` exceptions, and global exception handler for consistent API error responses.
- **Issue #31**: A2UI Orchestrator Refactor - Implemented adjacency list model (`ComponentGraph`) for A2UI components, optimizing structure for complex UIs. Added performance benchmark (`tests/benchmark_a2ui_graph.py`).
- **Issue #32**: @a2ui/lit Renderer - Modernized frontend client by refactoring `MeetingAssistantClient` into a Lit component (`MeetingAssistantApp.js`), improving state management and encapsulation.
- **Issue #23 (Phase 3)**: APM Integration - Added OpenTelemetry instrumentation foundation (`middleware/apm.py`) for distributed tracing and observability.
- **Issue #23 (Core)**: Build Core Kernel - Added comprehensive kernel API endpoints, monitoring, and health checks
  - Added kernel management endpoints: `/kernel/plugins/{plugin_id}`, `/kernel/plugins/{plugin_id}/enable`, `/kernel/plugins/{plugin_id}/disable`
  - Added capability execution endpoint: `/kernel/capabilities/{capability_id}/execute`
  - Added event management endpoints: `/kernel/events` with filtering support
  - Added search functionality: `/kernel/search` with domain filtering
  - Added monitoring endpoints: `/kernel/health`, `/kernel/metrics`, `/kernel/plugins/{plugin_id}/health`
  - Created comprehensive test suite (`test_kernel_api.py`) with 12 test cases covering all new endpoints
  - Fixed plugin loading and capability execution workflows
- AuthManager token creation failure due to foreign key constraint violations
- AuthManager unification between main.py and auth.py to ensure single instance usage
- User existence validation in auth.py create_token method to prevent invalid token creation
- **Issue #34**: Kernel plugin integration fragility - implemented lazy loading and dynamic discovery to prevent crashes from missing dependencies

## [Previous Versions]

*Note: Previous changelog entries would go here based on git history*