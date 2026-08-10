from dataclasses import dataclass
from typing import Self

from kiarina.agi.token_utils import ImageSize


@dataclass
class PDFImageInfo:
    page_number: int
    size: ImageSize

    @classmethod
    def create(cls, page_number: int, width: int, height: int) -> Self:
        return cls(page_number, ImageSize(width, height))
