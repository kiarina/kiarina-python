import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider_impl.google import (
    GoogleTextEmbeddingProvider,
    GoogleTextEmbeddingProviderSettings,
)


@pytest.fixture
def provider() -> GoogleTextEmbeddingProvider:
    provider = GoogleTextEmbeddingProvider(
        GoogleTextEmbeddingProviderSettings(
            model_name="gemini-embedding-2",
            dimension=1536,
        )
    )
    provider.name = "google"
    return provider


def test_properties(provider: GoogleTextEmbeddingProvider) -> None:
    print(f"__str__: {provider}")

    space = provider.get_space()
    assert space.kind == "text"
    assert space.dimension == 1536


@pytest.mark.costly
async def test_embed_text_request(
    provider: GoogleTextEmbeddingProvider,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    embedding = await provider.embed(
        "Hello, world!",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert embedding.kind == "text"
    assert embedding.space_id == provider.get_space().space_id
    assert len(embedding.vector) == 1536
    assert np.isfinite(embedding.to_numpy()).all()
    assert embedding.metadata["model_name"] == "gemini-embedding-2"
