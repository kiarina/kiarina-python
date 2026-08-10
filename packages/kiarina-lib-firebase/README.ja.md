# kiarina-lib-firebase

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase.svg)](https://badge.fury.io/py/kiarina-lib-firebase)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase.svg)](https://pypi.org/project/kiarina-lib-firebase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] What is this?
> Firebase カスタムトークンの交換と ID トークンの更新を行う非同期パッケージです。

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
  Firebase カスタムトークンを ID トークンとリフレッシュトークンへ交換します。
- **Refreshing an ID Token**
  リフレッシュトークンから新しい ID トークンを取得します。
- **Managing the Token Lifecycle**
  有効期限の前に ID トークンを自動更新し、並行する更新を直列化します。
- **Persisting Token Data**
  アプリケーション固有のキャッシュへトークンを保存し、次回の利用時に復元します。
- **Managing Multiple Configurations**
  pydantic-settings-manager で複数の Firebase 設定を管理します。

### Exchanging a Custom Token

Firebase Admin SDK などで発行したカスタムトークンを交換します。

```python
from kiarina.lib.firebase import exchange_custom_token

token_data = await exchange_custom_token(
    custom_token="firebase-custom-token",
    api_key="firebase-web-api-key",
)
```

無効なカスタムトークンには `InvalidCustomTokenError`、その他の Firebase API エラーや通信エラーには `FirebaseAPIError` が送出されます。

### Refreshing an ID Token

既存のリフレッシュトークンを使って、新しいトークン一式を取得します。

```python
from kiarina.lib.firebase import refresh_id_token

token_data = await refresh_id_token(
    refresh_token="firebase-refresh-token",
    api_key="firebase-web-api-key",
)
```

無効または期限切れのリフレッシュトークンには `InvalidRefreshTokenError` が送出されます。

### Managing the Token Lifecycle

`TokenManager` は ID トークンが期限切れになる前に更新します。既定では、有効期限まで300秒以下になると更新します。

```python
from kiarina.lib.firebase import TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_data=token_data,
)

id_token = await manager.get_id_token()
```

`refresh_token`、`token_data`、`token_data_cache` のいずれかを指定してください。

### Persisting Token Data

`TokenDataCache` を実装すると、`TokenManager` がトークンを復元し、更新後の値を保存します。

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

`settings_manager` は複数設定モードを使用します。pydantic-settings-manager v3 の構造化形式では、名前付き設定を `configs` の下に置きます。

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

アプリケーションの起動時に設定を読み込みます。

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

このパッケージだけを直接設定する場合は、構造化形式を `settings_manager.user_config` に代入します。

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

環境変数では単一の設定を指定できます。

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

Firebase カスタムトークンを ID トークンとリフレッシュトークンへ交換します。

- `InvalidCustomTokenError`: カスタムトークンが無効
- `FirebaseAPIError`: Firebase API がその他のエラーを返す、または通信に失敗する

#### `refresh_id_token`

```python
async def refresh_id_token(
    refresh_token: str,
    api_key: str,
) -> TokenData: ...
```

リフレッシュトークンを使って新しい ID トークンを取得します。

- `InvalidRefreshTokenError`: リフレッシュトークンが無効または期限切れ
- `FirebaseAPIError`: Firebase API がその他のエラーを返す、または通信に失敗する

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

ID トークンを保持し、有効期限まで `refresh_buffer_seconds` 以下になると更新します。複数のコルーチンが同時に利用しても、トークンの読み込みと更新はロックで直列化されます。

- `ValueError`: コンストラクターにトークンの取得元が指定されていない
- `AssertionError`: トークンを取得する前に、未設定の `refresh_token` または `token_data` と、それらに依存するプロパティへアクセスする

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

Firebase Authentication のトークン一式です。`from_api_response` は `issued_at` と有効期間の秒数から UTC の有効期限を計算します。`issued_at` を省略すると現在時刻を使用します。

#### `TokenDataCache`

```python
class TokenDataCache(Protocol):
    async def get(self) -> TokenData: ...

    async def set(self, token_data: TokenData) -> None: ...
```

トークン一式を読み書きする永続化インターフェースです。

#### `FirebaseSettings`

```python
class FirebaseSettings(BaseSettings):
    project_id: str
    api_key: SecretStr
```

`KIARINA_LIB_FIREBASE_` 接頭辞の環境変数に対応する Firebase Authentication 設定です。

#### `settings_manager`

```python
settings_manager: SettingsManager[FirebaseSettings] = SettingsManager(
    FirebaseSettings,
    multi=True,
)
```

複数の名前付き `FirebaseSettings` を管理する公開インスタンスです。

#### `FirebaseAuthError`

```python
class FirebaseAuthError(Exception): ...
```

このパッケージが送出する Firebase Authentication 例外の基底クラスです。

#### `InvalidCustomTokenError`

```python
class InvalidCustomTokenError(FirebaseAuthError): ...
```

カスタムトークンが無効な場合に送出されます。

#### `InvalidRefreshTokenError`

```python
class InvalidRefreshTokenError(FirebaseAuthError): ...
```

リフレッシュトークンが無効または期限切れの場合に送出されます。

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

Firebase API のその他のエラーや通信エラーを表します。利用できる場合は、HTTP ステータスコードを `status_code`、Firebase のエラーコードを `error_code` に保持します。
