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
  アプリケーション固有のストアへトークンを保存し、次回の利用時に復元します。
- **Sharing a Token Manager**
  設定からトークンマネージャーを構築するか名前で登録し、アプリケーションのどこからでも取得します。
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
    token_store=token_data,
)

id_token = await manager.get_id_token()
```

`token_store` には `TokenStore` または `TokenData` を指定します。`TokenData` は `InMemoryTokenStore` に包まれるため、トークンは常にストア経由で管理されます。

### Persisting Token Data

`FileTokenStore` はトークン一式を JSON ファイルに保持するため、再起動しても保存済みのリフレッシュトークンから再開できます。`TokenManager` は最初の `get_id_token()` でトークン一式を読み込み、更新のたびに保存します。

```python
from kiarina.lib.firebase import FileTokenStore, TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=FileTokenStore("~/.config/your-app/token.json"),
)
id_token = await manager.get_id_token()
```

`InMemoryTokenStore` はプロセス内にのみトークン一式を保持します。それ以外のバックエンドは `TokenStore` を実装してください。

### Sharing a Token Manager

`token_manager_registry` は、同じ名前の設定から `TokenManager` を構築します。`token_data_file_path` を設定するだけでよく、トークン一式は `FileTokenStore` によってそのファイルに保持されます。

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

# アプリケーションのどこからでも
id_token = await token_manager_registry.get().get_id_token()
```

名前を省略した `get()` は `settings_manager` と同じ設定を使うため、`default` と `settings_manager.active_key` に追従します。名前ごとに一度だけ構築され、以降は再利用されます。

別の `TokenStore` を使う場合はインスタンスを登録します。登録済みのインスタンスは設定より優先されます。

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

`token_store` からトークン一式を読み取り、有効期限まで `refresh_buffer_seconds` 以下になると更新します。読み取ったトークン一式はメモリに保持し、有効なあいだはそれを使います。更新が必要になると、まず `token_store` を読み直すため、他で更新された値があればそれを先に拾います。複数のコルーチンが同時に利用しても、ストアの読み取りと更新はロックで直列化されます。

`uid` を指定すると、マネージャーが読み込む／更新するトークン一式がそのユーザーのものであることを要求します。別のユーザーが残したトークン一式を検出できます。

`get_id_token()` と `refresh()` は `refresh_id_token` が送出する例外をそのまま伝播します。

**Raises**

- `ValueError`: トークン一式が `uid` のものではない場合

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

Firebase Authentication のトークン一式です。`from_api_response` は `id_token` の `exp` クレームを UTC の有効期限として使用します。`uid` はアクセスのたびに `id_token` の `sub` クレームを読み取ります。

**Raises**

- `ValueError`: `id_token` からクレームを読み取れない、または型が想定と異なる場合

#### `FileTokenStore`

```python
class FileTokenStore(TokenStore):
    file_path: str

    def __init__(self, file_path: str) -> None: ...
```

トークン一式を JSON ファイルに保持する `TokenStore` です。書き込みはアトミックかつプロセス間で排他され、新規ファイルは所有者のみのパーミッションで作成されます。`token_manager_registry` が設定から構築するマネージャーはこれを使用します。

**Raises**

- `FileNotFoundError`: ファイルが存在しない状態で `get()` を呼び出した場合

#### `InMemoryTokenStore`

```python
class InMemoryTokenStore(TokenStore):
    def __init__(self, token_data: TokenData) -> None: ...
```

プロセス内にのみトークン一式を保持する `TokenStore` です。`TokenManager` は `TokenData` をこれに包みます。

#### `TokenStore`

```python
class TokenStore(Protocol):
    async def get(self) -> TokenData: ...

    async def set(self, token_data: TokenData) -> None: ...
```

トークン一式を読み書きする永続化インターフェースです。`TokenManager` はこれをトークン一式の正本として扱います。

#### `FirebaseSettings`

```python
class FirebaseSettings(BaseSettings):
    project_id: str
    api_key: SecretStr
    uid: str | None = None
    token_data_file_path: str | None = None
```

`KIARINA_LIB_FIREBASE_` 接頭辞の環境変数に対応する Firebase Authentication 設定です。

**Fields**

- `project_id` (`str`): Firebase プロジェクト ID
- `api_key` (`SecretStr`): Firebase Web API キー
- `uid` (`str | None`): トークン一式が属するべき Firebase ユーザー ID。未設定の場合は任意のユーザーを受け入れる
- `token_data_file_path` (`str | None`): `token_manager_registry` がトークン一式を保存するファイルのパス

#### `token_manager_registry`

```python
token_manager_registry: ObjectRegistry[TokenManager, None]
```

`TokenManager` のレジストリです。`register()`、`get()`、`unregister()`、`is_registered()`、`list_names()`、`clear()` を使用します。

`get(name)` は登録済みのインスタンスを返すか、同じ名前の `FirebaseSettings` から構築して保持します。名前とエイリアスは `settings_manager` のものです。名前を省略した `get()` は同じ順序で解決します（`settings_manager.active_key`、設定の `default`、`"default"`）。

`resolve()` は登録済みインスタンスを参照しないため使用できません。

**Raises**

- `ValueError`: その名前の設定が存在しない、またはその設定に `token_data_file_path` がない

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
