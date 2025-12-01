# Changelog

All notable changes to kiarina-lib-anthropic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release with Anthropic API configuration management
- `AnthropicSettings` class with API key and base URL support
- API key protection using `SecretStr`
- Multiple configuration support via `pydantic-settings-manager`
- Environment variable configuration with `KIARINA_LIB_ANTHROPIC_` prefix
- Custom base URL support for Anthropic-compatible APIs
