import asyncio
import time

from .live_thread import LiveThread


class LiveThreadPool:
    """
    The live threads of a process, by thread id. A thread is taken out while a
    request uses it, so two requests never share one. Expired threads are
    stopped when the pool is next used, and the oldest when it is full. A thread
    left when the program exits ends with it, because its stdin closes.
    """

    def __init__(self) -> None:
        self._threads: dict[str, LiveThread] = {}

    def __len__(self) -> int:
        return len(self._threads)

    def take(self, thread_id: str) -> LiveThread | None:
        self._evict_expired()
        return self._threads.pop(thread_id, None)

    def put(self, live: LiveThread, *, idle_timeout: float, max_count: int) -> None:
        self._evict_expired()

        while self._threads and len(self._threads) >= max_count:
            oldest = min(self._threads.values(), key=lambda t: t.expires_at)
            self._threads.pop(oldest.thread_id).kill()

        live.expires_at = time.monotonic() + idle_timeout
        live.loop = asyncio.get_running_loop()
        self._threads[live.thread_id] = live

    def clear(self) -> None:
        for live in self._threads.values():
            live.kill()

        self._threads.clear()

    def _evict_expired(self) -> None:
        for thread_id, live in list(self._threads.items()):
            if not live.is_usable():
                self._threads.pop(thread_id).kill()
