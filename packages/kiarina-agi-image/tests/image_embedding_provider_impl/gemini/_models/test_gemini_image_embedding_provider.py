import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import calc_cosine_similarity
from kiarina.agi.image_embedding_provider_impl.gemini import (
    GeminiImageEmbeddingProvider,
    GeminiImageEmbeddingProviderSettings,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def provider_gemini_api() -> GeminiImageEmbeddingProvider:
    provider = GeminiImageEmbeddingProvider(
        GeminiImageEmbeddingProviderSettings(
            backend_type="gemini_api",
            google_auth_settings_key="api_key",
        )
    )
    provider.name = "gemini"
    return provider


@pytest.fixture
def provider_vertex_ai_credentials() -> GeminiImageEmbeddingProvider:
    provider = GeminiImageEmbeddingProvider(
        GeminiImageEmbeddingProviderSettings(
            backend_type="vertex_ai_credentials",
            google_auth_settings_key="service_account",
            vertex_ai_location="us-central1",
        )
    )
    provider.name = "gemini"
    return provider


@pytest.fixture
def provider(
    provider_gemini_api: GeminiImageEmbeddingProvider,
) -> GeminiImageEmbeddingProvider:
    return provider_gemini_api


def _image(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(64, 48, 3), dtype=np.uint8)


def test_get_space(provider: GeminiImageEmbeddingProvider) -> None:
    space = provider.get_space()
    assert space.kind == "seen"
    assert space.space_id.startswith("gemini-embedding-2:model=gemini-embedding-2:")
    assert ":dim=1536:" in space.space_id
    assert space.dimension == 1536


@pytest.mark.costly
async def test_gemini_image_embedding_provider(
    provider: GeminiImageEmbeddingProvider,
    run_context: RunContext,
    cost_recorder: CostRecorder,
) -> None:
    space = provider.get_space()

    result = await provider.embed(
        _image(0), cost_recorder=cost_recorder, run_context=run_context
    )

    assert result.kind == "seen"
    assert result.space_id == space.space_id
    assert result.to_numpy().shape == (space.dimension,)
    assert result.to_numpy().dtype == np.float32
    assert np.isclose(np.linalg.norm(result.to_numpy()), 1.0)
    assert cost_recorder.total_microdollars > 0


@pytest.mark.costly
async def test_deterministic_and_distinct(
    provider: GeminiImageEmbeddingProvider,
    run_context: RunContext,
    cost_recorder: CostRecorder,
) -> None:
    a1 = await provider.embed(
        _image(1), cost_recorder=cost_recorder, run_context=run_context
    )
    a2 = await provider.embed(
        _image(1), cost_recorder=cost_recorder, run_context=run_context
    )
    b = await provider.embed(
        _image(2), cost_recorder=cost_recorder, run_context=run_context
    )

    assert np.isclose(calc_cosine_similarity(a1, a2), 1.0, atol=1e-3)
    assert calc_cosine_similarity(a1, b) < 0.999
