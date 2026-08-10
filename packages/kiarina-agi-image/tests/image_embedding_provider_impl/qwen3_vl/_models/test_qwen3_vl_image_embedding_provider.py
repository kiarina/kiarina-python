import os

import httpx
import numpy as np
import pytest

from kiarina.agi.embedding import calc_cosine_similarity
from kiarina.agi.image_embedding_provider_impl.qwen3_vl import (
    Qwen3VLImageEmbeddingProvider,
    Qwen3VLImageEmbeddingProviderSettings,
)
from kiarina.agi.run_context import RunContext

_BASE_URL = os.environ.get(
    "KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_QWEN3_VL_BASE_URL",
    "http://localhost:8900",
)


@pytest.fixture
def qwen3_vl_base_url() -> str:
    try:
        response = httpx.get(f"{_BASE_URL}/health", timeout=2.0)
        response.raise_for_status()
    except Exception:
        pytest.skip(
            "Qwen3-VL embedding server is not reachable at "
            f"{_BASE_URL} (see models/qwen3-vl-embedding/README.md)"
        )

    return _BASE_URL


def _image(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(64, 48, 3), dtype=np.uint8)


async def test_qwen3_vl_image_embedding_provider(
    qwen3_vl_base_url: str,
    run_context: RunContext,
) -> None:
    provider = Qwen3VLImageEmbeddingProvider(
        Qwen3VLImageEmbeddingProviderSettings(base_url=qwen3_vl_base_url)
    )

    space = provider.get_space()
    assert space.kind == "seen"
    assert space.space_id.startswith("qwen3-vl:model=")
    assert ":dim=2048:" in space.space_id
    assert space.dimension == 2048

    result = await provider.embed(_image(0), run_context=run_context)

    assert result.kind == "seen"
    assert result.space_id == space.space_id
    assert result.to_numpy().shape == (2048,)
    assert result.to_numpy().dtype == np.float32
    assert np.isclose(np.linalg.norm(result.to_numpy()), 1.0)


async def test_deterministic_and_distinct(
    qwen3_vl_base_url: str,
    run_context: RunContext,
) -> None:
    provider = Qwen3VLImageEmbeddingProvider(
        Qwen3VLImageEmbeddingProviderSettings(base_url=qwen3_vl_base_url)
    )

    a1 = await provider.embed(_image(1), run_context=run_context)
    a2 = await provider.embed(_image(1), run_context=run_context)
    b = await provider.embed(_image(2), run_context=run_context)

    assert np.isclose(calc_cosine_similarity(a1, a2), 1.0)
    assert calc_cosine_similarity(a1, b) < 0.999
