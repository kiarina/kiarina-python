# Changelog

All notable changes to the kiarina-agi-text package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add the `kiarina-agi-text` package.

### Changed
- Add the GPT-5.5 chat model preset and remove obsolete OpenAI presets.
- Select chat model helper tests through `KIARINA_AGI_TEXT_TEST_CHAT_MODEL`, default to the mock model, configure verbose parallel retries and timeouts, use a smaller text fixture, and hide unsupported chat model presets.

## [2.6.0] - 2026-07-03

### Added
- Add chat logging, chat models, chat providers, and text embedding APIs.
- Add optional Anthropic, Google, OpenAI, and mock implementations.
