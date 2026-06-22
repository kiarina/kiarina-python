# kiarina-lib-redisearch

[English](README.md) | [日本語](README.ja.md)

kiarina namespace 向けの RediSearch client library です。

## Features

- schema definition と index management
- full-text search
- vector similarity search
- sync / async API
- schema migration helper
- Redis JSON document 操作

## Installation

```bash
pip install kiarina-lib-redisearch
```

## Quick Start

### Basic Usage (Sync)

```python
from redis import Redis
from kiarina.lib.redisearch import RediSearch, Schema, TextField, VectorField

schema = Schema(
    fields=[
        TextField(name="title"),
        VectorField(name="embedding", dims=1536),
    ],
)

redis = Redis.from_url("redis://localhost:6379", decode_responses=False)
client = RediSearch(redis=redis, index_name="idx:docs", schema=schema)

client.create_index()
client.set_document("doc:1", {"title": "Hello", "embedding": embedding_bytes})
results = client.search("hello")
```

### Async Usage

async Redis client と async RediSearch client を使って同じ操作を await できます。

## Schema Definition

### Field Types

Tag、Text、Numeric、Vector (FLAT / HNSW) field を定義できます。

```python
from kiarina.lib.redisearch import NumericField, TagField, TextField

fields = [
    TagField(name="category"),
    TextField(name="body"),
    NumericField(name="created_at"),
]
```

## Configuration

### Environment Variables

`KIARINA_LIB_REDISEARCH_` prefix の環境変数で設定できます。

### YAML Configuration

```yaml
kiarina.lib.redisearch:
  index_name: "idx:docs"
  key_prefix: "doc:"
```

## API Reference

### Index Operations

index の存在確認、作成、削除、reset、migration、info 取得を提供します。

### Document Operations

document の set / get / delete と Redis key 生成を提供します。

### Search Operations

document count、full-text search、vector similarity search を提供します。

### Advanced Filtering

filter API または condition list により、tag / numeric などの条件を組み立てられます。

### Filter Operators

field type に応じた filter operator を利用できます。

## Schema Migration

schema を code 上で更新したあと `migrate_index()` を呼び出すことで、差分検出に基づいて index を再作成できます。

## Testing

### Prerequisites

RediSearch module が有効な Redis が必要です。

### Running Tests

```bash
docker compose up -d redis
mise run package:test kiarina-lib-redisearch
mise run package:test kiarina-lib-redisearch --coverage
```

## Dependencies

- `numpy`
- `pydantic`
- `pydantic-settings`
- `pydantic-settings-manager`
- `redis`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Redis Stack / RediSearch](https://redis.io/docs/latest/develop/interact/search-and-query/)

