import asyncio
from io import BytesIO
from typing import TypeAlias

from kiarina.agi.file_utils import normalize_page

try:
    from pypdf import PdfReader, PdfWriter
except ImportError as exc:
    raise ImportError(
        "pypdf is required to use PDFFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-pdf]'"
    ) from exc

PDFBytes: TypeAlias = bytes


async def build_intermediate_pdf(
    raw_data: PDFBytes,
    *,
    start_page: int = 1,
    end_page: int = -1,
) -> PDFBytes:
    return await asyncio.to_thread(
        _build_intermediate_pdf, raw_data, start_page=start_page, end_page=end_page
    )


def _build_intermediate_pdf(
    raw_data: PDFBytes,
    *,
    start_page: int = 1,
    end_page: int = -1,
) -> PDFBytes:
    reader = PdfReader(BytesIO(raw_data))

    start_page = normalize_page(start_page, len(reader.pages))
    end_page = normalize_page(end_page, len(reader.pages))

    if start_page > end_page:
        raise ValueError("start_page must be less than or equal to end_page")

    writer = PdfWriter()
    for page_number in range(start_page - 1, end_page):
        writer.add_page(reader.pages[page_number])

    out = BytesIO()
    writer.write(out)
    return out.getvalue()
