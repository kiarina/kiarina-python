# Changelog

All notable changes to the kiarina-agi-text package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.28.0] - 2026-09-05

### Changed
- Support OpenAI Python 3.x.
- Support Anthropic Python 1.x.

## [2.22.1] - 2026-08-16

### Changed
- Set the `qwen3.6`, `qwen3.6-fast`, and `qwen3-omni` costs to zero. Local models incur no API charge, and the `lc_openai` provider defaults are not zero.

## [2.19.0] - 2026-07-27

### Added
- Add prefix text for converted file bundle media in chat messages.

### Fixed
- Support OpenAI tiered pricing and prompt cache write costs in cost records.

## [2.17.0] - 2026-07-26

### Changed
- Update chat model presets and aliases for current OpenAI, Anthropic, and Google models.

### Fixed
- Omit the deprecated `temperature` parameter from Claude 5 requests.

## [2.8.0] - 2026-07-08

### Changed
- Update `LCAnthropicVertexChatProvider` to use `get_cloud_options` from `kiarina-lib-google`.
- Use `kiarina-lib-google` to resolve Google Gen AI client options for Google chat and text embedding providers.

## [2.7.0] - 2026-07-06

### Added
- Add the `kiarina-agi-text` package.

### Changed
- Expand the package README with dependencies, installation, usage, configuration, and public API references.
- Add an `all` extra and consolidate optional dependency documentation.
- Add concrete type annotations to package tests and remove file-wide mypy suppressions.
- Add the GPT-5.5 chat model preset and remove obsolete OpenAI presets.
- Select chat model helper tests through `KIARINA_AGI_TEXT_TEST_CHAT_MODEL`, default to the mock model, configure verbose parallel retries and timeouts, use a smaller text fixture, and hide unsupported chat model presets.
- Show the selected chat model in pytest output and load package test variables from `.env.vscode` in VS Code.
- Move manually run chat and token overflow checks from skipped tests to package scripts.
- Enable targeted costly tests through `KIARINA_TEST_COSTLY`, the test task, and package Make shortcuts.

### Fixed
- Allow chat helpers to create a run context when one is not provided.

## [2.6.0] - 2026-07-03

### Added
- Add chat logging, chat models, chat providers, and text embedding APIs.
- Add optional Anthropic, Google, OpenAI, and mock implementations.
