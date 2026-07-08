import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import cast

from kiarina.agi.audio_source import AudioChunk, BaseAudioSource

from .._settings import QueueAudioSourceSettings


class QueueAudioSource(BaseAudioSource):
    def __init__(self, settings: QueueAudioSourceSettings) -> None:
        super().__init__()

        self.settings: QueueAudioSourceSettings = settings
        self._queue: asyncio.Queue[AudioChunk | None] | None = None

    @property
    def queue(self) -> asyncio.Queue[AudioChunk | None]:
        if self._queue is None:
            raise AssertionError("queue is not set")

        return self._queue

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if not isinstance(target, asyncio.Queue):
            raise TypeError("QueueAudioSource target must be an asyncio.Queue")

        self._queue = target

        try:
            yield
        finally:
            self._queue = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]:
        while True:
            chunk = await _read_queue(self.queue, stop_events)

            if chunk is None:
                break

            yield chunk


async def _read_queue(
    queue: asyncio.Queue[AudioChunk | None],
    stop_events: tuple[asyncio.Event, ...],
) -> AudioChunk | None:
    if not stop_events:
        return await queue.get()

    audio_task: asyncio.Future[AudioChunk | None] = asyncio.ensure_future(queue.get())
    stop_tasks = [asyncio.create_task(event.wait()) for event in stop_events]

    wait_tasks = {
        cast(asyncio.Future[object], audio_task),
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

    if audio_task in done:
        return audio_task.result()

    return None
