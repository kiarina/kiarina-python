from kiarina.agi.file_info import AudioFileInfo, FileInfo
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.file_segment_normalizer import BaseFileSegmentNormalizer
from kiarina.utils.file import FileBlob


class AudioFileSegmentNormalizer(BaseFileSegmentNormalizer):
    async def normalize_file_segments(
        self,
        file_infos: list[FileInfo],
        file_blob: FileBlob,
    ) -> list[FileInfo]:
        audio_file_infos = [fi for fi in file_infos if isinstance(fi, AudioFileInfo)]

        audio_file_infos.sort(key=lambda fi: fi.normalized_start_time)

        new_segments: list[AudioFileInfo] = []
        last_segment: AudioFileInfo | None = None
        last_segment_end_time = 0.0

        for file_info in audio_file_infos:
            start_time = file_info.normalized_start_time
            end_time = file_info.normalized_end_time

            if start_time >= last_segment_end_time:
                last_segment = await self._create_segment(
                    base_file_info=file_info,
                    file_blob=file_blob,
                    new_start_time=start_time,
                    new_end_time=end_time,
                )
                new_segments.append(last_segment)
                last_segment_end_time = end_time

            elif end_time <= last_segment_end_time:
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
                    last_segment_start_time = last_segment.normalized_start_time
                    new_last_segment_end_time = start_time

                    if last_segment_start_time < new_last_segment_end_time:
                        new_segments[-1] = await self._create_segment(
                            base_file_info=last_segment,
                            file_blob=file_blob,
                            new_start_time=last_segment_start_time,
                            new_end_time=new_last_segment_end_time,
                        )
                    else:
                        new_segments.pop()

                    last_segment = await self._create_segment(
                        base_file_info=file_info,
                        file_blob=file_blob,
                        new_start_time=start_time,
                        new_end_time=end_time,
                    )
                    new_segments.append(last_segment)
                    last_segment_end_time = end_time

                else:
                    last_segment = await self._create_segment(
                        base_file_info=file_info,
                        file_blob=file_blob,
                        new_start_time=last_segment_end_time,
                        new_end_time=end_time,
                    )
                    new_segments.append(last_segment)
                    last_segment_end_time = end_time

        return list(new_segments)

    async def _create_segment(
        self,
        *,
        base_file_info: AudioFileInfo,
        file_blob: FileBlob,
        new_start_time: float,
        new_end_time: float,
    ) -> AudioFileInfo:
        file = await rebuild_file_info(
            base_file_info,
            file_blob,
            update={
                "start_time": new_start_time,
                "end_time": (
                    new_end_time if new_end_time != base_file_info.duration else -1.0
                ),
            },
            run_context=self.run_context,
        )
        assert isinstance(file.file_info, AudioFileInfo)
        return file.file_info
