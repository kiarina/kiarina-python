from pathlib import Path

from kiarina.agi.file_info import PDFFileInfo
from kiarina.agi.file_info_builder_impl.pdf._operations.build_analysis_disabled import (
    build_analysis_disabled,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def test_build_analysis_disabled_preserves_existing_behavior(
    run_context: RunContext,
    many_page_pdf_file_path: Path,
) -> None:
    file_blob = await read_file(many_page_pdf_file_path)
    assert file_blob is not None

    result = await build_analysis_disabled(
        {
            "uri_or_file_path": file_blob.file_path,
            "start_page": 2,
            "end_page": 3,
            "analysis_dpi": 192,
        },
        file_blob,
        run_context=run_context,
    )

    assert isinstance(result.file_info, PDFFileInfo)
    assert result.file_info.page_count == 3
    assert result.file_info.segment_page_count == 2
    assert result.file_info.analysis_dpi == 192
    assert result.file_info.intermediate_file_path is not None
    assert result.intermediate_file_blob is not None
    assert result.intermediate_file_blob.mime_type == "application/pdf"
