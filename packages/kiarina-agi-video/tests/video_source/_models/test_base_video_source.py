import asyncio
from collections.abc import AsyncIterator

import numpy as np

from kiarina.agi.video_source import BaseVideoSource, VideoFrame


class ExampleVideoSource(BaseVideoSource):
    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]:
        for index in range(3):
            yield VideoFrame(
                pixels=np.zeros((4, 5, 3), dtype=np.uint8),
                timestamp=float(index),
                frame_index=index,
            )


async def test_base_video_source() -> None:
    video_source = ExampleVideoSource()
    video_source.name = "example"

    assert str(video_source) == "ExampleVideoSource"
    assert video_source.name == "example"

    async with video_source.open(None):
        frames = [frame async for frame in video_source.read()]

    assert len(frames) == 3
    assert frames[0].pixels.shape == (4, 5, 3)
    assert frames[0].timestamp == 0.0
    assert frames[0].frame_index == 0
