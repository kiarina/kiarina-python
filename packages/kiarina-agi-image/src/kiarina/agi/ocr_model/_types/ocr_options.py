from typing import TypedDict

from .._models.ocr_model import OCRModel
from .ocr_model_specifier import OCRModelSpecifier


class OCROptions(TypedDict, total=False):
    ocr_model: OCRModel | OCRModelSpecifier | None
