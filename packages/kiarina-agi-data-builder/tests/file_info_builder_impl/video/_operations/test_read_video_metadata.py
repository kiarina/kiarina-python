from pathlib import Path

import pytest

from kiarina.agi.file_info_builder_impl.video._operations.read_video_metadata import (
    read_video_metadata,
)


async def test_read_video_metadata(test_data_dir: Path) -> None:
    metadata = await read_video_metadata(
        str(test_data_dir / "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4")
    )

    assert metadata.duration == pytest.approx(13.0)
    assert metadata.width == 1600
    assert metadata.height == 900
    assert metadata.fps == pytest.approx(24.0)
    assert metadata.total_frames == 312
    assert metadata.has_audio_track is False
