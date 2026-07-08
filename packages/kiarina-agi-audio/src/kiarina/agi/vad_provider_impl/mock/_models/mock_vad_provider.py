from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.vad_provider import BaseVADProvider, SpeechProbability

from .._settings import MockVADProviderSettings


class MockVADProvider(BaseVADProvider):
    def __init__(self, settings: MockVADProviderSettings) -> None:
        super().__init__()

        self.settings: MockVADProviderSettings = settings
        self._index: int = 0

    async def _predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability:
        if sample_rate != self.settings.sample_rate:
            raise ValueError(
                f"MockVADProvider expects sample_rate {self.settings.sample_rate}, "
                f"got {sample_rate}."
            )

        probabilities = self.settings.speech_probabilities

        if not probabilities:
            return 0.0

        if self._index < len(probabilities):
            speech_prob = probabilities[self._index]
        elif self.settings.repeat_last:
            speech_prob = probabilities[-1]
        else:
            speech_prob = 0.0

        self._index += 1
        return speech_prob
