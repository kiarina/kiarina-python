# kiarina-lib-cloudflare-d1

[![PyPI](https://img.shields.io/pypi/v/kiarina-lib-cloudflare-d1.svg)](https://pypi.org/project/kiarina-lib-cloudflare-d1/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

[English](README.md) | 日本語

> [!NOTE]
> Cloudflare D1 REST API へ SQL クエリを送信する同期・非同期クライアントを提供します。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) |
| [kiarina-lib-cloudflare](../kiarina-lib-cloudflare/) | `>=1.5.0` | [MIT](../../LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-lib-cloudflare-d1
```

## Features

- **Database Configuration**
  D1 のデータベース ID と Cloudflare の認証情報を別々に管理します。
- **Parameterized Queries**
  SQL と位置パラメーターを D1 REST API へ送信します。
- **Named Configurations**
  複数のデータベースと Cloudflare アカウントを設定キーで切り替えます。
- **Synchronous and Asynchronous APIs**
  同じ操作を同期 API と非同期 API から利用できます。

### Configuring a Database

D1 と Cloudflare 認証の設定は、それぞれ複数の名前付き設定を保持できます。

```yaml
kiarina.lib.cloudflare_d1:
  default: production
  configs:
    production:
      database_id: "your-database-id"

kiarina.lib.cloudflare:
  default: production
  configs:
    production:
      account_id: "your-account-id"
      api_token: "your-api-token"
```

アプリケーションの起動時に設定を読み込みます。

```python
import yaml
from pydantic_settings_manager import load_user_configs

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})
```

単一のデフォルト設定は環境変数でも指定できます。

```bash
export KIARINA_LIB_CLOUDFLARE_D1_DATABASE_ID="your-database-id"
export KIARINA_LIB_CLOUDFLARE_ACCOUNT_ID="your-account-id"
export KIARINA_LIB_CLOUDFLARE_API_TOKEN="your-api-token"
```

### Using the Synchronous Client

`query` は HTTP ステータスにかかわらず D1 の JSON レスポンスを返します。`success` を確認するか、`raise_for_status` を呼び出してください。

```python
from kiarina.lib.cloudflare_d1 import create_d1_client

client = create_d1_client()
result = client.query(
    "SELECT * FROM users WHERE id = ?",
    [1],
)
result.raise_for_status()

for row in result.first.rows:
    print(row)
```

### Using Named Configurations

D1 設定と認証設定のキーは個別に選択できます。

```python
from kiarina.lib.cloudflare_d1 import create_d1_client

client = create_d1_client(
    settings_key="production",
    auth_settings_key="production",
)
```

### Using the Asynchronous Client

非同期クライアントでは `query` を await します。

```python
from kiarina.lib.cloudflare_d1.asyncio import create_d1_client

client = create_d1_client()
result = await client.query(
    "SELECT * FROM users WHERE id = ?",
    [1],
)
result.raise_for_status()
```

## API Reference

### `kiarina.lib.cloudflare_d1`

```python
from kiarina.lib.cloudflare_d1 import (
    D1Client,
    D1Settings,
    create_d1_client,
    settings_manager,
)
```

#### `create_d1_client`

```python
def create_d1_client(
    settings_key: str | None = None,
    *,
    auth_settings_key: str | None = None,
) -> D1Client: ...
```

設定マネージャーから D1 設定と Cloudflare 認証設定を取得し、同期クライアントを作成します。

**Parameters**

- `settings_key` (`str | None`): D1 設定のキー。`None` の場合はデフォルト設定を使用します。
- `auth_settings_key` (`str | None`): Cloudflare 認証設定のキー。`None` の場合はデフォルト設定を使用します。

#### `D1Client`

```python
class D1Client:
    def __init__(
        self,
        settings: D1Settings,
        *,
        auth_settings: CloudflareSettings,
    ) -> None: ...

    def query(
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> Result: ...
```

`query` の結果では次の属性とメソッドを利用できます。

- `success` (`bool`): API リクエスト全体が成功したかどうか。
- `result` (`list[QueryResult]`): 各 SQL ステートメントの結果。
- `errors` (`list[ResponseInfo]`): API が返したエラー。
- `messages` (`list[ResponseInfo]`): API が返したメッセージ。
- `first` (`QueryResult`): 最初の結果。結果がない場合は `ValueError` を送出します。
- `raise_for_status() -> None`: `success` が `False` の場合に `RuntimeError` を送出します。

各 `QueryResult` は `success`、`meta`、`results` を持ちます。`rows` は `results` の別名です。

#### `D1Settings`

```python
class D1Settings(BaseSettings):
    database_id: str
```

Cloudflare D1 データベースの設定です。

**Fields**

- `database_id` (`str`): Cloudflare D1 データベース ID。

#### `settings_manager`

```python
settings_manager: SettingsManager[D1Settings]
```

複数の名前付き D1 設定を管理します。

### `kiarina.lib.cloudflare_d1.asyncio`

```python
from kiarina.lib.cloudflare_d1.asyncio import (
    D1Client,
    D1Settings,
    create_d1_client,
    settings_manager,
)
```

#### `create_d1_client`

```python
def create_d1_client(
    settings_key: str | None = None,
    *,
    auth_settings_key: str | None = None,
) -> D1Client: ...
```

非同期クライアントを作成します。引数は同期 API と同じです。

#### `D1Client`

```python
class D1Client:
    def __init__(
        self,
        settings: D1Settings,
        *,
        auth_settings: CloudflareSettings,
    ) -> None: ...

    async def query(
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> Result: ...
```

引数と返り値は同期クライアントと同じです。

`D1Settings` と `settings_manager` は同期 API が公開するものと同じオブジェクトです。
