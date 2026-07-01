# kiarina-lib-firebase

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase.svg)](https://badge.fury.io/py/kiarina-lib-firebase)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase.svg)](https://pypi.org/project/kiarina-lib-firebase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
  Restore tokens from an application-specific cache and save refreshed values.
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
    token_data=token_data,
)

id_token = await manager.get_id_token()
```

Provide at least one of `refresh_token`, `token_data`, or `token_data_cache`.

### Persisting Token Data

Implement `TokenDataCache` to let `TokenManager` restore tokens and save refreshed values.

```python
from kiarina.lib.firebase import TokenData, TokenDataCache, TokenManager


class InMemoryTokenCache(TokenDataCache):
    def __init__(self, token_data: TokenData) -> None:
        self._token_data = token_data

    async def get(self) -> TokenData:
        return self._token_data

    async def set(self, token_data: TokenData) -> None:
        self._token_data = token_data


manager = TokenManager(
    api_key="firebase-web-api-key",
    token_data_cache=InMemoryTokenCache(token_data),
)
id_token = await manager.get_id_token()
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
    FirebaseAPIError,
    FirebaseAuthError,
    FirebaseSettings,
    InvalidCustomTokenError,
    InvalidRefreshTokenError,
    TokenData,
    TokenDataCache,
    TokenManager,
    exchange_custom_token,
    refresh_id_token,
    settings_manager,
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
    api_key: str

    def __init__(
        self,
        *,
        api_key: str,
        refresh_token: str | None = None,
        token_data: TokenData | None = None,
        token_data_cache: TokenDataCache | None = None,
        refresh_buffer_seconds: int = 300,
    ) -> None: ...

    @property
    def refresh_token(self) -> str: ...

    @property
    def token_data(self) -> TokenData: ...

    @property
    def id_token(self) -> str: ...

    @property
    def expires_at(self) -> datetime: ...

    async def get_id_token(self) -> str: ...

    async def refresh(self) -> TokenData: ...
```

Hold an ID token and refresh it when no more than `refresh_buffer_seconds` remain. Token loading and refreshes are serialized with a lock when multiple coroutines use the manager concurrently.

- `ValueError`: No token source is provided to the constructor
- `AssertionError`: An unset `refresh_token` or `token_data`, or a dependent property, is accessed before token retrieval

#### `TokenData`

```python
class TokenData(BaseModel):
    refresh_token: str
    id_token: str
    expires_at: datetime

    @classmethod
    def from_api_response(
        cls,
        id_token: str,
        refresh_token: str,
        expires_in: int,
        *,
        issued_at: datetime | None = None,
    ) -> TokenData: ...
```

A Firebase Authentication token set. `from_api_response` calculates the UTC expiration time from `issued_at` and the lifetime in seconds. It uses the current time when `issued_at` is omitted.

#### `TokenDataCache`

```python
class TokenDataCache(Protocol):
    async def get(self) -> TokenData: ...

    async def set(self, token_data: TokenData) -> None: ...
```

An interface for reading and writing a persistent token set.

#### `FirebaseSettings`

```python
class FirebaseSettings(BaseSettings):
    project_id: str
    api_key: SecretStr
```

Firebase Authentication settings that support environment variables with the `KIARINA_LIB_FIREBASE_` prefix.

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
