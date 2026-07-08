from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import (
    AudioFilePath,
    OutputFormat,
    TTSProvider,
    TTSProviderName,
    tts_provider_registry,
)

from .._schemas.tts_model_config import TTSModelConfig
from .._types.tts_model_name import TTSModelName


class TTSModel:
    def __init__(
        self,
        name: TTSModelName,
        config: TTSModelConfig,
    ) -> None:
        self.name: TTSModelName = name
        self.config: TTSModelConfig = config
        self._provider: TTSProvider | None = None

    def __str__(self) -> str:
        return self.name

    @property
    def provider_name(self) -> TTSProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def provider(self) -> TTSProvider:
        if self._provider is None:
            self._provider = tts_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    async def text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: OutputFormat,
        ignore_cache: bool = False,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> AudioFilePath:
        return await self.provider.text_to_speech(
            text,
            instructions=instructions,
            output_format=output_format,
            ignore_cache=ignore_cache,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
