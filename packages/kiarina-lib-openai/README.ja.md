# kiarina-lib-openai

[English](README.md) | 日本語

pydantic-settings-manager による設定管理を備えた OpenAI API 連携用 Python library です。

## Features

- **Configuration Management**: `pydantic-settings-manager` による柔軟な設定管理
- **Type Safety**: type hints と Pydantic validation
- **Secure Credential Handling**: API key を `SecretStr` で保護
- **Multiple Configurations**: project / environment ごとの複数設定
- **Environment Variable Support**: `KIARINA_LIB_OPENAI_` prefix の環境変数
- **Custom Base URL**: OpenAI-compatible API endpoint の指定

## Installation

```bash
pip install kiarina-lib-openai
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.openai import settings_manager

settings_manager.user_config = {
    "default": {
        "api_key": "sk-your-api-key-here",
    },
}

settings = settings_manager.settings
```

### Using with OpenAI Client

```python
from openai import OpenAI
from kiarina.lib.openai import settings_manager

client = OpenAI(**settings_manager.settings.to_client_kwargs())
```

### Environment Variable Configuration

```bash
export KIARINA_LIB_OPENAI_API_KEY="sk-your-api-key-here"
```

### Multiple Configurations

```python
settings_manager.user_config = {
    "project_a": {"api_key": "sk-project-a-key"},
    "project_b": {"api_key": "sk-project-b-key"},
}
settings_manager.active_key = "project_a"
```

### Custom Base URL

```python
settings_manager.user_config = {
    "custom": {
        "api_key": "your-custom-key",
        "base_url": "https://custom.openai-compatible.api.com/v1",
    },
}
```

## Configuration

### OpenAISettings

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `api_key` | `SecretStr` | Yes | - | OpenAI API key |
| `organization` | `str \| None` | No | `None` | organization ID |
| `base_url` | `str \| None` | No | `None` | custom base URL |

### Environment Variables

```bash
export KIARINA_LIB_OPENAI_API_KEY="sk-your-api-key"
export KIARINA_LIB_OPENAI_ORGANIZATION="org-your-organization"
export KIARINA_LIB_OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Programmatic Configuration

```python
from pydantic import SecretStr
from kiarina.lib.openai import OpenAISettings, settings_manager

settings = OpenAISettings(api_key=SecretStr("sk-your-api-key"))
settings_manager.user_config = {"default": {"api_key": "sk-your-api-key"}}
```

### Runtime Overrides

```python
settings_manager.cli_args = {"base_url": "https://custom.api.com/v1"}
```

## Security

### API Key Protection

API key は `SecretStr` で mask されます。実値が必要な場合だけ `.get_secret_value()` を使います。

## API Reference

### OpenAISettings

OpenAI API 設定用の Pydantic settings model です。`to_client_kwargs()` で OpenAI client 初期化用 kwargs に変換できます。

### settings_manager

OpenAI 設定用の global settings manager instance です。

## Development

### Prerequisites

Python 3.12+ が必要です。

### Setup

```bash
mise run setup
```

### Running Tests

```bash
mise run package:check kiarina-lib-openai
mise run package:test kiarina-lib-openai --coverage
```

## Dependencies

- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Contributing

issue や pull request は歓迎します。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager)

