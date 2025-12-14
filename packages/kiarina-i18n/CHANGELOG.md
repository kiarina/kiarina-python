# Changelog

All notable changes to kiarina-i18n will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of kiarina-i18n package
- `Translator` class for translation with fallback support
- `get_translator()` function with caching
- Template variable substitution using Python's string.Template
- Configuration management using pydantic-settings-manager
- Support for loading catalog from YAML file
- Type definitions for Language, I18nScope, I18nKey, and Catalog
