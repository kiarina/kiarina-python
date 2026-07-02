# kiarina-lib-anthropic

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-anthropic.svg)](https://badge.fury.io/py/kiarina-lib-anthropic)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-anthropic.svg)](https://pypi.org/project/kiarina-lib-anthropic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for managing Anthropic API credentials and endpoints with pydantic-settings-manager.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

The Anthropic Python SDK is not included as a dependency. Add it to the application that creates the client.

## Installation

```bash
pip install kiarina-lib-anthropic
```

## Features

- **Configuring an Anthropic Client**
  Store an API key and optional base URL as typed settings.
- **Managing Multiple Configurations**
  Switch between named settings for multiple projects or environments.
- **Loading Environment Variables**
  Load environment variables with the `KIARINA_LIB_ANTHROPIC_` prefix.
- **Protecting API Keys**
  Store the API key as `SecretStr` to prevent exposure in normal string representations.

### Configuring an Anthropic Client

Convert `AnthropicSettings` into arguments for an Anthropic SDK client.

```python
from anthropic import Anthropic

from kiarina.lib.anthropic import AnthropicSettings

settings = AnthropicSettings(api_key="sk-ant-...")
client = Anthropic(
    api_key=(
        settings.api_key.get_secret_value()
        if settings.api_key is not None
        else None
    ),
    base_url=settings.base_url,
)
```

Both `api_key` and `base_url` are optional. When omitted, behavior is determined by the client that receives the settings.

### Managing Multiple Configurations

`settings_manager` uses multiple-settings mode. Place named settings under `configs`.

```yaml
kiarina.lib.anthropic:
  default: production
  configs:
    development:
      api_key: sk-ant-development
    production:
      api_key: sk-ant-production
```

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.anthropic import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

To configure only this package directly, assign `settings_manager.user_config`.

```python
from kiarina.lib.anthropic import settings_manager

settings_manager.user_config = {
    "default": "development",
    "configs": {
        "development": {"api_key": "sk-ant-development"},
        "production": {"api_key": "sk-ant-production"},
    },
}
```

### Loading Environment Variables

Load a single configuration from environment variables.

```bash
export KIARINA_LIB_ANTHROPIC_API_KEY="sk-ant-..."
export KIARINA_LIB_ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

```python
from kiarina.lib.anthropic import AnthropicSettings

settings = AnthropicSettings()
```

### Protecting API Keys

`api_key` is a `SecretStr`. Extract its value explicitly only where required.

```python
api_key = (
    settings.api_key.get_secret_value()
    if settings.api_key is not None
    else None
)
```

## API Reference

### `kiarina.lib.anthropic`

```python
from kiarina.lib.anthropic import (
    AnthropicSettings,
    settings_manager,
)
```

#### `AnthropicSettings`

```python
class AnthropicSettings(BaseSettings):
    def __init__(
        self,
        *,
        api_key: SecretStr | None = None,
        base_url: str | None = None,
    ) -> None: ...
```

Anthropic client settings.

**Fields**

- `api_key` (`SecretStr | None`): Anthropic API key.
- `base_url` (`str | None`): Base URL for the Anthropic API.

#### `settings_manager`

```python
settings_manager: SettingsManager[AnthropicSettings]
```

Global instance that manages named Anthropic client settings.
