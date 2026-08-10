from typing import Any

from .._models.lc_google_genai_chat_provider import LCGoogleGenAIChatProvider
from .._settings import LCGoogleGenAIChatProviderSettings, settings_manager


def create_lc_google_genai_chat_provider(**kwargs: Any) -> LCGoogleGenAIChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = LCGoogleGenAIChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return LCGoogleGenAIChatProvider(settings)
