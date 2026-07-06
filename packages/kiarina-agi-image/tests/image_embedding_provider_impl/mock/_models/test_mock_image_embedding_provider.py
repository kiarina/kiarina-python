# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import numpy as np

from kiarina.agi.image_embedding_provider_impl.mock import (
    MockImageEmbeddingProvider,
    MockImageEmbeddingProviderSettings,
)


async def test_mock_image_embedding_provider(run_context) -> None:
    provider = MockImageEmbeddingProvider(
        MockImageEmbeddingProviderSettings(embedding=[0.0, 2.0], dimension=2)
    )

    space = provider.get_space()
    assert space.kind == "image"
    assert space.space_id == "mock:sha256=none:dim=2:norm=l2"
    assert space.dimension == 2

    result = await provider.embed(
        np.zeros((32, 24, 3), dtype=np.uint8), run_context=run_context
    )

    assert result.kind == "image"
    assert result.space_id == "mock:sha256=none:dim=2:norm=l2"
    assert np.allclose(result.to_numpy(), [0.0, 1.0])
    assert result.metadata["height"] == 32
    assert result.metadata["width"] == 24


async def test_without_normalize(run_context) -> None:
    provider = MockImageEmbeddingProvider(
        MockImageEmbeddingProviderSettings(
            embedding=[0.0, 2.0],
            dimension=2,
            normalize_embedding=False,
        )
    )

    result = await provider.embed(
        np.zeros((8, 8, 3), dtype=np.uint8), run_context=run_context
    )

    assert result.space_id == "mock:sha256=none:dim=2:norm=none"
    assert np.allclose(result.to_numpy(), [0.0, 2.0])


async def test_can_override_kind(run_context) -> None:
    provider = MockImageEmbeddingProvider(
        MockImageEmbeddingProviderSettings(kind="object")
    )

    result = await provider.embed(
        np.zeros((8, 8, 3), dtype=np.uint8), run_context=run_context
    )

    assert result.kind == "object"
