import numpy as np

from kiarina.agi.audio_embedding_provider_impl.mock import (
    MockAudioEmbeddingProvider,
    MockAudioEmbeddingProviderSettings,
)
from kiarina.agi.run_context import RunContext


async def test_mock_audio_embedding_provider(run_context: RunContext) -> None:
    provider = MockAudioEmbeddingProvider(
        MockAudioEmbeddingProviderSettings(embedding=[0.0, 2.0], dimension=2)
    )

    space = provider.get_space()
    assert space.kind == "speaker"
    assert space.space_id == "mock:sha256=none:sr=any:dim=2:norm=l2"
    assert space.dimension == 2

    result = await provider.embed(np.zeros(1600), 16000, run_context=run_context)

    assert result.kind == "speaker"
    assert result.space_id == "mock:sha256=none:sr=any:dim=2:norm=l2"
    assert np.allclose(result.to_numpy(), [0.0, 1.0])
    assert result.metadata["sample_rate"] == 16000
    assert result.metadata["samples"] == 1600


async def test_without_normalize(run_context: RunContext) -> None:
    provider = MockAudioEmbeddingProvider(
        MockAudioEmbeddingProviderSettings(
            embedding=[0.0, 2.0],
            dimension=2,
            normalize_embedding=False,
        )
    )

    result = await provider.embed(np.zeros(1600), 16000, run_context=run_context)

    assert result.kind == "speaker"
    assert result.space_id == "mock:sha256=none:sr=any:dim=2:norm=none"
    assert np.allclose(result.to_numpy(), [0.0, 2.0])


async def test_can_override_kind(run_context: RunContext) -> None:
    provider = MockAudioEmbeddingProvider(
        MockAudioEmbeddingProviderSettings(kind="sound")
    )

    result = await provider.embed(np.zeros(1600), 16000, run_context=run_context)

    assert result.kind == "sound"
