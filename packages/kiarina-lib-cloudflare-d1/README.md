# kiarina-lib-cloudflare-d1

English | [日本語](README.ja.md)

[![PyPI](https://img.shields.io/pypi/v/kiarina-lib-cloudflare-d1.svg)](https://pypi.org/project/kiarina-lib-cloudflare-d1/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE]
> Provides synchronous and asynchronous clients for sending SQL queries to the Cloudflare D1 REST API.

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
  Manage D1 database IDs separately from Cloudflare credentials.
- **Parameterized Queries**
  Send SQL and positional parameters to the D1 REST API.
- **Named Configurations**
  Select among multiple databases and Cloudflare accounts by settings key.
- **Synchronous and Asynchronous APIs**
  Use the same operation through synchronous and asynchronous clients.

### Configuring a Database

The D1 and Cloudflare authentication managers can each hold multiple named settings.

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

Load the settings when the application starts.

```python
import yaml
from pydantic_settings_manager import load_user_configs

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})
```

A single default configuration can also be provided with environment variables.

```bash
export KIARINA_LIB_CLOUDFLARE_D1_DATABASE_ID="your-database-id"
export KIARINA_LIB_CLOUDFLARE_ACCOUNT_ID="your-account-id"
export KIARINA_LIB_CLOUDFLARE_API_TOKEN="your-api-token"
```

### Using the Synchronous Client

`query` returns the D1 JSON response regardless of HTTP status. Check `success` or call `raise_for_status`.

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

D1 settings and authentication settings can be selected independently.

```python
from kiarina.lib.cloudflare_d1 import create_d1_client

client = create_d1_client(
    settings_key="production",
    auth_settings_key="production",
)
```

### Using the Asynchronous Client

Await `query` when using the asynchronous client.

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

Creates a synchronous client from D1 settings and Cloudflare authentication settings.

**Parameters**

- `settings_key` (`str | None`): D1 settings key. `None` selects the default settings.
- `auth_settings_key` (`str | None`): Cloudflare authentication settings key. `None` selects the default settings.

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

The query result provides these attributes and methods:

- `success` (`bool`): Whether the overall API request succeeded.
- `result` (`list[QueryResult]`): Results for the SQL statements.
- `errors` (`list[ResponseInfo]`): Errors returned by the API.
- `messages` (`list[ResponseInfo]`): Messages returned by the API.
- `first` (`QueryResult`): The first result. Raises `ValueError` when no result is available.
- `raise_for_status() -> None`: Raises `RuntimeError` when `success` is `False`.

Each `QueryResult` has `success`, `meta`, and `results` attributes. `rows` is an alias for `results`.

#### `D1Settings`

```python
class D1Settings(BaseSettings):
    database_id: str
```

Settings for a Cloudflare D1 database.

**Fields**

- `database_id` (`str`): Cloudflare D1 database ID.

#### `settings_manager`

```python
settings_manager: SettingsManager[D1Settings]
```

Manages multiple named D1 settings.

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

Creates an asynchronous client. Its parameters are the same as the synchronous API.

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

Its parameters and return values are the same as the synchronous client.

`D1Settings` and `settings_manager` are the same objects exported by the synchronous API.
