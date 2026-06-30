# kiarina-utils-app

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-utils-app.svg)](https://badge.fury.io/py/kiarina-utils-app)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-app.svg)](https://pypi.org/project/kiarina-utils-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> アプリケーション（特に CLI ツール）の土台となるユーティリティです。起動時のアプリ識別子設定、ユーザーディレクトリの解決、重複起動の制御を提供します。

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
