# kiarina-lib-firebase-rtdb

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase-rtdb.svg)](https://badge.fury.io/py/kiarina-lib-firebase-rtdb)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase-rtdb.svg)](https://pypi.org/project/kiarina-lib-firebase-rtdb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] What is this?
> Firebase Realtime Database からデータを取得し、リアルタイムの変更を監視する非同期パッケージです。

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
- **Watching Data Changes**
  Server-Sent Events で `put` と `patch` イベントを受信します。
- **Recovering the Stream**
  認証失効時に ID トークンを更新し、通信エラー時に指数バックオフで再接続します。
- **Stopping the Stream**
  `asyncio.Event` を使って監視を終了します。
- **Configuring Retries**
  環境変数または pydantic-settings-manager で再試行間隔を設定します。

### Retrieving Data

`TokenManager` から ID トークンを取得し、データベースのパスを指定します。

```python
from kiarina.lib.firebase import TokenManager
from kiarina.lib.firebase_rtdb import get_data

token_manager = TokenManager(
    api_key="firebase-web-api-key",
    refresh_token="firebase-refresh-token",
)

data = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    await token_manager.get_id_token(),
)
```

### Watching Data Changes

`watch_data` は、完全な置換を表す `put` イベントと部分更新を表す `patch` イベントを返します。

```python
from kiarina.lib.firebase_rtdb import watch_data

async for event in watch_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    token_manager,
):
    print(event.event_type, event.path, event.data)
```

認証が失効すると、`TokenManager.refresh()` を呼び出して直ちに再接続します。通信エラーには設定された指数バックオフを適用します。

### Stopping the Stream

`stop_event` を設定すると、次にストリームからデータを受信した時点で監視を終了します。即時の終了が必要な場合は、監視タスクをキャンセルしてください。

```python
import asyncio

from kiarina.lib.firebase_rtdb import watch_data

stop_event = asyncio.Event()

async for event in watch_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    token_manager,
    stop_event=stop_event,
):
    print(event.data)
    if event.data == "stop":
        stop_event.set()
```

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
    RTDBSettings,
    RTDBStreamCancelledError,
    get_data,
    settings_manager,
    watch_data,
)
```

#### `get_data`

```python
async def get_data(
    database_url: str,
    path: str,
    id_token: str,
) -> Any: ...
```

指定したパスの JSON データを取得します。

**Parameters**

- `database_url` (`str`): Firebase Realtime Database の URL
- `path` (`str`): 取得するデータのパス
- `id_token` (`str`): Firebase ID トークン

**Returns**

- `Any`: レスポンスの JSON 値

**Raises**

- `httpx.HTTPStatusError`: HTTP レスポンスがエラーを示す場合
- `httpx.HTTPError`: 通信に失敗した場合

#### `watch_data`

```python
async def watch_data(
    database_url: str,
    path: str,
    token_manager: TokenManager,
    *,
    stop_event: asyncio.Event | None = None,
) -> AsyncIterator[DataChangeEvent]: ...
```

指定したパスを監視し、Firebase の SSE ストリームからデータ変更を返します。

**Parameters**

- `database_url` (`str`): Firebase Realtime Database の URL
- `path` (`str`): 監視するデータのパス
- `token_manager` (`TokenManager`): ID トークンを管理するインスタンス
- `stop_event` (`asyncio.Event | None`): 監視の終了を通知するイベント

**Yields**

- `DataChangeEvent`: `put` または `patch` のデータ変更

**Raises**

- `RTDBStreamCancelledError`: Firebase がストリームをキャンセルした場合

通信エラーは内部で再試行されます。その他の予期しない例外は呼び出し元へ送出されます。

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

#### `RTDBSettings`

```python
class RTDBSettings(BaseSettings):
    max_retry_delay: float = 60.0
    initial_retry_delay: float = 1.0
    retry_delay_multiplier: float = 2.0
```

ストリームの再接続に使用する設定です。

**Fields**

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
