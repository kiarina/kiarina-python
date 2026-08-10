from pathlib import Path

import pytest

from kiarina.agi.file_info import VideoFileInfo
from kiarina.agi.file_info_builder_impl.video._operations.build_analysis_disabled import (
    build_analysis_disabled,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def test_build_analysis_disabled_keeps_source_metadata(
    run_context: RunContext,
    short_video_file_path: Path,
) -> None:
    file_blob = await read_file(short_video_file_path)
    assert file_blob is not None

    result = await build_analysis_disabled(
        {
            "uri_or_file_path": file_blob.file_path,
            "analysis_fps": 2.0,
        },
        file_blob,
        run_context=run_context,
    )

    assert isinstance(result.file_info, VideoFileInfo)
    assert result.file_info.width == 1600
    assert result.file_info.height == 900
    assert result.file_info.fps == pytest.approx(24.0)
    assert result.file_info.analysis_fps == pytest.approx(2.0)
    assert result.file_info.duration == pytest.approx(13.0)
    assert result.file_info.intermediate_file_path is not None
