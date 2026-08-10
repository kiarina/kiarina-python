# kiarina-lib-slack

[![PyPI version](https://badge.fury.io/py/kiarina-lib-slack.svg)](https://badge.fury.io/py/kiarina-lib-slack)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-slack.svg)](https://pypi.org/project/kiarina-lib-slack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> A package for managing Slack app credentials and OAuth information with pydantic-settings-manager.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

A Slack SDK is not included as a dependency. Add one to the application that creates the Slack client.

## Installation

```bash
pip install kiarina-lib-slack
```

## Features

- **Configuring a Slack App**
  Store Slack app credentials, OAuth scopes, and workspace information.
- **Managing Multiple Apps**
  Switch between named settings for multiple Slack apps.
- **Loading Environment Variables**
  Load environment variables with the `KIARINA_LIB_SLACK_` prefix.
- **Using Socket Mode**
  Store an app-level token for Socket Mode.
- **Protecting Secrets**
  Store client secrets, signing secrets, and tokens as `SecretStr`.

### Configuring a Slack App

`app_id`, `client_id`, `client_secret`, and `signing_secret` are required.

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

`settings_manager` uses multiple-settings mode. Place named settings under `configs`.

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

Set the `scopes` list as a JSON array.

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

For Socket Mode, set an `xapp-` token as `app_token`.

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

Extract secret values only where they are passed to an SDK.

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

Slack app settings.

**Fields**

- `app_id` (`str`): Slack app ID.
- `client_id` (`str`): Slack OAuth client ID.
- `client_secret` (`SecretStr`): Slack OAuth client secret.
- `signing_secret` (`SecretStr`): Slack request signing secret.
- `app_token` (`SecretStr | None`): App-level token for Socket Mode.
- `scopes` (`list[str]`): OAuth scopes requested by the Slack app.
- `team_id` (`str | None`): Slack workspace ID.
- `enterprise_id` (`str | None`): Slack Enterprise Grid organization ID.
- `bot_token` (`SecretStr | None`): Slack bot user OAuth token.

#### `settings_manager`

```python
settings_manager: SettingsManager[SlackSettings]
```

Global instance that manages named Slack app settings.
