import asyncio
import logging
from io import BytesIO

try:
    from pypdf import PdfReader
except ImportError as exc:
    raise ImportError(
        "pypdf is required to use PDFFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-pdf]'"
    ) from exc

from .._schemas.pdf import PDF
from .._schemas.pdf_content import PDFContent
from .._schemas.pdf_image_info import PDFImageInfo
from .._schemas.pdf_metadata import PDFMetadata
from .._types.pdf_bytes import PDFBytes

logger = logging.getLogger(__name__)


async def read_pdf(raw_data: PDFBytes) -> PDF:
    return await asyncio.to_thread(_read_pdf, raw_data)


def _read_pdf(raw_data: PDFBytes) -> PDF:
    reader = PdfReader(BytesIO(raw_data))

    texts: list[str] = []
    images: list[PDFImageInfo] = []

    for page_index, page in enumerate(reader.pages):
        if text := page.extract_text():
            texts.append(text)

        try:
            images.extend(_extract_image_infos(page_index + 1, page))
        except Exception as e:
            logger.warning(f"Failed to extract images from page {page_index + 1}: {e}")

    return PDF(
        metadata=PDFMetadata(page_count=len(reader.pages)),
        content=PDFContent(text="\n".join(texts), images=images),
    )


def _extract_image_infos(page_number: int, page: object) -> list[PDFImageInfo]:
    resources = page.get("/Resources")  # type: ignore[attr-defined]

    if not resources:
        return []

    xobject = resources.get("/XObject") if hasattr(resources, "get") else None

    if not xobject:
        return []

    image_infos: list[PDFImageInfo] = []

    for _, xobj in xobject.items():
        try:
            obj = xobj.get_object()
        except Exception:
            continue

        if not hasattr(obj, "get"):
            continue

        if obj.get("/Subtype") != "/Image":
            continue

        width = obj.get("/Width")
        height = obj.get("/Height")

        if isinstance(width, int) and isinstance(height, int):
            image_infos.append(PDFImageInfo.create(page_number, width, height))

    return image_infos
