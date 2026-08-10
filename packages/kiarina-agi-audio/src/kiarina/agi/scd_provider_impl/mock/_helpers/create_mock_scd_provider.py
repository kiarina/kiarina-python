from typing import Any

from .._models.mock_scd_provider import MockSCDProvider
from .._settings import MockSCDProviderSettings, settings_manager


def create_mock_scd_provider(**kwargs: Any) -> MockSCDProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockSCDProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockSCDProvider(settings)
