# kiarina-utils-app

[![PyPI version](https://badge.fury.io/py/kiarina-utils-app.svg)](https://badge.fury.io/py/kiarina-utils-app)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-app.svg)](https://pypi.org/project/kiarina-utils-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] What is this?
> アプリケーション（特に CLI ツール）の土台となるユーティリティです。起動時のアプリ識別子設定、ユーザーディレクトリの解決、重複起動の制御を提供します。

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
  起動時に一度だけアプリ名と作者を設定し、ディレクトリやロックの名前空間として利用します。
- **Resolving user directories**
  ユーザー固有のキャッシュ・設定・データディレクトリを、`XDG_*` 環境変数とプラットフォーム既定値を尊重して解決します。
- **Controlling single instance**
  OS レベルのアドバイザリファイルロックを使って、アプリの重複起動を防ぎます。

### Configuring the application identity

アプリケーションの起動時に、一度だけ `configure()` を呼び出します。
アプリ名と作者は一度だけ設定でき、再設定しようとすると `AppAlreadyConfiguredError`、設定前にアクセスすると `AppNotConfiguredError` になります（テストでは `reset()` でクリアできます）。

```python
from kiarina.utils.app import configure

configure(
    app_name="kiapi",
    app_author="kiarina",
)
```

### Resolving user directories

`user_directory` サービスは、ユーザー固有のディレクトリを `Path` で返します。

```python
from kiarina.utils.app import user_directory

cache_dir = user_directory.get_user_cache_dir()
config_dir = user_directory.get_user_config_dir()
data_dir = user_directory.get_user_data_dir()
```

解決の優先順位は次のとおりです。

1. 設定値による明示的な上書き（`~` はホームディレクトリに展開されます）。
2. `XDG_*` 環境変数（`XDG_CACHE_HOME` / `XDG_CONFIG_HOME` / `XDG_DATA_HOME`）が設定されている場合、アプリ名を結合したパス。**macOS を含むすべてのプラットフォームで XDG を優先します。**
3. 実行ユーザーのプラットフォーム既定値（[platformdirs](https://github.com/tox-dev/platformdirs) 経由）。

設定値は環境変数で上書きできます。

| Environment variable | Description |
| --- | --- |
| `KIARINA_UTILS_APP_USER_CACHE_DIR` | ユーザーキャッシュディレクトリを上書きします。 |
| `KIARINA_UTILS_APP_USER_CONFIG_DIR` | ユーザー設定ディレクトリを上書きします。 |
| `KIARINA_UTILS_APP_USER_DATA_DIR` | ユーザーデータディレクトリを上書きします。 |

### Controlling single instance

`single_instance` サービスは、ユーザーキャッシュディレクトリ配下のロックファイルを使って重複起動を防ぎます。
ロックは OS レベルのアドバイザリロックなので、プロセスが終了すれば自動的に解放されます。

```python
from kiarina.utils.app import single_instance
from kiarina.utils.app import AlreadyRunningError

try:
    single_instance.acquire()
except AlreadyRunningError:
    raise SystemExit("Another instance is already running.")

try:
    ...  # アプリ本体の処理
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

`configure()` で設定される共有アプリケーション識別子です。

#### `configure`

```python
def configure(app_name: str, app_author: str) -> None: ...
```

起動時に一度だけアプリケーションの識別子を設定します。アプリ名と作者は、ユーザーディレクトリやロックファイルの名前空間として使われます。

**Parameters**

- `app_name` (`str`): アプリケーション名。
- `app_author` (`str`): アプリケーションの作者。

**Raises**

- `AppAlreadyConfiguredError`: アプリ名または作者がすでに設定済みの場合。

#### `reset`

```python
def reset() -> None: ...
```

設定済みのアプリ名と作者をクリアします。テストでの利用を想定しています。

#### `single_instance`

`single_instance` サービスモジュールは、ユーザーキャッシュディレクトリ配下に置いた OS レベルのアドバイザリロックファイルを使って、重複起動を防ぎます。

```python
def acquire(*, timeout: float = 10.0) -> None: ...

def release() -> None: ...
```

- `acquire` は最大 `timeout` 秒まで待機してロックの取得を試み、すでに他のインスタンスが保持している場合は `AlreadyRunningError` を送出します。
- `release` は現在ロックを保持している場合に解放します。

**Parameters**

- `timeout` (`float`): ロック取得を待つ最大秒数（既定値: `10.0`）。

**Raises**

- `AlreadyRunningError`: 他のインスタンスがすでにロックを保持している場合。

#### `user_directory`

`user_directory` サービスモジュールは、設定値による上書き、`XDG_*` 環境変数、プラットフォーム既定値の順に尊重しながら、ユーザー固有のディレクトリを `Path` で解決します。

```python
def get_user_cache_dir() -> Path: ...

def get_user_config_dir() -> Path: ...

def get_user_data_dir() -> Path: ...
```

**Returns**

- `Path`: 解決されたユーザーキャッシュ・設定・データディレクトリ。

**Raises**

- `AppNotConfiguredError`: アプリ名または作者が未設定の場合（プラットフォーム既定値にフォールバックするとき）。

#### `AppSettings`

```python
class AppSettings(BaseSettings):
    user_cache_dir: str | None = None
    user_config_dir: str | None = None
    user_data_dir: str | None = None
```

ディレクトリ上書き用の Pydantic 設定モデルです。`KIARINA_UTILS_APP_` プレフィックスの環境変数を読み込みます。

**Fields**

- `user_cache_dir` (`str | None`): ユーザーキャッシュディレクトリの上書き（既定値: `None`）。
- `user_config_dir` (`str | None`): ユーザー設定ディレクトリの上書き（既定値: `None`）。
- `user_data_dir` (`str | None`): ユーザーデータディレクトリの上書き（既定値: `None`）。

#### `settings_manager`

```python
settings_manager: SettingsManager[AppSettings]
```

[pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) が提供する、`AppSettings` 用のグローバルな設定マネージャーインスタンスです。アクティブな設定には `settings_manager.settings` でアクセスします。

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
| `AppNotConfiguredError` | 設定前にアプリ名または作者へアクセスしたとき。 |
| `AppAlreadyConfiguredError` | アプリ名または作者の設定後に `configure()` を呼び出したとき。 |
| `AlreadyRunningError` | 他のインスタンスがロックを保持していて `single_instance.acquire()` が失敗したとき。 |
