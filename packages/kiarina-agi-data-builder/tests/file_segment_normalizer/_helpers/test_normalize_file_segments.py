from collections.abc import Iterator
from pathlib import Path

import pytest

from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.file_segment_normalizer import (
    BaseFileSegmentNormalizer,
    normalize_file_segments,
    settings_manager,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


class MyFileSegmentNormalizer(BaseFileSegmentNormalizer):
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]:
        return [file_infos[0].model_copy()]


@pytest.fixture
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "normalizers": {"text": f"{__name__}:MyFileSegmentNormalizer"}
    }
    yield
    settings_manager.cli_args = {}


async def test_normalize_file_segments(
    setup: None, run_context: RunContext, test_data_dir: Path
) -> None:
    file_path = str(test_data_dir / "json" / "user_list_5row_1kb.json")

    file_blob = await get_file_blob(file_path, run_context=run_context)
    assert file_blob is not None

    file_blobs = {file_path: file_blob}

    file1 = await build_file_info(
        {"uri_or_file_path": file_path}, file_blob, run_context=run_context
    )
    file2 = await build_file_info(
        {"uri_or_file_path": file_path}, file_blob, run_context=run_context
    )

    result = await normalize_file_segments(
        [file1.file_info, file2.file_info],
        file_blobs,
        run_context=run_context,
    )

    assert len(result) == 1
    assert file1.file_info is not result[0]
