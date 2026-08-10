import asyncio
from io import BytesIO

try:
    from pypdf import PdfReader
except ImportError as exc:
    raise ImportError(
        "pypdf is required to use PDFFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-pdf]'"
    ) from exc

from .._schemas.pdf_metadata import PDFMetadata
from .._types.pdf_bytes import PDFBytes


async def read_pdf_metadata(raw_data: PDFBytes) -> PDFMetadata:
    return await asyncio.to_thread(_read_pdf_metadata, raw_data)


def _read_pdf_metadata(raw_data: PDFBytes) -> PDFMetadata:
    reader = PdfReader(BytesIO(raw_data))
    return PDFMetadata(page_count=len(reader.pages))
