# kiarina-lib-redis

[![PyPI version](https://badge.fury.io/py/kiarina-lib-redis.svg)](https://badge.fury.io/py/kiarina-lib-redis)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-redis.svg)](https://pypi.org/project/kiarina-lib-redis/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] これは何？
> 同期・非同期の Redis client を設定、再試行、接続 cache とともに生成するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |
| [redis-py](https://github.com/redis/redis-py) | `>=6.4.0` | [MIT](https://github.com/redis/redis-py/blob/master/LICENSE) |

## Installation

```bash
pip install kiarina-lib-redis
```

## Features

- **Using a Synchronous Client**
  設定から同期 Redis client を生成できます。
- **Using an Asynchronous Client**
  同じ設定から非同期 Redis client を生成できます。
- **Managing Multiple Configurations**
  pydantic-settings-manager で複数の Redis 接続設定を管理できます。
- **Caching Clients**
  同じ cache key に対して同じ client instance を再利用できます。
- **Retrying Connection Errors**
  connection error と timeout error を exponential backoff で再試行できます。
- **Overriding Client Parameters**
  呼び出し時に URL、再試行、redis-py の初期化引数を上書きできます。

### Using a Synchronous Client

`kiarina.lib.redis` から同期 client を取得します。既定では `redis://localhost:6379` に接続します。

```python
from kiarina.lib.redis import get_redis

client = get_redis(decode_responses=True)
client.set("hello", "world")
assert client.get("hello") == "world"
```

### Using an Asynchronous Client

`kiarina.lib.redis.asyncio` から非同期 client を取得します。

```python
from kiarina.lib.redis.asyncio import get_redis

client = get_redis(decode_responses=True)
await client.set("hello", "world")
assert await client.get("hello") == "world"
```

### Managing Multiple Configurations

`settings_manager` は複数設定モードで構成されています。pydantic-settings-manager の structured format では、名前付き設定を `configs` に配置します。

```yaml
kiarina.lib.redis:
  default: development
  configs:
    development:
      url: redis://localhost:6379/0
    production:
      url: rediss://user:password@redis.example.com:6379/0
      use_retry: true
```

アプリケーションの bootstrap 処理で設定を読み込み、設定名を `get_redis` に渡します。

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.redis import get_redis

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

client = get_redis("production")
```

このパッケージだけを直接設定する場合は、`settings_manager.user_config` へ structured format を設定できます。

```python
from kiarina.lib.redis import get_redis, settings_manager

settings_manager.user_config = {
    "default": "development",
    "configs": {
        "development": {"url": "redis://localhost:6379/0"},
        "production": {
            "url": "rediss://user:password@redis.example.com:6379/0",
            "use_retry": True,
        },
    },
}

client = get_redis()
```

単一の設定は環境変数でも指定できます。`initialize_params` は JSON object として設定します。

```bash
export KIARINA_LIB_REDIS_URL="redis://localhost:6379/0"
export KIARINA_LIB_REDIS_USE_RETRY="true"
export KIARINA_LIB_REDIS_INITIALIZE_PARAMS='{"decode_responses":true}'
```

### Caching Clients

同期 client と非同期 client は別々に cache されます。既定の cache key は接続 URL です。同じ cache key で後から指定した引数は、既存の instance には適用されません。

```python
from kiarina.lib.redis import get_redis

default_client = get_redis()
assert get_redis() is default_client

queue_client = get_redis(cache_key="queue", db=1)
assert queue_client is not default_client
```

同じ URL に対して異なる初期化引数を使う場合は、明示的に異なる `cache_key` を指定してください。

### Retrying Connection Errors

`use_retry=True` の場合、`redis.ConnectionError` と `redis.TimeoutError` を再試行します。非同期 client では対応する `redis.asyncio` の例外を再試行します。

```python
from kiarina.lib.redis import get_redis

client = get_redis(use_retry=True)
```

再試行時は、`socket_timeout`、`socket_connect_timeout`、`health_check_interval`、`retry_attempts`、`retry_delay` の設定が適用されます。`retry_delay` は exponential backoff の最大待機時間です。

### Overriding Client Parameters

`url` と `use_retry` は呼び出しごとに上書きできます。追加の keyword arguments は `initialize_params` を上書きして `Redis.from_url()` に渡されます。

```python
from kiarina.lib.redis import get_redis

client = get_redis(
    url="redis://localhost:6379/1",
    use_retry=True,
    decode_responses=True,
)
```

## API Reference

### `kiarina.lib.redis`

```python
from kiarina.lib.redis import (
    RedisSettings,
    get_redis,
    settings_manager,
)
```

#### `get_redis`

```python
def get_redis(
    settings_key: str | None = None,
    *,
    cache_key: str | None = None,
    use_retry: bool | None = None,
    url: str | None = None,
    **kwargs: Any,
) -> redis.Redis: ...
```

同期 Redis client を返します。

**Parameters**

- `settings_key` (`str | None`): pydantic-settings-manager から取得する設定の名前。
- `cache_key` (`str | None`): client instance を区別する key。省略時は接続 URL。
- `use_retry` (`bool | None`): 再試行を有効にするか。省略時は設定値。
- `url` (`str | None`): Redis connection URL。省略時は設定値。
- `**kwargs` (`Any`): `initialize_params` を上書きして `Redis.from_url()` に渡す引数。

**Returns**

- `redis.Redis`: Cache された同期 Redis client。

#### `RedisSettings`

```python
class RedisSettings(BaseSettings):
    def __init__(
        self,
        *,
        url: SecretStr = SecretStr("redis://localhost:6379"),
        initialize_params: dict[str, Any] = {},
        use_retry: bool = False,
        socket_timeout: float = 6.0,
        socket_connect_timeout: float = 3.0,
        health_check_interval: int = 60,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ) -> None: ...
```

Redis client の設定。

**Fields**

- `url` (`SecretStr`): Redis connection URL。
- `initialize_params` (`dict[str, Any]`): `Redis.from_url()` に渡す追加の引数。
- `use_retry` (`bool`): Connection error と timeout error を再試行するか。
- `socket_timeout` (`float`): 再試行時の socket 読み書き timeout（秒）。
- `socket_connect_timeout` (`float`): 再試行時の socket connection timeout（秒）。
- `health_check_interval` (`int`): 再試行時の connection health check 間隔（秒）。
- `retry_attempts` (`int`): 再試行回数。
- `retry_delay` (`float`): Exponential backoff の最大待機時間（秒）。

#### `settings_manager`

```python
settings_manager: SettingsManager[RedisSettings]
```

名前付き Redis client 設定を管理する global instance です。

### `kiarina.lib.redis.asyncio`

```python
from kiarina.lib.redis.asyncio import (
    RedisSettings,
    get_redis,
    settings_manager,
)
```

#### `get_redis`

```python
def get_redis(
    settings_key: str | None = None,
    *,
    cache_key: str | None = None,
    use_retry: bool | None = None,
    url: str | None = None,
    **kwargs: Any,
) -> redis.asyncio.Redis: ...
```

非同期 Redis client を返します。

引数と cache の動作は `kiarina.lib.redis.get_redis` と同じです。

**Returns**

- `redis.asyncio.Redis`: Cache された非同期 Redis client。

#### `RedisSettings`

`kiarina.lib.redis.RedisSettings` と同じ class です。

#### `settings_manager`

`kiarina.lib.redis.settings_manager` と同じ instance です。
