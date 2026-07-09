from pathlib import Path

import pytest

from kiarina.agi.file import URIOrFilePath, get_file_blob
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_adjuster._operations.adjust_files_by_file_size import (
    adjust_files_by_file_size,
)
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


# fmt: off
@pytest.mark.parametrize(
    "file_paths, file_size_limit, expected_count",
    [
        pytest.param(
            ["mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3"],
            -1,
            4,
            id="1. no_limit",
        ),
        pytest.param(
            ["mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3"],
            1000 * 100,
            4,
            id="2. limit_100KB_time",
        ),
        pytest.param(
            ["pdf/image_and_text_3p_1800kb.pdf", "pdf/image_and_text_3p_1800kb.pdf", "pdf/image_and_text_3p_1800kb.pdf", "pdf/text_only_portrait_1p_17kb.pdf"],
            1000 * 100,
            1,
            id="3. limit_100KB_page",
        ),
    ],
)
async def test_adjust_files_by_file_size(
    file_paths: list[str], file_size_limit: int, expected_count: int, run_context: RunContext, test_data_dir: Path
) -> None:
    file_infos: list[FileInfo] = []
    file_blobs: dict[URIOrFilePath, FileBlob] = {}

    for file_path in file_paths:
        full_path = str(test_data_dir / file_path)
        file_blob = await get_file_blob(full_path, run_context=run_context)
        assert file_blob is not None

        file = await build_file_info(
            {"uri_or_file_path": full_path}, file_blob, run_context=run_context
        )
        file_infos.append(file.file_info)
        file_blobs[file.file_info.uri_or_file_path] = file_blob

    new_file_infos = await adjust_files_by_file_size(
        file_infos, file_blobs, file_size_limit, run_context=run_context
    )

    assert len(new_file_infos) == expected_count
