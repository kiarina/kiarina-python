# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-09-25

### Changed
- No changes

## [1.1.1] - 2025-09-11

### Changed
- No changes

## [1.1.0] - 2025-09-11

### Changed
- No changes

## [1.0.1] - 2025-09-11

### Changed
- No changes - version bump for consistency with other packages

## [1.0.0] - 2025-09-09

### Added
- Initial release of kiarina-lib-redis
- Redis client with configuration management using pydantic-settings-manager
- Connection pooling and caching
- Retry mechanism for connection failures
- Support for both sync and async operations
- Type safety with full type hints and Pydantic validation
- Environment variable configuration support
- Runtime configuration overrides
- Multiple named configurations support

### Dependencies
- redis>=6.4.0
- pydantic-settings>=2.10.1
- pydantic-settings-manager>=2.1.0
