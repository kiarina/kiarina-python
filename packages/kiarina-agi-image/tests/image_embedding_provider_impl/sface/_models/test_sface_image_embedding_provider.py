# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.embedding import calc_cosine_similarity
from kiarina.agi.image_embedding_provider_impl.sface import (
    SFaceImageEmbeddingProvider,
    SFaceImageEmbeddingProviderSettings,
)


@pytest.fixture
def sface_model_path() -> str:
    path = Path("models/sface/face_recognition_sface_2021dec.onnx")

    if not path.exists():
        pytest.skip(f"SFace ONNX model file not found at {path}")

    return str(path)


def _face(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(112, 112, 3), dtype=np.uint8)


async def test_sface_image_embedding_provider(
    sface_model_path,
    run_context,
) -> None:
    provider = SFaceImageEmbeddingProvider(
        SFaceImageEmbeddingProviderSettings(model_path=sface_model_path)
    )

    space = provider.get_space()
    assert space.kind == "face"
    assert space.space_id.startswith("sface:sha256=")
    assert ":dim=128:" in space.space_id
    assert space.dimension == 128

    result = await provider.embed(_face(0), run_context=run_context)

    assert result.kind == "face"
    assert result.space_id == space.space_id
    assert result.to_numpy().shape == (128,)
    assert result.to_numpy().dtype == np.float32
    assert np.isclose(np.linalg.norm(result.to_numpy()), 1.0)


async def test_deterministic_and_distinct(
    sface_model_path,
    run_context,
) -> None:
    provider = SFaceImageEmbeddingProvider(
        SFaceImageEmbeddingProviderSettings(model_path=sface_model_path)
    )

    a1 = await provider.embed(_face(1), run_context=run_context)
    a2 = await provider.embed(_face(1), run_context=run_context)
    b = await provider.embed(_face(2), run_context=run_context)

    assert np.isclose(calc_cosine_similarity(a1, a2), 1.0)
    assert calc_cosine_similarity(a1, b) < 0.999


async def test_resizes_non_112(
    sface_model_path,
    run_context,
) -> None:
    provider = SFaceImageEmbeddingProvider(
        SFaceImageEmbeddingProviderSettings(model_path=sface_model_path)
    )

    rng = np.random.default_rng(3)
    pixels = rng.integers(0, 256, size=(200, 160, 3), dtype=np.uint8)

    result = await provider.embed(pixels, run_context=run_context)

    assert result.to_numpy().shape == (128,)
