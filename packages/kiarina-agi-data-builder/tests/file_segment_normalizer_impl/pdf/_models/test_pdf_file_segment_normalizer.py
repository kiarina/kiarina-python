from pathlib import Path

import pytest

from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import FileInfo, PDFFileInfo
from kiarina.agi.file_info_builder import FileInfoSpec, build_file_info
from kiarina.agi.file_segment_normalizer import normalize_file_segments
from kiarina.agi.run_context import RunContext


# fmt: off
@pytest.mark.parametrize(
    "file_info_specs, result_count",
    [
        # no overlap
        pytest.param(
            [
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 1, "end_page": 3},
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 4, "end_page": 6},
            ],
            1,
            id="a1. no overlap",
        ),
        # complete overlap
        pytest.param(
            [
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 1, "end_page": 6},
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 2, "end_page": 4},
            ],
            1,
            id="a2. complete overlap",
        ),
        # partial overlap
        pytest.param(
            [
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 1, "end_page": 5},
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 4, "end_page": 8},
            ],
            1,
            id="a3. partial overlap",
        ),
        # partial overlap, older segment later
        pytest.param(
            [
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 4, "end_page": 8},
                {"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 1, "end_page": 5},
            ],
            1,
            id="a4. partial overlap, older segment later",
        ),
        # check _create_segment
        pytest.param(
            [{"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf"}],
            1,
            id="b1. create_segment all",
        ),
        pytest.param(
            [{"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 2, "end_page": -1}],
            1,
            id="b2. create_segment 2-last",
        ),
        pytest.param(
            [{"uri_or_file_path": "pdf/image_and_text_3p_1800kb.pdf", "start_page": 2, "end_page": 3}],
            1,
            id="b3. create_segment 2-3",
        ),
    ],
)
async def test_pdf(
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
        assert isinstance(file.file_info, PDFFileInfo)
        assert file.file_info.token_count > 0
        file_infos.append(file.file_info)

    result = await normalize_file_segments(
        file_infos, file_blobs, run_context=run_context
    )

    print("Result:")
    for fi in result:
        assert isinstance(fi, PDFFileInfo)
        print(f"  pages {fi.normalized_start_page}-{fi.normalized_end_page}")

    assert len(result) == result_count
