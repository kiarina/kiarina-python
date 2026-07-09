import os
from pathlib import Path

import pytest

from kiarina.agi.file_info import AudioFileInfo
from kiarina.agi.file_info_builder_impl.audio._operations.build_analysis_disabled import (
    build_analysis_disabled,
)
from kiarina.agi.file_info_builder_impl.audio._utils.read_audio_metadata import (
    read_audio_metadata,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def test_build_analysis_disabled_full(
    run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    result = await build_analysis_disabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert isinstance(result.file_info, AudioFileInfo)
    assert result.file_info.mime_type == file_blob.mime_type
    assert result.file_info.file_hash == file_blob.hash_string
    assert result.file_info.duration == pytest.approx(2.04, abs=0.1)
    assert result.file_info.token_count > 0
    assert result.file_blob is file_blob

    # sample.mp3 (stereo 44.1kHz) re-encoded to mono 16kbps must shrink.
    assert result.file_info.intermediate_file_path is not None
    assert result.file_info.intermediate_file_path.endswith(".mp3")
    assert result.intermediate_file_blob is not None
    assert result.file_info.file_size == len(result.intermediate_file_blob.raw_data)
    assert result.file_info.file_size < len(file_blob.raw_data)


async def test_build_analysis_disabled_segment(
    run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    result = await build_analysis_disabled(
        {
            "uri_or_file_path": file_blob.file_path,
            "start_time": 0.5,
            "end_time": 1.5,
        },
        file_blob,
        run_context=run_context,
    )

    assert result.file_info.intermediate_file_path is not None
    assert "_0.5_1.5.mp3" in result.file_info.intermediate_file_path
    assert os.path.exists(result.file_info.intermediate_file_path)

    metadata = await read_audio_metadata(result.file_info.intermediate_file_path)
    assert metadata.duration == pytest.approx(1.0, abs=0.15)


async def test_build_analysis_disabled_reuses_cached_intermediate(
    run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    first = await build_analysis_disabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )
    assert first.file_info.intermediate_file_path is not None

    mtime_before = os.path.getmtime(first.file_info.intermediate_file_path)

    second = await build_analysis_disabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert (
        second.file_info.intermediate_file_path
        == first.file_info.intermediate_file_path
    )
    assert second.file_info.intermediate_file_path is not None
    assert os.path.getmtime(second.file_info.intermediate_file_path) == mtime_before
