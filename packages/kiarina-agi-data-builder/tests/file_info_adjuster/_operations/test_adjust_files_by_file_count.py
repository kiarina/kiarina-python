from pathlib import Path

import pytest

from kiarina.agi.file_info import FileInfo, FileType
from kiarina.agi.file_info_adjuster._operations.adjust_files_by_file_count import (
    adjust_files_by_file_count,
)
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.run_context import RunContext


# fmt: off
@pytest.mark.parametrize(
    "file_paths, target_file_type, file_count_limit, expected_count",
    [
        pytest.param(
            ["csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv"],
            "text",
            -1,
            3,
            id="1. no_limit",
        ),
        pytest.param(
            ["csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv"],
            "text",
            2,
            2,
            id="2. limit_2",
        ),
        pytest.param(
            ["csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv", "csv/monthly_temperature_13row_141b.csv", "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4"],
            "text",
            2,
            3,
            id="3. limit_2_with_other_type",
        ),
    ],
)
async def test_adjust_files_by_file_count(
    file_paths: list[str],
    target_file_type: FileType,
    file_count_limit: int,
    expected_count: int,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    file_infos: list[FileInfo] = []

    for file_path in file_paths:
        file_info = await load_file_info(
            str(test_data_dir / file_path), run_context=run_context
        )
        assert file_info is not None

        file_infos.append(file_info)

    new_file_infos = adjust_files_by_file_count(
        file_infos,
        target_file_type,
        file_count_limit,
    )

    assert len(new_file_infos) == expected_count
