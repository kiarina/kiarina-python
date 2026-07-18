# Changelog

All notable changes to the kiarina-python project will be documented in this file.

This file contains the overall project changes. For package-specific changes, see the CHANGELOG.md in each package directory.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **kiarina**: Add the `all` extra that installs every bundled package with its own `all` extra enabled.
- **kiarina-agi-file**: Add the `all` extra that installs every optional dependency.

## [2.15.0] - 2026-07-14

### Added
- **kiarina-agi-image**: Add kiapi image generation with Flux2, Qwen, and ERNIE families.
- **kiarina-agi-image**: Add image segmentation APIs, BiRefNet ONNX and mock providers, and a background removal helper.
- **kiarina-agi-image**: Add OCR APIs with RapidOCR and mock providers.
- **kiarina-agi-video**: Add a kiapi video generation provider with the LTX-2 family.

### Changed
- **kiarina-agi-data-builder, kiarina-agi-video**: Replace MoviePy with direct FFmpeg processing through imageio-ffmpeg.
- **kiarina-agi-audio**: Replace pydub and ffprobe-dependent TTS audio processing with direct FFmpeg processing through imageio-ffmpeg.

## [2.14.0] - 2026-07-10

### Added
- **kiarina-agi-runner**: Add agent execution, task runner, and structured output helper APIs for AI agents.

## [2.13.0] - 2026-07-10

### Added
- **kiarina-agi-data-builder**: Add builders for AI agent messages, events, histories, tools, files, and file segments.

## [2.12.0] - 2026-07-10

### Added
- **kiarina-agi-tool**: Add tool execution, hooks, and tool logging APIs for AI agents.

## [2.11.0] - 2026-07-09

### Added
- **kiarina-agi-flow**: Add prompt, section, state, and workflow orchestration APIs for AI agents.

## [2.10.0] - 2026-07-09

### Added
- **kiarina-agi-video**: Add video sources and video generation APIs for AI agents.

### Changed
- **kiarina-agi-video**: Remove the OpenAI video generation provider.

## [2.9.0] - 2026-07-09

### Added
- **kiarina-agi-audio**: Add audio sources, speech, tagging, embeddings, and voice activity APIs for AI agents.

### Changed
- **kiarina-agi-audio**: Mark model download tests explicitly, skip them on GitHub Actions, and document pytest marker usage.
- **kiarina-agi-image**: Mark local model download tests explicitly and skip them on GitHub Actions.

### Fixed
- **kiarina-agi-audio**: Add the Python 3.13 `audioop` compatibility dependency for TTS providers.
- **kiarina-agi-audio**: Skip microphone source tests when PortAudio is unavailable.
- **kiarina-agi-audio**: Avoid external credentials and missing CI assets in audio provider tests.

## [2.8.0] - 2026-07-08

### Added
- **kiarina-lib-google**: Add `get_cloud_options` helper for dynamic Google Cloud client configuration

### Changed
- **kiarina-agi-file**: Update `GCSAssetRepository` to use `get_cloud_options`
- **kiarina-agi-text**: Update `LCAnthropicVertexChatProvider` to use `get_cloud_options`
- **kiarina-agi-image**: Add concrete type annotations to package tests and remove mypy suppressions.
- **kiarina-agi-image**: Add explicit costly image test shortcuts and VS Code pytest settings.
- **kiarina-lib-google, kiarina-agi-image, kiarina-agi-text**: Centralize Google Gen AI client options in `kiarina-lib-google` and remove provider-local backend settings.

## [2.7.0] - 2026-07-06

### Added
- **kiarina-agi-text**: Add chat, logging, and text embedding APIs for AI agents.

### Changed
- **kiarina-agi-base**: Default run context identifiers to `default` and add an option to require explicit identifiers.
- **kiarina-agi-data**: Replace broad `Any` annotations in package tests with concrete types.
- **kiarina-agi-text**: Add an `all` extra and consolidate optional dependency documentation.
- **kiarina-agi-text**: Add concrete type annotations to package tests and remove file-wide mypy suppressions.
- **kiarina-agi-text**: Add the GPT-5.5 chat model preset and remove obsolete OpenAI presets.
- **kiarina-agi-text**: Select chat model helper tests through `KIARINA_AGI_TEXT_TEST_CHAT_MODEL`, default to the mock model, configure verbose parallel retries and timeouts, use a smaller text fixture, and hide unsupported chat model presets.
- **kiarina-agi-text**: Show the selected chat model in pytest output and load package test variables from `.env.vscode` in VS Code.
- **kiarina-agi-text**: Move manually run chat and token overflow checks from skipped tests to package scripts.
- **kiarina-agi-text**: Enable targeted costly tests through `KIARINA_TEST_COSTLY`, the test task, and package Make shortcuts.
- Include package `scripts` directories in formatting, linting, and type checking.
- Add opt-in pytest arguments for package tests through `packages/<package>/tests/.pytest-args`.
- Add AI agent packages to the VS Code workspace.
- Standardize package README optional dependency tables and `all` extra installation guidance.

### Fixed
- **kiarina-agi-text**: Allow chat helpers to create a run context when one is not provided.

## [2.6.0] - 2026-07-03

### Added
- **kiarina-agi-data**: Add messages, events, embeddings, file metadata, and related data models for AI agents.

### Changed
- **kiarina-agi-data**: Align internal modules and mirrored tests with Crystal Architecture responsibilities.
- **kiarina-agi-data**: Move the `kiarina.agi.data` public modules directly under `kiarina.agi`.
- **kiarina-agi-file, kiarina-agi-data**: Move the `kiarina.agi.file` public modules directly under `kiarina.agi`.
- **kiarina-agi-base, kiarina-agi-data, kiarina-agi-file**: Move the `kiarina.agi.base` public modules directly under `kiarina.agi`.
- **kiarina-agi-data**: Correct test fixture type annotations.
- Run mypy against package tests and add the required test type annotations.

## [2.5.0] - 2026-07-03

### Added
- **kiarina-agi-file**: Add local and cloud asset repositories, caching, and file resolution for AI agents.

### Changed
- **kiarina-agi-base**: Align internal modules and mirrored tests with Crystal Architecture responsibilities.
- **kiarina-agi-file**: Align service modules and mirrored tests with Crystal Architecture responsibilities.
- **kiarina-agi-file**: Make Google Cloud Storage support optional through the `asset-repository-gcs` extra.
- Document the optional dependency policy for implementation packages.

### Fixed
- **kiarina-agi-file**: Keep GCS test settings untracked and skip integration tests when settings or credentials are unavailable.

## [2.4.0] - 2026-07-03

### Added
- **kiarina-agi-base**: Add core contexts, cost and request logging, recording, and token utilities for AI agents.

### Changed
- **kiarina-agi-base**: Remove empty internal package initializers.
- **kiarina-utils-app**: Export the shared `App` type and `app` instance.

## [2.3.1] - 2026-07-02

### Changed
- Streamline the repository README files and organize the package catalog, installation, development, and documentation guidance.
- Standardize README headers so status badges appear before language links.
- Replace the duplicate Test Settings runbook with a reference to `kiarina/test-settings`.
- **kiarina**: Streamline the meta-package README and document all included packages as dependencies.
- **kiarina-currency, kiarina-lib-firebase**: Improve package documentation, comments, docstrings, and settings metadata.
- **kiarina-i18n, kiarina-utils-file**: Expand and refine package documentation and simplify comments and docstrings.
- **kiarina-lib-cloudflare-d1**: Improve documentation, comments, and docstrings, and fix lazy imports for settings from the asynchronous API.
- **kiarina-lib-firebase-rtdb**: Improve documentation, simplify comments and docstrings, and replace the obsolete `kiarina-lib-firebase-auth` dependency.
- **kiarina-lib-google**: Clarify settings metadata, streamline comments and docstrings, and document ADC credential search order and all settings fields.
- **kiarina-lib-redis**: Clarify settings metadata, streamline comments and docstrings, and document all public APIs and client behavior.
- **kiarina-lib-redisearch**: Remove empty internal package initializers, improve documentation, and add metadata to public Pydantic fields.
- **kiarina-lib-anthropic, kiarina-lib-cloudflare, kiarina-lib-falkordb, kiarina-lib-openai, kiarina-lib-slack**: Clarify settings metadata, streamline comments and docstrings, and document all public APIs and configuration behavior.

## [2.3.0] - 2026-07-01

### Added
- **kiarina-utils-app**: Add a new package providing application foundation utilities: startup identity configuration (`configure()` / `reset()`), user directory resolution (`user_directory`) honoring `XDG_*` on all platforms with `platformdirs` fallbacks, and single-instance control (`single_instance`) via an OS-level file lock.
- Add `test-settings:resolve_gcs_uri` and `test-settings:delete` mise tasks. `resolve_gcs_uri` derives the storage prefix from the `origin` remote and `TEST_SETTINGS_BUCKET_NAME`/`TEST_SETTINGS_PROJECT_ID`, and `delete` removes all encrypted objects under that prefix.

### Changed
- Enable the Ruff `I` (isort) lint rule across the workspace and sort all imports accordingly. Configure isort with `known-first-party = ["kiarina"]` and `combine-as-imports = true` to keep first-party imports in their own group and preserve combined aliased imports.
- Enable the Ruff `UP` (pyupgrade) lint rule across the workspace. Modernize type annotations to PEP 585/604 builtins (`list`/`dict` and `X | Y`), move `Awaitable`/`Callable` imports to `collections.abc`, drop redundant `.encode("utf-8")` arguments, and convert a `str.format()` call to an f-string.
- Enable the Ruff `RUF` (ruff-specific) lint rule across the workspace, ignoring `RUF022` to preserve intentional comment-based grouping in `__all__`. Annotate class-constant lookup tables as `ClassVar` (`RUF012`), reposition `# fmt: off`/`# fmt: on` to valid statement-level locations so they keep protecting hand-formatted `parametrize` tables (`RUF028`), escape regex metacharacters in `pytest.raises(match=...)` patterns (`RUF043`), replace an ambiguous `×` with `x` in a comment (`RUF003`), and remove an unused `noqa` directive (`RUF100`).
- Enable the Ruff `W` (pycodestyle warnings) lint rule across the workspace and strip trailing whitespace from blank lines (`W293`), including inside a docstring and the `# fmt: off`-protected `parametrize` tables.
- Enable the Ruff `B` (flake8-bugbear) lint rule across the workspace. Chain re-raised exceptions with `raise ... from e` (`B904`), narrow blind `pytest.raises(Exception)` assertions to `pydantic.ValidationError` (`B017`), and bind property-access expressions that exist only to trigger an error to `_` (`B018`).
- Enable the Ruff `C4` (flake8-comprehensions) and the remaining `E` (pycodestyle errors) lint rules across the workspace, completing the linting ruleset; no code changes were required.
- **kiarina-lib-google**: Restructure the package README, correct configuration examples, document all public APIs, and add a service integration pattern.
- Rework the `test-settings:upload`/`test-settings:download` mise tasks to derive the GCS URI from `resolve_gcs_uri`, read age keys from a local key file, encrypt to every recipient in the key file, and accept arbitrary file names to upload.
- Convert the repository root into a uv virtual workspace by removing the non-distributable `[project]` table from the root `pyproject.toml`. The repository version is now tracked in a `VERSION` file, read and written by the `package:list` and `pyproject:bump-version` tasks.

### Changed (BREAKING)
- **kiarina-utils-common**: Rename the public `ConfigStr` type alias to `ConfigString`.

## [2.2.1] - 2026-06-25

### Added
- **kiarina-lib-google**: Add `CredentialsJSONString` and `SelfSignedJWT` type aliases to clarify string-based API contracts.

### Changed (BREAKING)
- **kiarina-lib-google**: Change the default OAuth scopes to an empty list, reuse stored user-account scopes when none are specified, and require explicit scopes for service account impersonation.

## [2.2.0] - 2026-06-24

### Added
- **kiarina-utils-common**: Add a component registry with aliases, presets, custom import paths, runtime registration, and configuration string resolution.
- **kiarina-utils-common**: Add a config registry with aliases, presets, runtime registration, immutable resolution, and Pydantic model support.
- **kiarina-utils-common**: Add an object registry with configuration-based creation, aliases, runtime registration, and cached object resolution.
- Add `test-settings:upload` and `test-settings:download` mise tasks for sharing age-encrypted `.env` and `test_settings.yaml` files through private Google Cloud Storage.
- Add a Test Settings runbook covering age key generation, private Cloud Storage setup, IAM, environment configuration, operation, and key rotation.

### Changed
- **kiarina-utils-common**: Streamline the package README, clarify its description, and document the config, component, and object registry APIs.
- Publish all release packages to PyPI in a single operation instead of treating the `kiarina` meta-package separately.
- Move the test asset download mise task to `test-assets:download`.
- Move package listing and selection mise tasks under the `package:` namespace, and expose release package filtering through `package:list --release`.
- Release only packages whose version matches the release version, while always updating the `kiarina` meta-package.
- Select the package before the task in the interactive `package` mise workflow.

## [2.1.0] - 2026-06-22

### Changed
- **kiarina-i18n**: Change `get_system_language()` return type annotation to `Language`.
- **kiarina-i18n**: Allow `get_i18n()` to omit `language` and automatically use `get_system_language()`.
- **kiarina-i18n**: Allow `get_i18n()` to accept regular Pydantic `BaseModel` classes and derive their scope from the public module path.
- **kiarina-i18n**: Move the module-level `catalog` singleton into the `_instances` layer.
- Add a `package` mise task and `make package` shortcut for choosing package workflows with fzf.
- Allow `package:*` mise tasks to select a package with fzf when no package name is provided.
- Rename the setup mise tasks to `setup` and `download-test-assets`.
- Replace the `setup:upgrade` mise task with the `make upgrade` shortcut for dependency upgrades.
- Move setup, dependency upgrade, changelog, and version mise tasks under namespaced task groups.
- Move shared test files from tracked `tests/data` paths to downloaded `tests/assets` paths.
- Move all-package mise tasks under the `all:` namespace and expose Makefile shortcuts for common workflows.
- Rename the root mise default task to `check` for a clearer verification command.
- Rename the package mise default task to `package:check` for explicit package verification.
- Merge the mise `lint-fix` task into `format` and the `typecheck` task into `lint`.
- Add an optional `--unsafe` flag to mise `format` tasks for applying Ruff unsafe fixes.

## [2.0.0] - 2026-06-10

### Changed (BREAKING)
- **kiarina-lib-cloudflare**: Renamed package from `kiarina-lib-cloudflare-auth` to `kiarina-lib-cloudflare`. The python module `kiarina.lib.cloudflare.auth` has been simplified to `kiarina.lib.cloudflare`. `CloudflareAuthSettings` has been renamed to `CloudflareSettings`, and the environment variable prefix `KIARINA_LIB_CLOUDFLARE_AUTH_` has been changed to `KIARINA_LIB_CLOUDFLARE_`.
- **kiarina-lib-cloudflare-d1**: The python module `kiarina.lib.cloudflare.d1` has been changed to `kiarina.lib.cloudflare_d1`.
- **kiarina-lib-google**: Renamed package from `kiarina-lib-google-auth` to `kiarina-lib-google`. The python module `kiarina.lib.google.auth` has been simplified to `kiarina.lib.google`. `GoogleAuthSettings` has been renamed to `GoogleSettings`, and the environment variable prefix `KIARINA_LIB_GOOGLE_AUTH_` has been changed to `KIARINA_LIB_GOOGLE_`.
- **kiarina-lib-firebase**: Renamed package from `kiarina-lib-firebase-auth` to `kiarina-lib-firebase`. The python module `kiarina.lib.firebase.auth` has been simplified to `kiarina.lib.firebase`. `FirebaseAuthSettings` has been renamed to `FirebaseSettings`, and the environment variable prefix `KIARINA_LIB_FIREBASE_AUTH_` has been changed to `KIARINA_LIB_FIREBASE_`.
- **kiarina-lib-firebase-rtdb**: The python module `kiarina.lib.firebase.rtdb` has been changed to `kiarina.lib.firebase_rtdb`. Environment variable prefix `KIARINA_LIB_FIREBASE_RTDB_` remains the same.

### Removed
- **kiarina-lib-atlassian**: Package removed from monorepo
- **kiarina-llm**: Package removed from monorepo
- **kiarina-lib-google-cloud-storage**: Package removed from monorepo

## [1.37.0] - 2026-05-27

### Added
- **kiarina-utils-common**: Add `brackets` parameter to `parse_config_string` for embedding nested specifier strings

### Changed (BREAKING)
- **kiarina-utils-common**: `parse_config_string` default separators changed to `"&"` / `"="` (was `","` / `":"`)

### Fixed
- **kiarina-lib-redisearch**: Handle `SEARCH_INDEX_NOT_FOUND` error from Redis 8.2+ bundled RediSearch

## [1.36.0] - 2026-02-07

### Added
- **kiarina-lib-atlassian**: Initial release with Atlassian API configuration management

## [1.35.0] - 2026-01-31

### Added
- **kiarina-lib-firebase-auth**: Added `TokenDataCache` protocol for persistent token storage implementations
- **kiarina-lib-firebase-auth**: `TokenManager` now supports `token_data_cache` parameter for automatic token persistence

### Changed
- **kiarina-lib-firebase-auth**: `TokenManager.refresh_token` and `TokenManager.token_data` are now properties that raise `AssertionError` if accessed before initialization

## [1.34.0] - 2026-01-31

### Changed
- **kiarina-lib-firebase-auth**: BREAKING - Renamed `TokenResponse` to `TokenData` with `expires_at` field
- **kiarina-lib-firebase-auth**: BREAKING - Changed `TokenManager` to use keyword-only arguments
- **kiarina-lib-firebase-rtdb**: Updated to use `kiarina-lib-firebase-auth>=1.33.0` with new `TokenData` schema

## [1.33.1] - 2026-01-31

### Fixed
- **kiarina-utils-file**: Fixed type checking errors when reading comment-only YAML files

## [1.33.0] - 2026-01-31

### Added
- **kiarina-lib-firebase-rtdb**: Initial release with Firebase Realtime Database REST API integration and real-time data watching

## [1.32.0] - 2026-01-30

### Added
- **kiarina-lib-firebase-auth**: Initial release with Firebase authentication REST API integration and automatic token management

## [1.31.1] - 2026-01-29

### Changed
- No changes

## [1.31.0] - 2026-01-29

### Added
- **kiarina-lib-slack**: Initial release with Slack API configuration management

## [1.30.0] - 2026-01-27

### Added
- **kiarina-utils-file**: Added `MarkdownContent.from_text()` classmethod for parsing Markdown text with YAML front matter directly from strings

## [1.29.0] - 2026-01-16

### Added
- **kiarina-currency**: Added `get_system_currency()` function for automatic system currency detection from locale settings

## [1.28.0] - 2026-01-16

### Added
- **kiarina-currency**: Initial release of currency exchange rate utilities with pluggable rate provider support

## [1.27.0] - 2026-01-12

### Added
- **kiarina-lib-openai**: Added `to_client_kwargs()` method to `OpenAISettings` for easy conversion to OpenAI client initialization parameters

## [1.26.0] - 2026-01-09

### Added
- **kiarina-i18n**: Added `get_system_language()` helper function for automatic system language detection

## [1.25.1] - 2026-01-08

### Changed
- No changes

## [1.25.0] - 2026-01-08

### Added
- **kiarina-i18n**: Added `add_from_dir()` and `add_from_package()` methods to `Catalog` for loading catalogs from directories and package resources

## [1.24.0] - 2026-01-08

### Changed
- **kiarina-i18n**: **BREAKING** - Catalog management has been completely redesigned with `Catalog` service class

## [1.23.0] - 2026-01-06

### Added
- **kiarina-llm**: Added `with_metadata()` method to `RunContext` for creating new instances with updated metadata

## [1.22.1] - 2026-01-06

### Changed
- **kiarina-lib-google-auth**: Upgraded dependencies and removed unnecessary type ignore comments

## [1.22.0] - 2026-01-05

### Added
- **kiarina-i18n**: Support for translating nested I18n models in `list[I18n]` and `dict[str, I18n]` fields

## [1.21.1] - 2026-01-05

### Fixed
- **kiarina-i18n**: Fixed bug where `default_factory` was lost in `translate_pydantic_model()` during field translation

## [1.21.0] - 2025-12-30

### Added
- **kiarina-llm**: New `kiarina.llm.app_context` subpackage for application-level context management

### Changed
- **kiarina-llm**: Refactored `RunContext` to use `AppContext` for application-level settings

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
- **CI**: Prevent duplicate dependency update PRs by checking for existing open PRs

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
