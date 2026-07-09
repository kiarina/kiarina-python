from kiarina.agi.file_info import FileInfo, PDFFileInfo
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.file_segment_normalizer import BaseFileSegmentNormalizer
from kiarina.utils.file import FileBlob


class PDFFileSegmentNormalizer(BaseFileSegmentNormalizer):
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]:
        pdf_file_infos = [fi for fi in file_infos if isinstance(fi, PDFFileInfo)]

        pdf_file_infos.sort(key=lambda fi: fi.normalized_start_page)

        new_segments: list[PDFFileInfo] = []
        last_segment: PDFFileInfo | None = None
        last_segment_end_page = 0

        for file_info in pdf_file_infos:
            start_page = file_info.normalized_start_page
            end_page = file_info.normalized_end_page

            if start_page > last_segment_end_page:
                last_segment = await self._create_segment(
                    base_file_info=file_info,
                    file_blob=file_blob,
                    new_start_page=start_page,
                    new_end_page=end_page,
                )
                new_segments.append(last_segment)
                last_segment_end_page = end_page

            elif end_page <= last_segment_end_page:
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
                    last_segment_start_page = last_segment.normalized_start_page
                    new_last_segment_end_page = start_page - 1

                    if last_segment_start_page <= new_last_segment_end_page:
                        new_segments[-1] = await self._create_segment(
                            base_file_info=last_segment,
                            file_blob=file_blob,
                            new_start_page=last_segment_start_page,
                            new_end_page=new_last_segment_end_page,
                        )
                    else:
                        new_segments.pop()

                    last_segment = await self._create_segment(
                        base_file_info=file_info,
                        file_blob=file_blob,
                        new_start_page=start_page,
                        new_end_page=end_page,
                    )
                    new_segments.append(last_segment)
                    last_segment_end_page = end_page

                else:
                    last_segment = await self._create_segment(
                        base_file_info=file_info,
                        file_blob=file_blob,
                        new_start_page=last_segment_end_page + 1,
                        new_end_page=end_page,
                    )
                    new_segments.append(last_segment)
                    last_segment_end_page = end_page

        return list(new_segments)

    async def _create_segment(
        self,
        *,
        base_file_info: PDFFileInfo,
        file_blob: FileBlob,
        new_start_page: int,
        new_end_page: int,
    ) -> PDFFileInfo:
        file = await rebuild_file_info(
            base_file_info,
            file_blob,
            update={
                "start_page": new_start_page,
                "end_page": (
                    new_end_page if new_end_page != base_file_info.page_count else -1
                ),
            },
            run_context=self.run_context,
        )
        assert isinstance(file.file_info, PDFFileInfo)
        return file.file_info
