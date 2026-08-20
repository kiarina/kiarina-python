# Changelog

All notable changes to kiarina-lib-firebase-rtdb will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Renamed the `firebase_token_manager_name` setting to `firebase_settings_key`

## [2.24.0] - 2026-08-21

### Changed
- `get_data`, `update_data`, and `watch_data` use the default of `token_manager_registry` when `firebase_token_manager_name` is not configured

## [2.23.0] - 2026-08-20

### Added
- `firebase_token_manager_name` setting, used to get a `TokenManager` from `token_manager_registry` when no token is passed

### Changed
- **BREAKING**: `get_data` and `update_data` take `id_token` as an optional keyword argument, and `update_data` takes `values` as its third positional argument
- **BREAKING**: `watch_data` takes `token_manager` as an optional keyword argument

## [2.22.0] - 2026-08-14

### Added
- `RTDBQuery` builds and JSON-encodes the REST query parameters, and `get_data` accepts it through the new `query` keyword argument
- `update_data` applies a multi-path update, deleting the keys whose value is `None`

### Fixed
- `watch_data` no longer exits when the token refresh triggered by `auth_revoked` fails; transient failures now go through the exponential backoff, and only unrecoverable errors such as `InvalidRefreshTokenError` are propagated
- `watch_data` now backs off when `auth_revoked` arrives before any event, instead of reconnecting in a tight loop

## [2.3.1] - 2026-07-02

### Changed
- Improved the package documentation and simplified comments and docstrings
- Replaced the obsolete `kiarina-lib-firebase-auth` dependency with `kiarina-lib-firebase`

## [2.1.0] - 2026-06-22

### Changed
- No changes

## [2.0.0] - 2026-06-10

### Changed
- Renamed internal module structure from `kiarina.lib.firebase.rtdb` to `kiarina.lib.firebase_rtdb`
- Updated dependency from `kiarina-lib-firebase-auth` to `kiarina-lib-firebase`
- Updated settings key to `kiarina.lib.firebase_rtdb`

## [1.37.0] - 2026-05-27

### Changed
- No changes

## [1.35.0] - 2026-01-31

### Changed
- No changes

## [1.34.0] - 2026-01-31

### Changed
- Updated to use `kiarina-lib-firebase-auth>=1.33.0` with new `TokenData` schema and keyword-only `TokenManager` initialization

## [1.33.1] - 2026-01-31

### Changed
- No changes

## [1.33.0] - 2026-01-31

### Added
- Initial release with Firebase Realtime Database REST API integration
- `get_data()` function for retrieving data from Firebase RTDB
- `watch_data()` function for real-time data watching with Server-Sent Events
- `DataChangeEvent` schema for representing data change events
- `RTDBStreamCancelledError` exception for stream cancellation handling
- Automatic ID token refresh via `TokenManager` integration
- Network error handling with exponential backoff retry
- Configurable retry settings via `RTDBSettings`
- Comprehensive test suite with Firebase Admin SDK integration
- Example script for testing watch functionality
