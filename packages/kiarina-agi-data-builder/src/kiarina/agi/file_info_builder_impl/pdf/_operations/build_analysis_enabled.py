import os
from hashlib import sha1

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleMediaContent,
    FileBundleTextContent,
)
from kiarina.agi.file_info import PDFFileInfo
from kiarina.agi.file_info_builder import BuildResult, FileInfoSpec
from kiarina.agi.file_utils import normalize_page
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_pdf_token
from kiarina.utils.file import FileBlob

from .._settings import PDFFileInfoBuilderSettings
from .build_intermediate_pdf import build_intermediate_pdf
from .build_page_image_bundle import build_page_image_bundle
from .read_pdf import read_pdf
from .read_pdf_metadata import read_pdf_metadata

BUNDLE_VERSION = 2


async def build_analysis_enabled(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
    settings: PDFFileInfoBuilderSettings,
) -> BuildResult:
    source_metadata = await read_pdf_metadata(file_blob.raw_data)
    page_count = source_metadata.page_count
    start_page = normalize_page(file_info_spec.get("start_page", 1), page_count)
    end_page = normalize_page(file_info_spec.get("end_page", -1), page_count)

    if start_page > end_page:
        raise ValueError("start_page must be less than or equal to end_page")

    analysis_dpi = file_info_spec.get("analysis_dpi", 144)

    if analysis_dpi <= 0:
        raise ValueError("analysis_dpi must be positive")

    target_raw_data = file_blob.raw_data

    if start_page != 1 or end_page != page_count:
        target_raw_data = await build_intermediate_pdf(
            file_blob.raw_data,
            start_page=start_page,
            end_page=end_page,
        )

    pdf = await read_pdf(target_raw_data)
    output_base_path = create_local_repository(run_context).generate_cache_path(
        os.path.join("intermediate", "pdf", file_blob.hash_string)
    )
    bundle_file_path = _get_bundle_file_path(
        output_base_path,
        start_page=start_page,
        end_page=end_page,
        analysis_dpi=analysis_dpi,
        settings=settings,
    )
    bundle_file_blob = await kfa.read_file(bundle_file_path)

    if bundle_file_blob is None:
        bundle = _build_pdf_bundle(target_raw_data)
        bundle += await build_page_image_bundle(
            target_raw_data,
            analysis_dpi=analysis_dpi,
            start_page_number=start_page,
        )

        if pdf.content.text.strip():
            bundle += FileBundle.create(
                manifest_contents=[
                    FileBundleTextContent(
                        text=pdf.content.text,
                        visibility="unsupported",
                    )
                ]
            )

        bundle_raw_data = bundle.to_bytes()
        await kfa.write_binary(bundle_file_path, bundle_raw_data)
        bundle_file_blob = FileBlob(
            bundle_file_path,
            mime_type=FileBundle.MIME_TYPE,
            raw_data=bundle_raw_data,
        )

    token_count = calc_pdf_token(
        pdf.content.text,
        [image.size for image in pdf.content.images],
    )

    return BuildResult(
        file_info=PDFFileInfo.model_validate(
            {
                **file_info_spec,
                "mime_type": file_blob.mime_type,
                "file_hash": file_blob.hash_string,
                "page_count": page_count,
                "analysis_dpi": analysis_dpi,
                "file_size": len(bundle_file_blob.raw_data),
                "token_count": token_count,
                "intermediate_file_path": bundle_file_blob.file_path,
                "asset_uri": None,
            }
        ),
        file_blob=file_blob,
        intermediate_file_blob=bundle_file_blob,
    )


def _build_pdf_bundle(raw_data: bytes) -> FileBundle:
    file_path = "document.pdf"
    return FileBundle.create(
        manifest_contents=[
            FileBundleMediaContent(
                type="pdf",
                file_path=file_path,
                mime_type="application/pdf",
                visibility="supported",
            )
        ],
        files={file_path: raw_data},
    )


def _get_bundle_file_path(
    output_base_path: str,
    *,
    start_page: int,
    end_page: int,
    analysis_dpi: int,
    settings: PDFFileInfoBuilderSettings,
) -> str:
    signature_source = {
        "bundle_version": BUNDLE_VERSION,
        "start_page": start_page,
        "end_page": end_page,
        "analysis_dpi": analysis_dpi,
        "settings": settings.model_dump(mode="json"),
    }
    signature = sha1(
        repr(sorted(signature_source.items())).encode("utf-8")
    ).hexdigest()[:12]
    return f"{output_base_path}_analysis_{signature}.zip"
