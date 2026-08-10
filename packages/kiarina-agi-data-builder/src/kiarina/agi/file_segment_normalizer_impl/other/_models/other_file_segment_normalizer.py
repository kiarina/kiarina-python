from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_segment_normalizer import BaseFileSegmentNormalizer
from kiarina.utils.file import FileBlob


class OtherFileSegmentNormalizer(BaseFileSegmentNormalizer):
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]:
        if not file_infos:
            return []

        file_infos.sort(key=lambda fi: fi.created_at, reverse=True)
        return [file_infos[0]]
