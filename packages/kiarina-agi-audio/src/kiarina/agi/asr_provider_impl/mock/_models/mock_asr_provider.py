import logging

from kiarina.agi.asr_provider import (
    ASRSegment,
    BaseASRProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._settings import MockASRProviderSettings

logger = logging.getLogger(__name__)


class MockASRProvider(BaseASRProvider):
    """
    Mock ASR Provider Implementation for Testing
    """

    def __init__(self, settings: MockASRProviderSettings) -> None:
        super().__init__()

        self.settings: MockASRProviderSettings = settings

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"

    async def _speech_to_text(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> str:
        logger.info("Mock ASR: %d samples at %d Hz", len(samples), sample_rate)

        return self.settings.result_text

    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        logger.info("Mock ASR segments: %d samples at %d Hz", len(samples), sample_rate)
        return self.settings.result_segments.copy()
