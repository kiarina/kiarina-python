from typing import Any

from kiarina.agi.audio_embedding_provider import (
    AudioEmbeddingProvider,
    AudioEmbeddingProviderName,
    audio_embedding_provider_registry,
)
from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext

from .._schemas.audio_embedding_model_config import AudioEmbeddingModelConfig
from .._types.audio_embedding_model_name import AudioEmbeddingModelName


class AudioEmbeddingModel:
    def __init__(
        self,
        name: AudioEmbeddingModelName,
        config: AudioEmbeddingModelConfig,
    ) -> None:
        self.name: AudioEmbeddingModelName = name
        self.config: AudioEmbeddingModelConfig = config
        self._provider: AudioEmbeddingProvider | None = None

    @property
    def provider_name(self) -> AudioEmbeddingProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> AudioEmbeddingProvider:
        if self._provider is None:
            self._provider = audio_embedding_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    def get_space(self) -> EmbeddingSpace:
        return self.provider.get_space()

    async def embed(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        return await self.provider.embed(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
