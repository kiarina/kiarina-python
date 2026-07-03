# Changelog

All notable changes to the kiarina-utils-app package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Export the shared `App` type and `app` instance.

## [2.3.0] - 2026-07-01

### Added
- Initial release of `kiarina-utils-app`.
- `configure()` / `reset()` for setting the application identity (name and author) at startup, raising `AppAlreadyConfiguredError` on reconfiguration and `AppNotConfiguredError` when accessed before configuration.
- `user_directory` service: `get_user_cache_dir()`, `get_user_config_dir()`, and `get_user_data_dir()`, honoring `XDG_*` environment variables on all platforms with `platformdirs` fallbacks and settings overrides.
- `single_instance` service: `acquire()` / `release()` for OS-level single-instance control, raising `AlreadyRunningError` when another instance is already running.
- Public exports for `AppSettings` and `settings_manager`.
