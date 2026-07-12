from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_ocr_provider import create_mock_ocr_provider
    from ._models.mock_ocr_provider import MockOCRProvider
    from ._settings import MockOCRProviderSettings, settings_manager

__all__ = [
    "create_mock_ocr_provider",
    "MockOCRProvider",
    "MockOCRProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        "create_mock_ocr_provider": "._helpers.create_mock_ocr_provider",
        "MockOCRProvider": "._models.mock_ocr_provider",
        "MockOCRProviderSettings": "._settings",
        "settings_manager": "._settings",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
