from pathlib import Path

from kiarina.agi.file_info_builder_impl.video._operations.read_video_metadata import (
    read_video_metadata,
)


async def test_read_video_metadata(test_data_dir: Path) -> None:
    metadata = await read_video_metadata(
        str(test_data_dir / "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4")
    )

    print("Video Metadata:")
    print(f"  Duration: {metadata.duration}")
    print(f"  Width: {metadata.width}")
    print(f"  Height: {metadata.height}")
    print(f"  FPS: {metadata.fps}")
    print(f"  Total Frames: {metadata.total_frames}")
    print(f"  Has Audio Track: {metadata.has_audio_track}")
