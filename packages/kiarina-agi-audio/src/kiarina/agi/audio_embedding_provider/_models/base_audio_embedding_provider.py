from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.audio_types import AudioSamples, MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext

from .._types.audio_embedding_provider import AudioEmbeddingProvider
from .._types.audio_embedding_provider_name import AudioEmbeddingProviderName


class BaseAudioEmbeddingProvider(AudioEmbeddingProvider, ABC):
    def __init__(self) -> None:
        self._name: AudioEmbeddingProviderName | None = None

    @property
    def name(self) -> AudioEmbeddingProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("AudioEmbeddingProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: AudioEmbeddingProviderName) -> None:
        self._name = value

    async def embed(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        samples = _to_mono(samples)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(audio_embedding_provider=f"{self}")

        space = self.get_space()

        embedding = await self._embed(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        if embedding.kind != space.kind:
            raise ValueError(
                f"Embedding kind mismatch: {embedding.kind!r} != {space.kind!r}."
            )

        if embedding.space_id != space.space_id:
            raise ValueError(
                "Embedding space_id mismatch: "
                f"{embedding.space_id!r} != {space.space_id!r}."
            )

        if len(embedding.vector) != space.dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"{len(embedding.vector)} != {space.dimension}."
            )

        return embedding

    @abstractmethod
    def get_space(self) -> EmbeddingSpace: ...

    @abstractmethod
    async def _embed(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding: ...

    def __str__(self) -> str:
        return self.__class__.__name__


def _to_mono(samples: AudioSamples) -> MonoSamples:
    samples = np.asarray(samples)

    if samples.ndim == 1:
        return samples

    if samples.ndim == 2:
        return samples[0] if samples.shape[0] == 1 else samples.mean(axis=0)

    raise ValueError(
        f"samples must be 1D or 2D [Channels, Samples], got shape {samples.shape}."
    )
