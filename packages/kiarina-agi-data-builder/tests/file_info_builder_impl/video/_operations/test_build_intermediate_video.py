import os
import subprocess
from pathlib import Path

import pytest

from kiarina.agi.file_info_builder_impl.video._operations.build_intermediate_video import (
    _export_1fps_resized_mp3_mono_16kbps_h264_mp4,
    build_intermediate_video,
)
from kiarina.agi.file_info_builder_impl.video._operations.read_video_metadata import (
    read_video_metadata,
)


@pytest.mark.parametrize(
    "start_time,end_time,expected_duration,expected_frames",
    [
        pytest.param(0.0, -1.0, 13.0, 13, id="1. full_clip"),
        pytest.param(1.0, 3.0, 2.0, 2, id="2. partial_clip"),
    ],
)
async def test_build_intermediate_video(
    short_video_file_path: Path,
    start_time: float,
    end_time: float,
    expected_duration: float,
    expected_frames: int,
    tmp_path: Path,
) -> None:
    input_file_path = short_video_file_path

    input_metadata = await read_video_metadata(str(input_file_path))

    output_file_path = await build_intermediate_video(
        str(input_file_path),
        str(tmp_path / "optimized_video"),
        start_time=start_time,
        end_time=end_time,
    )

    assert output_file_path is not None

    output_metadata = await read_video_metadata(output_file_path)

    assert os.path.getsize(output_file_path) < os.path.getsize(input_file_path)
    assert output_metadata.duration == pytest.approx(expected_duration)
    assert output_metadata.width == 1280
    assert output_metadata.height == 720
    assert output_metadata.fps == pytest.approx(1.0)
    assert output_metadata.total_frames == expected_frames
    assert output_metadata.has_audio_track is input_metadata.has_audio_track

    os.remove(output_file_path)


def test_build_intermediate_video_removes_failed_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_file_path = tmp_path / "failed.mp4"
    output_file_path.write_bytes(b"partial")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=1, stderr="encode failed"
        ),
    )

    with pytest.raises(RuntimeError, match="encode failed"):
        _export_1fps_resized_mp3_mono_16kbps_h264_mp4(
            "input.mp4",
            str(output_file_path),
            duration=1.0,
            width=1280,
            height=720,
            start_time=0.0,
            end_time=1.0,
        )

    assert not output_file_path.exists()
