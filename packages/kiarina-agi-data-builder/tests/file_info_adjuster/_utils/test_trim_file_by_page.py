from pathlib import Path

from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import PDFFileInfo
from kiarina.agi.file_info_adjuster import trim_file_by_page
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext


async def test_resize_from_start(run_context: RunContext, test_data_dir: Path) -> None:
    file_path = str(test_data_dir / "pdf/image_and_text_3p_1800kb.pdf")

    file_blob = await get_file_blob(file_path, run_context=run_context)
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": file_path},
        file_blob,
        run_context=run_context,
    )
    assert isinstance(file.file_info, PDFFileInfo)

    new_file_info = await trim_file_by_page(
        file_info=file.file_info,
        file_blob=file_blob,
        keep_page_count=1,
        run_context=run_context,
    )

    assert new_file_info.token_count < file.file_info.token_count


async def test_resize_from_end(run_context: RunContext, test_data_dir: Path) -> None:
    file_path = str(test_data_dir / "pdf/image_and_text_3p_1800kb.pdf")

    file_blob = await get_file_blob(file_path, run_context=run_context)
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": file_path, "keep_from_end": True},
        file_blob,
        run_context=run_context,
    )
    assert isinstance(file.file_info, PDFFileInfo)

    new_file_info = await trim_file_by_page(
        file_info=file.file_info,
        file_blob=file_blob,
        keep_page_count=1,
        run_context=run_context,
    )

    assert new_file_info.token_count < file.file_info.token_count
