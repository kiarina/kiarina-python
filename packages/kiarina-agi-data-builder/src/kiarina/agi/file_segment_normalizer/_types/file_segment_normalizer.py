from typing import Protocol, runtime_checkable

from kiarina.agi.file_info import FileInfo
from kiarina.utils.file import FileBlob


@runtime_checkable
class FileSegmentNormalizer(Protocol):
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]: ...
