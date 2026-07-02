# kiarina-lib-firebase-rtdb

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase-rtdb.svg)](https://badge.fury.io/py/kiarina-lib-firebase-rtdb)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase-rtdb.svg)](https://pypi.org/project/kiarina-lib-firebase-rtdb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> An asynchronous package for retrieving data from Firebase Realtime Database and watching real-time changes.

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
  Retrieves data at a path through the Firebase Realtime Database REST API.
- **Watching Data Changes**
  Receives `put` and `patch` events through Server-Sent Events.
- **Recovering the Stream**
  Refreshes the ID token after authentication revocation and reconnects with exponential backoff after network errors.
- **Stopping the Stream**
  Stops a watch with an `asyncio.Event`.
- **Configuring Retries**
  Configures retry intervals through environment variables or pydantic-settings-manager.

### Retrieving Data

Get an ID token from `TokenManager` and specify a database path.

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

`watch_data` yields `put` events for complete replacements and `patch` events for partial updates.

```python
from kiarina.lib.firebase_rtdb import watch_data

async for event in watch_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    token_manager,
):
    print(event.event_type, event.path, event.data)
```

When authentication is revoked, it calls `TokenManager.refresh()` and reconnects immediately. Network errors use the configured exponential backoff.

### Stopping the Stream

Setting `stop_event` ends the watch when the stream next receives data. Cancel the watch task when an immediate stop is required.

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

Retry settings use a single-mode `settings_manager`.

```yaml
kiarina.lib.firebase_rtdb:
  max_retry_delay: 60.0
  initial_retry_delay: 1.0
  retry_delay_multiplier: 2.0
```

Load the settings when the application starts.

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.firebase_rtdb import settings_manager

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

settings = settings_manager.get_settings()
```

To configure only this package, assign the values directly to `settings_manager.user_config`.

```python
from kiarina.lib.firebase_rtdb import settings_manager

settings_manager.user_config = {
    "max_retry_delay": 60.0,
    "initial_retry_delay": 1.0,
    "retry_delay_multiplier": 2.0,
}
```

The same values are available as environment variables.

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

Retrieves JSON data at the specified path.

**Parameters**

- `database_url` (`str`): Firebase Realtime Database URL
- `path` (`str`): Path of the data to retrieve
- `id_token` (`str`): Firebase ID token

**Returns**

- `Any`: JSON value from the response

**Raises**

- `httpx.HTTPStatusError`: The HTTP response indicates an error
- `httpx.HTTPError`: The request fails

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

Watches the specified path and yields data changes from the Firebase SSE stream.

**Parameters**

- `database_url` (`str`): Firebase Realtime Database URL
- `path` (`str`): Path of the data to watch
- `token_manager` (`TokenManager`): Instance that manages the ID token
- `stop_event` (`asyncio.Event | None`): Event that requests the watch to stop

**Yields**

- `DataChangeEvent`: A `put` or `patch` data change

**Raises**

- `RTDBStreamCancelledError`: Firebase cancels the stream

Network errors are retried internally. Other unexpected exceptions are propagated to the caller.

#### `DataChangeEvent`

```python
@dataclass
class DataChangeEvent:
    event_type: Literal["put", "patch"]
    path: str
    data: Any
```

A data change received from Firebase Realtime Database.

**Fields**

- `event_type` (`Literal["put", "patch"]`): Event type
- `path` (`str`): Relative path that changed
- `data` (`Any`): Updated data

#### `RTDBSettings`

```python
class RTDBSettings(BaseSettings):
    max_retry_delay: float = 60.0
    initial_retry_delay: float = 1.0
    retry_delay_multiplier: float = 2.0
```

Settings used when reconnecting a stream.

**Fields**

- `max_retry_delay` (`float`): Maximum retry interval in seconds
- `initial_retry_delay` (`float`): Initial retry interval in seconds
- `retry_delay_multiplier` (`float`): Value multiplied by the retry interval after a network error

#### `settings_manager`

```python
settings_manager: SettingsManager[RTDBSettings]
```

Manages a single `RTDBSettings` configuration.

#### `RTDBStreamCancelledError`

```python
class RTDBStreamCancelledError(Exception): ...
```

Indicates that Firebase cancelled the SSE stream.
