import asyncio

import numpy as np

from kiarina.agi.audio_source_impl.numpy import (
    NumpyAudioSource,
    NumpyAudioSourceSettings,
)


async def test_numpy_audio_source() -> None:
    audio = np.arange(10, dtype=np.float32)
    audio_source = NumpyAudioSource(
        NumpyAudioSourceSettings(
            sample_rate=8000,
            chunk_size=4,
            start_timestamp=100.0,
        )
    )

    async with audio_source.open(audio):
        chunks = [chunk async for chunk in audio_source.read()]

    assert [chunk.samples.shape for chunk in chunks] == [(1, 4), (1, 4), (1, 2)]
    assert chunks[0].samples.dtype == np.float32
    assert chunks[0].sample_rate == 8000
    assert [chunk.timestamp for chunk in chunks] == [100.0, 100.0005, 100.001]


async def test_multichannel() -> None:
    audio = np.zeros((2, 10), dtype=np.float32)
    audio_source = NumpyAudioSource(
        NumpyAudioSourceSettings(chunk_size=4, start_timestamp=200.0)
    )

    async with audio_source.open(audio):
        chunks = [chunk async for chunk in audio_source.read()]

    assert [chunk.samples.shape for chunk in chunks] == [(2, 4), (2, 4), (2, 2)]
    assert [chunk.timestamp for chunk in chunks] == [200.0, 200.00025, 200.0005]


async def test_stop_events() -> None:
    audio = np.arange(10, dtype=np.float32)
    audio_source = NumpyAudioSource(NumpyAudioSourceSettings(chunk_size=4))

    outer_stop = asyncio.Event()
    inner_stop = asyncio.Event()
    inner_stop.set()

    async with audio_source.open(audio):
        chunks = [chunk async for chunk in audio_source.read(outer_stop, inner_stop)]

    assert chunks == []
