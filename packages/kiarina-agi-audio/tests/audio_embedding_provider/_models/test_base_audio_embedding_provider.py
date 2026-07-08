import numpy as np
import pytest

from kiarina.agi.audio_embedding_provider import (
    BaseAudioEmbeddingProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext


class ExampleAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind="example",
            space_id="example:sha256=none:sr=16000:dim=2:norm=l2",
            dimension=2,
        )

    async def _embed(
        self,
        samples: MonoSamples,
        sample_rate: int,
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


class CapturingAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
    def __init__(self) -> None:
        super().__init__()
        self.samples: MonoSamples | None = None
        self.result = Embedding.from_numpy(
            kind="example",
            space_id="example:sha256=none:sr=16000:dim=2:norm=none",
            vector=np.array([3.0, 4.0], dtype=np.float32),
        )

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind="example",
            space_id="example:sha256=none:sr=16000:dim=2:norm=none",
            dimension=2,
        )

    async def _embed(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        self.samples = samples
        return self.result


async def test_base_audio_embedding_provider(run_context: RunContext) -> None:
    provider = ExampleAudioEmbeddingProvider()
    provider.name = "example"

    print(f"__str__: {provider!s}")
    print(f"name: {provider.name}")

    result = await provider.embed(np.zeros(1600), 16000, run_context=run_context)

    assert result.kind == "example"
    assert result.space_id == "example:sha256=none:sr=16000:dim=2:norm=l2"
    assert result.to_numpy().dtype == np.float32
    assert np.allclose(result.to_numpy(), [0.6, 0.8])


async def test_returns_embed_result(run_context: RunContext) -> None:
    provider = CapturingAudioEmbeddingProvider()

    result = await provider.embed(np.zeros(1600), 16000, run_context=run_context)

    assert result is provider.result


async def test_keeps_zero_vector(run_context: RunContext) -> None:
    class ZeroAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
        def get_space(self) -> EmbeddingSpace:
            return EmbeddingSpace(
                kind="example",
                space_id="example:sha256=none:sr=16000:dim=2:norm=l2",
                dimension=2,
            )

        async def _embed(
            self,
            samples: MonoSamples,
            sample_rate: int,
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

    provider = ZeroAudioEmbeddingProvider()
    result = await provider.embed(np.zeros(1600), 16000, run_context=run_context)

    assert np.allclose(result.to_numpy(), [0.0, 0.0])


async def test_accepts_stereo(run_context: RunContext) -> None:
    provider = CapturingAudioEmbeddingProvider()

    stereo = np.array(
        [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
        ],
        dtype=np.float32,
    )

    result = await provider.embed(stereo, 16000, run_context=run_context)

    assert result is provider.result
    assert provider.samples is not None
    assert provider.samples.ndim == 1
    assert np.allclose(provider.samples, [2.0, 3.0, 4.0])


async def test_rejects_invalid_shape(run_context: RunContext) -> None:
    provider = ExampleAudioEmbeddingProvider()

    with pytest.raises(ValueError, match="samples must be 1D or 2D"):
        await provider.embed(np.zeros((1, 2, 3)), 16000, run_context=run_context)


async def test_rejects_dimension_mismatch(run_context: RunContext) -> None:
    class BadAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
        def get_space(self) -> EmbeddingSpace:
            return EmbeddingSpace(
                kind="example",
                space_id="example:sha256=none:sr=16000:dim=3:norm=l2",
                dimension=3,
            )

        async def _embed(
            self,
            samples: MonoSamples,
            sample_rate: int,
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

    provider = BadAudioEmbeddingProvider()

    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        await provider.embed(np.zeros(1600), 16000, run_context=run_context)
