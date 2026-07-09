from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import (
    AudioFileInfo,
    FileInfo,
    PDFFileInfo,
    VideoFileInfo,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._utils.trim_file_by_page import trim_file_by_page
from .._utils.trim_file_by_time import trim_file_by_time


async def adjust_files_by_file_size(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    file_size_limit: int,
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    if file_size_limit == -1:
        return file_infos

    new_file_infos: list[FileInfo] = []
    media_file_infos: list[FileInfo] = []

    for file_info in file_infos:
        if file_info.type not in ["image", "audio", "video", "pdf"]:
            new_file_infos.append(file_info)
        else:
            media_file_infos.append(file_info)

    media_file_infos.sort(key=lambda fi: -fi.created_at.timestamp())

    total_file_size = 0
    new_media_file_infos: list[FileInfo] = []

    for media_file_info in media_file_infos:
        if total_file_size + media_file_info.file_size <= file_size_limit:
            new_media_file_infos.append(media_file_info)
            total_file_size += media_file_info.file_size
            continue

        remaining_file_size = file_size_limit - total_file_size

        if remaining_file_size > 0:
            new_media_file_info = await _adjust_media_file(
                file_info=media_file_info,
                file_blob=file_blobs[media_file_info.uri_or_file_path],
                remaining_file_size=remaining_file_size,
                run_context=run_context,
            )

            if new_media_file_info is None:
                continue

            new_media_file_infos.append(new_media_file_info)

        break

    new_file_infos.extend(new_media_file_infos)
    new_file_infos.sort(key=lambda fi: fi.created_at)

    return new_file_infos


async def _adjust_media_file(
    *,
    file_info: FileInfo,
    file_blob: FileBlob,
    remaining_file_size: int,
    run_context: RunContext,
) -> FileInfo | None:
    if isinstance(file_info, (AudioFileInfo, VideoFileInfo)):
        return await _adjust_by_time(
            file_info=file_info,
            file_blob=file_blob,
            remaining_file_size=remaining_file_size,
            run_context=run_context,
        )

    if isinstance(file_info, PDFFileInfo):
        return await _adjust_by_page(
            file_info=file_info,
            file_blob=file_blob,
            remaining_file_size=remaining_file_size,
            run_context=run_context,
        )

    return None


async def _adjust_by_time(
    *,
    file_info: AudioFileInfo | VideoFileInfo,
    file_blob: FileBlob,
    remaining_file_size: int,
    run_context: RunContext,
) -> FileInfo | None:
    duration = file_info.segment_duration
    file_size = file_info.file_size

    if file_size == 0 or duration <= 0:
        return None

    remaining_duration = remaining_file_size / (file_size / duration) - 1.0

    while True:
        if remaining_duration <= 1.0:
            return None

        new_file_info = await trim_file_by_time(
            file_info=file_info,
            file_blob=file_blob,
            keep_duration=remaining_duration,
            run_context=run_context,
        )

        if new_file_info.file_size <= remaining_file_size:
            break

        remaining_duration /= 2

    return new_file_info


async def _adjust_by_page(
    *,
    file_info: PDFFileInfo,
    file_blob: FileBlob,
    remaining_file_size: int,
    run_context: RunContext,
) -> FileInfo | None:
    page_count = file_info.segment_page_count
    file_size = file_info.file_size

    if file_size == 0 or page_count <= 0:
        return None

    remaining_page_count = remaining_file_size // (file_size // page_count) - 1

    while True:
        if remaining_page_count <= 0:
            return None

        new_file_info = await trim_file_by_page(
            file_info=file_info,
            file_blob=file_blob,
            keep_page_count=remaining_page_count,
            run_context=run_context,
        )

        if new_file_info.file_size <= remaining_file_size:
            break

        remaining_page_count //= 2

    return new_file_info
