from typing import Any

import pytest

from kiarina.lib.redis import get_redis
from kiarina.lib.redisearch import RedisearchClient, RedisearchSettings
from kiarina.lib.redisearch_schema import RedisearchSchema


@pytest.fixture
def redis() -> Any:
    return get_redis(cache_key="kiarina.lib.redisearch")


@pytest.fixture
def client(key_prefix: Any, index_name: Any, redis: Any, fields: Any) -> Any:
    return RedisearchClient(
        RedisearchSettings(
            key_prefix=key_prefix,
            index_name=index_name,
        ),
        schema=RedisearchSchema.from_field_dicts(fields),
        redis=redis,
    )
