from typing import Any

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.vad_provider import (
    SpeechProbability,
    VADProvider,
    VADProviderName,
    vad_provider_registry,
)

from .._schemas.vad_model_config import VADModelConfig
from .._types.vad_model_name import VADModelName


class VADModel:
    def __init__(self, name: VADModelName, config: VADModelConfig) -> None:
        self.name: VADModelName = name
        self.config: VADModelConfig = config
        self._provider: VADProvider | None = None

    @property
    def provider_name(self) -> VADProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> VADProvider:
        if self._provider is None:
            self._provider = vad_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    async def predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability:
        return await self.provider.predict(samples, sample_rate)

    def __str__(self) -> str:
        return self.name
