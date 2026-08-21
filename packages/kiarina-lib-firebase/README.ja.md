# kiarina-lib-firebase

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase.svg)](https://badge.fury.io/py/kiarina-lib-firebase)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase.svg)](https://pypi.org/project/kiarina-lib-firebase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] What is this?
> カスタムトークンの交換と ID トークンの更新を行う、非同期の Firebase Authentication クライアントです。

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
  Firebase カスタムトークンをトークン一式へ交換します。
- **Refreshing an ID Token**
  リフレッシュトークンから新しいトークン一式を取得します。
- **Managing the Token Lifecycle**
  有効期限の前に ID トークンを自動更新し、並行する更新を直列化します。
- **Persisting the Token**
  トークン一式をファイル、メモリ、または独自のストアに保持します。
- **Sharing a Token Manager**
  設定からトークンマネージャーを構築し、アプリケーションのどこからでも取得します。
- **Managing Multiple Configurations**
  pydantic-settings-manager で複数の Firebase 設定を管理します。

### Exchanging a Custom Token

Firebase Admin SDK などの信頼できる環境で発行したカスタムトークンを交換します。

```python
from kiarina.lib.firebase import exchange_custom_token

token = await exchange_custom_token(
    custom_token="firebase-custom-token",
    api_key="firebase-web-api-key",
)

print(token.uid, token.project_id, token.expires_at)
```

`Token` が保持するのは `refresh_token` と `id_token` だけです。それ以外は ID トークンから読み取るため、値が ID トークンと食い違うことがありません。

無効なカスタムトークンには `InvalidCustomTokenError` が送出されます。その他の Firebase API エラーや通信失敗には `FirebaseAPIError` が送出されます。

### Refreshing an ID Token

既存のトークン一式から、新しいトークン一式を取得します。`TokenManager` が自動的に行うため、直接呼ぶのは自分でライフサイクルを管理する場合だけです。

```python
from kiarina.lib.firebase import refresh_id_token

token = await refresh_id_token(token, api_key="firebase-web-api-key")
```

返されるトークン一式にはリフレッシュトークンが引き継がれます。無効または期限切れのリフレッシュトークンには `InvalidRefreshTokenError` が送出されます。

### Managing the Token Lifecycle

`TokenManager` は ID トークンが期限切れになる前に更新します。既定では、有効期限まで300秒以下になると更新します。

```python
from kiarina.lib.firebase import InMemoryTokenStore, TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=InMemoryTokenStore(token),
)

token = await manager.get_token()
```

マネージャーはトークン一式の読み書きを `TokenStore` 経由で行い、それ以外の状態を持ちません。

### Persisting the Token

`FileTokenStore` はトークン一式を JSON ファイルに保持するため、再起動しても保存済みのリフレッシュトークンから再開できます。

```python
from kiarina.lib.firebase import FileTokenStore, TokenManager

manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=FileTokenStore("~/.config/your-app/token.json"),
)

token = await manager.get_token()
```

`InMemoryTokenStore` はプロセス内にのみトークン一式を保持します。それ以外のバックエンドは `TokenStore` を実装してください。

### Sharing a Token Manager

`create_token_manager` は設定から `TokenManager` を構築します。API キーとトークンファイルを 1 箇所にまとめられます。

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

`token_manager_registry` も同じことを行い、さらにマネージャーを保持するため、アプリケーション全体で 1 つを共有できます。

```python
from kiarina.lib.firebase import token_manager_registry

# アプリケーションのどこからでも
token = await token_manager_registry.get().get_token()
```

名前を省略した `get()` は `settings_manager` と同じ設定を使うため、`default` と `settings_manager.active_key` に追従します。名前ごとに一度だけ構築され、以降は再利用されます。

別の `TokenStore` を使う場合はインスタンスを登録します。登録済みのインスタンスは設定より優先されます。

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

`settings_manager` は複数設定モードを使用します。pydantic-settings-manager v3 の構造化形式では、名前付き設定を `configs` の下に置きます。

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

アプリケーションの起動時に設定を読み込みます。

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings("production")
```

このパッケージだけを直接設定する場合は、構造化形式を `settings_manager.user_config` へ代入します。

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

単一の設定であれば、環境変数でも指定できます。

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

Firebase カスタムトークンをトークン一式へ交換します。

**Raises**

- `InvalidCustomTokenError`: カスタムトークンが無効な場合
- `FirebaseAPIError`: Firebase API がその他のエラーを返す、または通信に失敗した場合

#### `refresh_id_token`

```python
async def refresh_id_token(
    token: Token,
    api_key: str,
) -> Token: ...
```

`token` のリフレッシュトークンを使って新しいトークン一式を取得します。

**Raises**

- `InvalidRefreshTokenError`: リフレッシュトークンが無効または期限切れの場合
- `FirebaseAPIError`: Firebase API がその他のエラーを返す、または通信に失敗した場合

#### `create_token_manager`

```python
def create_token_manager(
    firebase_settings_key: str | None = None,
    *,
    token_store: TokenStore | Token | None = None,
    refresh_buffer_seconds: int = 300,
) -> TokenManager: ...
```

指定したキーの `FirebaseSettings` から `TokenManager` を構築します。`token_store` には `TokenStore` または `Token` を指定でき、省略した場合は `token_file_path` から `FileTokenStore` を構築します。

**Raises**

- `ValueError`: そのキーの設定が存在しない、またはトークンストアを解決できない場合

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

`token_store` からトークン一式を読み取り、有効期限まで `refresh_buffer_seconds` 以下になると更新します。読み取ったトークン一式はメモリに保持し、有効なあいだはそれを使います。更新が必要になると、まず `token_store` を読み直すため、他で更新された値があればそれを先に拾います。複数のコルーチンが同時に利用しても、ストアの読み取りと更新はロックで直列化されます。

`get_token()` と `refresh()` は `refresh_id_token` が送出する例外をそのまま伝播します。

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

Firebase Authentication のトークン一式です。`project_id`、`uid`、`expires_at` は `id_token` の `aud`、`sub`、`exp` クレームから読み取るため、保存・永続化されるのは 2 つのトークンだけです。イミュータブルなので、キャッシュした値が `id_token` と食い違うことはありません。

**Raises**

- `ValueError`: `id_token` からクレームを読み取れない、または型が想定と異なる場合

#### `FileTokenStore`

```python
class FileTokenStore(TokenStore):
    file_path: str

    def __init__(self, file_path: str) -> None: ...
```

トークン一式を JSON ファイルに保持する `TokenStore` です。書き込みはアトミックかつプロセス間で排他され、新規ファイルは所有者のみのパーミッションで作成されます。

**Raises**

- `FileNotFoundError`: ファイルが存在しない状態で `get()` を呼び出した場合

#### `InMemoryTokenStore`

```python
class InMemoryTokenStore(TokenStore):
    def __init__(self, token: Token) -> None: ...
```

プロセス内にのみトークン一式を保持する `TokenStore` です。

#### `TokenStore`

```python
class TokenStore(Protocol):
    async def get(self) -> Token: ...

    async def set(self, token: Token) -> None: ...
```

トークン一式を読み書きする永続化インターフェースです。`TokenManager` はこれをトークン一式の正本として扱います。

#### `FirebaseSettings`

```python
class FirebaseSettings(BaseSettings):
    api_key: SecretStr
    token_file_path: str | None = None
```

`KIARINA_LIB_FIREBASE_` 接頭辞の環境変数に対応する Firebase Authentication 設定です。

**Fields**

- `api_key` (`SecretStr`): Firebase Web API キー
- `token_file_path` (`str | None`): トークン一式を保存するファイルのパス

#### `token_manager_registry`

```python
token_manager_registry: ObjectRegistry[TokenManager, FirebaseSettings]
```

`TokenManager` のレジストリです。`register()`、`get()`、`unregister()`、`is_registered()`、`list_names()`、`clear()` を使用します。

`get(name)` は登録済みのインスタンスを返すか、同じ名前の `FirebaseSettings` から構築して保持します。名前とエイリアスは `settings_manager` のものです。名前を省略した `get()` は同じ順序で解決します（`settings_manager.active_key`、設定の `default`、`"default"`）。

`resolve()` は登録済みインスタンスを参照しないため使用できません。

**Raises**

- `ValueError`: その名前の設定が存在しない、またはその設定に `token_file_path` がない場合

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

その他の Firebase API エラーと通信失敗を表します。取得できる場合、HTTP ステータスコードは `status_code` に、Firebase のエラーコードは `error_code` に格納されます。
