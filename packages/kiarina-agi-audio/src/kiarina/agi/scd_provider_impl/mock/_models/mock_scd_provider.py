import math

import numpy as np

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.scd_provider import BaseSCDProvider, SCDResult

from .._settings import MockSCDProviderSettings


class MockSCDProvider(BaseSCDProvider):
    def __init__(self, settings: MockSCDProviderSettings) -> None:
        super().__init__()

        self.settings: MockSCDProviderSettings = settings

    async def _predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult:
        if self.settings.speaker_probabilities is not None:
            probabilities = np.asarray(
                self.settings.speaker_probabilities,
                dtype=np.float32,
            )

        else:
            frame_samples = sample_rate * self.settings.frame_ms / 1000
            num_frames = max(1, math.ceil(len(samples) / frame_samples))

            probabilities = np.zeros(
                (num_frames, self.settings.num_speakers),
                dtype=np.float32,
            )

            if self.settings.num_speakers > 0:
                probabilities[:, 0] = self.settings.default_probability

        return SCDResult(
            speaker_probabilities=probabilities,
            frame_ms=self.settings.frame_ms,
        )
