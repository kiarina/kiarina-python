from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.audio_types import MonoSamples

from .._schemas.scd_result import SCDResult
from .._types.scd_provider import SCDProvider
from .._types.scd_provider_name import SCDProviderName


class BaseSCDProvider(SCDProvider, ABC):
    def __init__(self) -> None:
        self._name: SCDProviderName | None = None

    @property
    def name(self) -> SCDProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("SCDProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: SCDProviderName) -> None:
        self._name = value

    async def predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult:
        if samples.ndim != 1:
            raise ValueError(
                f"SCDProvider expects mono 1D samples, got shape {samples.shape}."
            )

        result = await self._predict(samples, sample_rate)
        probabilities = np.asarray(result.speaker_probabilities, dtype=np.float32)

        if probabilities.ndim != 2:
            raise ValueError(
                "SCDProvider expects speaker probabilities shaped as "
                f"[num_frames, num_speakers], got shape {probabilities.shape}."
            )

        if result.frame_ms <= 0:
            raise ValueError(
                f"SCDProvider expects positive frame_ms, got {result.frame_ms}."
            )

        return SCDResult(
            speaker_probabilities=np.clip(probabilities, 0.0, 1.0),
            frame_ms=result.frame_ms,
        )

    @abstractmethod
    async def _predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult: ...

    def __str__(self) -> str:
        return self.__class__.__name__
