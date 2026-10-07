import asyncio
import tempfile
import time

from kiarina.agi.chat_provider_impl.codex._models.live_thread import (
    LiveThread,
)
from kiarina.agi.chat_provider_impl.codex._models.live_thread_pool import (
    LiveThreadPool,
)


class _Session:
    def __init__(self) -> None:
        self.killed = False

    def kill(self) -> None:
        self.killed = True

    async def close(self) -> None:
        self.killed = True


def _live(thread_id: str) -> tuple[LiveThread, _Session]:
    session = _Session()
    live = LiveThread(
        session=session,  # type: ignore[arg-type]
        directory=tempfile.TemporaryDirectory(),
        thread_id=thread_id,
    )
    return live, session


async def test_live_thread_pool() -> None:
    pool = LiveThreadPool()
    (a, a_session), (b, b_session), (c, c_session) = _live("a"), _live("b"), _live("c")

    pool.put(a, idle_timeout=60, max_count=2)
    pool.put(b, idle_timeout=60, max_count=2)
    pool.put(c, idle_timeout=60, max_count=2)

    # The oldest is stopped when the pool is full.
    assert a_session.killed
    assert len(pool) == 2
    assert pool.take("a") is None

    # Taking removes it, so two requests never share a thread.
    taken = pool.take("b")
    assert taken is b
    assert pool.take("b") is None

    # An expired thread is stopped when the pool is next used.
    c.expires_at = time.monotonic() - 1
    assert pool.take("c") is None
    assert c_session.killed

    pool.put(b, idle_timeout=60, max_count=2)
    pool.clear()
    assert b_session.killed
    assert len(pool) == 0


async def test_live_thread_pool_other_loop() -> None:
    pool = LiveThreadPool()
    live, session = _live("a")
    pool.put(live, idle_timeout=60, max_count=2)

    # A thread kept by another event loop cannot be used from this one.
    live.loop = asyncio.new_event_loop()

    try:
        assert pool.take("a") is None
        assert session.killed
    finally:
        live.loop.close()


async def test_live_thread_close() -> None:
    live, session = _live("a")
    await live.close()

    assert session.killed
