from kiarina.agi.audio_tagging_provider import (
    AudioTagPrediction,
    BaseAudioTaggingProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._settings import MockAudioTaggingProviderSettings


class MockAudioTaggingProvider(BaseAudioTaggingProvider):
    def __init__(self, settings: MockAudioTaggingProviderSettings) -> None:
        super().__init__()
        self.settings: MockAudioTaggingProviderSettings = settings

    async def _predict(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]:
        return [
            AudioTagPrediction(label=label, score=score)
            for label, score in self.settings.predictions
        ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
