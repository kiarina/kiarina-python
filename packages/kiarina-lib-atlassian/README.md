# kiarina-lib-atlassian

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> Atlassian API integration with configuration management using pydantic-settings-manager.

## Purpose

`kiarina-lib-atlassian` provides a simple and secure way to manage Atlassian API credentials (Jira, Confluence, etc.) using pydantic-settings-manager. This library enables the implementation of Atlassian-related functionality by separating and managing API credentials from the application.

## Installation

```bash
pip install kiarina-lib-atlassian
```

## Quick Start

```python
from kiarina.lib.atlassian import settings_manager

# Configure Atlassian credentials
settings_manager.user_config = {
    "jira": {
        "url": "https://your-domain.atlassian.net",
        "username": "your-email@example.com",
        "password": "your-api-token"
    }
}

# Get settings
settings = settings_manager.get_settings("jira")
print(f"Jira URL: {settings.url}")
print(f"Username: {settings.username}")
# Access API token securely
api_token = settings.password.get_secret_value()
```

## API Reference

### AtlassianSettings

Configuration settings for Atlassian API.

**Fields:**
- `url: str` - API endpoint URL (e.g., "https://your-domain.atlassian.net")
- `username: str` - Atlassian account email address
- `password: SecretStr` - Atlassian API token (stored securely)

**Example:**
```python
from pydantic import SecretStr
from kiarina.lib.atlassian import AtlassianSettings

settings = AtlassianSettings(
    url="https://example.atlassian.net",
    username="user@example.com",
    password=SecretStr("your-api-token")
)
```

### settings_manager

Global settings manager instance for Atlassian API configuration.

**Type:** `SettingsManager[AtlassianSettings]`

**Multi-configuration support:** Enabled (can manage multiple Atlassian instances)

**Example:**
```python
from kiarina.lib.atlassian import settings_manager

# Configure multiple instances
settings_manager.user_config = {
    "jira": {
        "url": "https://jira.example.com",
        "username": "jira@example.com",
        "password": "jira-token"
    },
    "confluence": {
        "url": "https://confluence.example.com",
        "username": "confluence@example.com",
        "password": "confluence-token"
    }
}

# Get specific configuration
jira_settings = settings_manager.get_settings("jira")
confluence_settings = settings_manager.get_settings("confluence")
```

## Configuration

### YAML Configuration

```yaml
# config/production.yaml
kiarina.lib.atlassian:
  jira:
    url: "https://your-domain.atlassian.net"
    username: "your-email@example.com"
    password: "${ATLASSIAN_API_TOKEN}"
  
  confluence:
    url: "https://your-domain.atlassian.net"
    username: "your-email@example.com"
    password: "${ATLASSIAN_API_TOKEN}"
```

### Environment Variables

Settings can be configured via environment variables with the prefix `KIARINA_LIB_ATLASSIAN_`:

```bash
export KIARINA_LIB_ATLASSIAN__JIRA__URL="https://your-domain.atlassian.net"
export KIARINA_LIB_ATLASSIAN__JIRA__USERNAME="your-email@example.com"
export KIARINA_LIB_ATLASSIAN__JIRA__PASSWORD="your-api-token"
```

### Bootstrap Pattern

For multi-module applications, use the bootstrap pattern:

```python
# bootstrap.py
import yaml
from pydantic_settings_manager import load_user_configs

def bootstrap():
    with open("config/production.yaml") as f:
        config = yaml.safe_load(f)
    load_user_configs(config)

# main.py
from bootstrap import bootstrap
from kiarina.lib.atlassian import settings_manager

bootstrap()
settings = settings_manager.get_settings("jira")
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=kiarina.lib.atlassian --cov-report=html
```

## Dependencies

- **pydantic** (>=2.10.5): Data validation and settings management
- **pydantic-settings** (>=2.7.1): Settings management from various sources
- **pydantic-settings-manager** (>=2.3.0): Advanced settings management with multi-configuration support

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - Parent monorepo
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Settings management library
