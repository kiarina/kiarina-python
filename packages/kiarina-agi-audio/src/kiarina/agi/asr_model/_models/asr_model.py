from typing import Any

from kiarina.agi.asr_provider import (
    ASRProvider,
    ASRProviderName,
    ASRSegment,
    asr_provider_registry,
)
from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.asr_model_config import ASRModelConfig
from .._types.asr_model_name import ASRModelName


class ASRModel:
    def __init__(
        self,
        name: ASRModelName,
        config: ASRModelConfig,
    ) -> None:
        self.name: ASRModelName = name
        self.config: ASRModelConfig = config
        self._provider: ASRProvider | None = None

    @property
    def provider_name(self) -> ASRProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> ASRProvider:
        if self._provider is None:
            self._provider = asr_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    async def speech_to_text(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> str:
        return await self.provider.speech_to_text(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    async def speech_to_segments(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        return await self.provider.speech_to_segments(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
