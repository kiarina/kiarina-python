# kiarina-lib-openai

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-openai.svg)](https://badge.fury.io/py/kiarina-lib-openai)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-openai.svg)](https://pypi.org/project/kiarina-lib-openai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for managing OpenAI API credentials and endpoints with pydantic-settings-manager.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

The OpenAI Python SDK is not included as a dependency. Add it to the application that creates the client.

## Installation

```bash
pip install kiarina-lib-openai
```

## Features

- **Configuring an OpenAI Client**
  Generate OpenAI SDK client arguments from settings.
- **Managing Multiple Configurations**
  Switch between named settings for multiple projects or environments.
- **Loading Environment Variables**
  Load environment variables with the `KIARINA_LIB_OPENAI_` prefix.
- **Using Compatible APIs**
  Set an OpenAI-compatible API endpoint with `base_url`.
- **Protecting API Keys**
  Store the API key as `SecretStr`.

### Configuring an OpenAI Client

`to_client_kwargs()` converts only configured values to OpenAI SDK argument names.

```python
from openai import OpenAI

from kiarina.lib.openai import OpenAISettings

settings = OpenAISettings(api_key="sk-...")
client = OpenAI(**settings.to_client_kwargs())
```

`organization_id` becomes `organization`. When `api_key`, `organization_id`, and `base_url` are all `None`, the method returns an empty `dict`.

### Managing Multiple Configurations

`settings_manager` uses multiple-settings mode. Place named settings under `configs`.

```yaml
kiarina.lib.openai:
  default: production
  configs:
    development:
      api_key: sk-development
    production:
      api_key: sk-production
      organization_id: org-production
```

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.openai import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

To configure only this package directly, assign `settings_manager.user_config`.

```python
from kiarina.lib.openai import settings_manager

settings_manager.user_config = {
    "default": "development",
    "configs": {
        "development": {"api_key": "sk-development"},
        "production": {
            "api_key": "sk-production",
            "organization_id": "org-production",
        },
    },
}
```

### Loading Environment Variables

Load a single configuration from environment variables.

```bash
export KIARINA_LIB_OPENAI_API_KEY="sk-..."
export KIARINA_LIB_OPENAI_ORGANIZATION_ID="org-..."
export KIARINA_LIB_OPENAI_BASE_URL="https://api.openai.com/v1"
```

```python
from kiarina.lib.openai import OpenAISettings

settings = OpenAISettings()
```

### Using Compatible APIs

```python
from openai import OpenAI

from kiarina.lib.openai import OpenAISettings

settings = OpenAISettings(
    api_key="compatible-api-key",
    base_url="https://example.com/v1",
)
client = OpenAI(**settings.to_client_kwargs())
```

### Protecting API Keys

`to_client_kwargs()` returns the secret value of `api_key` so it can be passed to the OpenAI SDK. Do not log the returned dictionary.

## API Reference

### `kiarina.lib.openai`

```python
from kiarina.lib.openai import (
    OpenAISettings,
    settings_manager,
)
```

#### `OpenAISettings`

```python
class OpenAISettings(BaseSettings):
    def __init__(
        self,
        *,
        api_key: SecretStr | None = None,
        organization_id: str | None = None,
        base_url: str | None = None,
    ) -> None: ...

    def to_client_kwargs(self) -> dict[str, Any]: ...
```

OpenAI client settings.

**Fields**

- `api_key` (`SecretStr | None`): OpenAI API key.
- `organization_id` (`str | None`): OpenAI organization ID.
- `base_url` (`str | None`): Base URL for the OpenAI API.

##### `to_client_kwargs`

Converts fields whose values are not `None` into OpenAI SDK client arguments.

**Returns**

- `dict[str, Any]`: A dictionary containing configured values among `api_key`, `organization`, and `base_url`.

#### `settings_manager`

```python
settings_manager: SettingsManager[OpenAISettings]
```

Global instance that manages named OpenAI client settings.
