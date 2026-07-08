from typing import Protocol, runtime_checkable

from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.audio_tag_prediction import AudioTagPrediction
from .audio_tagging_provider_name import AudioTaggingProviderName


@runtime_checkable
class AudioTaggingProvider(Protocol):
    name: AudioTaggingProviderName

    async def predict(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]: ...
