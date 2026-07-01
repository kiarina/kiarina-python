from collections.abc import Awaitable
from typing import Literal, overload

from ..schemas.redisearch_context import RedisearchContext
from .get_info import get_info


@overload
def exists_index(
    mode: Literal["sync"],
    ctx: RedisearchContext,
) -> bool: ...


@overload
def exists_index(
    mode: Literal["async"],
    ctx: RedisearchContext,
) -> Awaitable[bool]: ...


def exists_index(
    mode: Literal["sync", "async"],
    ctx: RedisearchContext,
) -> bool | Awaitable[bool]:

    def _handle_exception(e: Exception) -> bool:
        msg = str(e)
        # <= Redis 7
        if msg == "Unknown index name":
            return False
        # Redis 8
        elif "no such index" in msg:
            return False
        # Redis 8.2+: SEARCH_INDEX_NOT_FOUND Index not found: <name>
        elif "Index not found" in msg or "SEARCH_INDEX_NOT_FOUND" in msg:
            return False

        raise

    def _sync() -> bool:
        try:
            get_info(mode="sync", ctx=ctx)
            return True
        except Exception as e:
            return _handle_exception(e)

    async def _async() -> bool:
        try:
            await get_info(mode="async", ctx=ctx)
            return True
        except Exception as e:
            return _handle_exception(e)

    if mode == "sync":
        return _sync()
    else:
        return _async()
