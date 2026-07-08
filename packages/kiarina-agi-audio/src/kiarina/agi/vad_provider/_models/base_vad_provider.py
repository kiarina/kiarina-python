from abc import ABC, abstractmethod

from kiarina.agi.audio_types import MonoSamples

from .._types.speech_probability import SpeechProbability
from .._types.vad_provider import VADProvider
from .._types.vad_provider_name import VADProviderName


class BaseVADProvider(VADProvider, ABC):
    def __init__(self) -> None:
        self._name: VADProviderName | None = None

    @property
    def name(self) -> VADProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("VADProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: VADProviderName) -> None:
        self._name = value

    async def predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability:
        if samples.ndim != 1:
            raise ValueError(
                f"VADProvider expects mono 1D samples, got shape {samples.shape}."
            )

        speech_prob = await self._predict(samples, sample_rate)

        if speech_prob < 0.0:
            return 0.0

        if speech_prob > 1.0:
            return 1.0

        return speech_prob

    @abstractmethod
    async def _predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability: ...

    def __str__(self) -> str:
        return self.__class__.__name__
