# kiarina-lib-firebase

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase.svg)](https://badge.fury.io/py/kiarina-lib-firebase)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase.svg)](https://pypi.org/project/kiarina-lib-firebase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> An asynchronous Firebase Authentication client for exchanging custom tokens and keeping ID tokens fresh.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) |
| [kiarina-utils-common](https://github.com/kiarina/kiarina-python) | `>=2.10.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-utils-file](https://github.com/kiarina/kiarina-python) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.10.6` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-lib-firebase
```

## Features

- **Exchanging a Custom Token**
  Exchange a Firebase custom token for a token set.
- **Refreshing an ID Token**
  Retrieve a new token set from a refresh token.
- **Managing the Token Lifecycle**
  Refresh an ID token before expiration and serialize concurrent refreshes.
- **Persisting the Token**
  Keep the token set in a file, in memory, or in a store of your own.
- **Sharing a Token Manager**
  Build a token manager from settings and get it anywhere in the application.
- **Managing Multiple Configurations**
  Manage multiple Firebase configurations with pydantic-settings-manager.

### Exchanging a Custom Token

Exchange a custom token issued by the Firebase Admin SDK or another trusted environment.

```python
from kiarina.lib.firebase import exchange_custom_token

token = await exchange_custom_token(
    custom_token="firebase-custom-token",
    api_key="firebase-web-api-key",
)

print(token.uid, token.project_id, token.expires_at)
```

`Token` stores only `refresh_token` and `id_token`. Everything else is read from the ID token, so the values can never disagree with it.

An invalid custom token raises `InvalidCustomTokenError`. Other Firebase API errors and communication failures raise `FirebaseAPIError`.

### Refreshing an ID Token

Retrieve a new token set from an existing one. `TokenManager` does this on its own, so call it directly only when managing the lifecycle yourself.

```python
from kiarina.lib.firebase import refresh_id_token

token = await refresh_id_token(token, api_key="firebase-web-api-key")
```

The refresh token in the returned set carries over. An invalid or expired refresh token raises `InvalidRefreshTokenError`.

### Managing the Token Lifecycle

`TokenManager` refreshes an ID token before it expires. By default, it refreshes when no more than 300 seconds remain.

```python
from kiarina.lib.firebase import InMemoryTokenStore, TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=InMemoryTokenStore(token),
)

token = await manager.get_token()
```

The manager reads and writes the token set through a `TokenStore`, and holds no other state.

### Persisting the Token

`FileTokenStore` keeps the token set in a JSON file, so a restart resumes from the stored refresh token.

```python
from kiarina.lib.firebase import FileTokenStore, TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=FileTokenStore("~/.config/your-app/token.json"),
)

token = await manager.get_token()
```

`InMemoryTokenStore` keeps the token set in the process only. Implement `TokenStore` for any other backend.

### Sharing a Token Manager

`create_token_manager` builds a `TokenManager` from the settings, so the API key and the token file live in one place.

```yaml
kiarina.lib.firebase:
  default: production
  configs:
    production:
      api_key: production-api-key
      token_file_path: ~/.config/your-app/token.json
```

```python
from kiarina.lib.firebase import create_token_manager

manager = create_token_manager()
token = await manager.get_token()
```

`token_manager_registry` does the same, and keeps the manager so the whole application shares one.

```python
from kiarina.lib.firebase import token_manager_registry

# Anywhere in the application
token = await token_manager_registry.get().get_token()
```

`get()` without a name uses the same settings as `settings_manager`, so it follows `default` and `settings_manager.active_key`. Each name is built once and reused.

Register an instance to use a different `TokenStore`. A registered instance takes priority over the settings.

```python
from kiarina.lib.firebase import TokenManager, token_manager_registry

token_manager_registry.register(
    "production",
    TokenManager(
        api_key="firebase-web-api-key",
        token_store=your_token_store,
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
      api_key: development-api-key
      token_file_path: ~/.config/your-app/development.json
    production:
      api_key: production-api-key
      token_file_path: ~/.config/your-app/production.json
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
        "development": {"api_key": "development-api-key"},
        "production": {"api_key": "production-api-key"},
    },
}

settings = settings_manager.get_settings()
```

A single configuration can also be supplied through environment variables.

```bash
export KIARINA_LIB_FIREBASE_API_KEY="your-api-key"
export KIARINA_LIB_FIREBASE_TOKEN_FILE_PATH="~/.config/your-app/token.json"
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
    Token,
    TokenManager,
    TokenStore,
    create_token_manager,
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
) -> Token: ...
```

Exchange a Firebase custom token for a token set.

**Raises**

- `InvalidCustomTokenError`: The custom token is invalid
- `FirebaseAPIError`: The Firebase API returns another error or communication fails

#### `refresh_id_token`

```python
async def refresh_id_token(
    token: Token,
    api_key: str,
) -> Token: ...
```

Retrieve a new token set with the refresh token in `token`.

**Raises**

- `InvalidRefreshTokenError`: The refresh token is invalid or expired
- `FirebaseAPIError`: The Firebase API returns another error or communication fails

#### `create_token_manager`

```python
def create_token_manager(
    firebase_settings_key: str | None = None,
    *,
    token_store: TokenStore | Token | None = None,
    refresh_buffer_seconds: int = 300,
) -> TokenManager: ...
```

Build a `TokenManager` from the `FirebaseSettings` of the given key. `token_store` accepts a `TokenStore` or a `Token`; when it is omitted, a `FileTokenStore` is built from `token_file_path`.

**Raises**

- `ValueError`: No settings exist under the key, or the token store cannot be resolved

#### `TokenManager`

```python
class TokenManager:
    def __init__(
        self,
        *,
        api_key: str,
        token_store: TokenStore,
        refresh_buffer_seconds: int = 300,
    ) -> None: ...

    async def get_token(self) -> Token: ...

    async def refresh(self) -> Token: ...
```

Read the token set from `token_store` and refresh it when no more than `refresh_buffer_seconds` remain. The manager caches the token set in memory and uses it while it stays valid. Once it needs a refresh, the manager reads `token_store` again first, so a value refreshed elsewhere is picked up before a new refresh is requested. Store reads and refreshes are serialized with a lock when multiple coroutines use the manager concurrently.

`get_token()` and `refresh()` propagate the exceptions raised by `refresh_id_token`.

#### `Token`

```python
class Token(BaseModel):
    model_config = ConfigDict(frozen=True)

    refresh_token: str
    id_token: str

    @cached_property
    def project_id(self) -> str: ...

    @cached_property
    def uid(self) -> str: ...

    @cached_property
    def expires_at(self) -> datetime: ...
```

A Firebase Authentication token set. `project_id`, `uid`, and `expires_at` are read from the `aud`, `sub`, and `exp` claims in `id_token`, so only the two tokens are stored and persisted. The model is frozen, which keeps the cached values consistent with `id_token`.

**Raises**

- `ValueError`: The claim cannot be read from `id_token`, or it has an unexpected type

#### `FileTokenStore`

```python
class FileTokenStore(TokenStore):
    file_path: str

    def __init__(self, file_path: str) -> None: ...
```

A `TokenStore` that keeps the token set in a JSON file. Writes are atomic and locked between processes, and a new file is created with owner-only permissions.

**Raises**

- `FileNotFoundError`: `get()` is called before the file exists

#### `InMemoryTokenStore`

```python
class InMemoryTokenStore(TokenStore):
    def __init__(self, token: Token) -> None: ...
```

A `TokenStore` that keeps the token set in the process only.

#### `TokenStore`

```python
class TokenStore(Protocol):
    async def get(self) -> Token: ...

    async def set(self, token: Token) -> None: ...
```

An interface for reading and writing a persistent token set. `TokenManager` treats it as the authoritative source of the token set.

#### `FirebaseSettings`

```python
class FirebaseSettings(BaseSettings):
    api_key: SecretStr
    token_file_path: str | None = None
```

Firebase Authentication settings that support environment variables with the `KIARINA_LIB_FIREBASE_` prefix.

**Fields**

- `api_key` (`SecretStr`): Firebase Web API key
- `token_file_path` (`str | None`): Path of the file that the token set is stored in

#### `token_manager_registry`

```python
token_manager_registry: ObjectRegistry[TokenManager, FirebaseSettings]
```

A registry of `TokenManager` instances. Use `register()`, `get()`, `unregister()`, `is_registered()`, `list_names()`, and `clear()`.

`get(name)` returns the registered instance, or builds one from the `FirebaseSettings` of the same name and keeps it. Names and aliases are those of `settings_manager`, and `get()` without a name resolves in the same order: `settings_manager.active_key`, then the `default` in the settings, then `"default"`.

`resolve()` is unusable because it does not read registered instances.

**Raises**

- `ValueError`: No settings exist under the name, or `token_file_path` is not configured in them

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
