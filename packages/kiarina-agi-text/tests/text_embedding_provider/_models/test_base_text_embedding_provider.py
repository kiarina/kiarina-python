# mypy: ignore-errors

import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider import BaseTextEmbeddingProvider


class ExampleTextEmbeddingProvider(BaseTextEmbeddingProvider):
    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind="example",
            space_id="example:sha256=none:dim=2:norm=l2",
            dimension=2,
        )

    async def _embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        space = self.get_space()
        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=np.array([0.6, 0.8], dtype=np.float32),
        )


async def test_base_text_embedding_provider(run_context: RunContext) -> None:
    provider = ExampleTextEmbeddingProvider()
    provider.name = "example"

    print(f"__str__: {provider!s}")
    print(f"name: {provider.name}")

    result = await provider.embed("hello", run_context=run_context)

    assert result.kind == "example"
    assert result.space_id == "example:sha256=none:dim=2:norm=l2"
    assert result.to_numpy().dtype == np.float32
    assert np.allclose(result.to_numpy(), [0.6, 0.8])


async def test_rejects_dimension_mismatch(run_context: RunContext) -> None:
    class BadTextEmbeddingProvider(BaseTextEmbeddingProvider):
        def get_space(self) -> EmbeddingSpace:
            return EmbeddingSpace(
                kind="example",
                space_id="example:sha256=none:dim=3:norm=l2",
                dimension=3,
            )

        async def _embed(
            self,
            text: str,
            *,
            cost_recorder: CostRecorder,
            run_context: RunContext,
        ) -> Embedding:
            space = self.get_space()
            return Embedding.from_numpy(
                kind=space.kind,
                space_id=space.space_id,
                vector=np.zeros(2, dtype=np.float32),
            )

    provider = BadTextEmbeddingProvider()

    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        await provider.embed("hello", run_context=run_context)
