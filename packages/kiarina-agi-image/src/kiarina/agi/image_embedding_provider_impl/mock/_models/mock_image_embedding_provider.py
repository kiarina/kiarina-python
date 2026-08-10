import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.image_embedding_provider import (
    BaseImageEmbeddingProvider,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._settings import MockImageEmbeddingProviderSettings


class MockImageEmbeddingProvider(BaseImageEmbeddingProvider):
    def __init__(self, settings: MockImageEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: MockImageEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind=self.settings.kind,
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
        )

    async def _embed(
        self,
        pixels: ImagePixels,
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
                "height": int(pixels.shape[0]),
                "width": int(pixels.shape[1]),
            },
        )

    def _embedding_space_id(self) -> str:
        if self.settings.space_id is not None:
            return self.settings.space_id

        norm = "l2" if self.normalize_embedding else "none"
        return f"mock:sha256=none:dim={self.settings.dimension}:norm={norm}"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
