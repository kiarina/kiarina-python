import asyncio
from typing import Any

from kiarina.lib.firebase import TokenManager
from kiarina.lib.firebase_rtdb import watch_data


async def test_unauthorized(database_url: str, token_manager: TokenManager) -> None:
    # In unauthorized case, the stream does not end
    async def _task() -> None:
        async for _ in watch_data(
            database_url, "/posts/other_user", token_manager=token_manager
        ):
            pass

    watch_task = asyncio.create_task(_task())

    try:
        await asyncio.wait_for(watch_task, timeout=1.0)
    except asyncio.TimeoutError:
        watch_task.cancel()

        try:
            await watch_task
        except asyncio.CancelledError:
            pass


async def test_happy_path(
    database_url: str, user_id: str, token_manager: TokenManager
) -> None:
    values: list[Any] = []
    stop_event = asyncio.Event()

    async def _task() -> None:
        nonlocal values

        async for value in watch_data(
            database_url,
            f"/posts/{user_id}",
            stop_event=stop_event,
            token_manager=token_manager,
        ):
            assert isinstance(value, dict)
            assert value.get("content") == "hello"

            values.append(value)

    watch_task = asyncio.create_task(_task())

    await asyncio.sleep(1)

    stop_event.set()

    try:
        # Normally stops on keep-alive event,
        # but it takes time, so stop with timeout
        await asyncio.wait_for(watch_task, timeout=2.0)

    except asyncio.TimeoutError:
        watch_task.cancel()

        try:
            await watch_task
        except asyncio.CancelledError:
            pass

    assert len(values) > 0
