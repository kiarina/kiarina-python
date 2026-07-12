from copy import deepcopy

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.ocr_provider import BaseOCRProvider, OCRResult
from kiarina.agi.run_context import RunContext

from .._settings import MockOCRProviderSettings


class MockOCRProvider(BaseOCRProvider):
    def __init__(self, settings: MockOCRProviderSettings) -> None:
        super().__init__()
        self.settings = settings

    def _ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[OCRResult]:
        return deepcopy(self.settings.results)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
