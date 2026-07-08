from typing import Any

from .._models.silero_vad_provider import SileroVADProvider
from .._settings import SileroVADProviderSettings, settings_manager


def create_silero_vad_provider(**kwargs: Any) -> SileroVADProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = SileroVADProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return SileroVADProvider(settings)
