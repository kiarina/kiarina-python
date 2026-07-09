from collections.abc import Sequence

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._models.chat_overflow import ChatOverflow
from .._operations.adjust_files_by_duration import adjust_files_by_duration
from .._operations.adjust_files_by_file_count import adjust_files_by_file_count
from .._operations.adjust_files_by_file_size import adjust_files_by_file_size
from .._operations.adjust_files_by_page_count import adjust_files_by_page_count
from .._operations.adjust_files_by_token_count import adjust_files_by_token_count


async def adjust_files(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    limits: ChatLimits,
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    """
    Adjust the list of files to fit within the specified limits.

    Note:
    - FileInfo with pinned=True are excluded from automatic adjustment.
      They are always kept and returned as-is.

    Priority:
    1. File count limits (image, audio, video, PDF, text)
    2. PDF page count limit
    3. Total file size limit
    4. Duration limit (audio, video)
    5. Token count limit
    """
    pinned_file_infos = [fi for fi in file_infos if fi.pinned]
    unpinned_file_infos = [fi for fi in file_infos if not fi.pinned]

    overflow = ChatOverflow(
        limits=limits, estimates=_get_files_estimates(unpinned_file_infos)
    )

    if overflow.is_overflow():
        unpinned_file_infos = await _adjust_files_unpinned_only(
            unpinned_file_infos,
            file_blobs,
            limits,
            run_context=run_context,
        )

    merged = pinned_file_infos + unpinned_file_infos
    merged.sort(key=lambda fi: fi.created_at)
    return merged


async def _adjust_files_unpinned_only(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    limits: ChatLimits,
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    overflow = ChatOverflow(limits=limits, estimates=_get_files_estimates(file_infos))

    if not overflow.is_overflow():
        return file_infos

    # --------------------------------------------------
    # 1. File count limits

    if overflow.image_file_count > 0:
        file_infos = adjust_files_by_file_count(
            file_infos, "image", limits.image_file_count_limit
        )

    if overflow.audio_file_count > 0:
        file_infos = adjust_files_by_file_count(
            file_infos, "audio", limits.audio_file_count_limit
        )

    if overflow.video_file_count > 0:
        file_infos = adjust_files_by_file_count(
            file_infos, "video", limits.video_file_count_limit
        )

    if overflow.pdf_file_count > 0:
        file_infos = adjust_files_by_file_count(
            file_infos, "pdf", limits.pdf_file_count_limit
        )

    # --------------------------------------------------
    # 2. PDF page count limit

    overflow = ChatOverflow(limits=limits, estimates=_get_files_estimates(file_infos))

    if overflow.pdf_page_count > 0:
        file_infos = await adjust_files_by_page_count(
            file_infos, file_blobs, limits.pdf_page_count_limit, run_context=run_context
        )

    # --------------------------------------------------
    # 3. Total file size limit

    overflow = ChatOverflow(limits=limits, estimates=_get_files_estimates(file_infos))

    if overflow.file_size > 0:
        file_infos = await adjust_files_by_file_size(
            file_infos, file_blobs, limits.file_size_limit, run_context=run_context
        )

    # --------------------------------------------------
    # 4. Duration limit (audio, video)

    overflow = ChatOverflow(limits=limits, estimates=_get_files_estimates(file_infos))

    if overflow.audio_duration > 0:
        file_infos = await adjust_files_by_duration(
            file_infos,
            file_blobs,
            "audio",
            limits.audio_duration_limit,
            run_context=run_context,
        )

    if overflow.video_duration > 0:
        file_infos = await adjust_files_by_duration(
            file_infos,
            file_blobs,
            "video",
            limits.video_duration_limit,
            run_context=run_context,
        )

    # --------------------------------------------------
    # 5. Token count limit

    overflow = ChatOverflow(limits=limits, estimates=_get_files_estimates(file_infos))

    if overflow.token_count > 0:
        file_infos = await adjust_files_by_token_count(
            file_infos, file_blobs, limits.token_count_limit, run_context=run_context
        )

    return file_infos


def _get_files_estimates(file_infos: Sequence[FileInfo]) -> ChatEstimates:
    return sum((fi.to_estimates() for fi in file_infos), ChatEstimates())
