from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .image_embedding_provider_name import ImageEmbeddingProviderName


@runtime_checkable
class ImageEmbeddingProvider(Protocol):
    name: ImageEmbeddingProviderName

    def get_space(self) -> EmbeddingSpace: ...

    async def embed(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding: ...
