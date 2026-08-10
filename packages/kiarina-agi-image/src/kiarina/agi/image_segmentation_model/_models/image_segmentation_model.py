from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_segmentation_provider import (
    ImageSegmentationProvider,
    ImageSegmentationProviderName,
    ImageSegmentationResult,
    image_segmentation_provider_registry,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._schemas.image_segmentation_model_config import ImageSegmentationModelConfig
from .._types.image_segmentation_model_name import ImageSegmentationModelName


class ImageSegmentationModel:
    def __init__(
        self,
        name: ImageSegmentationModelName,
        config: ImageSegmentationModelConfig,
    ) -> None:
        self.name = name
        self.config = config
        self._provider: ImageSegmentationProvider | None = None

    @property
    def provider_name(self) -> ImageSegmentationProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> ImageSegmentationProvider:
        if self._provider is None:
            self._provider = image_segmentation_provider_registry.create(
                self.provider_name, **self.provider_config
            )
        return self._provider

    async def segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageSegmentationResult:
        return await self.provider.segment(
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
