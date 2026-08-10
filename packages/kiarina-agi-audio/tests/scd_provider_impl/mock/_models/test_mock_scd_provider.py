import numpy as np

from kiarina.agi.scd_provider_impl.mock import (
    MockSCDProvider,
    MockSCDProviderSettings,
)


async def test_mock_scd_provider() -> None:
    provider = MockSCDProvider(
        MockSCDProviderSettings(
            speaker_probabilities=[
                [0.1, 0.9],
                [0.8, 0.2],
            ],
            frame_ms=100.0,
        )
    )

    result = await provider.predict(np.zeros(1600), 16000)

    assert result.frame_ms == 100.0
    assert np.allclose(result.speaker_probabilities, [[0.1, 0.9], [0.8, 0.2]])


async def test_mock_scd_provider_default_probabilities() -> None:
    provider = MockSCDProvider(
        MockSCDProviderSettings(
            frame_ms=100.0,
            num_speakers=2,
            default_probability=0.7,
        )
    )

    result = await provider.predict(np.zeros(3200), 16000)

    assert result.frame_ms == 100.0
    assert result.speaker_probabilities.shape == (2, 2)
    assert np.allclose(result.speaker_probabilities, [[0.7, 0.0], [0.7, 0.0]])
