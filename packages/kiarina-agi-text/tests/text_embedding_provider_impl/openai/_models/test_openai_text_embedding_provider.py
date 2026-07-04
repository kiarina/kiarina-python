from typing import Any

import numpy as np
import pytest

from kiarina.agi.text_embedding_provider_impl.openai import (
    OpenAITextEmbeddingProvider,
    OpenAITextEmbeddingProviderSettings,
)


@pytest.fixture
def provider() -> OpenAITextEmbeddingProvider:
    provider = OpenAITextEmbeddingProvider(
        OpenAITextEmbeddingProviderSettings(
            model_name="text-embedding-3-small",
            dimension=1536,
            cost_microdollars_per_1k_tokens=20,
        )
    )
    provider.name = "openai"
    return provider


def test_properties(provider: OpenAITextEmbeddingProvider) -> None:
    print(f"__str__: {provider}")
    print(f"openai_settings: {provider.openai_settings}")
    print(f"model_name: {provider.settings.model_name}")

    space = provider.get_space()
    assert space.kind == "text"
    assert space.dimension == 1536


@pytest.mark.costly
async def test_embed_text_request(
    provider: OpenAITextEmbeddingProvider,
    cost_recorder: Any,
    run_context: Any,
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
    assert embedding.metadata["model_name"] == "text-embedding-3-small"
    assert embedding.metadata["prompt_tokens"] > 0
