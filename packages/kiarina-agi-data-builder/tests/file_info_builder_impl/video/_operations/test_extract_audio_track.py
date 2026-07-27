import subprocess
from pathlib import Path

from kiarina.agi.file_info_builder_impl.audio._utils.read_audio_metadata import (
    read_audio_metadata,
)
from kiarina.agi.file_info_builder_impl.video._operations.extract_audio_track import (
    extract_audio_track,
)
from kiarina.agi.file_info_builder_impl.video._utils.get_ffmpeg_exe import (
    get_ffmpeg_exe,
)


async def test_extract_audio_track(test_data_dir: Path, tmp_path: Path) -> None:
    input_video_path = (
        test_data_dir / "mp4" / "shape_animation_1600x900_24fps_13s_4400kb.mp4"
    )
    input_audio_path = test_data_dir / "mp3" / "tone_2s_16kb.mp3"
    video_with_audio_path = tmp_path / "video_with_audio.mp4"
    subprocess.run(
        [
            get_ffmpeg_exe(),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_video_path),
            "-i",
            str(input_audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(video_with_audio_path),
        ],
        check=True,
    )

    output_path = await extract_audio_track(
        str(video_with_audio_path),
        str(tmp_path / "audio.mp3"),
    )

    metadata = await read_audio_metadata(output_path)
    assert metadata.duration > 1.9
    assert metadata.nchannels == 1
