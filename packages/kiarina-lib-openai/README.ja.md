# kiarina-lib-openai

[![PyPI version](https://badge.fury.io/py/kiarina-lib-openai.svg)](https://badge.fury.io/py/kiarina-lib-openai)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-openai.svg)](https://pypi.org/project/kiarina-lib-openai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] これは何？
> OpenAI API の認証情報と接続先を pydantic-settings-manager で管理するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

OpenAI Python SDK は依存関係に含まれません。Client を生成するアプリケーション側で追加してください。

## Installation

```bash
pip install kiarina-lib-openai
```

## Features

- **Configuring an OpenAI Client**
  OpenAI SDK の client 引数を設定から生成できます。
- **Managing Multiple Configurations**
  複数の project や環境の設定を名前で切り替えられます。
- **Loading Environment Variables**
  `KIARINA_LIB_OPENAI_` prefix の環境変数を読み込めます。
- **Using Compatible APIs**
  `base_url` で OpenAI-compatible API の接続先を指定できます。
- **Protecting API Keys**
  API key を `SecretStr` で保持します。

### Configuring an OpenAI Client

`to_client_kwargs()` は値が設定された項目だけを OpenAI SDK の引数名へ変換します。

```python
from openai import OpenAI

from kiarina.lib.openai import OpenAISettings

settings = OpenAISettings(api_key="sk-...")
client = OpenAI(**settings.to_client_kwargs())
```

`organization_id` は `organization` に変換されます。`api_key`、`organization_id`、`base_url` がすべて `None` の場合は空の `dict` を返します。

### Managing Multiple Configurations

`settings_manager` は複数設定モードです。名前付き設定を `configs` に配置します。

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

このパッケージだけを直接設定する場合は、`settings_manager.user_config` を設定できます。

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

単一の設定は環境変数から読み込めます。

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

`to_client_kwargs()` は OpenAI SDK に渡すため、`api_key` の秘密値を返します。戻り値を log に記録しないでください。

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

OpenAI client の設定。

**Fields**

- `api_key` (`SecretStr | None`): OpenAI API key。
- `organization_id` (`str | None`): OpenAI organization ID。
- `base_url` (`str | None`): OpenAI API の base URL。

##### `to_client_kwargs`

値が `None` ではない field を OpenAI SDK の client 引数へ変換します。

**Returns**

- `dict[str, Any]`: `api_key`、`organization`、`base_url` のうち、設定された値を持つ辞書。

#### `settings_manager`

```python
settings_manager: SettingsManager[OpenAISettings]
```

名前付き OpenAI client 設定を管理する global instance です。
