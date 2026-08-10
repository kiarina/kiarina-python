from kiarina.agi.file_info import (
    AudioFileInfo,
    FileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .trim_file_by_line import trim_file_by_line
from .trim_file_by_page import trim_file_by_page
from .trim_file_by_time import trim_file_by_time


async def trim_file_by_token(
    *,
    file_info: FileInfo,
    file_blob: FileBlob,
    keep_token_count: int,
    run_context: RunContext,
) -> FileInfo | None:
    if isinstance(file_info, TextFileInfo):
        return await _trim_text_file_by_token(
            file_info=file_info,
            file_blob=file_blob,
            keep_token_count=keep_token_count,
            run_context=run_context,
        )

    elif isinstance(file_info, (AudioFileInfo, VideoFileInfo)):
        return await _trim_media_file_by_token(
            file_info=file_info,
            file_blob=file_blob,
            keep_token_count=keep_token_count,
            run_context=run_context,
        )

    elif isinstance(file_info, PDFFileInfo):
        return await _trim_pdf_file_by_token(
            file_info=file_info,
            file_blob=file_blob,
            keep_token_count=keep_token_count,
            run_context=run_context,
        )

    else:
        return None


async def _trim_text_file_by_token(
    *,
    file_info: TextFileInfo,
    file_blob: FileBlob,
    keep_token_count: int,
    run_context: RunContext,
) -> TextFileInfo | None:
    line_count = file_info.segment_line_count
    token_count = file_info.token_count

    if token_count == 0 or line_count <= 0:
        return None

    keep_line_count = keep_token_count * line_count // token_count - 1

    while True:
        if keep_line_count <= 0:
            return None

        new_file_info = await trim_file_by_line(
            file_info=file_info,
            file_blob=file_blob,
            keep_line_count=keep_line_count,
            run_context=run_context,
        )

        if new_file_info.token_count <= keep_token_count:
            break

        keep_line_count //= 2

    return new_file_info


async def _trim_media_file_by_token(
    *,
    file_info: AudioFileInfo | VideoFileInfo,
    file_blob: FileBlob,
    keep_token_count: int,
    run_context: RunContext,
) -> AudioFileInfo | VideoFileInfo | None:
    duration = file_info.segment_duration
    token_count = file_info.token_count

    if token_count == 0 or duration <= 0:
        return None

    keep_duration = keep_token_count * duration / token_count - 1.0

    while True:
        if keep_duration <= 1.0:
            return None

        new_file_info = await trim_file_by_time(
            file_info=file_info,
            file_blob=file_blob,
            keep_duration=keep_duration,
            run_context=run_context,
        )

        if new_file_info.token_count <= keep_token_count:
            break

        keep_duration /= 2

    return new_file_info


async def _trim_pdf_file_by_token(
    *,
    file_info: PDFFileInfo,
    file_blob: FileBlob,
    keep_token_count: int,
    run_context: RunContext,
) -> PDFFileInfo | None:
    page_count = file_info.segment_page_count
    token_count = file_info.token_count

    if token_count == 0 or page_count <= 0:
        return None

    keep_page_count = keep_token_count * page_count // token_count - 1

    while True:
        if keep_page_count <= 0:
            return None

        new_file_info = await trim_file_by_page(
            file_info=file_info,
            file_blob=file_blob,
            keep_page_count=keep_page_count,
            run_context=run_context,
        )

        if new_file_info.token_count <= keep_token_count:
            break

        keep_page_count //= 2

    return new_file_info
