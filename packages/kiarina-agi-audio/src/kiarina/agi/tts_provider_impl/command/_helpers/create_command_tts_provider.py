from typing import Any

from .._models.command_tts_provider import CommandTTSProvider
from .._settings import CommandTTSProviderSettings, settings_manager


def create_command_tts_provider(**kwargs: Any) -> CommandTTSProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = CommandTTSProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return CommandTTSProvider(settings)
