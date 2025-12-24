# Changelog

All notable changes to the kiarina meta-package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.20.1] - 2025-12-25

### Changed
- **kiarina-i18n**: Optimized caching strategy to only cache file I/O operations

## [1.20.0] - 2025-12-19

### Removed
- **kiarina-i18n**: **BREAKING** - Removed `create_pydantic_schema()` function from `kiarina.i18n_pydantic`

## [1.19.0] - 2025-12-19

### Added
- **kiarina-i18n**: `kiarina.i18n_pydantic` subpackage with `create_pydantic_schema()` for creating translated Pydantic model schemas

## [1.18.2] - 2025-12-17

### Added
- **kiarina-i18n**: `translate_pydantic_model()` now translates model `__doc__` (docstring)

## [1.18.1] - 2025-12-16

### Added
- **kiarina-i18n**: `clear_cache()` helper function for i18n cache management

## [1.18.0] - 2025-12-16

### Added
- **kiarina-i18n**: `translate_pydantic_model()` function to translate Pydantic model field descriptions for LLM tool schemas
- **kiarina-i18n**: `get_catalog()` helper function to get translation catalog independently for custom translation logic

### Changed
- **kiarina-i18n**: **BREAKING** - `I18n` class now uses `scope` as a class parameter instead of an instance field

## [1.17.0] - 2025-12-15

### Added
- **kiarina-i18n**: Type-safe class-based I18n API with `I18n` base class and `get_i18n()` function

## [1.16.0] - 2025-12-15

### Added
- **kiarina-i18n**: Initial release of internationalization (i18n) utilities package

## [1.15.1] - 2025-12-14

### Changed
- **kiarina-llm**: Refactored internal module structure and added default values to RunContext fields

## [1.15.0] - 2025-12-13

### Added
- **kiarina-lib-google-auth**: Added API key authentication support

## [1.14.0] - 2025-12-13

### Fixed
- **kiarina-lib-google-auth**: Fixed scope application for service account credentials

## [1.13.0] - 2025-12-09

### Added
- **kiarina-llm**: Add `currency` field to `RunContext` model for currency information management

### Changed
- Update dependencies to latest versions

## [1.12.0] - 2025-12-05

### Changed
- **kiarina-lib-cloudflare-d1**: **BREAKING** - Refactored internal module structure and renamed function parameters for consistency
- **kiarina-lib-falkordb**: Refactored internal module structure following project architecture rules
- **kiarina-lib-google-auth**: Refactored internal module structure and renamed function parameters for consistency
- **kiarina-lib-google-cloud-storage**: Refactored internal module structure and renamed function parameters for consistency
- **kiarina-lib-redis**: Refactored internal module structure and unified sync/async helper implementations
- **kiarina-lib-redisearch**: Renamed function parameters for consistency

## [1.11.2] - 2025-12-02

### Added
- **kiarina-utils-common**: `ConfigStr` type alias for configuration string format documentation

## [1.11.1] - 2025-12-01

### Changed
- **kiarina-lib-anthropic**: Made `api_key` field optional to support environment variable configuration
- **kiarina-lib-openai**: Made `api_key` field optional to support environment variable configuration

## [1.11.0] - 2025-12-01

### Added
- **kiarina-lib-anthropic**: New package for Anthropic API integration with secure API key management and multi-configuration support
- **kiarina-lib-openai**: New package for OpenAI API integration with secure API key management and multi-configuration support

### Changed
- **kiarina-lib-anthropic**: Add environment variable prefix `KIARINA_LIB_ANTHROPIC_` for settings
- **kiarina-lib-cloudflare-auth**: Add environment variable prefix `KIARINA_LIB_CLOUDFLARE_AUTH_` for settings
- **kiarina-lib-cloudflare-d1**: Add environment variable prefix `KIARINA_LIB_CLOUDFLARE_D1_` for settings
- **kiarina-lib-google-cloud-storage**: Add environment variable prefix `KIARINA_LIB_GOOGLE_CLOUD_STORAGE_` for settings
- **kiarina-lib-openai**: Add environment variable prefix `KIARINA_LIB_OPENAI_` for settings

## [1.10.0] - 2025-12-01

### Added
- **kiarina-utils-common**: `import_object` function for dynamic object importing from import paths (useful for plugin systems)

## [1.9.0] - 2025-11-26

### Changed
- **kiarina-lib-redisearch**: **BREAKING** - Separated schema from settings configuration (schema now passed directly to create_redisearch_client)
- **kiarina-lib-redisearch**: Improved internal code organization by restructuring modules and removing redundant code

## [1.8.0] - 2025-10-24

### Changed
- **kiarina-lib-falkordb**: Updated `kiarina-falkordb` dependency from `>=1.2.0` to `>=1.3.0`

## [1.7.0] - 2025-10-21

### Added
- **Project**: Added coverage support to package test tasks with `--coverage` flag
- **kiarina-utils-file**: Added TypeScript MIME type mapping for `.ts` extension

### Changed
- **kiarina-lib-google-auth**: Simplified credentials retrieval and caching logic in user account credentials handling
- **kiarina-lib-cloudflare-d1**: Improved D1 tests with better error handling and added sample environment files
- **Project**: Improved package test tasks with smarter module detection
- **Dependencies**: Updated project dependencies

## [1.6.3] - 2025-10-13

### Added
- **Project**: Added `upgrade` task for dependency management with optional sync

### Changed
- **kiarina-lib-google-auth**: Improved test configuration using YAML-based settings file with pydantic-settings-manager
- **kiarina-lib-google-cloud-storage**: Converted tests from mock-based to real integration tests with multi-tenancy patterns
- **kiarina-lib-google-cloud-storage**: Simplified test settings loading using `load_user_configs`
- **All packages**: Updated `pydantic-settings-manager` dependency from `>=2.1.0` to `>=2.3.0`
- **All packages**: Refactored to use `settings_manager.get_settings` instead of deprecated `get_settings_by_key`
- **Documentation**: Improved bootstrap pattern documentation and updated development workflow with mise
- **Documentation**: Added documentation management flow playbook
- **Documentation**: Translated task list instruction to English

### Fixed
- **kiarina-lib-google-cloud-storage**: Added sample env and test settings files for easier setup

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
