from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext

from .text_embedding_provider_name import TextEmbeddingProviderName


@runtime_checkable
class TextEmbeddingProvider(Protocol):
    name: TextEmbeddingProviderName

    def get_space(self) -> EmbeddingSpace: ...

    async def embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding: ...
