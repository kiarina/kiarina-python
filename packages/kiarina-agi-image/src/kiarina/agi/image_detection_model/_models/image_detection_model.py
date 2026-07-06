from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import (
    DetectedObject,
    ImageDetectionProvider,
    ImageDetectionProviderName,
    image_detection_provider_registry,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._schemas.image_detection_model_config import ImageDetectionModelConfig
from .._types.image_detection_model_name import ImageDetectionModelName


class ImageDetectionModel:
    def __init__(
        self,
        name: ImageDetectionModelName,
        config: ImageDetectionModelConfig,
    ) -> None:
        self.name: ImageDetectionModelName = name
        self.config: ImageDetectionModelConfig = config
        self._provider: ImageDetectionProvider | None = None

    @property
    def provider_name(self) -> ImageDetectionProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> ImageDetectionProvider:
        if self._provider is None:
            self._provider = image_detection_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    async def detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        return await self.provider.detect(
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
