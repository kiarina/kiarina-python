from typing import Any

from .._models.command_asr_provider import CommandASRProvider
from .._settings import CommandASRProviderSettings, settings_manager


def create_command_asr_provider(**kwargs: Any) -> CommandASRProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = CommandASRProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return CommandASRProvider(settings)
