from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider import (
    ImageGenerationProvider,
    ImageGenerationProviderName,
    ImageGenerationResult,
    image_generation_provider_registry,
)
from kiarina.agi.run_context import RunContext

from .._schemas.image_generation_model_config import ImageGenerationModelConfig
from .._types.image_generation_model_name import ImageGenerationModelName


class ImageGenerationModel:
    def __init__(
        self,
        name: ImageGenerationModelName,
        config: ImageGenerationModelConfig,
    ) -> None:
        self.name: ImageGenerationModelName = name
        self.config: ImageGenerationModelConfig = config
        self._provider: ImageGenerationProvider | None = None

    def __str__(self) -> str:
        return self.name

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def provider_name(self) -> ImageGenerationProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> ImageGenerationProvider:
        if self._provider is None:
            self._provider = image_generation_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    async def generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        return await self.provider.generate(
            prompt,
            file_paths=file_paths,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
