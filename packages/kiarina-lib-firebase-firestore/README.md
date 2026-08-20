# kiarina-lib-firebase-firestore

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase-firestore.svg)](https://badge.fury.io/py/kiarina-lib-firebase-firestore)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase-firestore.svg)](https://pypi.org/project/kiarina-lib-firebase-firestore/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> An asynchronous read-only package for retrieving documents from Cloud Firestore with a Firebase ID token.

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
  Retrieves the document at a path through the Firestore REST API.
- **Listing Documents**
  Lists documents in a collection with pagination.
- **Decoding Firestore Values**
  Converts Firestore typed values (such as `integerValue`) into Python values.
- **Read Only by Design**
  Provides no write APIs. Writes are expected to go through the server side (such as an API server).
- **Resolving the Token**
  Passes a token explicitly, or gets a registered token manager by the configured name.
- **Configuring the Client**
  Configures the endpoint and timeout through environment variables or pydantic-settings-manager.

### Retrieving a Document

Pass a Firebase ID token obtained through `TokenManager` ([kiarina-lib-firebase](../kiarina-lib-firebase/)) or similar, and the document path.

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

Returns `None` when the document does not exist. Raises `httpx.HTTPStatusError` (403) when denied by security rules.

### Listing Documents

`list_documents` lists documents in a collection. By default, documents are returned in document-name order.

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

Omitting `id_token` gets a `TokenManager` from `token_manager_registry` by the configured name.

```yaml
kiarina.lib.firebase_firestore:
  firebase_token_manager_name: production
```

Register the token manager under that name when the application starts.

```python
from kiarina.lib.firebase import TokenManager, token_manager_registry

token_manager_registry.register(
    "production",
    TokenManager(api_key="firebase-web-api-key", token_store=token_store),
)

snapshot = await get_document("your-project-id", "users/user_1/posts/post_1")
```

Omitting `firebase_token_manager_name` too uses the default of `token_manager_registry`, which follows the `kiarina.lib.firebase` settings.

### Configuring the Client

Settings are managed by the single-configuration `settings_manager`.

```yaml
kiarina.lib.firebase_firestore:
  base_url: https://firestore.googleapis.com
  timeout: 30.0
```

Load the settings at application startup.

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase_firestore import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings()
```

To configure only this package directly, assign values to `settings_manager.user_config`.

```python
from kiarina.lib.firebase_firestore import settings_manager

settings_manager.user_config = {
    "base_url": "http://localhost:8080",
    "timeout": 30.0,
}
```

Environment variables are also supported. Point `base_url` at a Firestore emulator for local testing.

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

Retrieves the document at the specified path.

**Parameters**

- `project_id` (`str`): Google Cloud project ID
- `path` (`str`): Document path (e.g. `"users/user_1/posts/post_1"`)
- `database_id` (`str`): Database ID. Defaults to `"(default)"`
- `id_token` (`str | None`): Firebase ID token. Resolved from `token_manager_registry` when omitted

**Returns**

- `DocumentSnapshot | None`: The document, or `None` when it does not exist

**Raises**

- `ValueError`: When `id_token` is omitted and `token_manager_registry` cannot resolve a `TokenManager`
- `httpx.HTTPStatusError`: When the HTTP response indicates an error (except 404)
- `httpx.HTTPError`: When communication fails

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

Lists documents in a collection.

**Parameters**

- `project_id` (`str`): Google Cloud project ID
- `collection_path` (`str`): Collection path (e.g. `"users/user_1/posts"`)
- `database_id` (`str`): Database ID. Defaults to `"(default)"`
- `page_size` (`int | None`): Maximum number of documents per page
- `page_token` (`str | None`): The `next_page_token` from the previous page
- `order_by` (`str | None`): Sort order (e.g. `"createTime desc"`)
- `id_token` (`str | None`): Firebase ID token. Resolved from `token_manager_registry` when omitted

**Returns**

- `DocumentList`: A page of documents

**Raises**

- `ValueError`: When `id_token` is omitted and `token_manager_registry` cannot resolve a `TokenManager`
- `httpx.HTTPStatusError`: When the HTTP response indicates an error
- `httpx.HTTPError`: When communication fails

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

A document retrieved from Cloud Firestore.

**Fields**

- `name` (`str`): Full resource name of the document
- `fields` (`dict[str, Any]`): Fields converted into Python values
- `create_time` (`datetime`): Creation time
- `update_time` (`datetime`): Update time

**Properties**

- `path` (`str`): Path relative to the database root (e.g. `"users/user_1/posts/post_1"`)
- `id` (`str`): Document ID (the last segment of the path)

Field values are converted as follows.

| Firestore | Python |
| --- | --- |
| `nullValue` | `None` |
| `booleanValue` | `bool` |
| `integerValue` | `int` |
| `doubleValue` | `float` |
| `timestampValue` | `datetime` |
| `stringValue` | `str` |
| `bytesValue` | `bytes` |
| `referenceValue` | `str` (resource name) |
| `geoPointValue` | `dict` (`latitude` / `longitude`) |
| `arrayValue` | `list` |
| `mapValue` | `dict` |

#### `DocumentList`

```python
@dataclass
class DocumentList:
    documents: list[DocumentSnapshot]
    next_page_token: str | None
```

A page of documents listed from a collection.

**Fields**

- `documents` (`list[DocumentSnapshot]`): Documents in this page
- `next_page_token` (`str | None`): Token for retrieving the next page. `None` on the last page

#### `FirestoreSettings`

```python
class FirestoreSettings(BaseSettings):
    firebase_token_manager_name: str | None = None
    base_url: str = "https://firestore.googleapis.com"
    timeout: float = 30.0
```

Settings for the Firestore REST client.

**Fields**

- `firebase_token_manager_name` (`str | None`): Name of the `TokenManager` to get from `token_manager_registry` when no token is passed. The registry default is used when this is not set
- `base_url` (`str`): Base URL of the Firestore REST API. Point this at a Firestore emulator for local testing
- `timeout` (`float`): HTTP request timeout in seconds

#### `settings_manager`

```python
settings_manager = SettingsManager(FirestoreSettings)
```

The [SettingsManager](https://github.com/kiarina/pydantic-settings-manager) for `FirestoreSettings`.

## License

MIT License - See [LICENSE](../../LICENSE) for details.
