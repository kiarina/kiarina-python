# kiarina-lib-falkordb

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-lib-falkordb.svg)](https://badge.fury.io/py/kiarina-lib-falkordb)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-falkordb.svg)](https://pypi.org/project/kiarina-lib-falkordb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] これは何？
> 同期・非同期の FalkorDB client を設定、再試行、接続 cache とともに生成するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-falkordb](https://github.com/kiarina/falkordb-py) | `>=1.3.0` | [MIT](https://github.com/kiarina/falkordb-py/blob/main/LICENSE) |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |
| [redis-py](https://github.com/redis/redis-py) | `>=6.4.0` | [MIT](https://github.com/redis/redis-py/blob/master/LICENSE) |

## Installation

```bash
pip install kiarina-lib-falkordb
```

## Features

- **Using a Synchronous Client**
  設定から同期 FalkorDB client を生成できます。
- **Using an Asynchronous Client**
  同じ設定から非同期 FalkorDB client を生成できます。
- **Managing Multiple Configurations**
  複数の FalkorDB 接続設定を名前で管理できます。
- **Caching Clients**
  同じ cache key に対して client instance を再利用できます。
- **Retrying Connection Errors**
  Redis connection error と timeout error を再試行できます。
- **Overriding Client Parameters**
  URL、再試行、初期化引数を呼び出し時に上書きできます。

### Using a Synchronous Client

```python
from kiarina.lib.falkordb import get_falkordb

client = get_falkordb()
graph = client.select_graph("example")
result = graph.query("RETURN 1")
```

既定では `falkor://localhost:6379` に接続します。

### Using an Asynchronous Client

```python
from kiarina.lib.falkordb.asyncio import get_falkordb

client = get_falkordb()
graph = client.select_graph("example")
result = await graph.query("RETURN 1")
```

### Managing Multiple Configurations

`settings_manager` は複数設定モードです。名前付き設定を `configs` に配置します。

```yaml
kiarina.lib.falkordb:
  default: development
  configs:
    development:
      url: falkor://localhost:6379
    production:
      url: falkors://user:password@falkordb.example.com:6379
      use_retry: true
```

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.falkordb import get_falkordb

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

client = get_falkordb("production")
```

単一の設定は環境変数でも指定できます。`initialize_params` は JSON object として設定します。

```bash
export KIARINA_LIB_FALKORDB_URL="falkor://localhost:6379"
export KIARINA_LIB_FALKORDB_USE_RETRY="true"
export KIARINA_LIB_FALKORDB_INITIALIZE_PARAMS='{}'
```

### Caching Clients

同期 client と非同期 client は別々に cache されます。既定の cache key は接続 URL です。同じ cache key で後から指定した引数は、既存の instance には適用されません。

```python
from kiarina.lib.falkordb import get_falkordb

default_client = get_falkordb()
assert get_falkordb() is default_client

analytics_client = get_falkordb(cache_key="analytics")
assert analytics_client is not default_client
```

### Retrying Connection Errors

`use_retry=True` の場合、`redis.ConnectionError` と `redis.TimeoutError` を exponential backoff で再試行します。非同期 client では対応する `redis.asyncio` の例外を再試行します。

```python
from kiarina.lib.falkordb import get_falkordb

client = get_falkordb(use_retry=True)
```

`socket_timeout`、`socket_connect_timeout`、`health_check_interval`、`retry_attempts`、`retry_delay` は再試行時に適用されます。

### Overriding Client Parameters

追加の keyword arguments は `initialize_params` を上書きして `FalkorDB.from_url()` に渡されます。

```python
from kiarina.lib.falkordb import get_falkordb

client = get_falkordb(
    url="falkor://localhost:6379",
    use_retry=True,
)
```

## API Reference

### `kiarina.lib.falkordb`

```python
from kiarina.lib.falkordb import (
    FalkorDBSettings,
    get_falkordb,
    settings_manager,
)
```

#### `get_falkordb`

```python
def get_falkordb(
    settings_key: str | None = None,
    *,
    cache_key: str | None = None,
    use_retry: bool | None = None,
    url: str | None = None,
    **kwargs: Any,
) -> falkordb.FalkorDB: ...
```

同期 FalkorDB client を返します。

**Parameters**

- `settings_key` (`str | None`): 取得する設定の名前。
- `cache_key` (`str | None`): Client instance を区別する key。省略時は接続 URL。
- `use_retry` (`bool | None`): 再試行を有効にするか。省略時は設定値。
- `url` (`str | None`): FalkorDB connection URL。省略時は設定値。
- `**kwargs` (`Any`): `initialize_params` を上書きする client 初期化引数。

**Returns**

- `falkordb.FalkorDB`: Cache された同期 FalkorDB client。

#### `FalkorDBSettings`

```python
class FalkorDBSettings(BaseSettings):
    def __init__(
        self,
        *,
        url: SecretStr = SecretStr("falkor://localhost:6379"),
        initialize_params: dict[str, Any] = {},
        use_retry: bool = False,
        socket_timeout: float = 6.0,
        socket_connect_timeout: float = 3.0,
        health_check_interval: int = 60,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ) -> None: ...
```

FalkorDB client の設定。

**Fields**

- `url` (`SecretStr`): FalkorDB connection URL。
- `initialize_params` (`dict[str, Any]`): `FalkorDB.from_url()` に渡す追加の引数。
- `use_retry` (`bool`): Connection error と timeout error を再試行するか。
- `socket_timeout` (`float`): 再試行時の socket 読み書き timeout（秒）。
- `socket_connect_timeout` (`float`): 再試行時の socket connection timeout（秒）。
- `health_check_interval` (`int`): 再試行時の health check 間隔（秒）。
- `retry_attempts` (`int`): 再試行回数。
- `retry_delay` (`float`): Exponential backoff の最大待機時間（秒）。

#### `settings_manager`

```python
settings_manager: SettingsManager[FalkorDBSettings]
```

名前付き FalkorDB client 設定を管理する global instance です。

### `kiarina.lib.falkordb.asyncio`

```python
from kiarina.lib.falkordb.asyncio import (
    FalkorDBSettings,
    get_falkordb,
    settings_manager,
)
```

#### `get_falkordb`

```python
def get_falkordb(
    settings_key: str | None = None,
    *,
    cache_key: str | None = None,
    use_retry: bool | None = None,
    url: str | None = None,
    **kwargs: Any,
) -> falkordb.asyncio.FalkorDB: ...
```

非同期 FalkorDB client を返します。引数と cache の動作は同期版と同じです。

#### `FalkorDBSettings`

`kiarina.lib.falkordb.FalkorDBSettings` と同じ class です。

#### `settings_manager`

`kiarina.lib.falkordb.settings_manager` と同じ instance です。
