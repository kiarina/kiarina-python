from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.ocr_provider import (
    OCRProvider,
    OCRProviderName,
    OCRResult,
    ocr_provider_registry,
)
from kiarina.agi.run_context import RunContext

from .._schemas.ocr_model_config import OCRModelConfig
from .._types.ocr_model_name import OCRModelName


class OCRModel:
    def __init__(self, name: OCRModelName, config: OCRModelConfig) -> None:
        self.name = name
        self.config = config
        self._provider: OCRProvider | None = None

    @property
    def provider_name(self) -> OCRProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> OCRProvider:
        if self._provider is None:
            self._provider = ocr_provider_registry.create(
                self.provider_name, **self.provider_config
            )
        return self._provider

    async def ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[OCRResult]:
        return await self.provider.ocr(
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
