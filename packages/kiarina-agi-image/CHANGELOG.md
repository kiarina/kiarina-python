# Changelog

All notable changes to the kiarina-agi-image package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Mark local model download tests explicitly and skip them on GitHub Actions.

## [2.8.0] - 2026-07-08

### Added
- Add the `kiarina-agi-image` package.
- Add lazy default model downloads for YuNet, D-FINE, SFace, and SigLIP2.
- Add configurable default download metadata for local image providers.

### Changed
- Add concrete type annotations to package tests and remove mypy suppressions.
- Add explicit costly image test shortcuts and VS Code pytest settings.
- Use user cache model downloads in real local provider tests.
- Use `kiarina-lib-google` to resolve Google Gen AI client options for Gemini embedding and Google image generation providers.

## [2.7.0] - 2026-07-06

### Added
- Add image detection, embedding, and generation APIs.
- Add optional D-FINE, Gemini, Google, OpenAI, Qwen3-VL, SFace, SigLIP2, and YuNet implementations.
