# Changelog

All notable changes to the kiarina meta-package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **kiarina-utils-file**: Improved `detect_mime_type()` API with `MimeDetectionOptions` TypedDict to reduce cognitive load

### Fixed
- **kiarina-utils-file**: Fixed symbolic link handling in read/write operations

## [1.2.0] - 2025-09-25

### Added
- **kiarina-llm**: Content measurement utilities for LLM-handled content

## [1.1.1] - 2025-01-15

### Changed
- **kiarina-lib-falkordb**: Switched from `falkordb` to `kiarina-falkordb` dependency for better compatibility and maintenance

## [1.1.0] - 2025-09-11

### Added
- Initial meta-package release
- Provides convenient installation of all kiarina packages via `pip install kiarina`
- Includes all core packages: kiarina-utils-common, kiarina-utils-file, kiarina-llm, kiarina-lib-redis, kiarina-lib-falkordb, kiarina-lib-redisearch
