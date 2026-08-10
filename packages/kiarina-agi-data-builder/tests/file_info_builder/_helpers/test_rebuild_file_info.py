from pathlib import Path

from kiarina.agi.file_info_builder import (
    build_file_info,
    rebuild_file_info,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def test_rebuild_file_info(run_context: RunContext, test_data_dir: Path) -> None:
    file_blob = await read_file(str(test_data_dir / "txt" / "utf-8_1027line_125kb.txt"))
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    file2 = await rebuild_file_info(
        file.file_info,
        file_blob,
        update={
            "start_line": 2,
            "end_line": -1,
        },
        run_context=run_context,
    )

    assert file2.file_info.id == file.file_info.id
    assert file2.file_info.created_at == file.file_info.created_at
    assert file2.file_info.token_count < file.file_info.token_count


async def test_rebuild_pdf_file_info_preserves_analysis_dpi(
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    file_blob = await read_file(
        str(test_data_dir / "pdf" / "text_only_portrait_1p_17kb.pdf")
    )
    assert file_blob is not None

    file = await build_file_info(
        {
            "uri_or_file_path": file_blob.file_path,
            "analysis_dpi": 192,
        },
        file_blob,
        run_context=run_context,
    )
    rebuilt = await rebuild_file_info(
        file.file_info,
        file_blob,
        update={},
        run_context=run_context,
    )

    assert file.file_info.type == "pdf"
    assert rebuilt.file_info.type == "pdf"
    assert rebuilt.file_info.analysis_dpi == 192
