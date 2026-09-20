from collections.abc import Iterator

import pytest

from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_segment_normalizer import (
    BaseFileSegmentNormalizer,
    FileSegmentNormalizer,
    file_segment_normalizer_registry,
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
    file_segment_normalizer_registry.clear()


def test_preset(run_context: RunContext) -> None:
    normalizer = file_segment_normalizer_registry.resolve("text", run_context)
    assert isinstance(normalizer, FileSegmentNormalizer)


def test_custom(cleanup: None, run_context: RunContext) -> None:
    settings_manager.cli_args = {
        "customs": {"text": f"{__name__}:MyFileSegmentNormalizer"}
    }

    normalizer = file_segment_normalizer_registry.resolve("text", run_context)
    assert isinstance(normalizer, MyFileSegmentNormalizer)


def test_register(cleanup: None, run_context: RunContext) -> None:
    file_segment_normalizer_registry.register("text", MyFileSegmentNormalizer)

    normalizer = file_segment_normalizer_registry.resolve("text", run_context)
    assert isinstance(normalizer, MyFileSegmentNormalizer)


def test_unregistered(run_context: RunContext) -> None:
    with pytest.raises(ValueError, match="FileSegmentNormalizer is not registered"):
        file_segment_normalizer_registry.resolve("unknown", run_context)
