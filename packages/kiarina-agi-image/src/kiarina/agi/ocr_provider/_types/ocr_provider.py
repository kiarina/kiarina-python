from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._views.ocr_result import OCRResult
from .ocr_provider_name import OCRProviderName


@runtime_checkable
class OCRProvider(Protocol):
    name: OCRProviderName

    async def ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[OCRResult]: ...
