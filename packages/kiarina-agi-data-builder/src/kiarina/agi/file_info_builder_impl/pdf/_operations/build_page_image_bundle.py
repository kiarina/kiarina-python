import asyncio
from io import BytesIO

try:
    import pypdfium2 as pdfium  # type: ignore[import-untyped]
except ImportError as exc:
    raise ImportError(
        "pypdfium2 is required to render PDF pages. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-pdf]'"
    ) from exc

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError(
        "Pillow is required to encode PDF page images. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-pdf]'"
    ) from exc

from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleContentInput,
    FileBundleMediaContent,
)

from .._types.pdf_bytes import PDFBytes


async def build_page_image_bundle(
    raw_data: PDFBytes,
    *,
    analysis_dpi: int,
    start_page_number: int,
) -> FileBundle:
    return await asyncio.to_thread(
        _build_page_image_bundle,
        raw_data,
        analysis_dpi=analysis_dpi,
        start_page_number=start_page_number,
    )


def _build_page_image_bundle(
    raw_data: PDFBytes,
    *,
    analysis_dpi: int,
    start_page_number: int,
) -> FileBundle:
    document = pdfium.PdfDocument(raw_data)
    contents: list[FileBundleContentInput] = []
    files: dict[str, bytes] = {}

    try:
        for page_index in range(len(document)):
            page_number = start_page_number + page_index
            file_path = f"pages/page_{page_number:04d}.jpg"
            page = document[page_index]

            try:
                bitmap = page.render(scale=analysis_dpi / 72)

                try:
                    image: Image.Image = bitmap.to_pil().convert("RGB")

                    try:
                        buffer = BytesIO()
                        image.save(buffer, "JPEG", quality=85, optimize=True)
                    finally:
                        image.close()
                finally:
                    bitmap.close()
            finally:
                page.close()

            contents.append(
                FileBundleMediaContent(
                    type="image",
                    file_path=file_path,
                    mime_type="image/jpeg",
                    visibility="unsupported",
                    prefix_text=f'<image page_number="{page_number}" />',
                )
            )
            files[file_path] = buffer.getvalue()
    finally:
        document.close()

    return FileBundle.create(manifest_contents=contents, files=files)
