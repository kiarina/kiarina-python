# kiarina-utils-app

[![PyPI version](https://badge.fury.io/py/kiarina-utils-app.svg)](https://badge.fury.io/py/kiarina-utils-app)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-app.svg)](https://pypi.org/project/kiarina-utils-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> Foundation utilities for applications (especially CLI tools): configuring the application identity at startup, resolving user directories, and controlling single-instance execution.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [platformdirs](https://github.com/tox-dev/platformdirs) | `>=4.10.0` | [MIT](https://github.com/tox-dev/platformdirs/blob/main/LICENSE) |
| [filelock](https://github.com/tox-dev/filelock) | `>=3.19.1` | [MIT](https://github.com/tox-dev/filelock/blob/main/LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-utils-app
```

## Features

- **Configuring the application identity**
  Set the application name and author once at startup, used as the namespace for directories and locks.
- **Resolving user directories**
  Resolve user-specific cache, config, and data directories, honoring `XDG_*` environment variables and platform defaults.
- **Controlling single instance**
  Prevent duplicate application instances using an OS-level advisory file lock.

### Configuring the application identity

Call `configure()` once when the application starts.
The name and author can each be set only once; reconfiguring raises `AppAlreadyConfiguredError`, and accessing them before configuration raises `AppNotConfiguredError` (use `reset()` to clear them in tests).

```python
from kiarina.utils.app import configure

configure(
    app_name="kiapi",
    app_author="kiarina",
)
```

### Resolving user directories

The `user_directory` service returns user-specific directories as `Path` objects.

```python
from kiarina.utils.app import user_directory

cache_dir = user_directory.get_user_cache_dir()
config_dir = user_directory.get_user_config_dir()
data_dir = user_directory.get_user_data_dir()
```

The resolution order is:

1. An explicit override from settings (`~` is expanded to the home directory).
2. The `XDG_*` environment variable (`XDG_CACHE_HOME` / `XDG_CONFIG_HOME` / `XDG_DATA_HOME`), joined with the app name, when set. **XDG takes priority on all platforms, including macOS.**
3. The platform default for the running user (via [platformdirs](https://github.com/tox-dev/platformdirs)).

The settings can be overridden with environment variables:

| Environment variable | Description |
| --- | --- |
| `KIARINA_UTILS_APP_USER_CACHE_DIR` | Override the user cache directory. |
| `KIARINA_UTILS_APP_USER_CONFIG_DIR` | Override the user config directory. |
| `KIARINA_UTILS_APP_USER_DATA_DIR` | Override the user data directory. |

### Controlling single instance

The `single_instance` service prevents duplicate instances using a lock file under the user cache directory.
The lock is an OS-level advisory lock, so it is released automatically when the process exits.

```python
from kiarina.utils.app import single_instance
from kiarina.utils.app import AlreadyRunningError

try:
    single_instance.acquire()
except AlreadyRunningError:
    raise SystemExit("Another instance is already running.")

try:
    ...  # run the application
finally:
    single_instance.release()
```

## API Reference

### `kiarina.utils.app`

```python
from kiarina.utils.app import (
    app,
    App,
    configure,
    reset,
    single_instance,
    user_directory,
    AppSettings,
    settings_manager,
    AlreadyRunningError,
    AppAlreadyConfiguredError,
    AppNotConfiguredError,
)
```

#### `app` and `App`

```python
class App:
    app_name: str
    app_author: str

app: App
```

The shared application identity configured by `configure()`.

#### `configure`

```python
def configure(app_name: str, app_author: str) -> None: ...
```

Set the application identity once at startup. The name and author are used as the namespace for user directories and lock files.

**Parameters**

- `app_name` (`str`): Application name.
- `app_author` (`str`): Application author.

**Raises**

- `AppAlreadyConfiguredError`: The name or author has already been set.

#### `reset`

```python
def reset() -> None: ...
```

Clear the configured application name and author. Intended for use in tests.

#### `single_instance`

The `single_instance` service module prevents duplicate instances using an OS-level advisory lock file placed under the user cache directory.

```python
def acquire(*, timeout: float = 10.0) -> None: ...

def release() -> None: ...
```

- `acquire` attempts to take the lock, waiting up to `timeout` seconds, and raises `AlreadyRunningError` if another instance already holds it.
- `release` releases the lock if it is currently held.

**Parameters**

- `timeout` (`float`): Maximum seconds to wait for the lock (default: `10.0`).

**Raises**

- `AlreadyRunningError`: Another instance already holds the lock.

#### `user_directory`

The `user_directory` service module resolves user-specific directories as `Path` objects, honoring settings overrides, `XDG_*` environment variables, and platform defaults in that order.

```python
def get_user_cache_dir() -> Path: ...

def get_user_config_dir() -> Path: ...

def get_user_data_dir() -> Path: ...
```

**Returns**

- `Path`: The resolved user cache, config, or data directory.

**Raises**

- `AppNotConfiguredError`: The application name or author has not been configured (when falling back to platform defaults).

#### `AppSettings`

```python
class AppSettings(BaseSettings):
    user_cache_dir: str | None = None
    user_config_dir: str | None = None
    user_data_dir: str | None = None
```

Pydantic settings model for directory overrides. Reads environment variables with the prefix `KIARINA_UTILS_APP_`.

**Fields**

- `user_cache_dir` (`str | None`): Override for the user cache directory (default: `None`).
- `user_config_dir` (`str | None`): Override for the user config directory (default: `None`).
- `user_data_dir` (`str | None`): Override for the user data directory (default: `None`).

#### `settings_manager`

```python
settings_manager: SettingsManager[AppSettings]
```

Global settings manager instance for `AppSettings`, provided by [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager). Access the active settings via `settings_manager.settings`.

```python
from kiarina.utils.app import settings_manager

settings_manager.user_config = {
    "user_cache_dir": "~/.cache/kiapi",
}
```

#### Exceptions

```python
class AppNotConfiguredError(RuntimeError): ...
class AppAlreadyConfiguredError(RuntimeError): ...
class AlreadyRunningError(RuntimeError): ...
```

| Exception | Raised when |
| --- | --- |
| `AppNotConfiguredError` | The application name or author is accessed before being configured. |
| `AppAlreadyConfiguredError` | `configure()` is called after the name or author has already been set. |
| `AlreadyRunningError` | `single_instance.acquire()` fails because another instance holds the lock. |
