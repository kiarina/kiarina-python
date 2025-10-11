# Changelog

All notable changes to the kiarina-python project will be documented in this file.

This file contains the overall project changes. For package-specific changes, see the CHANGELOG.md in each package directory.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **kiarina-lib-google-auth**: Improved test configuration using YAML-based settings file with pydantic-settings-manager

## [1.6.2] - 2025-10-10

### Changed
- **kiarina-lib-google-cloud-storage**: Improved blob name handling with `blob_name_pattern` supporting template patterns with placeholders

## [1.6.1] - 2025-10-10

### Changed
- **kiarina**: Added `kiarina-lib-cloudflare-d1>=1.6.0` to dependencies

## [1.6.0] - 2025-10-10

### Added
- **kiarina-lib-cloudflare-d1**: Initial release with Cloudflare D1 client library

### Changed
- **kiarina-lib-google-cloud-storage**: **BREAKING** - Separated authentication configuration from storage configuration

## [1.5.0] - 2025-10-10

### Added
- **kiarina-lib-google-cloud-storage**: Initial release with Google Cloud Storage client library

## [1.4.0] - 2025-10-09

### Added
- add project knowledge, playbooks, and runbooks for kiarina-python
- **kiarina-lib-cloudflare-auth**: Initial release with Cloudflare authentication library
- **kiarina-lib-google-auth**: Initial release with Google Cloud authentication library
- **kiarina-utils-file**: Markdown file support with YAML front matter parsing (`read_markdown()` function and `MarkdownContent` type)

### Changed
- **kiarina-lib-cloudflare-auth**: API tokens use `SecretStr` for enhanced credential protection
- **kiarina-lib-falkordb**: **BREAKING** - Changed `url` field to use `SecretStr` for enhanced security
- **kiarina-lib-google-auth**: Credential data fields use `SecretStr` for enhanced protection
- **kiarina-lib-redis**: **BREAKING** - Changed `url` field to use `SecretStr` for enhanced security

## [1.3.0] - 2025-10-05

### Changed
- **kiarina-utils-file**: **BREAKING** - Changed MIME type detection strategy to prioritize file extensions over content analysis
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
- **kiarina**: New meta-package for convenient installation of all kiarina packages via `pip install kiarina`

## [1.0.1] - 2025-09-11

### Fixed
- **kiarina-utils-file**: Fixed file permission preservation in `write_binary()` operations

## [1.0.0] - 2025-09-09

### Added
- Initial project setup with uv workspace
- GitHub Actions CI/CD pipeline
- Multiple kiarina namespace packages:
  - kiarina-utils-common: Common utilities with configuration string parsing
  - kiarina-utils-file: Comprehensive file operation utilities with async support
  - kiarina-llm: LLM-related utilities
  - kiarina-lib-falkordb: FalkorDB integration with configuration management
  - kiarina-lib-redis: Redis integration utilities
  - kiarina-lib-redisearch: RediSearch integration utilities

### Infrastructure
- Comprehensive GitHub Actions workflows (CI, release, dependency updates, security audit)
- Dependabot configuration for automated dependency updates
- Issue and PR templates
- mise-based task management
- uv workspace configuration for monorepo management
- Complete test coverage with pytest
- Type checking with mypy
- Code formatting and linting with ruff

## Package Versions

For detailed changes in each package, see:
- [kiarina-utils-common](./packages/kiarina-utils-common/CHANGELOG.md)
- [kiarina-utils-file](./packages/kiarina-utils-file/CHANGELOG.md)
- [kiarina-llm](./packages/kiarina-llm/CHANGELOG.md)
- [kiarina-lib-falkordb](./packages/kiarina-lib-falkordb/CHANGELOG.md)
- [kiarina-lib-redis](./packages/kiarina-lib-redis/CHANGELOG.md)
- [kiarina-lib-redisearch](./packages/kiarina-lib-redisearch/CHANGELOG.md)
