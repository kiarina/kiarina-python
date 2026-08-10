import asyncio
from collections.abc import AsyncIterator

import numpy as np

from kiarina.agi.audio_source import AudioChunk, BaseAudioSource


class ExampleAudioSource(BaseAudioSource):
    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]:
        for _ in range(3):
            yield AudioChunk(
                samples=np.zeros((1, 16000), dtype=np.float32),
                sample_rate=16000,
                timestamp=0.0,
            )


async def test_base_audio_source() -> None:
    audio_source = ExampleAudioSource()
    audio_source.name = "example"

    assert str(audio_source) == "ExampleAudioSource"
    assert audio_source.name == "example"

    audio_source.name = "example"
    assert audio_source.name == "example"

    async with audio_source.open(None):
        chunks = [chunk async for chunk in audio_source.read()]

    assert len(chunks) == 3
    assert chunks[0].samples.shape == (1, 16000)
    assert chunks[0].sample_rate == 16000
    assert chunks[0].timestamp == 0.0
