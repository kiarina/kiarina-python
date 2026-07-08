from typing import Any

from .._models.pyannote_scd_provider import PyannoteSCDProvider
from .._settings import PyannoteSCDProviderSettings, settings_manager


def create_pyannote_scd_provider(**kwargs: Any) -> PyannoteSCDProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = PyannoteSCDProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return PyannoteSCDProvider(settings)
