from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import FileInfo, PDFFileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._utils.trim_file_by_page import trim_file_by_page


async def adjust_files_by_page_count(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    page_count_limit: int,
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    if page_count_limit == -1:
        return file_infos

    new_file_infos: list[FileInfo] = []
    pdf_file_infos: list[PDFFileInfo] = []

    for file_info in file_infos:
        if isinstance(file_info, PDFFileInfo):
            pdf_file_infos.append(file_info)
        else:
            new_file_infos.append(file_info)

    pdf_file_infos.sort(key=lambda fi: -fi.created_at.timestamp())

    total_page_count = 0
    new_pdf_file_infos: list[FileInfo] = []

    for pdf_file_info in pdf_file_infos:
        page_count = pdf_file_info.segment_page_count

        if total_page_count + page_count <= page_count_limit:
            new_pdf_file_infos.append(pdf_file_info)
            total_page_count += page_count
            continue

        remaining_page_count = page_count_limit - total_page_count

        if remaining_page_count > 0:
            new_pdf_file_info = await trim_file_by_page(
                file_info=pdf_file_info,
                file_blob=file_blobs[pdf_file_info.uri_or_file_path],
                keep_page_count=remaining_page_count,
                run_context=run_context,
            )
            new_pdf_file_infos.append(new_pdf_file_info)

        break

    new_file_infos.extend(new_pdf_file_infos)
    new_file_infos.sort(key=lambda fi: fi.created_at)

    return new_file_infos
