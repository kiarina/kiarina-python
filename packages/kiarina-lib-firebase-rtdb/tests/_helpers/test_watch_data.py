import asyncio
from typing import Any

from kiarina.lib.firebase import TokenManager
from kiarina.lib.firebase_rtdb import RTDBMirror, update_data, watch_data


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


async def test_mirror_follows_changes_and_skips_own_writes(
    database_url: str, user_id: str, token_manager: TokenManager
) -> None:
    parent = f"/posts/{user_id}"
    path = f"{parent}/mirror_test"
    token = await token_manager.get_token()
    await update_data(
        database_url,
        parent,
        {"mirror_test": {"a": {"read": False}, "b": {"read": False}}},
        token=token,
    )

    mirror = RTDBMirror()
    values: asyncio.Queue[Any] = asyncio.Queue()
    stop_event = asyncio.Event()

    async def _watch() -> None:
        async for value in watch_data(
            database_url,
            path,
            stop_event=stop_event,
            token_manager=token_manager,
            mirror=mirror,
        ):
            await values.put(value)

    async def _next() -> Any:
        return await asyncio.wait_for(values.get(), timeout=10.0)

    watch_task = asyncio.create_task(_watch())

    try:
        assert await _next() == {"a": {"read": False}, "b": {"read": False}}

        # An own write is visible at once, and its echo is not yielded.
        await update_data(
            database_url, path, {"a/read": True}, token=token, mirror=mirror
        )
        assert mirror.value == {"a": {"read": True}, "b": {"read": False}}

        # A deletion by someone else is the next value.
        await update_data(database_url, path, {"b": None}, token=token)
        assert await _next() == {"a": {"read": True}}

        # A patch adds a child next to the existing one.
        await update_data(database_url, path, {"c/read": False}, token=token)
        assert await _next() == {"a": {"read": True}, "c": {"read": False}}

        # Deleting the whole path yields None.
        await update_data(database_url, parent, {"mirror_test": None}, token=token)
        assert await _next() is None
        assert values.empty()

    finally:
        stop_event.set()
        watch_task.cancel()

        try:
            await watch_task
        except asyncio.CancelledError:
            pass

        await update_data(database_url, parent, {"mirror_test": None}, token=token)
