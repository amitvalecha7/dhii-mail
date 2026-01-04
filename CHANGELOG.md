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
- AuthManager token creation failure due to foreign key constraint violations
- AuthManager unification between main.py and auth.py to ensure single instance usage
- User existence validation in auth.py create_token method to prevent invalid token creation
- **Issue #34**: Kernel plugin integration fragility - implemented lazy loading and dynamic discovery to prevent crashes from missing dependencies

## [Previous Versions]

*Note: Previous changelog entries would go here based on git history*