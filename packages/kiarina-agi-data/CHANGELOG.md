# Changelog

All notable changes to the kiarina-agi-data package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Replace broad `Any` annotations in package tests with concrete types.

## [2.6.0] - 2026-07-03

### Added
- Add messages, events, embeddings, file metadata, and related data models for AI agents.

### Changed
- Align internal modules and mirrored tests with Crystal Architecture responsibilities.
- Move public modules from `kiarina.agi.data` to `kiarina.agi`.
- Import AI agent file APIs directly from `kiarina.agi`.
- Import shared AI agent utilities from `kiarina.agi`.
- Correct test fixture type annotations.
