# Changelog

All notable changes to the kiarina meta-package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **kiarina-lib-google-auth**: Improved test configuration using YAML-based settings file with pydantic-settings-manager
- **All packages**: Updated `pydantic-settings-manager` dependency from `>=2.1.0` to `>=2.3.0`

## [1.6.2] - 2025-10-10

### Changed
- **kiarina-lib-google-cloud-storage**: Improved blob name handling with `blob_name_pattern` supporting template patterns with placeholders

## [1.6.1] - 2025-10-10

### Changed
- Added `kiarina-lib-cloudflare-d1>=1.6.0` to dependencies

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
- Initial meta-package release
- Provides convenient installation of all kiarina packages via `pip install kiarina`
- Includes all core packages: kiarina-utils-common, kiarina-utils-file, kiarina-llm, kiarina-lib-redis, kiarina-lib-falkordb, kiarina-lib-redisearch
