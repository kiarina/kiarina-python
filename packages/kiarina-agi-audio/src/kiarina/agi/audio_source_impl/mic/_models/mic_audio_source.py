import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any, cast

import numpy as np

from kiarina.agi.audio_source import AudioChunk, BaseAudioSource

from .._settings import MicAudioSourceSettings

try:
    import sounddevice as sd  # type: ignore
except ImportError as exc:
    raise ImportError(
        "sounddevice is required to use MicAudioSource. "
        "Install it with: pip install 'kiarina-agi-audio[audio-source-mic]'"
    ) from exc


class MicAudioSource(BaseAudioSource):
    def __init__(self, settings: MicAudioSourceSettings) -> None:
        super().__init__()

        self.settings: MicAudioSourceSettings = settings
        self._queue: asyncio.Queue[AudioChunk] = asyncio.Queue(
            maxsize=settings.max_queue_size
        )
        self._stream: sd.InputStream | None = None
        self._unix_offset: float | None = None

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if target is not None and not isinstance(target, int | str):
            raise TypeError("MicAudioSource target must be a device id/name or None")

        loop = asyncio.get_running_loop()

        def callback(
            indata: np.ndarray, frames: int, time_info: Any, status: Any
        ) -> None:
            if self._unix_offset is None:
                self._unix_offset = time.time() - float(time_info.currentTime)

            # sounddevice yields [Samples, Channels]; normalize to [Channels, Samples]
            samples = np.asarray(indata, dtype=np.float32).T.copy()
            chunk = AudioChunk(
                samples=samples,
                sample_rate=self.settings.sample_rate,
                timestamp=self._unix_offset + float(time_info.inputBufferAdcTime),
            )
            loop.call_soon_threadsafe(self._put_nowait, chunk)

        self._stream = sd.InputStream(
            samplerate=self.settings.sample_rate,
            blocksize=self.settings.chunk_size,
            channels=self.settings.channels,
            dtype="float32",
            device=target if target is not None else self.settings.device,
            callback=callback,
        )
        self._stream.start()

        try:
            yield
        finally:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._unix_offset = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]:
        while True:
            chunk = await _read_queue(self._queue, stop_events)

            if chunk is None:
                break

            yield chunk

    def _put_nowait(self, chunk: AudioChunk) -> None:
        if self._queue.full():
            self._queue.get_nowait()

        self._queue.put_nowait(chunk)


async def _read_queue(
    queue: asyncio.Queue[AudioChunk],
    stop_events: tuple[asyncio.Event, ...],
) -> AudioChunk | None:
    if not stop_events:
        return await queue.get()

    audio_task: asyncio.Future[AudioChunk] = asyncio.ensure_future(queue.get())
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
