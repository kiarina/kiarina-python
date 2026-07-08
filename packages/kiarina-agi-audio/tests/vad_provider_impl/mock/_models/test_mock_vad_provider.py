import numpy as np

from kiarina.agi.vad_provider_impl.mock import (
    MockVADProvider,
    MockVADProviderSettings,
)


async def test_mock_vad_provider() -> None:
    provider = MockVADProvider(
        MockVADProviderSettings(
            speech_probabilities=[0.1, 0.9],
        )
    )

    assert await provider.predict(np.zeros(512), 16000) == 0.1
    assert await provider.predict(np.zeros(512), 16000) == 0.9
    assert await provider.predict(np.zeros(512), 16000) == 0.9
