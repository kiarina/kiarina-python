# kiarina-lib-falkordb

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-falkordb.svg)](https://badge.fury.io/py/kiarina-lib-falkordb)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-falkordb.svg)](https://pypi.org/project/kiarina-lib-falkordb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for creating synchronous and asynchronous FalkorDB clients with settings, retries, and connection caching.

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
  Create a synchronous FalkorDB client from settings.
- **Using an Asynchronous Client**
  Create an asynchronous FalkorDB client from the same settings.
- **Managing Multiple Configurations**
  Manage multiple named FalkorDB connection settings.
- **Caching Clients**
  Reuse a client instance for the same cache key.
- **Retrying Connection Errors**
  Retry Redis connection and timeout errors.
- **Overriding Client Parameters**
  Override the URL, retry behavior, and initialization arguments per call.

### Using a Synchronous Client

```python
from kiarina.lib.falkordb import get_falkordb

client = get_falkordb()
graph = client.select_graph("example")
result = graph.query("RETURN 1")
```

It connects to `falkor://localhost:6379` by default.

### Using an Asynchronous Client

```python
from kiarina.lib.falkordb.asyncio import get_falkordb

client = get_falkordb()
graph = client.select_graph("example")
result = await graph.query("RETURN 1")
```

### Managing Multiple Configurations

`settings_manager` uses multiple-settings mode. Place named settings under `configs`.

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

A single configuration can also be supplied through environment variables. Set `initialize_params` as a JSON object.

```bash
export KIARINA_LIB_FALKORDB_URL="falkor://localhost:6379"
export KIARINA_LIB_FALKORDB_USE_RETRY="true"
export KIARINA_LIB_FALKORDB_INITIALIZE_PARAMS='{}'
```

### Caching Clients

Synchronous and asynchronous clients use separate caches. The connection URL is the default cache key. Arguments supplied after a client has been cached under the same key do not affect the existing instance.

```python
from kiarina.lib.falkordb import get_falkordb

default_client = get_falkordb()
assert get_falkordb() is default_client

analytics_client = get_falkordb(cache_key="analytics")
assert analytics_client is not default_client
```

### Retrying Connection Errors

With `use_retry=True`, the client retries `redis.ConnectionError` and `redis.TimeoutError` with exponential backoff. The asynchronous client retries the corresponding `redis.asyncio` exceptions.

```python
from kiarina.lib.falkordb import get_falkordb

client = get_falkordb(use_retry=True)
```

The `socket_timeout`, `socket_connect_timeout`, `health_check_interval`, `retry_attempts`, and `retry_delay` settings apply in retry mode.

### Overriding Client Parameters

Additional keyword arguments override `initialize_params` and are passed to `FalkorDB.from_url()`.

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

Returns a synchronous FalkorDB client.

**Parameters**

- `settings_key` (`str | None`): Name of the settings to retrieve.
- `cache_key` (`str | None`): Key that identifies the client instance. Defaults to the connection URL.
- `use_retry` (`bool | None`): Whether to enable retries. Defaults to the setting.
- `url` (`str | None`): FalkorDB connection URL. Defaults to the setting.
- `**kwargs` (`Any`): Client initialization arguments that override `initialize_params`.

**Returns**

- `falkordb.FalkorDB`: Cached synchronous FalkorDB client.

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

FalkorDB client settings.

**Fields**

- `url` (`SecretStr`): FalkorDB connection URL.
- `initialize_params` (`dict[str, Any]`): Additional arguments passed to `FalkorDB.from_url()`.
- `use_retry` (`bool`): Whether to retry connection and timeout errors.
- `socket_timeout` (`float`): Socket read and write timeout in seconds in retry mode.
- `socket_connect_timeout` (`float`): Socket connection timeout in seconds in retry mode.
- `health_check_interval` (`int`): Health check interval in seconds in retry mode.
- `retry_attempts` (`int`): Number of retry attempts.
- `retry_delay` (`float`): Maximum exponential backoff delay in seconds.

#### `settings_manager`

```python
settings_manager: SettingsManager[FalkorDBSettings]
```

Global instance that manages named FalkorDB client settings.

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

Returns an asynchronous FalkorDB client. Its parameters and caching behavior match the synchronous version.

#### `FalkorDBSettings`

The same class as `kiarina.lib.falkordb.FalkorDBSettings`.

#### `settings_manager`

The same instance as `kiarina.lib.falkordb.settings_manager`.
