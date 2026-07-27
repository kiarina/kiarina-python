import os
from io import BytesIO
from pathlib import Path
from typing import cast

from pypdf import PdfWriter

from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleMediaContent,
    FileBundleTextContent,
)
from kiarina.agi.file_info import PDFFileInfo
from kiarina.agi.file_info_builder import FileInfoSpec
from kiarina.agi.file_info_builder_impl.pdf._operations.build_analysis_enabled import (
    _get_bundle_file_path,
    build_analysis_enabled,
)
from kiarina.agi.file_info_builder_impl.pdf._settings import (
    PDFFileInfoBuilderSettings,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob
from kiarina.utils.file.asyncio import read_file


def _settings() -> PDFFileInfoBuilderSettings:
    return PDFFileInfoBuilderSettings(analysis_enabled=True)


def test_bundle_cache_signature_includes_analysis_inputs() -> None:
    output_base_path = "/tmp/document"
    base = _get_bundle_file_path(
        output_base_path,
        start_page=1,
        end_page=3,
        analysis_dpi=144,
        settings=_settings(),
    )
    changed_segment = _get_bundle_file_path(
        output_base_path,
        start_page=2,
        end_page=3,
        analysis_dpi=144,
        settings=_settings(),
    )
    changed_dpi = _get_bundle_file_path(
        output_base_path,
        start_page=1,
        end_page=3,
        analysis_dpi=192,
        settings=_settings(),
    )
    changed_settings = _get_bundle_file_path(
        output_base_path,
        start_page=1,
        end_page=3,
        analysis_dpi=144,
        settings=PDFFileInfoBuilderSettings(analysis_enabled=False),
    )

    assert len({base, changed_segment, changed_dpi, changed_settings}) == 4


async def test_build_analysis_enabled_creates_capability_bundle(
    run_context: RunContext,
    many_page_pdf_file_path: Path,
) -> None:
    file_blob = await read_file(many_page_pdf_file_path)
    assert file_blob is not None

    result = await build_analysis_enabled(
        {
            "uri_or_file_path": file_blob.file_path,
            "start_page": -2,
            "end_page": -1,
            "analysis_dpi": 144,
        },
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )

    assert isinstance(result.file_info, PDFFileInfo)
    assert result.file_info.page_count == 3
    assert result.file_info.segment_page_count == 2
    assert result.intermediate_file_blob is not None
    assert result.file_info.file_size == len(result.intermediate_file_blob.raw_data)
    assert result.intermediate_file_blob.mime_type == FileBundle.MIME_TYPE

    bundle = FileBundle.from_bytes(result.intermediate_file_blob.raw_data)
    assert len(bundle.manifest.contents) == 4

    document = bundle.manifest.contents[0]
    assert isinstance(document, FileBundleMediaContent)
    assert document.type == "pdf"
    assert document.file_path == "document.pdf"
    assert document.visibility == "supported"

    page_images = cast(list[FileBundleMediaContent], bundle.manifest.contents[1:3])
    assert [content.prefix_text for content in page_images] == [
        '<image page_number="2" />',
        '<image page_number="3" />',
    ]
    assert all(content.visibility == "unsupported" for content in page_images)

    text = bundle.manifest.contents[-1]
    assert isinstance(text, FileBundleTextContent)
    assert text.visibility == "unsupported"
    assert "まとめ" in text.text


async def test_build_analysis_enabled_omits_empty_text(
    run_context: RunContext,
    tmp_path: Path,
) -> None:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=595.5, height=842)
    writer.write(buffer)
    file_path = tmp_path / "blank.pdf"
    file_blob = FileBlob(
        str(file_path),
        mime_type="application/pdf",
        raw_data=buffer.getvalue(),
    )

    result = await build_analysis_enabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )
    assert result.intermediate_file_blob is not None
    bundle = FileBundle.from_bytes(result.intermediate_file_blob.raw_data)

    assert all(
        not isinstance(content, FileBundleTextContent)
        for content in bundle.manifest.contents
    )


async def test_build_analysis_enabled_reuses_cached_bundle(
    run_context: RunContext,
    many_page_pdf_file_path: Path,
) -> None:
    file_blob = await read_file(many_page_pdf_file_path)
    assert file_blob is not None
    spec: FileInfoSpec = {
        "uri_or_file_path": file_blob.file_path,
        "analysis_dpi": 96,
    }

    first = await build_analysis_enabled(
        spec,
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )
    bundle_path = first.file_info.intermediate_file_path
    assert bundle_path is not None
    mtime = os.path.getmtime(bundle_path)

    second = await build_analysis_enabled(
        spec,
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )

    assert second.file_info.intermediate_file_path == bundle_path
    assert os.path.getmtime(bundle_path) == mtime
