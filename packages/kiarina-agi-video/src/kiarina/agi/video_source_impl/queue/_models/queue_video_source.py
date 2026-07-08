import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import cast

from kiarina.agi.video_source import BaseVideoSource, VideoFrame

from .._settings import QueueVideoSourceSettings


class QueueVideoSource(BaseVideoSource):
    def __init__(self, settings: QueueVideoSourceSettings) -> None:
        super().__init__()

        self.settings: QueueVideoSourceSettings = settings
        self._queue: asyncio.Queue[VideoFrame | None] | None = None

    @property
    def queue(self) -> asyncio.Queue[VideoFrame | None]:
        if self._queue is None:
            raise AssertionError("queue is not set")

        return self._queue

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if not isinstance(target, asyncio.Queue):
            raise TypeError("QueueVideoSource target must be an asyncio.Queue")

        self._queue = target

        try:
            yield
        finally:
            self._queue = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]:
        while True:
            frame = await _read_queue(self.queue, stop_events)

            if frame is None:
                break

            yield frame


async def _read_queue(
    queue: asyncio.Queue[VideoFrame | None],
    stop_events: tuple[asyncio.Event, ...],
) -> VideoFrame | None:
    if not stop_events:
        return await queue.get()

    frame_task: asyncio.Future[VideoFrame | None] = asyncio.ensure_future(queue.get())
    stop_tasks = [asyncio.create_task(event.wait()) for event in stop_events]

    wait_tasks = {
        cast(asyncio.Future[object], frame_task),
        *(cast(asyncio.Future[object], task) for task in stop_tasks),
    }

    done, pending = await asyncio.wait(
        wait_tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    for task in pending:
        with suppress(asyncio.CancelledError):
            await task

    if frame_task in done:
        return frame_task.result()

    return None
