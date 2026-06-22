# kiarina-lib-redis

[English](README.md) | [日本語](README.ja.md)

kiarina namespace 向けの Redis client library です。

## Purpose

pydantic-settings-manager による設定管理を使って、Redis client を一貫した方法で作成・管理します。

## Installation

```bash
pip install kiarina-lib-redis
```

## Quick Start

### Synchronous Usage

```python
from kiarina.lib.redis import get_redis

redis = get_redis()
redis.set("hello", "world")
print(redis.get("hello"))
```

### Asynchronous Usage

```python
from kiarina.lib.redis.asyncio import get_redis

redis = get_redis()
await redis.set("hello", "world")
print(await redis.get("hello"))
```

## API Reference

### `get_redis()`

現在の設定から Redis client を返します。設定 key や cache key を使って複数接続を扱えます。

### `RedisSettings`

Redis connection URL などを保持する settings model です。

### `settings_manager`

複数 environment の Redis 設定を管理する global settings manager です。

## Configuration

### YAML Configuration

```yaml
kiarina.lib.redis:
  url: "redis://localhost:6379/0"
```

### Environment Variables

`KIARINA_LIB_REDIS_` prefix の環境変数で設定できます。

### URL Formats

`redis://`、`rediss://` など redis-py が対応する URL 形式を利用できます。

## Testing

```bash
docker compose up -d redis
mise run package:test kiarina-lib-redis
mise run package:test kiarina-lib-redis --coverage
```

## Dependencies

- `redis`
- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Redis](https://redis.io/)

