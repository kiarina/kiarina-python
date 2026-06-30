# kiarina-utils-app

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-utils-app.svg)](https://badge.fury.io/py/kiarina-utils-app)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-app.svg)](https://pypi.org/project/kiarina-utils-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> Foundation utilities for applications (especially CLI tools): configuring the application identity at startup, resolving user directories, and controlling single-instance execution.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [platformdirs](https://github.com/tox-dev/platformdirs) | `>=4.10.0` | [MIT](https://github.com/tox-dev/platformdirs/blob/main/LICENSE) |
| [filelock](https://github.com/tox-dev/filelock) | `>=3.19.1` | [Unlicense](https://github.com/tox-dev/filelock/blob/main/LICENSE) |
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
