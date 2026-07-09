from kiarina.agi.file_info import PDFFileInfo
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


async def trim_file_by_page(
    *,
    file_info: PDFFileInfo,
    file_blob: FileBlob,
    keep_page_count: int,
    run_context: RunContext,
) -> PDFFileInfo:
    start_page = file_info.normalized_start_page
    end_page = file_info.normalized_end_page
    page_count = file_info.page_count

    if file_info.keep_from_end:
        new_start_page = max(end_page - keep_page_count + 1, start_page)
        new_end_page = end_page
    else:
        new_start_page = start_page
        new_end_page = min(start_page + keep_page_count - 1, end_page)

    file = await rebuild_file_info(
        file_info,
        file_blob,
        update={
            "start_page": new_start_page,
            "end_page": new_end_page if new_end_page != page_count else -1,
        },
        run_context=run_context,
    )
    assert isinstance(file.file_info, PDFFileInfo)
    return file.file_info
