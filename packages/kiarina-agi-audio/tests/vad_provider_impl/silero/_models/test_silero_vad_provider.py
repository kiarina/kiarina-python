import numpy as np
import pytest

from kiarina.agi.vad_provider_impl.silero import (
    SileroVADProvider,
    SileroVADProviderSettings,
)


@pytest.mark.downloads_model
async def test_silero_vad_provider() -> None:
    provider = SileroVADProvider(SileroVADProviderSettings())
    speech_prob = await provider.predict(np.zeros(512, dtype=np.float32), 16000)

    assert 0.0 <= speech_prob <= 1.0
