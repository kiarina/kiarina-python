from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import (
    AudioFileInfo,
    FileInfo,
    FileType,
    VideoFileInfo,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._utils.trim_file_by_time import trim_file_by_time


async def adjust_files_by_duration(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    target_file_type: FileType,
    duration_limit: float,
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    if duration_limit == -1.0:
        return file_infos

    new_file_infos: list[FileInfo] = []
    target_file_infos: list[FileInfo] = []

    for file_info in file_infos:
        if file_info.type != target_file_type:
            new_file_infos.append(file_info)
        else:
            target_file_infos.append(file_info)

    target_file_infos.sort(key=lambda fi: -fi.created_at.timestamp())

    total_duration = 0.0
    new_target_file_infos: list[FileInfo] = []

    for file_info in target_file_infos:
        assert isinstance(file_info, (AudioFileInfo, VideoFileInfo))
        duration = file_info.segment_duration

        if total_duration + duration <= duration_limit:
            new_target_file_infos.append(file_info)
            total_duration += duration
            continue

        remaining_duration = duration_limit - total_duration

        if remaining_duration > 1.0:
            new_file_info = await trim_file_by_time(
                file_info=file_info,
                file_blob=file_blobs[file_info.uri_or_file_path],
                keep_duration=remaining_duration,
                run_context=run_context,
            )
            new_target_file_infos.append(new_file_info)

        break

    new_file_infos.extend(new_target_file_infos)
    new_file_infos.sort(key=lambda fi: fi.created_at)

    return new_file_infos
