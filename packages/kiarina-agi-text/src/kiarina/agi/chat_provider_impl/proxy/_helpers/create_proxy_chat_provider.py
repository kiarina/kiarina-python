from typing import Any

from .._models.proxy_chat_provider import ProxyChatProvider
from .._settings import ProxyChatProviderSettings, settings_manager


def create_proxy_chat_provider(
    **kwargs: Any,
) -> ProxyChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = ProxyChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return ProxyChatProvider(settings)
