# Changelog

All notable changes to the kiarina-agi-file package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.8.0] - 2026-07-08

### Changed
- Update `GCSAssetRepository` to use `get_cloud_options` from `kiarina-lib-google`.

## [2.6.0] - 2026-07-03

### Changed
- Move public modules from `kiarina.agi.file` to `kiarina.agi`.
- Import shared AI agent utilities from `kiarina.agi`.

## [2.5.0] - 2026-07-03

### Added
- Add local and cloud asset repositories, caching, and file resolution for AI agents.

### Changed
- Align service modules and mirrored tests with Crystal Architecture responsibilities.
- Make Google Cloud Storage support optional through the `asset-repository-gcs` extra.

### Fixed
- Keep GCS test settings untracked and skip integration tests when settings or credentials are unavailable.

## [2.4.0] - 2026-07-03

### Added
- Add local and cloud asset repositories, asset caching, and file resolution for AI agents.
