import os

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info import PDFFileInfo
from kiarina.agi.file_info_builder import BuildResult, FileInfoSpec
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_pdf_token
from kiarina.utils.file import FileBlob

from .build_intermediate_pdf import build_intermediate_pdf
from .read_pdf import read_pdf
from .read_pdf_metadata import read_pdf_metadata


async def build_analysis_disabled(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
) -> BuildResult:
    pdf_metadata = await read_pdf_metadata(file_blob.raw_data)
    page_count = pdf_metadata.page_count
    analysis_dpi = file_info_spec.get("analysis_dpi", 144)

    if analysis_dpi <= 0:
        raise ValueError("analysis_dpi must be positive")

    intermediate_file_blob: FileBlob | None = None
    intermediate_file_path: str | None = None

    start_page = file_info_spec.get("start_page", 1)
    end_page = file_info_spec.get("end_page", -1)
    normalized_end_page = page_count if end_page == -1 else end_page

    if start_page != 1 or normalized_end_page != page_count:
        intermediate_file_path = create_local_repository(
            run_context
        ).generate_cache_path(
            os.path.join(
                "intermediate",
                "pdf",
                f"{file_blob.hash_string}_{start_page}_{normalized_end_page}.pdf",
            )
        )

        intermediate_file_blob = await kfa.read_file(intermediate_file_path)

        if intermediate_file_blob is None:
            raw_data = await build_intermediate_pdf(
                file_blob.raw_data,
                start_page=start_page,
                end_page=end_page,
            )
            intermediate_file_blob = FileBlob(
                intermediate_file_path,
                mime_type="application/pdf",
                raw_data=raw_data,
            )
            await kfa.write_file(intermediate_file_blob)

    target_blob = intermediate_file_blob or file_blob
    pdf = await read_pdf(target_blob.raw_data)
    token_count = calc_pdf_token(
        pdf.content.text,
        [pdf_image_info.size for pdf_image_info in pdf.content.images],
    )

    return BuildResult(
        file_info=PDFFileInfo.model_validate(
            {
                **file_info_spec,
                "mime_type": file_blob.mime_type,
                "file_hash": file_blob.hash_string,
                "page_count": page_count,
                "analysis_dpi": analysis_dpi,
                "file_size": len(target_blob.raw_data),
                "token_count": token_count,
                "intermediate_file_path": intermediate_file_path,
                "asset_uri": None,
            }
        ),
        file_blob=file_blob,
        intermediate_file_blob=intermediate_file_blob,
    )
