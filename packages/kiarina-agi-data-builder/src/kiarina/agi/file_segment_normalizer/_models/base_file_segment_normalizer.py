from abc import ABC, abstractmethod

from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._types.file_segment_normalizer import FileSegmentNormalizer


class BaseFileSegmentNormalizer(FileSegmentNormalizer, ABC):
    def __init__(self, run_context: RunContext) -> None:
        self.run_context: RunContext = run_context

    @abstractmethod
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]: ...
