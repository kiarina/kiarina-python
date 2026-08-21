# kiarina-lib-firebase

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase.svg)](https://badge.fury.io/py/kiarina-lib-firebase)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase.svg)](https://pypi.org/project/kiarina-lib-firebase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> An asynchronous package for exchanging Firebase custom tokens and refreshing ID tokens.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.10.6` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-lib-firebase
```

## Features

- **Exchanging a Custom Token**
  Exchange a Firebase custom token for an ID token and refresh token.
- **Refreshing an ID Token**
  Retrieve a new ID token from a refresh token.
- **Managing the Token Lifecycle**
  Refresh an ID token before expiration and serialize concurrent refreshes.
- **Persisting Token Data**
  Restore tokens from an application-specific store and save refreshed values.
- **Sharing a Token Manager**
  Build a token manager from settings, or register one by name, and get it anywhere in the application.
- **Managing Multiple Configurations**
  Manage multiple Firebase configurations with pydantic-settings-manager.

### Exchanging a Custom Token

Exchange a custom token issued by the Firebase Admin SDK or another trusted environment.

```python
from kiarina.lib.firebase import exchange_custom_token

token_data = await exchange_custom_token(
    custom_token="firebase-custom-token",
    api_key="firebase-web-api-key",
)
```

An invalid custom token raises `InvalidCustomTokenError`. Other Firebase API errors and communication failures raise `FirebaseAPIError`.

### Refreshing an ID Token

Use an existing refresh token to retrieve a new token set.

```python
from kiarina.lib.firebase import refresh_id_token

token_data = await refresh_id_token(
    refresh_token="firebase-refresh-token",
    api_key="firebase-web-api-key",
)
```

An invalid or expired refresh token raises `InvalidRefreshTokenError`.

### Managing the Token Lifecycle

`TokenManager` refreshes an ID token before it expires. By default, it refreshes when no more than 300 seconds remain.

```python
from kiarina.lib.firebase import TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=token_data,
)

id_token = await manager.get_id_token()
```

`token_store` accepts a `TokenStore` or a `TokenData`. A `TokenData` is wrapped in an `InMemoryTokenStore`, so tokens are always managed through a store.

### Persisting Token Data

`FileTokenStore` keeps the token set in a JSON file, so a restart resumes from the stored refresh token. `TokenManager` loads the token set on the first `get_id_token()` call and saves every refreshed value.

```python
from kiarina.lib.firebase import FileTokenStore, TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=FileTokenStore("~/.config/your-app/token.json"),
)
id_token = await manager.get_id_token()
```

`InMemoryTokenStore` keeps the token set in the process only. Implement `TokenStore` for any other backend.

### Sharing a Token Manager

`token_manager_registry` builds a `TokenManager` from the settings of the same name. Setting `token_data_file_path` is enough, and the token set is then kept in that file through `FileTokenStore`.

```yaml
kiarina.lib.firebase:
  default: production
  configs:
    production:
      project_id: production-project
      api_key: production-api-key
      token_data_file_path: ~/.config/your-app/token.json
```

```python
from kiarina.lib.firebase import token_manager_registry

# Anywhere in the application
id_token = await token_manager_registry.get().get_id_token()
```

`get()` without a name uses the same settings as `settings_manager`, so it follows `default` and `settings_manager.active_key`. Each name is built once and reused.

Register an instance to use a different `TokenStore`. A registered instance takes priority over the settings.

```python
from kiarina.lib.firebase import TokenManager, token_manager_registry

token_manager_registry.register(
    "production",
    TokenManager(
        api_key="firebase-web-api-key",
        token_store=InMemoryTokenStore(token_data),
    ),
)
```

### Managing Multiple Configurations

`settings_manager` uses multi-configuration mode. In the pydantic-settings-manager v3 structured format, named settings are placed under `configs`.

```yaml
kiarina.lib.firebase:
  default: production
  configs:
    development:
      project_id: development-project
      api_key: development-api-key
    production:
      project_id: production-project
      api_key: production-api-key
```

Load the configuration during application bootstrap.

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

To configure only this package directly, assign the structured format to `settings_manager.user_config`.

```python
from kiarina.lib.firebase import settings_manager

settings_manager.user_config = {
    "default": "production",
    "configs": {
        "development": {
            "project_id": "development-project",
            "api_key": "development-api-key",
        },
        "production": {
            "project_id": "production-project",
            "api_key": "production-api-key",
        },
    },
}

settings = settings_manager.get_settings()
```

A single configuration can also be supplied through environment variables.

```bash
export KIARINA_LIB_FIREBASE_PROJECT_ID="your-project-id"
export KIARINA_LIB_FIREBASE_API_KEY="your-api-key"
```

## API Reference

### `kiarina.lib.firebase`

```python
from kiarina.lib.firebase import (
    FileTokenStore,
    FirebaseAPIError,
    FirebaseAuthError,
    FirebaseSettings,
    InMemoryTokenStore,
    InvalidCustomTokenError,
    InvalidRefreshTokenError,
    TokenData,
    TokenManager,
    TokenStore,
    exchange_custom_token,
    refresh_id_token,
    settings_manager,
    token_manager_registry,
)
```

#### `exchange_custom_token`

```python
async def exchange_custom_token(
    custom_token: str,
    api_key: str,
) -> TokenData: ...
```

Exchange a Firebase custom token for an ID token and refresh token.

- `InvalidCustomTokenError`: The custom token is invalid
- `FirebaseAPIError`: The Firebase API returns another error or communication fails

#### `refresh_id_token`

```python
async def refresh_id_token(
    refresh_token: str,
    api_key: str,
) -> TokenData: ...
```

Retrieve a new ID token with a refresh token.

- `InvalidRefreshTokenError`: The refresh token is invalid or expired
- `FirebaseAPIError`: The Firebase API returns another error or communication fails

#### `TokenManager`

```python
class TokenManager:
    def __init__(
        self,
        *,
        api_key: str,
        token_store: TokenStore | TokenData,
        uid: str | None = None,
        refresh_buffer_seconds: int = 300,
    ) -> None: ...

    async def get_id_token(self) -> str: ...

    async def refresh(self) -> TokenData: ...
```

Read the token set from `token_store` and refresh it when no more than `refresh_buffer_seconds` remain. The manager caches the token set in memory and uses it while it stays valid. Once it needs a refresh, the manager reads `token_store` again first, so a value refreshed elsewhere is picked up before a new refresh is requested. Store reads and refreshes are serialized with a lock when multiple coroutines use the manager concurrently.

Setting `uid` requires every token set the manager reads or refreshes to belong to that user, which catches a stored token set left behind by another user.

`get_id_token()` and `refresh()` propagate the exceptions raised by `refresh_id_token`.

**Raises**

- `ValueError`: The token set does not belong to `uid`

#### `TokenData`

```python
class TokenData(BaseModel):
    refresh_token: str
    id_token: str
    expires_at: datetime

    @property
    def uid(self) -> str: ...

    @classmethod
    def from_api_response(cls, id_token: str, refresh_token: str) -> Self: ...
```

A Firebase Authentication token set. `from_api_response` reads the `exp` claim from `id_token` and uses it as the UTC expiration time. `uid` reads the `sub` claim from `id_token` on each access.

**Raises**

- `ValueError`: The claim cannot be read from `id_token`, or it has an unexpected type

#### `FileTokenStore`

```python
class FileTokenStore(TokenStore):
    file_path: str

    def __init__(self, file_path: str) -> None: ...
```

A `TokenStore` that keeps the token set in a JSON file. Writes are atomic and locked between processes, and a new file is created with owner-only permissions. `token_manager_registry` uses it for the managers it builds from settings.

**Raises**

- `FileNotFoundError`: `get()` is called before the file exists

#### `InMemoryTokenStore`

```python
class InMemoryTokenStore(TokenStore):
    def __init__(self, token_data: TokenData) -> None: ...
```

A `TokenStore` that keeps the token set in the process only. `TokenManager` wraps a `TokenData` in it.

#### `TokenStore`

```python
class TokenStore(Protocol):
    async def get(self) -> TokenData: ...

    async def set(self, token_data: TokenData) -> None: ...
```

An interface for reading and writing a persistent token set. `TokenManager` treats it as the authoritative source of the token set.

#### `FirebaseSettings`

```python
class FirebaseSettings(BaseSettings):
    project_id: str
    api_key: SecretStr
    uid: str | None = None
    token_data_file_path: str | None = None
```

Firebase Authentication settings that support environment variables with the `KIARINA_LIB_FIREBASE_` prefix.

**Fields**

- `project_id` (`str`): Firebase project ID
- `api_key` (`SecretStr`): Firebase Web API key
- `uid` (`str | None`): Firebase user ID that the token set must belong to. Any user is accepted when this is not set
- `token_data_file_path` (`str | None`): Path of the file that `token_manager_registry` stores the token set in

#### `token_manager_registry`

```python
token_manager_registry: ObjectRegistry[TokenManager, None]
```

A registry of `TokenManager` instances. Use `register()`, `get()`, `unregister()`, `is_registered()`, `list_names()`, and `clear()`.

`get(name)` returns the registered instance, or builds one from the `FirebaseSettings` of the same name and keeps it. Names and aliases are those of `settings_manager`, and `get()` without a name resolves in the same order: `settings_manager.active_key`, then the `default` in the settings, then `"default"`.

`resolve()` is unusable because it does not read registered instances.

**Raises**

- `ValueError`: No settings exist under the name, or `token_data_file_path` is not configured in them

#### `settings_manager`

```python
settings_manager: SettingsManager[FirebaseSettings] = SettingsManager(
    FirebaseSettings,
    multi=True,
)
```

The public instance that manages multiple named `FirebaseSettings`.

#### `FirebaseAuthError`

```python
class FirebaseAuthError(Exception): ...
```

The base class for Firebase Authentication exceptions raised by this package.

#### `InvalidCustomTokenError`

```python
class InvalidCustomTokenError(FirebaseAuthError): ...
```

Raised when a custom token is invalid.

#### `InvalidRefreshTokenError`

```python
class InvalidRefreshTokenError(FirebaseAuthError): ...
```

Raised when a refresh token is invalid or expired.

#### `FirebaseAPIError`

```python
class FirebaseAPIError(FirebaseAuthError):
    status_code: int | None
    error_code: str | None

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str | None = None,
    ) -> None: ...
```

Represents other Firebase API errors and communication failures. When available, the HTTP status code is stored in `status_code` and the Firebase error code is stored in `error_code`.
