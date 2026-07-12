from typing import Any

from .._models.mock_ocr_provider import MockOCRProvider
from .._settings import MockOCRProviderSettings, settings_manager


def create_mock_ocr_provider(**kwargs: Any) -> MockOCRProvider:
    settings = settings_manager.get_settings()
    if kwargs:
        settings = MockOCRProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )
    return MockOCRProvider(settings)
