import numpy as np

from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider_impl.mock import (
    MockTextEmbeddingProvider,
    MockTextEmbeddingProviderSettings,
)


async def test_mock_text_embedding_provider(run_context: RunContext) -> None:
    provider = MockTextEmbeddingProvider(
        MockTextEmbeddingProviderSettings(
            dimension=2,
            embedding=[3.0, 4.0],
        )
    )
    provider.name = "mock"

    space = provider.get_space()
    assert space.kind == "text"
    assert space.dimension == 2

    result = await provider.embed("hello", run_context=run_context)

    assert np.allclose(result.to_numpy(), [0.6, 0.8])
    assert result.metadata["text_length"] == 5
