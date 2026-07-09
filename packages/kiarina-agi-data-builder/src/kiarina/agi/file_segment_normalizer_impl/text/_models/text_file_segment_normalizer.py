from kiarina.agi.file_info import FileInfo, TextFileInfo
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.file_segment_normalizer import BaseFileSegmentNormalizer
from kiarina.utils.file import FileBlob


class TextFileSegmentNormalizer(BaseFileSegmentNormalizer):
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]:
        text_file_infos = [fi for fi in file_infos if isinstance(fi, TextFileInfo)]

        text_file_infos.sort(key=lambda fi: fi.normalized_start_line)

        new_segments: list[TextFileInfo] = []
        last_segment: TextFileInfo | None = None
        last_segment_end_line = 0

        for file_info in text_file_infos:
            start_line = file_info.normalized_start_line
            end_line = file_info.normalized_end_line

            if start_line > last_segment_end_line:
                last_segment = await self._create_segment(
                    base_file_info=file_info,
                    file_blob=file_blob,
                    new_start_line=start_line,
                    new_end_line=end_line,
                )
                new_segments.append(last_segment)
                last_segment_end_line = end_line

            elif end_line <= last_segment_end_line:
                if last_segment and last_segment.created_at < file_info.created_at:
                    last_segment = last_segment.model_copy(
                        update={
                            "id": file_info.id,
                            "created_at": file_info.created_at,
                        }
                    )
                    new_segments[-1] = last_segment

            else:
                if last_segment and last_segment.created_at < file_info.created_at:
                    last_segment_start_line = last_segment.normalized_start_line
                    new_last_segment_end_line = start_line - 1

                    if last_segment_start_line <= new_last_segment_end_line:
                        new_segments[-1] = await self._create_segment(
                            base_file_info=last_segment,
                            file_blob=file_blob,
                            new_start_line=last_segment_start_line,
                            new_end_line=new_last_segment_end_line,
                        )
                    else:
                        new_segments.pop()

                    last_segment = await self._create_segment(
                        base_file_info=file_info,
                        file_blob=file_blob,
                        new_start_line=start_line,
                        new_end_line=end_line,
                    )
                    new_segments.append(last_segment)
                    last_segment_end_line = end_line

                else:
                    last_segment = await self._create_segment(
                        base_file_info=file_info,
                        file_blob=file_blob,
                        new_start_line=last_segment_end_line + 1,
                        new_end_line=end_line,
                    )
                    new_segments.append(last_segment)
                    last_segment_end_line = end_line

        return list(new_segments)

    async def _create_segment(
        self,
        *,
        base_file_info: TextFileInfo,
        file_blob: FileBlob,
        new_start_line: int,
        new_end_line: int,
    ) -> TextFileInfo:
        line_count = file_blob.raw_text.count("\n") + 1

        file = await rebuild_file_info(
            base_file_info,
            file_blob,
            update={
                "start_line": new_start_line,
                "end_line": new_end_line if new_end_line != line_count else -1,
            },
            run_context=self.run_context,
        )
        assert isinstance(file.file_info, TextFileInfo)
        return file.file_info
