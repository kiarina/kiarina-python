import numpy as np

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.vad_provider import BaseVADProvider, SpeechProbability


class ExampleVADProvider(BaseVADProvider):
    async def _predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability:
        if np.all(samples < 0.0):
            return -0.5
        elif np.all(samples > 1.0):
            return 1.5
        else:
            return 0.5


async def test_base_vad_provider() -> None:
    vad_provider = ExampleVADProvider()
    vad_provider.name = "example"

    print(f"__str__: {vad_provider!s}")
    print(f"name: {vad_provider.name}")

    samples_negative = np.array([-1.0])
    samples_positive = np.array([2.5])
    samples_mixed = np.array([0.5])

    assert await vad_provider.predict(samples_negative, 16000) == 0.0
    assert await vad_provider.predict(samples_positive, 16000) == 1.0
    assert await vad_provider.predict(samples_mixed, 16000) == 0.5
