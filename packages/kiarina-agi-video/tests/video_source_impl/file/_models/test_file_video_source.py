import asyncio

import numpy as np
import pytest


async def test_file_video_source(video_file_path: str) -> None:
    pytest.importorskip("imageio_ffmpeg")
    from kiarina.agi.video_source_impl.file import (
        FileVideoSource,
        FileVideoSourceSettings,
    )

    video_source = FileVideoSource(
        FileVideoSourceSettings(fps=4, start_timestamp=100.0)
    )

    async with video_source.open(video_file_path):
        frames = [frame async for frame in video_source.read()]

    assert len(frames) == 52
    assert frames[0].pixels.shape == (900, 1600, 3)
    assert frames[0].pixels.dtype == np.uint8
    assert frames[0].frame_index == 0
    assert frames[0].timestamp == 100.0
    assert frames[-1].frame_index == 51
    assert frames[-1].timestamp == 112.75


async def test_file_video_source_stops(video_file_path: str) -> None:
    pytest.importorskip("imageio_ffmpeg")
    from kiarina.agi.video_source_impl.file import (
        FileVideoSource,
        FileVideoSourceSettings,
    )

    stop_event = asyncio.Event()
    video_source = FileVideoSource(FileVideoSourceSettings(fps=4))

    async with video_source.open(video_file_path):
        frames = []
        async for frame in video_source.read(stop_event):
            frames.append(frame)
            stop_event.set()

    assert len(frames) == 1
