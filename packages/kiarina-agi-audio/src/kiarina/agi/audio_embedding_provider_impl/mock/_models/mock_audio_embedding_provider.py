import numpy as np

from kiarina.agi.audio_embedding_provider import (
    BaseAudioEmbeddingProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.run_context import RunContext

from .._settings import MockAudioEmbeddingProviderSettings


class MockAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
    def __init__(self, settings: MockAudioEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: MockAudioEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind=self.settings.kind,
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
        )

    async def _embed(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        space = self.get_space()
        vector = np.asarray(self.settings.embedding, dtype=np.float32)

        if self.normalize_embedding:
            vector = l2_normalize(vector)

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=vector,
            metadata={
                "sample_rate": sample_rate,
                "samples": len(samples),
            },
        )

    def _embedding_space_id(self) -> str:
        if self.settings.space_id is not None:
            return self.settings.space_id

        norm = "l2" if self.normalize_embedding else "none"
        return f"mock:sha256=none:sr=any:dim={self.settings.dimension}:norm={norm}"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
