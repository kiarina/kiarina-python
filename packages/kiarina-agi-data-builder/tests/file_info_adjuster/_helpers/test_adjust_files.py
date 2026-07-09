from pathlib import Path

import pytest

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.file import URIOrFilePath, get_file_blob
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_adjuster import adjust_files
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


# fmt: off
@pytest.mark.parametrize(
    "file_paths, limits, expected_count",
    [
        pytest.param(
            [
                "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv",
                "jpg/grid_4000x3000_1400kb.jpg", "jpg/grid_4000x3000_1400kb.jpg", "jpg/grid_4000x3000_1400kb.jpg",
                "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3",
                "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4",
                "pdf/text_only_portrait_1p_17kb.pdf", "pdf/image_and_text_3p_1800kb.pdf", "pdf/image_and_text_3p_1800kb.pdf",
            ],
            ChatLimits(
                token_count_limit=3500,
                file_size_limit=1000 * 1000 * 50,  # 50 MB
                image_file_count_limit=2,
                audio_duration_limit=3.0,
                audio_file_count_limit=2,
                video_duration_limit=3.0,
                video_file_count_limit=2,
                pdf_page_count_limit=3,
                pdf_file_count_limit=2,
            ),
            4,
            id="1. all_within_limits",
        ),
        pytest.param(
            [
                "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv",
                "jpg/grid_4000x3000_1400kb.jpg", "jpg/grid_4000x3000_1400kb.jpg", "jpg/grid_4000x3000_1400kb.jpg",
                "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3", "mp3/tone_2s_16kb.mp3",
                "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4",
                "pdf/text_only_portrait_1p_17kb.pdf", "pdf/image_and_text_3p_1800kb.pdf", "pdf/image_and_text_3p_1800kb.pdf",
            ],
            ChatLimits(
                token_count_limit=5000,
                file_size_limit=1000 * 50,  # 50 KB
                image_file_count_limit=2,
                audio_duration_limit=3.0,
                audio_file_count_limit=2,
                video_duration_limit=3.0,
                video_file_count_limit=2,
                pdf_page_count_limit=3,
                pdf_file_count_limit=2,
            ),
            4,
            id="2. file_size_limit_50KB",
        ),
    ],
)
async def test_adjust_files(
    file_paths: list[str], limits: ChatLimits, expected_count: int, run_context: RunContext, test_data_dir: Path
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

    new_file_infos = await adjust_files(
        file_infos, file_blobs, limits, run_context=run_context
    )

    token_count = 0

    for fi in new_file_infos:
        print(f"Retained file: {fi.uri_or_file_path}, token_count={fi.token_count}")
        token_count += fi.token_count

    print(f"Total token count of retained files: {token_count}")

    assert len(new_file_infos) == expected_count
