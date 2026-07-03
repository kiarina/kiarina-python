from typing import Any

from .._models.lc_openai_chat_provider import LCOpenAIChatProvider
from .._settings import LCOpenAIChatProviderSettings, settings_manager


def create_lc_openai_chat_provider(**kwargs: Any) -> LCOpenAIChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = LCOpenAIChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return LCOpenAIChatProvider(settings)
