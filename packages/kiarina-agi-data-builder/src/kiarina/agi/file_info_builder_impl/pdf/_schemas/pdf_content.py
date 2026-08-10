from dataclasses import dataclass

from .pdf_image_info import PDFImageInfo


@dataclass
class PDFContent:
    text: str
    images: list[PDFImageInfo]
