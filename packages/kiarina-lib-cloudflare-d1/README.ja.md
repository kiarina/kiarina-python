# kiarina-lib-cloudflare-d1

[English](README.md) | 日本語

kiarina namespace 向けの Cloudflare D1 database client library です。

## Purpose

Cloudflare authentication 設定と D1 resource 設定を分け、設定ベースで D1 query を実行するための薄い client を提供します。

## Installation

```bash
pip install kiarina-lib-cloudflare-d1
```

## Quick Start

### Basic Usage (Sync)

```python
from kiarina.lib.cloudflare_d1 import create_d1_client

client = create_d1_client()
result = client.query("SELECT * FROM users WHERE id = ?", [1])

if result.success:
    print(result.results)
```

### Async Usage

async client を使うことで、HTTP request を await できます。

### CRUD Operations

`query()` に SQL と parameters を渡して create / read / update / delete を実行します。

### Error Handling

Cloudflare D1 API の error response は result object または例外として扱います。

## API Reference

### Functions

#### `create_d1_client()`

現在の settings manager 設定から D1 client を作成します。settings key を指定して複数環境を扱えます。

### Classes

#### `D1Client`

Cloudflare D1 REST API に query を送信する client です。

#### `Result`

D1 API response 全体を表す result object です。

#### `QueryResult`

個別 query の結果、metadata、rows を表します。

#### `ResponseInfo`

response metadata を保持します。

## Configuration

### YAML Configuration

```yaml
kiarina.lib.cloudflare:
  account_id: "your-account-id"
  api_token: "your-api-token"

kiarina.lib.cloudflare_d1:
  database_id: "your-database-id"
```

### Settings Reference

#### `D1Settings`

D1 database ID など、D1 resource 側の設定を保持します。

#### Authentication Settings

Cloudflare 認証情報は `kiarina-lib-cloudflare` の settings を利用します。

## Testing

```bash
mise run package:check kiarina-lib-cloudflare-d1
mise run package:test kiarina-lib-cloudflare-d1 --coverage
```

## Dependencies

- `httpx`
- `kiarina-lib-cloudflare`
- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Cloudflare D1](https://developers.cloudflare.com/d1/)

