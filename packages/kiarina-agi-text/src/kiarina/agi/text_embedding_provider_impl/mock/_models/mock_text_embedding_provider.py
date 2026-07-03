from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider import BaseTextEmbeddingProvider

from .._settings import MockTextEmbeddingProviderSettings

try:
    import numpy as np
except ImportError as exc:
    raise ImportError(
        "numpy is required to use MockTextEmbeddingProvider. "
        "Install it with: "
        "pip install 'kiarina-agi-text[text-embedding-provider-mock]'"
    ) from exc


class MockTextEmbeddingProvider(BaseTextEmbeddingProvider):
    def __init__(self, settings: MockTextEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: MockTextEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind=self.settings.kind,
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
        )

    async def _embed(
        self,
        text: str,
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
                "text_length": len(text),
            },
        )

    def _embedding_space_id(self) -> str:
        if self.settings.space_id is not None:
            return self.settings.space_id

        norm = "l2" if self.normalize_embedding else "none"
        return f"mock:sha256=none:dim={self.settings.dimension}:norm={norm}"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
