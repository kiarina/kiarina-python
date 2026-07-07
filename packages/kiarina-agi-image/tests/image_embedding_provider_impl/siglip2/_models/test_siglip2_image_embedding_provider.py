import numpy as np

from kiarina.agi.embedding import calc_cosine_similarity
from kiarina.agi.image_embedding_provider_impl.siglip2 import (
    SigLIP2ImageEmbeddingProvider,
    SigLIP2ImageEmbeddingProviderSettings,
)
from kiarina.agi.run_context import RunContext


def _image(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(64, 48, 3), dtype=np.uint8)


async def test_siglip2_image_embedding_provider(
    run_context: RunContext,
) -> None:
    provider = SigLIP2ImageEmbeddingProvider(SigLIP2ImageEmbeddingProviderSettings())

    space = provider.get_space()
    assert space.kind == "object"
    assert space.space_id.startswith("siglip2:sha256=")
    assert ":dim=768:" in space.space_id
    assert space.dimension == 768

    result = await provider.embed(_image(0), run_context=run_context)

    assert result.kind == "object"
    assert result.space_id == space.space_id
    assert result.to_numpy().shape == (768,)
    assert result.to_numpy().dtype == np.float32
    assert np.isclose(np.linalg.norm(result.to_numpy()), 1.0)


async def test_deterministic_and_distinct(
    run_context: RunContext,
) -> None:
    provider = SigLIP2ImageEmbeddingProvider(SigLIP2ImageEmbeddingProviderSettings())

    a1 = await provider.embed(_image(1), run_context=run_context)
    a2 = await provider.embed(_image(1), run_context=run_context)
    b = await provider.embed(_image(2), run_context=run_context)

    assert np.isclose(calc_cosine_similarity(a1, a2), 1.0)
    assert calc_cosine_similarity(a1, b) < 0.999
