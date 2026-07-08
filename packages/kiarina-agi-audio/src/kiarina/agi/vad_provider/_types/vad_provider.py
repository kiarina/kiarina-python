from typing import Protocol, runtime_checkable

from kiarina.agi.audio_types import MonoSamples

from .speech_probability import SpeechProbability
from .vad_provider_name import VADProviderName


@runtime_checkable
class VADProvider(Protocol):
    name: VADProviderName

    async def predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability: ...
