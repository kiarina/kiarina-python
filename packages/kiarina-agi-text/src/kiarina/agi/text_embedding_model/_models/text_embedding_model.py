from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider import (
    TextEmbeddingProvider,
    TextEmbeddingProviderName,
    text_embedding_provider_registry,
)

from .._schemas.text_embedding_model_config import TextEmbeddingModelConfig
from .._types.text_embedding_model_name import TextEmbeddingModelName


class TextEmbeddingModel:
    def __init__(
        self,
        name: TextEmbeddingModelName,
        config: TextEmbeddingModelConfig,
    ) -> None:
        self.name: TextEmbeddingModelName = name
        self.config: TextEmbeddingModelConfig = config
        self._provider: TextEmbeddingProvider | None = None

    @property
    def provider_name(self) -> TextEmbeddingProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> TextEmbeddingProvider:
        if self._provider is None:
            self._provider = text_embedding_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    def get_space(self) -> EmbeddingSpace:
        return self.provider.get_space()

    async def embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        return await self.provider.embed(
            text,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
