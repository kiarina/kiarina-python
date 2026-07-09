from kiarina.agi.file_info import AudioFileInfo, VideoFileInfo
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

MediaFileInfo = AudioFileInfo | VideoFileInfo


async def trim_file_by_time(
    *,
    file_info: MediaFileInfo,
    file_blob: FileBlob,
    keep_duration: float,
    run_context: RunContext,
) -> MediaFileInfo:
    start_time = file_info.normalized_start_time
    end_time = file_info.normalized_end_time
    duration = file_info.duration

    if file_info.keep_from_end:
        new_start_time = max(end_time - keep_duration, start_time)
        new_end_time = end_time
    else:
        new_start_time = start_time
        new_end_time = min(start_time + keep_duration, end_time)

    file = await rebuild_file_info(
        file_info,
        file_blob,
        update={
            "start_time": new_start_time,
            "end_time": new_end_time if new_end_time != duration else -1.0,
        },
        run_context=run_context,
    )
    assert isinstance(file.file_info, (AudioFileInfo, VideoFileInfo))
    return file.file_info
