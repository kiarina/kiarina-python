# kiarina-lib-slack

[English](README.md) | [日本語](README.ja.md)

kiarina namespace 向けの Slack API client 設定 library です。

## Features

- **Configuration Management**: Slack App 設定を `pydantic-settings-manager` で管理
- **Type Safety**: type hints と Pydantic validation
- **Secure Credential Handling**: secret / token を `SecretStr` で保護
- **Multiple Configurations**: app / workspace ごとの複数設定
- **Environment Variable Support**: `KIARINA_LIB_SLACK_` prefix の環境変数

## Installation

```bash
pip install kiarina-lib-slack
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.slack import settings_manager

settings_manager.user_config = {
    "default": {
        "app_id": "A01234567",
        "client_id": "1234567890.1234567890",
        "client_secret": "your-client-secret",
        "signing_secret": "your-signing-secret",
        "bot_token": "xoxb-your-bot-token",
    },
}

settings = settings_manager.settings
```

### Using with Slack SDK

```python
from slack_sdk import WebClient
from kiarina.lib.slack import settings_manager

settings = settings_manager.settings
client = WebClient(token=settings.bot_token.get_secret_value())
```

### Environment Variable Configuration

```bash
export KIARINA_LIB_SLACK_APP_ID="A01234567"
export KIARINA_LIB_SLACK_CLIENT_ID="1234567890.1234567890"
export KIARINA_LIB_SLACK_CLIENT_SECRET="your-client-secret"
export KIARINA_LIB_SLACK_SIGNING_SECRET="your-signing-secret"
export KIARINA_LIB_SLACK_BOT_TOKEN="xoxb-your-bot-token"
```

### Multiple Configurations

```python
settings_manager.user_config = {
    "app_a": {"app_id": "A...", "client_id": "...", "client_secret": "...", "signing_secret": "..."},
    "app_b": {"app_id": "B...", "client_id": "...", "client_secret": "...", "signing_secret": "..."},
}
settings_manager.active_key = "app_a"
```

### Socket Mode with App Token

Socket Mode を使う場合は `app_token` に `xapp-...` token を設定します。

## Configuration

### SlackSettings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_id` | `str` | Yes | Slack App ID |
| `client_id` | `str` | Yes | Slack Client ID |
| `client_secret` | `SecretStr` | Yes | Slack Client Secret |
| `signing_secret` | `SecretStr` | Yes | Slack Signing Secret |
| `scopes` | `list[str]` | No | OAuth scopes |
| `app_token` | `SecretStr \| None` | No | Socket Mode 用 App-Level Token |
| `team_id` | `str \| None` | No | Slack Team ID |
| `enterprise_id` | `str \| None` | No | Slack Enterprise ID |
| `bot_token` | `SecretStr \| None` | No | Bot User OAuth Token |

### Environment Variables

`KIARINA_LIB_SLACK_` prefix の環境変数で各 field を設定できます。

### Programmatic Configuration

```python
from pydantic import SecretStr
from kiarina.lib.slack import SlackSettings

settings = SlackSettings(
    app_id="A01234567",
    client_id="1234567890.1234567890",
    client_secret=SecretStr("your-client-secret"),
    signing_secret=SecretStr("your-signing-secret"),
)
```

### Runtime Overrides

```python
settings_manager.cli_args = {"team_id": "T99999999"}
```

## Security

### Secret Protection

`client_secret`、`signing_secret`、`app_token`、`bot_token` は `SecretStr` で保護されます。

## API Reference

### SlackSettings

Slack App 設定用の Pydantic settings model です。

### settings_manager

Slack 設定用の global settings manager instance です。

## Development

### Prerequisites

Python 3.12+ が必要です。

### Setup

```bash
mise run setup
```

### Running Tests

```bash
mise run package:check kiarina-lib-slack
mise run package:test kiarina-lib-slack --coverage
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

