# Changelog

All notable changes to kiarina-lib-firebase-firestore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- `get_document` and `list_documents` use the default of `token_manager_registry` when `firebase_token_manager_name` is not configured

## [2.23.0] - 2026-08-20

### Added
- `firebase_token_manager_name` setting, used to get a `TokenManager` from `token_manager_registry` when no token is passed

### Changed
- **BREAKING**: `get_document` and `list_documents` take `id_token` as an optional keyword argument

## [2.20.0] - 2026-07-28

### Added

- Add `get_document()` for retrieving a Cloud Firestore document with a Firebase ID token
- Add `list_documents()` for listing collection documents with pagination
- Add `DocumentSnapshot` / `DocumentList` schemas with Firestore value decoding
- Add `FirestoreSettings` for configuring the REST endpoint and timeout
