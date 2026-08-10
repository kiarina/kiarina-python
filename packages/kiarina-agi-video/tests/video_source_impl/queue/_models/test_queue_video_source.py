import asyncio

import numpy as np

from kiarina.agi.video_source import VideoFrame
from kiarina.agi.video_source_impl.queue import (
    QueueVideoSource,
    QueueVideoSourceSettings,
)


async def test_queue_video_source() -> None:
    queue: asyncio.Queue[VideoFrame | None] = asyncio.Queue()
    await queue.put(
        VideoFrame(
            pixels=np.zeros((4, 5, 3), dtype=np.uint8),
            timestamp=100.0,
            frame_index=7,
        )
    )
    await queue.put(None)

    video_source = QueueVideoSource(QueueVideoSourceSettings())

    async with video_source.open(queue):
        frames = [frame async for frame in video_source.read()]

    assert len(frames) == 1
    assert frames[0].pixels.shape == (4, 5, 3)
    assert frames[0].timestamp == 100.0
    assert frames[0].frame_index == 7


async def test_stop_events() -> None:
    queue: asyncio.Queue[VideoFrame | None] = asyncio.Queue()
    video_source = QueueVideoSource(QueueVideoSourceSettings())

    outer_stop = asyncio.Event()
    inner_stop = asyncio.Event()
    inner_stop.set()

    async with video_source.open(queue):
        frames = [frame async for frame in video_source.read(outer_stop, inner_stop)]

    assert frames == []
