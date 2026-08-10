import pytest
from redis.asyncio import Redis

from kiarina.lib.redis.asyncio import get_redis
from kiarina.lib.redisearch.asyncio import RedisearchClient, RedisearchSettings
from kiarina.lib.redisearch_schema import RedisearchSchema


@pytest.fixture
def redis() -> Redis:
    return get_redis(cache_key="kiarina.lib.redisearch")


@pytest.fixture
def client(
    key_prefix: str,
    index_name: str,
    redis: Redis,
    fields: list[dict[str, object]],
) -> RedisearchClient:
    return RedisearchClient(
        RedisearchSettings(
            key_prefix=key_prefix,
            index_name=index_name,
        ),
        schema=RedisearchSchema.from_field_dicts(fields),
        redis=redis,
    )
