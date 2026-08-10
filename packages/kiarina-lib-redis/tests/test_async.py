from kiarina.lib.redis.asyncio import get_redis


async def test_get_redis() -> None:
    redis1 = get_redis(use_retry=True, decode_responses=True)
    redis2 = get_redis()
    assert redis1 is redis2

    redis3 = get_redis(cache_key="other")
    assert redis1 is not redis3

    await redis1.set("test_get_redis", "hello")
    value = await redis1.get("test_get_redis")
    assert value == "hello"
