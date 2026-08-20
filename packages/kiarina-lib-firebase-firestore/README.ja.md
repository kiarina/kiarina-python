# kiarina-lib-firebase-firestore

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase-firestore.svg)](https://badge.fury.io/py/kiarina-lib-firebase-firestore)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase-firestore.svg)](https://pypi.org/project/kiarina-lib-firebase-firestore/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] What is this?
> Firebase ID トークンで Cloud Firestore からドキュメントを取得する、読み取り専用の非同期パッケージです。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.10.6` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-lib-firebase-firestore
```

## Features

- **Retrieving a Document**
  Firestore REST API から指定したパスのドキュメントを取得します。
- **Listing Documents**
  コレクション内のドキュメントをページング付きで一覧します。
- **Decoding Firestore Values**
  Firestore の型付き値（`integerValue` など）を Python の値に変換して返します。
- **Read Only by Design**
  書き込み API は提供しません。書き込みはサーバーサイド（API サーバーなど）で行う前提です。
- **Resolving the Token**
  トークンを明示的に渡すか、設定した名前で登録済みのトークンマネージャーを取得します。
- **Configuring the Client**
  環境変数または pydantic-settings-manager で接続先とタイムアウトを設定します。

### Retrieving a Document

`TokenManager`（[kiarina-lib-firebase](../kiarina-lib-firebase/)）などで取得した Firebase ID トークンと、ドキュメントのパスを指定します。

```python
from kiarina.lib.firebase import TokenManager, refresh_id_token
from kiarina.lib.firebase_firestore import get_document

token_data = await refresh_id_token(
    refresh_token="firebase-refresh-token",
    api_key="firebase-web-api-key",
)

token_manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=token_data,
)

snapshot = await get_document(
    "your-project-id",
    "users/user_1/posts/post_1",
    id_token=await token_manager.get_id_token(),
)

if snapshot is not None:
    print(snapshot.id, snapshot.fields)
```

ドキュメントが存在しない場合は `None` を返します。セキュリティルールで拒否された場合は `httpx.HTTPStatusError`（403）を送出します。

### Listing Documents

`list_documents` は、コレクション内のドキュメントを一覧します。既定ではドキュメント名順に返されます。

```python
from kiarina.lib.firebase_firestore import list_documents

result = await list_documents(
    "your-project-id",
    "users/user_1/posts",
    page_size=100,
    id_token=id_token,
)

for snapshot in result.documents:
    print(snapshot.id, snapshot.fields)

if result.next_page_token is not None:
    next_page = await list_documents(
        "your-project-id",
        "users/user_1/posts",
        page_size=100,
        page_token=result.next_page_token,
        id_token=id_token,
    )
```

### Resolving the Token

`id_token` を省略すると、設定した名前で `token_manager_registry` から `TokenManager` を取得します。

```yaml
kiarina.lib.firebase_firestore:
  firebase_token_manager_name: production
```

アプリケーションの起動時に、その名前でトークンマネージャーを登録します。

```python
from kiarina.lib.firebase import TokenManager, token_manager_registry

token_manager_registry.register(
    "production",
    TokenManager(api_key="firebase-web-api-key", token_store=token_store),
)

snapshot = await get_document("your-project-id", "users/user_1/posts/post_1")
```

`firebase_token_manager_name` も省略した場合は `token_manager_registry` のデフォルトを使用します。これは `kiarina.lib.firebase` の設定に従います。

### Configuring the Client

設定は、単一設定モードの `settings_manager` で管理されます。

```yaml
kiarina.lib.firebase_firestore:
  base_url: https://firestore.googleapis.com
  timeout: 30.0
```

アプリケーションの起動時に設定を読み込みます。

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase_firestore import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings()
```

このパッケージだけを直接設定する場合は、値を `settings_manager.user_config` に代入します。

```python
from kiarina.lib.firebase_firestore import settings_manager

settings_manager.user_config = {
    "base_url": "http://localhost:8080",
    "timeout": 30.0,
}
```

環境変数でも指定できます。`base_url` を Firestore エミュレーターに向けることで、ローカルテストに使用できます。

```bash
export KIARINA_LIB_FIREBASE_FIRESTORE_BASE_URL=http://localhost:8080
export KIARINA_LIB_FIREBASE_FIRESTORE_TIMEOUT=30.0
```

## API Reference

### `kiarina.lib.firebase_firestore`

```python
from kiarina.lib.firebase_firestore import (
    DocumentList,
    DocumentSnapshot,
    FirestoreSettings,
    get_document,
    list_documents,
    settings_manager,
)
```

#### `get_document`

```python
async def get_document(
    project_id: str,
    path: str,
    *,
    database_id: str = "(default)",
    id_token: str | None = None,
) -> DocumentSnapshot | None: ...
```

指定したパスのドキュメントを取得します。

**Parameters**

- `project_id` (`str`): Google Cloud プロジェクト ID
- `path` (`str`): ドキュメントのパス（例: `"users/user_1/posts/post_1"`）
- `database_id` (`str`): データベース ID。デフォルトは `"(default)"`
- `id_token` (`str | None`): Firebase ID トークン。省略時は `token_manager_registry` から解決する

**Returns**

- `DocumentSnapshot | None`: ドキュメント。存在しない場合は `None`

**Raises**

- `ValueError`: `id_token` を省略し、`token_manager_registry` が `TokenManager` を解決できない場合
- `httpx.HTTPStatusError`: HTTP レスポンスがエラーを示す場合（404 を除く）
- `httpx.HTTPError`: 通信に失敗した場合

#### `list_documents`

```python
async def list_documents(
    project_id: str,
    collection_path: str,
    *,
    database_id: str = "(default)",
    page_size: int | None = None,
    page_token: str | None = None,
    order_by: str | None = None,
    id_token: str | None = None,
) -> DocumentList: ...
```

コレクション内のドキュメントを一覧します。

**Parameters**

- `project_id` (`str`): Google Cloud プロジェクト ID
- `collection_path` (`str`): コレクションのパス（例: `"users/user_1/posts"`）
- `database_id` (`str`): データベース ID。デフォルトは `"(default)"`
- `page_size` (`int | None`): 1 ページあたりの最大件数
- `page_token` (`str | None`): 前のページの `next_page_token`
- `order_by` (`str | None`): 並び順（例: `"createTime desc"`）
- `id_token` (`str | None`): Firebase ID トークン。省略時は `token_manager_registry` から解決する

**Returns**

- `DocumentList`: ドキュメントのページ

**Raises**

- `ValueError`: `id_token` を省略し、`token_manager_registry` が `TokenManager` を解決できない場合
- `httpx.HTTPStatusError`: HTTP レスポンスがエラーを示す場合
- `httpx.HTTPError`: 通信に失敗した場合

#### `DocumentSnapshot`

```python
@dataclass
class DocumentSnapshot:
    name: str
    fields: dict[str, Any]
    create_time: datetime
    update_time: datetime

    @property
    def path(self) -> str: ...

    @property
    def id(self) -> str: ...
```

Cloud Firestore から取得したドキュメントです。

**Fields**

- `name` (`str`): ドキュメントの完全なリソース名
- `fields` (`dict[str, Any]`): Python の値に変換されたフィールド
- `create_time` (`datetime`): 作成日時
- `update_time` (`datetime`): 更新日時

**Properties**

- `path` (`str`): データベースルートからの相対パス（例: `"users/user_1/posts/post_1"`）
- `id` (`str`): ドキュメント ID（パスの最後のセグメント）

フィールドの値は下記の対応で変換されます。

| Firestore | Python |
| --- | --- |
| `nullValue` | `None` |
| `booleanValue` | `bool` |
| `integerValue` | `int` |
| `doubleValue` | `float` |
| `timestampValue` | `datetime` |
| `stringValue` | `str` |
| `bytesValue` | `bytes` |
| `referenceValue` | `str`（リソース名） |
| `geoPointValue` | `dict`（`latitude` / `longitude`） |
| `arrayValue` | `list` |
| `mapValue` | `dict` |

#### `DocumentList`

```python
@dataclass
class DocumentList:
    documents: list[DocumentSnapshot]
    next_page_token: str | None
```

コレクションから一覧したドキュメントのページです。

**Fields**

- `documents` (`list[DocumentSnapshot]`): このページのドキュメント
- `next_page_token` (`str | None`): 次のページを取得するためのトークン。最後のページでは `None`

#### `FirestoreSettings`

```python
class FirestoreSettings(BaseSettings):
    firebase_token_manager_name: str | None = None
    base_url: str = "https://firestore.googleapis.com"
    timeout: float = 30.0
```

Firestore REST クライアントの設定です。

**Fields**

- `firebase_token_manager_name` (`str | None`): トークンを渡さない場合に `token_manager_registry` から取得する `TokenManager` の名前。未設定の場合はレジストリのデフォルトを使用する
- `base_url` (`str`): Firestore REST API のベース URL。Firestore エミュレーターに向けることでローカルテストに使用できます
- `timeout` (`float`): HTTP リクエストのタイムアウト（秒）

#### `settings_manager`

```python
settings_manager = SettingsManager(FirestoreSettings)
```

`FirestoreSettings` の [SettingsManager](https://github.com/kiarina/pydantic-settings-manager) です。

## License

MIT License - 詳細は [LICENSE](../../LICENSE) を参照してください。
