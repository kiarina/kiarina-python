import os
from pathlib import Path

import pytest

from kiarina.agi.file_info_builder_impl.video._operations.build_intermediate_video import (
    build_intermediate_video,
)
from kiarina.agi.file_info_builder_impl.video._operations.read_video_metadata import (
    read_video_metadata,
)


@pytest.mark.parametrize(
    "start_time,end_time",
    [
        pytest.param(0.0, -1.0, id="1. full_clip"),
        pytest.param(1.0, 3.0, id="2. partial_clip"),
    ],
)
async def test_build_intermediate_video(
    short_video_file_path: Path, start_time: float, end_time: float, tmp_path: Path
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

    print(f"Output file path: {output_file_path}")
    print("File size:")
    print(f"  Old: {os.path.getsize(input_file_path)} bytes")
    print(f"  New: {os.path.getsize(output_file_path)} bytes")
    print("Metadata:")
    print(f"  Old: {input_metadata}")
    print(f"  New: {output_metadata}")

    os.remove(output_file_path)
