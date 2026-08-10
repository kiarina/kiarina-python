from collections.abc import Iterator

import pytest

from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_segment_normalizer import (
    BaseFileSegmentNormalizer,
    FileSegmentNormalizer,
    create_file_segment_normalizer,
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
        return file_infos


@pytest.fixture
def cleanup() -> Iterator[None]:
    yield
    settings_manager.cli_args = {}


def test_preset(run_context: RunContext) -> None:
    normalizer = create_file_segment_normalizer("text", run_context=run_context)
    assert isinstance(normalizer, FileSegmentNormalizer)


def test_custom_normalizer(cleanup: None, run_context: RunContext) -> None:
    settings_manager.cli_args = {
        "normalizers": {"text": f"{__name__}:MyFileSegmentNormalizer"}
    }

    normalizer = create_file_segment_normalizer("text", run_context=run_context)
    assert isinstance(normalizer, MyFileSegmentNormalizer)
