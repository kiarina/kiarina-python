from typing import Any

from kiarina.agi.audio_tagging_provider import (
    AudioTaggingProvider,
    AudioTaggingProviderName,
    AudioTagPrediction,
    audio_tagging_provider_registry,
)
from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.audio_tagging_model_config import AudioTaggingModelConfig
from .._types.audio_tagging_model_name import AudioTaggingModelName


class AudioTaggingModel:
    def __init__(
        self,
        name: AudioTaggingModelName,
        config: AudioTaggingModelConfig,
    ) -> None:
        self.name: AudioTaggingModelName = name
        self.config: AudioTaggingModelConfig = config
        self._provider: AudioTaggingProvider | None = None

    @property
    def provider_name(self) -> AudioTaggingProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> AudioTaggingProvider:
        if self._provider is None:
            self._provider = audio_tagging_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    async def predict(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]:
        return await self.provider.predict(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    def __str__(self) -> str:
        return self.name
