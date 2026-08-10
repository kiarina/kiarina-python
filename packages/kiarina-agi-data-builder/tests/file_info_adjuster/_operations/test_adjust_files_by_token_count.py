from pathlib import Path

import pytest

from kiarina.agi.file import URIOrFilePath, get_file_blob
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_adjuster._operations.adjust_files_by_token_count import (
    adjust_files_by_token_count,
)
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


# fmt: off
@pytest.mark.parametrize(
    "file_paths, token_count_limit, expected_count",
    [
        pytest.param(
            ["pdf/text_only_portrait_1p_17kb.pdf", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp3/tone_2s_16kb.mp3", "png/miineko_256x256_799b.png", "csv/monthly_temperature_13row_141b.csv", "html/simple_160b.html"],
            -1,
            6,
            id="1. no_limit",
        ),
        pytest.param(
            ["pdf/text_only_portrait_1p_17kb.pdf", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp3/tone_2s_16kb.mp3", "png/miineko_256x256_799b.png", "csv/monthly_temperature_13row_141b.csv", "html/simple_160b.html"],
            10000,
            6,
            id="2. limit_10000_tokens",
        ),
        pytest.param(
            ["pdf/text_only_portrait_1p_17kb.pdf", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp3/tone_2s_16kb.mp3", "png/miineko_256x256_799b.png", "csv/monthly_temperature_13row_141b.csv", "html/simple_160b.html"],
            4000,
            5,
            id="3. limit_4000_tokens",
        ),
    ],
)
async def test_adjust_files_by_token_count(
    file_paths: list[str], token_count_limit: int, expected_count: int, run_context: RunContext, test_data_dir: Path
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

    new_file_infos = await adjust_files_by_token_count(
        file_infos, file_blobs, token_count_limit, run_context=run_context
    )

    for new_file_info in new_file_infos:
        print(f"{new_file_info.uri_or_file_path}: {new_file_info.token_count} tokens")
        print(new_file_info.model_dump_json(indent=2))

    assert len(new_file_infos) == expected_count
