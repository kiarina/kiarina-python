from abc import ABC, abstractmethod

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext

from .._types.text_embedding_provider import TextEmbeddingProvider
from .._types.text_embedding_provider_name import TextEmbeddingProviderName


class BaseTextEmbeddingProvider(TextEmbeddingProvider, ABC):
    def __init__(self) -> None:
        self._name: TextEmbeddingProviderName | None = None

    @property
    def name(self) -> TextEmbeddingProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("TextEmbeddingProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: TextEmbeddingProviderName) -> None:
        self._name = value

    async def embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        text = self._normalize_text(text)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(text_embedding_provider=f"{self}")

        space = self.get_space()

        embedding = await self._embed(
            text,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        if embedding.kind != space.kind:
            raise ValueError(
                f"Embedding kind mismatch: {embedding.kind!r} != {space.kind!r}."
            )

        if embedding.space_id != space.space_id:
            raise ValueError(
                "Embedding space_id mismatch: "
                f"{embedding.space_id!r} != {space.space_id!r}."
            )

        if len(embedding.vector) != space.dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"{len(embedding.vector)} != {space.dimension}."
            )

        return embedding

    @abstractmethod
    def get_space(self) -> EmbeddingSpace: ...

    @abstractmethod
    async def _embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding: ...

    def _normalize_text(self, text: str) -> str:
        return text

    def __str__(self) -> str:
        return self.__class__.__name__
