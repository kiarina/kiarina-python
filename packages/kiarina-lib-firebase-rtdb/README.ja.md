# kiarina-lib-firebase-rtdb

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase-rtdb.svg)](https://badge.fury.io/py/kiarina-lib-firebase-rtdb)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase-rtdb.svg)](https://pypi.org/project/kiarina-lib-firebase-rtdb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] What is this?
> Firebase Realtime Database のデータを取得・検索・更新し、リアルタイムの変更を監視する非同期パッケージです。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) |
| [kiarina-lib-firebase](../kiarina-lib-firebase/) | `>=2.1.0` | [MIT](../../LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.10.6` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-lib-firebase-rtdb
```

## Features

- **Retrieving Data**
  Firebase Realtime Database REST API から指定したパスのデータを取得します。
- **Querying Data**
  REST のクエリパラメータをエンコードする `RTDBQuery` で、並べ替え・件数制限・範囲指定を行います。
- **Updating Data**
  multi-path update を書き込み、`None` を送ってキーを削除します。
- **Watching Data Changes**
  Server-Sent Events で `put` と `patch` イベントを受信します。
- **Recovering the Stream**
  認証失効時に ID トークンを更新し、通信エラーやトークン更新の失敗時に指数バックオフで再接続します。
- **Stopping the Stream**
  `asyncio.Event` を使って監視を終了します。
- **Resolving the Token**
  トークンを明示的に渡すか、指定した `kiarina.lib.firebase` 設定のトークンマネージャーを使用します。
- **Configuring Retries**
  環境変数または pydantic-settings-manager で再試行間隔を設定します。

### Retrieving Data

`TokenManager` から ID トークンを取得し、データベースのパスを指定します。

```python
from kiarina.lib.firebase import TokenManager, refresh_id_token
from kiarina.lib.firebase_rtdb import get_data

token_data = await refresh_id_token(
    refresh_token="firebase-refresh-token",
    api_key="firebase-web-api-key",
)

token_manager = TokenManager(
    api_key="firebase-web-api-key",
    token_store=token_data,
)

data = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    id_token=await token_manager.get_id_token(),
)
```

### Querying Data

`RTDBQuery` は REST のクエリパラメータを組み立て、REST API が要求する JSON エンコードを行います。`$key` による並べ替えはインデックス定義が不要で、キーが ULID であれば時系列順になります。

```python
from kiarina.lib.firebase_rtdb import RTDBQuery, get_data

data = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/messages",
    query=RTDBQuery(order_by="$key", limit_to_last=5),
    id_token=await token_manager.get_id_token(),
)
```

`start_after` を指定すると、すでに取得済みの最後のキーより後に追加されたエントリだけを取得します。

```python
query = RTDBQuery(order_by="$key", start_after="01ABCDEF...")
```

`shallow` はすべての値を `true` に切り詰め、キーだけを返します。REST API は他のパラメータとの併用を拒否するため、`RTDBQuery` はその組み合わせを検証エラーにします。

```python
keys = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/messages",
    query=RTDBQuery(shallow=True),
    id_token=await token_manager.get_id_token(),
)
```

### Updating Data

`update_data` は multi-path update を送信します。キーは指定したパスからの相対パスで、値が `None` のキーは削除されます。

```python
from kiarina.lib.firebase_rtdb import update_data

await update_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/messages",
    {"01ABCDEF.../read": True, "01OLDEST...": None},
    id_token=await token_manager.get_id_token(),
)
```

### Watching Data Changes

`watch_data` は、完全な置換を表す `put` イベントと部分更新を表す `patch` イベントを返します。

```python
from kiarina.lib.firebase_rtdb import watch_data

async for event in watch_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    token_manager=token_manager,
):
    print(event.event_type, event.path, event.data)
```

認証が失効すると、`TokenManager.refresh()` を呼び出して再接続します。ID トークンの寿命は 1 時間なので、監視を継続する限りこの再接続は定期的に発生します。再接続の直後に Firebase が対象パス全体を `put` として送るため、切断中の変更はそのスナップショットに反映されます。

通信エラーと、トークン更新の一時的な失敗には、設定された指数バックオフを適用します。リフレッシュトークンが無効になった場合など、再試行しても回復しないエラーは呼び出し元へ送出します。

### Stopping the Stream

`stop_event` を設定すると、次にストリームからデータを受信した時点で監視を終了します。即時の終了が必要な場合は、監視タスクをキャンセルしてください。

```python
import asyncio

from kiarina.lib.firebase_rtdb import watch_data

stop_event = asyncio.Event()

async for event in watch_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    stop_event=stop_event,
    token_manager=token_manager,
):
    print(event.data)
    if event.data == "stop":
        stop_event.set()
```

### Resolving the Token

`id_token` と `token_manager` を省略すると、`firebase_settings_key` が指す `kiarina.lib.firebase` 設定の `TokenManager` を使用します。

```yaml
kiarina.lib.firebase:
  configs:
    production:
      project_id: production-project
      api_key: production-api-key
      token_data_file_path: ~/.config/your-app/token.json

kiarina.lib.firebase_rtdb:
  firebase_settings_key: production
```

```python
data = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
)
```

`token_manager_registry` がその設定からトークンマネージャーを構築します。別の `TokenStore` を使う場合は、同じキーでインスタンスを登録してください。

`firebase_settings_key` を省略した場合は `token_manager_registry` のデフォルト、つまり `kiarina.lib.firebase` の `settings_manager` が解決する設定を使用します。

### Configuring Retries

再試行設定は、単一設定モードの `settings_manager` で管理されます。

```yaml
kiarina.lib.firebase_rtdb:
  max_retry_delay: 60.0
  initial_retry_delay: 1.0
  retry_delay_multiplier: 2.0
```

アプリケーションの起動時に設定を読み込みます。

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase_rtdb import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings()
```

このパッケージだけを直接設定する場合は、値を `settings_manager.user_config` に代入します。

```python
from kiarina.lib.firebase_rtdb import settings_manager

settings_manager.user_config = {
    "max_retry_delay": 60.0,
    "initial_retry_delay": 1.0,
    "retry_delay_multiplier": 2.0,
}
```

環境変数でも指定できます。

```bash
export KIARINA_LIB_FIREBASE_RTDB_MAX_RETRY_DELAY=60.0
export KIARINA_LIB_FIREBASE_RTDB_INITIAL_RETRY_DELAY=1.0
export KIARINA_LIB_FIREBASE_RTDB_RETRY_DELAY_MULTIPLIER=2.0
```

## API Reference

### `kiarina.lib.firebase_rtdb`

```python
from kiarina.lib.firebase_rtdb import (
    DataChangeEvent,
    RTDBQuery,
    RTDBSettings,
    RTDBStreamCancelledError,
    get_data,
    settings_manager,
    update_data,
    watch_data,
)
```

#### `get_data`

```python
async def get_data(
    database_url: str,
    path: str,
    *,
    query: RTDBQuery | None = None,
    id_token: str | None = None,
) -> Any: ...
```

指定したパスの JSON データを取得します。

**Parameters**

- `database_url` (`str`): Firebase Realtime Database の URL
- `path` (`str`): 取得するデータのパス
- `query` (`RTDBQuery | None`): リクエストへ付与するクエリパラメータ
- `id_token` (`str | None`): Firebase ID トークン。省略時は `token_manager_registry` から解決する

**Returns**

- `Any`: レスポンスの JSON 値

**Raises**

- `ValueError`: トークンを省略し、`token_manager_registry` が `TokenManager` を解決できない場合
- `httpx.HTTPStatusError`: HTTP レスポンスがエラーを示す場合
- `httpx.HTTPError`: 通信に失敗した場合

#### `update_data`

```python
async def update_data(
    database_url: str,
    path: str,
    values: Mapping[str, Any],
    *,
    id_token: str | None = None,
) -> Any: ...
```

指定したパスへ multi-path update を適用します。

**Parameters**

- `database_url` (`str`): Firebase Realtime Database の URL
- `path` (`str`): 更新を適用するパス
- `values` (`Mapping[str, Any]`): `path` からの相対キーと新しい値。`None` はそのキーを削除する
- `id_token` (`str | None`): Firebase ID トークン。省略時は `token_manager_registry` から解決する

**Returns**

- `Any`: レスポンスの JSON 値

**Raises**

- `ValueError`: トークンを省略し、`token_manager_registry` が `TokenManager` を解決できない場合
- `httpx.HTTPStatusError`: HTTP レスポンスがエラーを示す場合
- `httpx.HTTPError`: 通信に失敗した場合

#### `watch_data`

```python
async def watch_data(
    database_url: str,
    path: str,
    *,
    stop_event: asyncio.Event | None = None,
    token_manager: TokenManager | None = None,
) -> AsyncIterator[DataChangeEvent]: ...
```

指定したパスを監視し、Firebase の SSE ストリームからデータ変更を返します。

**Parameters**

- `database_url` (`str`): Firebase Realtime Database の URL
- `path` (`str`): 監視するデータのパス
- `stop_event` (`asyncio.Event | None`): 監視の終了を通知するイベント
- `token_manager` (`TokenManager | None`): ID トークンを管理するインスタンス。省略時は `token_manager_registry` から解決する

**Yields**

- `DataChangeEvent`: `put` または `patch` のデータ変更

**Raises**

- `ValueError`: トークンを省略し、`token_manager_registry` が `TokenManager` を解決できない場合
- `RTDBStreamCancelledError`: Firebase がストリームをキャンセルした場合
- `InvalidRefreshTokenError`: リフレッシュトークンが使用できなくなった場合
- `FirebaseAPIError`: 再試行しても回復しないエラーでトークン更新が失敗した場合

通信エラーとトークン更新の一時的な失敗は内部で再試行されます。その他の予期しない例外は呼び出し元へ送出されます。

#### `DataChangeEvent`

```python
@dataclass
class DataChangeEvent:
    event_type: Literal["put", "patch"]
    path: str
    data: Any
```

Firebase Realtime Database から受信したデータ変更です。

**Fields**

- `event_type` (`Literal["put", "patch"]`): イベントの種類
- `path` (`str`): 変更された相対パス
- `data` (`Any`): 変更後のデータ

#### `RTDBQuery`

```python
class RTDBQuery(BaseModel):
    order_by: str | None = None
    limit_to_first: int | None = None
    limit_to_last: int | None = None
    start_at: QueryValue | None = None
    start_after: QueryValue | None = None
    end_at: QueryValue | None = None
    end_before: QueryValue | None = None
    equal_to: QueryValue | None = None
    shallow: bool = False
```

Firebase Realtime Database REST API のクエリパラメータです。`QueryValue` は `str | bool | int | float` です。

**Fields**

- `order_by` (`str | None`): 並べ替えに使う子キー、または `"$key"`, `"$value"`, `"$priority"`
- `limit_to_first` (`int | None`): 並べ替えた結果の先頭から取得する件数
- `limit_to_last` (`int | None`): 並べ替えた結果の末尾から取得する件数
- `start_at` (`QueryValue | None`): 並べ替えた結果の下限（含む）
- `start_after` (`QueryValue | None`): 並べ替えた結果の下限（含まない）
- `end_at` (`QueryValue | None`): 並べ替えた結果の上限（含む）
- `end_before` (`QueryValue | None`): 並べ替えた結果の上限（含まない）
- `equal_to` (`QueryValue | None`): 並べ替え対象の子が一致すべき値
- `shallow` (`bool`): すべての値を `true` に切り詰める

**Methods**

- `to_params() -> dict[str, str]`: 値を JSON エンコードした REST クエリパラメータを返す

**Raises**

- `ValidationError`: `shallow` を他のパラメータと併用した場合、`order_by` なしで絞り込みを指定した場合、または排他のパラメータを同時に指定した場合

#### `RTDBSettings`

```python
class RTDBSettings(BaseSettings):
    firebase_settings_key: str | None = None
    max_retry_delay: float = 60.0
    initial_retry_delay: float = 1.0
    retry_delay_multiplier: float = 2.0
```

トークンの解決とストリームの再接続に使用する設定です。

**Fields**

- `firebase_settings_key` (`str | None`): トークンを渡さない場合に使用する `TokenManager` に対応する `kiarina.lib.firebase` の設定キー。`kiarina.lib.firebase` のエイリアスも指定できる。未設定の場合は `token_manager_registry` のデフォルトを使用する
- `max_retry_delay` (`float`): 再試行間隔の最大値（秒）
- `initial_retry_delay` (`float`): 最初の再試行までの間隔（秒）
- `retry_delay_multiplier` (`float`): 通信エラー後に再試行間隔へ乗じる値

#### `settings_manager`

```python
settings_manager: SettingsManager[RTDBSettings]
```

`RTDBSettings` の単一設定を管理します。

#### `RTDBStreamCancelledError`

```python
class RTDBStreamCancelledError(Exception): ...
```

Firebase が SSE ストリームをキャンセルしたことを示します。
