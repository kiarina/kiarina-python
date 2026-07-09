from pathlib import Path

import pytest

from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import FileInfo, OtherFileInfo
from kiarina.agi.file_info_builder import FileInfoSpec, build_file_info
from kiarina.agi.file_segment_normalizer import normalize_file_segments
from kiarina.agi.run_context import RunContext

pytestmark = pytest.mark.skip(
    reason="Shared test assets do not include an unknown binary file for OtherFileInfo."
)


# fmt: off
@pytest.mark.parametrize(
    "file_info_specs, result_count",
    [
        # empty
        pytest.param(
            [],
            0,
            id="1. empty",
        ),
        # 1 file 2 segments
        pytest.param(
            [
                {"uri_or_file_path": "html/simple_160b.html"},
                {"uri_or_file_path": "html/simple_160b.html"},
            ],
            1,
            id="a2. 1 file 2 segments",
        ),
        # 2 files
        pytest.param(
            [
                {"uri_or_file_path": "html/simple_160b.html"},
                {"uri_or_file_path": "csv/monthly_temperature_13row_141b.csv"},
            ],
            2,
            id="a3. 2 files",
        ),
    ],
)
async def test_other(
    file_info_specs: list[FileInfoSpec],
    result_count: int,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    file_infos: list[FileInfo] = []
    file_blobs = {}

    for spec in file_info_specs:
        file_path = str(test_data_dir / spec["uri_or_file_path"])
        spec = {**spec, "uri_or_file_path": file_path}

        file_blob = await get_file_blob(file_path, run_context=run_context)
        assert file_blob is not None
        file_blobs[file_path] = file_blob

        file = await build_file_info(
            spec, file_blob, run_context=run_context
        )
        assert isinstance(file.file_info, OtherFileInfo)
        file_infos.append(file.file_info)

    result = await normalize_file_segments(
        file_infos, file_blobs, run_context=run_context
    )

    print("Result:")
    for fi in result:
        assert isinstance(fi, OtherFileInfo)
        print(f"  {fi.uri_or_file_path} ({fi.mime_type})")

    assert len(result) == result_count
