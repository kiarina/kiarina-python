# kiarina-lib-cloudflare

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-cloudflare.svg)](https://badge.fury.io/py/kiarina-lib-cloudflare)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-cloudflare.svg)](https://pypi.org/project/kiarina-lib-cloudflare/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for managing Cloudflare account credentials with pydantic-settings-manager.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

A Cloudflare SDK is not included as a dependency. Add one to the application that uses the credentials.

## Installation

```bash
pip install kiarina-lib-cloudflare
```

## Features

- **Configuring Cloudflare Authentication**
  Store an account ID and API token as typed settings.
- **Managing Multiple Accounts**
  Switch between named settings for multiple accounts.
- **Loading Environment Variables**
  Load environment variables with the `KIARINA_LIB_CLOUDFLARE_` prefix.
- **Protecting API Tokens**
  Store the API token as `SecretStr`.

### Configuring Cloudflare Authentication

```python
from kiarina.lib.cloudflare import CloudflareSettings

settings = CloudflareSettings(
    account_id="0123456789abcdef",
    api_token="secret-token",
)
```

Extract the token where it is needed to create a Cloudflare client.

```python
account_id = settings.account_id
api_token = settings.api_token.get_secret_value()
```

### Managing Multiple Accounts

`settings_manager` uses multiple-settings mode. Place named settings under `configs`.

```yaml
kiarina.lib.cloudflare:
  default: production
  configs:
    development:
      account_id: development-account
      api_token: development-token
    production:
      account_id: production-account
      api_token: production-token
```

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.cloudflare import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

To configure only this package directly, assign `settings_manager.user_config`.

```python
from kiarina.lib.cloudflare import settings_manager

settings_manager.user_config = {
    "default": "development",
    "configs": {
        "development": {
            "account_id": "development-account",
            "api_token": "development-token",
        },
        "production": {
            "account_id": "production-account",
            "api_token": "production-token",
        },
    },
}
```

### Loading Environment Variables

Load a single configuration from environment variables.

```bash
export KIARINA_LIB_CLOUDFLARE_ACCOUNT_ID="0123456789abcdef"
export KIARINA_LIB_CLOUDFLARE_API_TOKEN="secret-token"
```

```python
from kiarina.lib.cloudflare import CloudflareSettings

settings = CloudflareSettings()
```

### Protecting API Tokens

`api_token` is a `SecretStr`. Extract its value explicitly only where required.

```python
api_token = settings.api_token.get_secret_value()
```

## API Reference

### `kiarina.lib.cloudflare`

```python
from kiarina.lib.cloudflare import (
    CloudflareSettings,
    settings_manager,
)
```

#### `CloudflareSettings`

```python
class CloudflareSettings(BaseSettings):
    def __init__(
        self,
        *,
        account_id: str,
        api_token: SecretStr,
    ) -> None: ...
```

Cloudflare account settings.

**Fields**

- `account_id` (`str`): Cloudflare account ID.
- `api_token` (`SecretStr`): Cloudflare API token.

#### `settings_manager`

```python
settings_manager: SettingsManager[CloudflareSettings]
```

Global instance that manages named Cloudflare account settings.
