from typing import Protocol, runtime_checkable

from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.asr_segment import ASRSegment
from .asr_provider_name import ASRProviderName


@runtime_checkable
class ASRProvider(Protocol):
    name: ASRProviderName

    async def speech_to_text(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> str: ...

    async def speech_to_segments(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[ASRSegment]: ...
