from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.image_embedding_provider import (
    ImageEmbeddingProvider,
    ImageEmbeddingProviderName,
    image_embedding_provider_registry,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._schemas.image_embedding_model_config import ImageEmbeddingModelConfig
from .._types.image_embedding_model_name import ImageEmbeddingModelName


class ImageEmbeddingModel:
    def __init__(
        self,
        name: ImageEmbeddingModelName,
        config: ImageEmbeddingModelConfig,
    ) -> None:
        self.name: ImageEmbeddingModelName = name
        self.config: ImageEmbeddingModelConfig = config
        self._provider: ImageEmbeddingProvider | None = None

    @property
    def provider_name(self) -> ImageEmbeddingProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> ImageEmbeddingProvider:
        if self._provider is None:
            self._provider = image_embedding_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    def get_space(self) -> EmbeddingSpace:
        return self.provider.get_space()

    async def embed(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        return await self.provider.embed(
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
