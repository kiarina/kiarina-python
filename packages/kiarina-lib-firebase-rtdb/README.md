# kiarina-lib-firebase-rtdb

[![PyPI version](https://badge.fury.io/py/kiarina-lib-firebase-rtdb.svg)](https://badge.fury.io/py/kiarina-lib-firebase-rtdb)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-firebase-rtdb.svg)](https://pypi.org/project/kiarina-lib-firebase-rtdb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> An asynchronous package for reading, querying and updating Firebase Realtime Database, and watching real-time changes.

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
- **Querying Data**
  Orders, limits and ranges the result with `RTDBQuery`, which encodes the REST query parameters.
- **Updating Data**
  Writes a multi-path update, and deletes keys by sending `None`.
- **Watching Data Changes**
  Receives `put` and `patch` events through Server-Sent Events.
- **Recovering the Stream**
  Refreshes the ID token after authentication revocation and reconnects with exponential backoff after network errors and token refresh failures.
- **Stopping the Stream**
  Stops a watch with an `asyncio.Event`.
- **Resolving the Token**
  Passes a token explicitly, or uses the token manager of the named `kiarina.lib.firebase` settings.
- **Configuring Retries**
  Configures retry intervals through environment variables or pydantic-settings-manager.

### Retrieving Data

Get an ID token from `TokenManager` and specify a database path.

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

`RTDBQuery` builds the REST query parameters and JSON-encodes their values, which the REST API requires. Ordering by `$key` needs no index and is chronological when keys are ULIDs.

```python
from kiarina.lib.firebase_rtdb import RTDBQuery, get_data

data = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/messages",
    query=RTDBQuery(order_by="$key", limit_to_last=5),
    id_token=await token_manager.get_id_token(),
)
```

Pass `start_after` to fetch only the entries added after the last key already seen.

```python
query = RTDBQuery(order_by="$key", start_after="01ABCDEF...")
```

`shallow` truncates every value to `true` and returns the keys alone. The REST API rejects it together with any other parameter, so `RTDBQuery` raises a validation error for that combination.

```python
keys = await get_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/messages",
    query=RTDBQuery(shallow=True),
    id_token=await token_manager.get_id_token(),
)
```

### Updating Data

`update_data` sends a multi-path update. Keys are paths relative to the given path, and a `None` value deletes the key.

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

`watch_data` yields `put` events for complete replacements and `patch` events for partial updates.

```python
from kiarina.lib.firebase_rtdb import watch_data

async for event in watch_data(
    "https://your-project-default-rtdb.firebaseio.com",
    "/agents/state",
    token_manager=token_manager,
):
    print(event.event_type, event.path, event.data)
```

When authentication is revoked, it calls `TokenManager.refresh()` and reconnects. An ID token lives for one hour, so this reconnect happens periodically for as long as the watch runs. Right after a reconnect Firebase sends the whole path as a `put`, so changes made while disconnected are reflected in that snapshot.

Network errors and transient token refresh failures use the configured exponential backoff. Errors that retrying cannot recover from, such as an invalidated refresh token, are propagated to the caller.

### Stopping the Stream

Setting `stop_event` ends the watch when the stream next receives data. Cancel the watch task when an immediate stop is required.

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

Omitting `id_token` and `token_manager` uses the `TokenManager` of the `kiarina.lib.firebase` settings named by `firebase_settings_key`.

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

`token_manager_registry` builds the token manager from those settings. Register an instance under the same key to use a different `TokenStore`.

Omitting `firebase_settings_key` uses the default of `token_manager_registry`, which is the `kiarina.lib.firebase` settings that its `settings_manager` resolves.

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

Retrieves JSON data at the specified path.

**Parameters**

- `database_url` (`str`): Firebase Realtime Database URL
- `path` (`str`): Path of the data to retrieve
- `query` (`RTDBQuery | None`): Query parameters appended to the request
- `id_token` (`str | None`): Firebase ID token. Resolved from `token_manager_registry` when omitted

**Returns**

- `Any`: JSON value from the response

**Raises**

- `ValueError`: The token is omitted and `token_manager_registry` cannot resolve a `TokenManager`
- `httpx.HTTPStatusError`: The HTTP response indicates an error
- `httpx.HTTPError`: The request fails

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

Applies a multi-path update at the specified path.

**Parameters**

- `database_url` (`str`): Firebase Realtime Database URL
- `path` (`str`): Path the update is applied to
- `values` (`Mapping[str, Any]`): Keys relative to `path` and their new values. `None` deletes the key
- `id_token` (`str | None`): Firebase ID token. Resolved from `token_manager_registry` when omitted

**Returns**

- `Any`: JSON value from the response

**Raises**

- `ValueError`: The token is omitted and `token_manager_registry` cannot resolve a `TokenManager`
- `httpx.HTTPStatusError`: The HTTP response indicates an error
- `httpx.HTTPError`: The request fails

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

Watches the specified path and yields data changes from the Firebase SSE stream.

**Parameters**

- `database_url` (`str`): Firebase Realtime Database URL
- `path` (`str`): Path of the data to watch
- `stop_event` (`asyncio.Event | None`): Event that requests the watch to stop
- `token_manager` (`TokenManager | None`): Instance that manages the ID token. Resolved from `token_manager_registry` when omitted

**Yields**

- `DataChangeEvent`: A `put` or `patch` data change

**Raises**

- `ValueError`: The token is omitted and `token_manager_registry` cannot resolve a `TokenManager`
- `RTDBStreamCancelledError`: Firebase cancels the stream
- `InvalidRefreshTokenError`: The refresh token is no longer usable
- `FirebaseAPIError`: Token refresh fails with an error that retrying cannot recover from

Network errors and transient token refresh failures are retried internally. Other unexpected exceptions are propagated to the caller.

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

Query parameters for the Firebase Realtime Database REST API. `QueryValue` is `str | bool | int | float`.

**Fields**

- `order_by` (`str | None`): Child key to order by, or `"$key"`, `"$value"` or `"$priority"`
- `limit_to_first` (`int | None`): Number of items to take from the beginning of the ordered result
- `limit_to_last` (`int | None`): Number of items to take from the end of the ordered result
- `start_at` (`QueryValue | None`): Inclusive lower bound of the ordered result
- `start_after` (`QueryValue | None`): Exclusive lower bound of the ordered result
- `end_at` (`QueryValue | None`): Inclusive upper bound of the ordered result
- `end_before` (`QueryValue | None`): Exclusive upper bound of the ordered result
- `equal_to` (`QueryValue | None`): Exact value the ordered child must match
- `shallow` (`bool`): Truncate each value to `true`

**Methods**

- `to_params() -> dict[str, str]`: Returns the REST query parameters with JSON-encoded values

**Raises**

- `ValidationError`: `shallow` is combined with another parameter, a filter is used without `order_by`, or mutually exclusive parameters are set together

#### `RTDBSettings`

```python
class RTDBSettings(BaseSettings):
    firebase_settings_key: str | None = None
    max_retry_delay: float = 60.0
    initial_retry_delay: float = 1.0
    retry_delay_multiplier: float = 2.0
```

Settings used when resolving the token and reconnecting a stream.

**Fields**

- `firebase_settings_key` (`str | None`): Key of the `kiarina.lib.firebase` settings whose `TokenManager` is used when no token is passed. An alias of `kiarina.lib.firebase` is also accepted. The default of `token_manager_registry` is used when this is not set
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
