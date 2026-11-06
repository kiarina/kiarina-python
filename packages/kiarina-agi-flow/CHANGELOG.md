# Changelog

All notable changes to the kiarina-agi-flow package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.37.0] - 2026-11-06

### Changed
- Move custom section resizing to `BaseSection._resize()`. The public `resize()` wrapper always invalidates cached estimates; `HistorySection` and `FileInfoSection` use the hook. Subclasses overriding `resize()` must migrate to `_resize()`.
- Report fixed-section capacity failures as `TokenOverflowError` with the effective local limit, matching exhausted resizable sections.

### Fixed
- Keep the original prompt limits unchanged during local resize iterations while retaining provider token-count calibration. Overflow responses without reported counts reduce the current allowance.
- Exhaust empty-file history pools instead of leaving `is_resizable()` true indefinitely. No no-progress or resize-count cutoff is imposed by the prompt.

## [2.11.0] - 2026-07-09

### Added
- Add the `kiarina-agi-flow` package.
