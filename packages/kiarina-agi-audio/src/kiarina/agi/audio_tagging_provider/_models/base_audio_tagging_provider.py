from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.audio_types import AudioSamples, MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.audio_tag_prediction import AudioTagPrediction
from .._types.audio_tagging_provider import AudioTaggingProvider
from .._types.audio_tagging_provider_name import AudioTaggingProviderName


class BaseAudioTaggingProvider(AudioTaggingProvider, ABC):
    def __init__(self) -> None:
        self._name: AudioTaggingProviderName | None = None

    @property
    def name(self) -> AudioTaggingProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("AudioTaggingProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: AudioTaggingProviderName) -> None:
        self._name = value

    async def predict(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]:
        samples = _to_mono(samples)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(audio_tagging_provider=f"{self}")

        return await self._predict(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    @abstractmethod
    async def _predict(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]: ...

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
