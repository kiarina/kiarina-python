# kiarina-lib-redis

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-redis.svg)](https://badge.fury.io/py/kiarina-lib-redis)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-redis.svg)](https://pypi.org/project/kiarina-lib-redis/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for creating synchronous and asynchronous Redis clients with settings, retries, and connection caching.

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
  Create a synchronous Redis client from settings.
- **Using an Asynchronous Client**
  Create an asynchronous Redis client from the same settings.
- **Managing Multiple Configurations**
  Manage multiple Redis connection settings with pydantic-settings-manager.
- **Caching Clients**
  Reuse the same client instance for the same cache key.
- **Retrying Connection Errors**
  Retry connection and timeout errors with exponential backoff.
- **Overriding Client Parameters**
  Override the URL, retry behavior, and redis-py initialization parameters per call.

### Using a Synchronous Client

Get a synchronous client from `kiarina.lib.redis`. It connects to `redis://localhost:6379` by default.

```python
from kiarina.lib.redis import get_redis

client = get_redis(decode_responses=True)
client.set("hello", "world")
assert client.get("hello") == "world"
```

### Using an Asynchronous Client

Get an asynchronous client from `kiarina.lib.redis.asyncio`.

```python
from kiarina.lib.redis.asyncio import get_redis

client = get_redis(decode_responses=True)
await client.set("hello", "world")
assert await client.get("hello") == "world"
```

### Managing Multiple Configurations

`settings_manager` uses multiple-settings mode. In the pydantic-settings-manager structured format, named settings belong under `configs`.

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

Load the configuration during application bootstrap, then pass a settings name to `get_redis`.

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.redis import get_redis

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

client = get_redis("production")
```

To configure only this package directly, assign the structured format to `settings_manager.user_config`.

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

A single configuration can also be supplied through environment variables. Set `initialize_params` as a JSON object.

```bash
export KIARINA_LIB_REDIS_URL="redis://localhost:6379/0"
export KIARINA_LIB_REDIS_USE_RETRY="true"
export KIARINA_LIB_REDIS_INITIALIZE_PARAMS='{"decode_responses":true}'
```

### Caching Clients

Synchronous and asynchronous clients use separate caches. The connection URL is the default cache key. Arguments supplied after a client has been cached under the same key do not affect the existing instance.

```python
from kiarina.lib.redis import get_redis

default_client = get_redis()
assert get_redis() is default_client

queue_client = get_redis(cache_key="queue", db=1)
assert queue_client is not default_client
```

Specify a different `cache_key` when using different initialization parameters for the same URL.

### Retrying Connection Errors

With `use_retry=True`, the client retries `redis.ConnectionError` and `redis.TimeoutError`. The asynchronous client retries the corresponding `redis.asyncio` exceptions.

```python
from kiarina.lib.redis import get_redis

client = get_redis(use_retry=True)
```

Retry mode applies the `socket_timeout`, `socket_connect_timeout`, `health_check_interval`, `retry_attempts`, and `retry_delay` settings. `retry_delay` is the maximum exponential backoff delay.

### Overriding Client Parameters

Override `url` and `use_retry` per call. Additional keyword arguments override `initialize_params` and are passed to `Redis.from_url()`.

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

Returns a synchronous Redis client.

**Parameters**

- `settings_key` (`str | None`): Name of the settings to retrieve from pydantic-settings-manager.
- `cache_key` (`str | None`): Key that identifies the client instance. Defaults to the connection URL.
- `use_retry` (`bool | None`): Whether to enable retries. Defaults to the setting.
- `url` (`str | None`): Redis connection URL. Defaults to the setting.
- `**kwargs` (`Any`): Arguments that override `initialize_params` and are passed to `Redis.from_url()`.

**Returns**

- `redis.Redis`: Cached synchronous Redis client.

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

Redis client settings.

**Fields**

- `url` (`SecretStr`): Redis connection URL.
- `initialize_params` (`dict[str, Any]`): Additional arguments passed to `Redis.from_url()`.
- `use_retry` (`bool`): Whether to retry connection and timeout errors.
- `socket_timeout` (`float`): Socket read and write timeout in seconds in retry mode.
- `socket_connect_timeout` (`float`): Socket connection timeout in seconds in retry mode.
- `health_check_interval` (`int`): Connection health check interval in seconds in retry mode.
- `retry_attempts` (`int`): Number of retry attempts.
- `retry_delay` (`float`): Maximum exponential backoff delay in seconds.

#### `settings_manager`

```python
settings_manager: SettingsManager[RedisSettings]
```

Global instance that manages named Redis client settings.

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

Returns an asynchronous Redis client.

The parameters and caching behavior are the same as for `kiarina.lib.redis.get_redis`.

**Returns**

- `redis.asyncio.Redis`: Cached asynchronous Redis client.

#### `RedisSettings`

The same class as `kiarina.lib.redis.RedisSettings`.

#### `settings_manager`

The same instance as `kiarina.lib.redis.settings_manager`.
