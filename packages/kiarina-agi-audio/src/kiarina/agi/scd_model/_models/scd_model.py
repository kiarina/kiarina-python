from typing import Any

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.scd_provider import (
    SCDProvider,
    SCDProviderName,
    SCDResult,
    scd_provider_registry,
)

from .._schemas.scd_model_config import SCDModelConfig
from .._types.scd_model_name import SCDModelName


class SCDModel:
    def __init__(self, name: SCDModelName, config: SCDModelConfig) -> None:
        self.name: SCDModelName = name
        self.config: SCDModelConfig = config
        self._provider: SCDProvider | None = None

    @property
    def provider_name(self) -> SCDProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> SCDProvider:
        if self._provider is None:
            self._provider = scd_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    async def predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult:
        return await self.provider.predict(samples, sample_rate)

    def __str__(self) -> str:
        return self.name
