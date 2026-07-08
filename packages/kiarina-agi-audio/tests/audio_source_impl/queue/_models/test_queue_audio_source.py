import asyncio

import numpy as np

from kiarina.agi.audio_source import AudioChunk
from kiarina.agi.audio_source_impl.queue import (
    QueueAudioSource,
    QueueAudioSourceSettings,
)


async def test_queue_audio_source() -> None:
    queue: asyncio.Queue[AudioChunk | None] = asyncio.Queue()
    await queue.put(
        AudioChunk(
            samples=np.ones((1, 4), dtype=np.float32),
            sample_rate=8000,
            timestamp=1.25,
        )
    )
    await queue.put(None)

    audio_source = QueueAudioSource(QueueAudioSourceSettings())

    async with audio_source.open(queue):
        chunks = [chunk async for chunk in audio_source.read()]

    assert len(chunks) == 1
    assert chunks[0].samples.shape == (1, 4)
    assert chunks[0].sample_rate == 8000
    assert chunks[0].timestamp == 1.25


async def test_stop_events() -> None:
    queue: asyncio.Queue[AudioChunk | None] = asyncio.Queue()
    audio_source = QueueAudioSource(QueueAudioSourceSettings())

    outer_stop = asyncio.Event()
    inner_stop = asyncio.Event()
    inner_stop.set()

    async with audio_source.open(queue):
        chunks = [chunk async for chunk in audio_source.read(outer_stop, inner_stop)]

    assert chunks == []
