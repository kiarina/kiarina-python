# kiarina-lib-falkordb

[English](README.md) | 日本語

kiarina namespace 向けの FalkorDB client library です。

## Features

- pydantic-settings-manager による FalkorDB 接続設定
- sync / async API
- connection cache
- runtime override

## Installation

```bash
pip install kiarina-lib-falkordb
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.falkordb import get_falkordb

db = get_falkordb()
graph = db.select_graph("example")
result = graph.query("RETURN 1")
```

### Async Usage

async API を使う場合は、async 用 module から client を取得します。

### Runtime Overrides

```python
from kiarina.lib.falkordb import settings_manager

settings_manager.cli_args = {"host": "localhost", "port": 6379}
```

## API Reference

### `get_falkordb()`

現在の設定から FalkorDB client を返します。cache key を使って複数接続を分けられます。

## Configuration

### YAML Configuration (Recommended)

```yaml
kiarina.lib.falkordb:
  host: "localhost"
  port: 6379
```

### Configuration Reference

host、port、username、password、database など FalkorDB / Redis 接続に必要な項目を設定できます。

## Testing

```bash
docker compose up -d falkordb
mise run test kiarina-lib-falkordb
mise run test kiarina-lib-falkordb --coverage
```

## Dependencies

- `kiarina-falkordb`
- `redis`
- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [FalkorDB](https://www.falkordb.com/)

