from dataclasses import dataclass

from .pdf_content import PDFContent
from .pdf_metadata import PDFMetadata


@dataclass
class PDF:
    metadata: PDFMetadata
    content: PDFContent
