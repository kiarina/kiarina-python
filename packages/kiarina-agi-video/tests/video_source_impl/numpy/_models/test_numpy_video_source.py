import asyncio

import numpy as np

from kiarina.agi.video_source_impl.numpy import (
    NumpyVideoSource,
    NumpyVideoSourceSettings,
)


async def test_numpy_video_source() -> None:
    pixels = np.zeros((3, 4, 5, 3), dtype=np.uint8)
    video_source = NumpyVideoSource(
        NumpyVideoSourceSettings(fps=2, start_timestamp=100.0)
    )

    async with video_source.open(pixels):
        frames = [frame async for frame in video_source.read()]

    assert [frame.pixels.shape for frame in frames] == [(4, 5, 3)] * 3
    assert [frame.frame_index for frame in frames] == [0, 1, 2]
    assert [frame.timestamp for frame in frames] == [100.0, 100.5, 101.0]


async def test_single_frame() -> None:
    pixels = np.zeros((4, 5, 3), dtype=np.uint8)
    video_source = NumpyVideoSource(
        NumpyVideoSourceSettings(fps=10, start_timestamp=200.0)
    )

    async with video_source.open(pixels):
        frames = [frame async for frame in video_source.read()]

    assert len(frames) == 1
    assert frames[0].pixels.shape == (4, 5, 3)
    assert frames[0].timestamp == 200.0


async def test_stop_events() -> None:
    pixels = np.zeros((3, 4, 5, 3), dtype=np.uint8)
    video_source = NumpyVideoSource(NumpyVideoSourceSettings())

    outer_stop = asyncio.Event()
    inner_stop = asyncio.Event()
    inner_stop.set()

    async with video_source.open(pixels):
        frames = [frame async for frame in video_source.read(outer_stop, inner_stop)]

    assert frames == []
