from typing import Any

from .._models.mock_chat_provider import MockChatProvider
from .._settings import MockChatProviderSettings, settings_manager


def create_mock_chat_provider(**kwargs: Any) -> MockChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockChatProvider(settings)
