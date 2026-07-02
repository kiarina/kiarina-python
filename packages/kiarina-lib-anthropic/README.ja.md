# kiarina-lib-anthropic

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-lib-anthropic.svg)](https://badge.fury.io/py/kiarina-lib-anthropic)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-anthropic.svg)](https://pypi.org/project/kiarina-lib-anthropic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] これは何？
> Anthropic API の認証情報と接続先を pydantic-settings-manager で管理するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

Anthropic Python SDK は依存関係に含まれません。Client を生成するアプリケーション側で追加してください。

## Installation

```bash
pip install kiarina-lib-anthropic
```

## Features

- **Configuring an Anthropic Client**
  API key と任意の base URL を型付き設定として保持できます。
- **Managing Multiple Configurations**
  複数の project や環境の設定を名前で切り替えられます。
- **Loading Environment Variables**
  `KIARINA_LIB_ANTHROPIC_` prefix の環境変数を読み込めます。
- **Protecting API Keys**
  API key を `SecretStr` で保持し、通常の文字列表現への露出を防ぎます。

### Configuring an Anthropic Client

`AnthropicSettings` を Anthropic SDK の client 引数へ変換して使用します。

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

`api_key` と `base_url` は省略可能です。省略時の動作は、設定を渡す client 側で決まります。

### Managing Multiple Configurations

`settings_manager` は複数設定モードです。名前付き設定を `configs` に配置します。

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

このパッケージだけを直接設定する場合は、`settings_manager.user_config` を設定できます。

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

単一の設定は環境変数から読み込めます。

```bash
export KIARINA_LIB_ANTHROPIC_API_KEY="sk-ant-..."
export KIARINA_LIB_ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

```python
from kiarina.lib.anthropic import AnthropicSettings

settings = AnthropicSettings()
```

### Protecting API Keys

`api_key` は `SecretStr` です。実際の値が必要な場所でのみ明示的に取り出します。

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

Anthropic client の設定。

**Fields**

- `api_key` (`SecretStr | None`): Anthropic API key。
- `base_url` (`str | None`): Anthropic API の base URL。

#### `settings_manager`

```python
settings_manager: SettingsManager[AnthropicSettings]
```

名前付き Anthropic client 設定を管理する global instance です。
