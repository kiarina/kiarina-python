from kiarina.lib.redis import get_redis


def test_get_redis():
    redis1 = get_redis(use_retry=True, decode_responses=True)
    redis2 = get_redis()
    assert redis1 is redis2

    redis3 = get_redis(cache_key="other")
    assert redis1 is not redis3

    redis1.set("test_get_redis", "hello")
    value = redis1.get("test_get_redis")
    assert value == "hello"
