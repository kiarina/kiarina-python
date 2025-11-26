import redis.asyncio

from ..._settings import settings_manager
from ..models.redisearch_client import RedisearchClient


def create_redisearch_client(
    config_key: str | None = None,
    *,
    redis: redis.asyncio.Redis,
) -> RedisearchClient:
    settings = settings_manager.get_settings(config_key)
    return RedisearchClient(settings, redis=redis)
