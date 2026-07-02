# kiarina-lib-slack

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-lib-slack.svg)](https://badge.fury.io/py/kiarina-lib-slack)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-slack.svg)](https://pypi.org/project/kiarina-lib-slack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] これは何？
> Slack app の認証情報と OAuth 情報を pydantic-settings-manager で管理するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

Slack SDK は依存関係に含まれません。Slack client を生成するアプリケーション側で追加してください。

## Installation

```bash
pip install kiarina-lib-slack
```

## Features

- **Configuring a Slack App**
  Slack app の認証情報、OAuth scope、workspace 情報を保持できます。
- **Managing Multiple Apps**
  複数の Slack app 設定を名前で切り替えられます。
- **Loading Environment Variables**
  `KIARINA_LIB_SLACK_` prefix の環境変数を読み込めます。
- **Using Socket Mode**
  Socket Mode 用の app-level token を保持できます。
- **Protecting Secrets**
  Client secret、signing secret、token を `SecretStr` で保持します。

### Configuring a Slack App

`app_id`、`client_id`、`client_secret`、`signing_secret` は必須です。

```python
from kiarina.lib.slack import SlackSettings

settings = SlackSettings(
    app_id="A0123456789",
    client_id="123456789.123456789",
    client_secret="client-secret",
    signing_secret="signing-secret",
    bot_token="xoxb-...",
    scopes=["chat:write"],
)
```

### Managing Multiple Apps

`settings_manager` は複数設定モードです。名前付き設定を `configs` に配置します。

```yaml
kiarina.lib.slack:
  default: production
  configs:
    development:
      app_id: A_DEVELOPMENT
      client_id: development-client
      client_secret: development-secret
      signing_secret: development-signing-secret
    production:
      app_id: A_PRODUCTION
      client_id: production-client
      client_secret: production-secret
      signing_secret: production-signing-secret
```

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.slack import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

### Loading Environment Variables

List 型の `scopes` は JSON array として設定します。

```bash
export KIARINA_LIB_SLACK_APP_ID="A0123456789"
export KIARINA_LIB_SLACK_CLIENT_ID="123456789.123456789"
export KIARINA_LIB_SLACK_CLIENT_SECRET="client-secret"
export KIARINA_LIB_SLACK_SIGNING_SECRET="signing-secret"
export KIARINA_LIB_SLACK_SCOPES='["chat:write"]'
```

```python
from kiarina.lib.slack import SlackSettings

settings = SlackSettings()
```

### Using Socket Mode

Socket Mode では `app_token` に `xapp-` token を設定します。

```python
settings = SlackSettings(
    app_id="A0123456789",
    client_id="123456789.123456789",
    client_secret="client-secret",
    signing_secret="signing-secret",
    app_token="xapp-...",
)
```

### Protecting Secrets

秘密値は実際に SDK へ渡す場所でのみ取り出します。

```python
bot_token = (
    settings.bot_token.get_secret_value()
    if settings.bot_token is not None
    else None
)
```

## API Reference

### `kiarina.lib.slack`

```python
from kiarina.lib.slack import (
    SlackSettings,
    settings_manager,
)
```

#### `SlackSettings`

```python
class SlackSettings(BaseSettings):
    def __init__(
        self,
        *,
        app_id: str,
        client_id: str,
        client_secret: SecretStr,
        signing_secret: SecretStr,
        app_token: SecretStr | None = None,
        scopes: list[str] = [],
        team_id: str | None = None,
        enterprise_id: str | None = None,
        bot_token: SecretStr | None = None,
    ) -> None: ...
```

Slack app の設定。

**Fields**

- `app_id` (`str`): Slack app ID。
- `client_id` (`str`): Slack OAuth client ID。
- `client_secret` (`SecretStr`): Slack OAuth client secret。
- `signing_secret` (`SecretStr`): Slack request signing secret。
- `app_token` (`SecretStr | None`): Socket Mode 用の app-level token。
- `scopes` (`list[str]`): Slack app が要求する OAuth scope。
- `team_id` (`str | None`): Slack workspace ID。
- `enterprise_id` (`str | None`): Slack Enterprise Grid organization ID。
- `bot_token` (`SecretStr | None`): Slack bot user OAuth token。

#### `settings_manager`

```python
settings_manager: SettingsManager[SlackSettings]
```

名前付き Slack app 設定を管理する global instance です。
