from ..schemas.redisearch_context import RedisearchContext


def get_key(ctx: RedisearchContext, id: str) -> str:
    return f"{ctx.settings.key_prefix}{id}"
