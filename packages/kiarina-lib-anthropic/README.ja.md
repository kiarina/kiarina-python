# kiarina-lib-anthropic

[English](README.md) | 日本語

pydantic-settings-manager による設定管理を備えた Anthropic API 連携用 Python library です。

## Features

- **Configuration Management**: `pydantic-settings-manager` による柔軟な設定管理
- **Type Safety**: type hints と Pydantic validation
- **Secure Credential Handling**: API key を `SecretStr` で保護
- **Multiple Configurations**: project / environment ごとの複数設定
- **Environment Variable Support**: `KIARINA_LIB_ANTHROPIC_` prefix の環境変数
- **Custom Base URL**: Anthropic-compatible API endpoint の指定

## Installation

```bash
pip install kiarina-lib-anthropic
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.anthropic import settings_manager

settings_manager.user_config = {
    "default": {
        "api_key": "sk-ant-your-api-key-here",
    },
}

settings = settings_manager.settings
print(settings.api_key.get_secret_value()[:10])
```

### Environment Variable Configuration

```bash
export KIARINA_LIB_ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

### Multiple Configurations

```python
from kiarina.lib.anthropic import settings_manager

settings_manager.user_config = {
    "project_a": {"api_key": "sk-ant-project-a-key"},
    "project_b": {"api_key": "sk-ant-project-b-key"},
}

settings_manager.active_key = "project_a"
project_a_settings = settings_manager.settings
```

### Custom Base URL

```python
settings_manager.user_config = {
    "custom": {
        "api_key": "your-custom-key",
        "base_url": "https://custom.anthropic-compatible.api.com",
    },
}
```

## Configuration

この library は [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) を使って設定を管理します。

### AnthropicSettings

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `api_key` | `SecretStr` | Yes | - | Anthropic API key |
| `base_url` | `str \| None` | No | `None` | custom base URL |

### Environment Variables

```bash
export KIARINA_LIB_ANTHROPIC_API_KEY="sk-ant-your-api-key"
export KIARINA_LIB_ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

### Programmatic Configuration

```python
from pydantic import SecretStr
from kiarina.lib.anthropic import AnthropicSettings, settings_manager

settings = AnthropicSettings(api_key=SecretStr("sk-ant-your-api-key"))
settings_manager.user_config = {"default": {"api_key": "sk-ant-your-api-key"}}
```

### Runtime Overrides

```python
settings_manager.cli_args = {"base_url": "https://custom.api.com"}
```

## Security

### API Key Protection

API key は `SecretStr` で保持され、文字列表現では mask されます。実値が必要な場合のみ `.get_secret_value()` を呼び出します。

## API Reference

### AnthropicSettings

Anthropic API 設定用の Pydantic settings model です。

### settings_manager

Anthropic 設定用の global settings manager instance です。

## Development

### Prerequisites

Python 3.12+ が必要です。

### Setup

```bash
mise run setup
```

### Running Tests

```bash
cd packages/kiarina-lib-anthropic && make check
mise run test kiarina-lib-anthropic --coverage
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

