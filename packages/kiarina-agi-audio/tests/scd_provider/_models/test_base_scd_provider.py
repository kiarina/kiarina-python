import numpy as np
import pytest

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.scd_provider import BaseSCDProvider, SCDResult


class ExampleSCDProvider(BaseSCDProvider):
    async def _predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult:
        return SCDResult(
            speaker_probabilities=np.array(
                [
                    [-0.5, 0.5],
                    [0.5, 1.5],
                ],
                dtype=np.float32,
            ),
            frame_ms=100.0,
        )


async def test_base_scd_provider() -> None:
    scd_provider = ExampleSCDProvider()
    scd_provider.name = "example"

    print(f"__str__: {scd_provider!s}")
    print(f"name: {scd_provider.name}")

    result = await scd_provider.predict(np.zeros(1600), 16000)

    assert result.frame_ms == 100.0
    assert result.speaker_probabilities.tolist() == [[0.0, 0.5], [0.5, 1.0]]


async def test_base_scd_provider_rejects_stereo() -> None:
    scd_provider = ExampleSCDProvider()

    with pytest.raises(ValueError, match="SCDProvider expects mono 1D samples"):
        await scd_provider.predict(np.zeros((2, 1600)), 16000)
