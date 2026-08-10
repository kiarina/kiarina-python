# kiarina-lib-cloudflare

[![PyPI version](https://badge.fury.io/py/kiarina-lib-cloudflare.svg)](https://badge.fury.io/py/kiarina-lib-cloudflare)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-cloudflare.svg)](https://pypi.org/project/kiarina-lib-cloudflare/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] これは何？
> Cloudflare account の認証情報を pydantic-settings-manager で管理するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

Cloudflare SDK は依存関係に含まれません。認証情報を使用するアプリケーション側で追加してください。

## Installation

```bash
pip install kiarina-lib-cloudflare
```

## Features

- **Configuring Cloudflare Authentication**
  Account ID と API token を型付き設定として保持できます。
- **Managing Multiple Accounts**
  複数 account の設定を名前で切り替えられます。
- **Loading Environment Variables**
  `KIARINA_LIB_CLOUDFLARE_` prefix の環境変数を読み込めます。
- **Protecting API Tokens**
  API token を `SecretStr` で保持します。

### Configuring Cloudflare Authentication

```python
from kiarina.lib.cloudflare import CloudflareSettings

settings = CloudflareSettings(
    account_id="0123456789abcdef",
    api_token="secret-token",
)
```

Cloudflare client を生成するときは、必要な場所で token を取り出します。

```python
account_id = settings.account_id
api_token = settings.api_token.get_secret_value()
```

### Managing Multiple Accounts

`settings_manager` は複数設定モードです。名前付き設定を `configs` に配置します。

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

このパッケージだけを直接設定する場合は、`settings_manager.user_config` を設定できます。

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

単一の設定は環境変数から読み込めます。

```bash
export KIARINA_LIB_CLOUDFLARE_ACCOUNT_ID="0123456789abcdef"
export KIARINA_LIB_CLOUDFLARE_API_TOKEN="secret-token"
```

```python
from kiarina.lib.cloudflare import CloudflareSettings

settings = CloudflareSettings()
```

### Protecting API Tokens

`api_token` は `SecretStr` です。実際の値が必要な場所でのみ明示的に取り出します。

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

Cloudflare account の設定。

**Fields**

- `account_id` (`str`): Cloudflare account ID。
- `api_token` (`SecretStr`): Cloudflare API token。

#### `settings_manager`

```python
settings_manager: SettingsManager[CloudflareSettings]
```

名前付き Cloudflare account 設定を管理する global instance です。
