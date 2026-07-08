import pytest


async def test_file_video_source(video_file_path: str) -> None:
    pytest.importorskip("moviepy")
    from kiarina.agi.video_source_impl.file import (
        FileVideoSource,
        FileVideoSourceSettings,
    )

    video_source = FileVideoSource(
        FileVideoSourceSettings(fps=4, start_timestamp=100.0)
    )

    async with video_source.open(video_file_path):
        frames = [frame async for frame in video_source.read()]

    assert len(frames) > 0
    assert frames[0].pixels.shape == (900, 1600, 3)
    assert frames[0].frame_index == 0
    assert frames[0].timestamp == 100.0
