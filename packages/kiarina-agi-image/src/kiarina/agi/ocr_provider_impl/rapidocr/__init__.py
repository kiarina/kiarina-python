from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_rapidocr_provider import create_rapidocr_provider
    from ._models.rapidocr_provider import RapidOCRProvider
    from ._settings import RapidOCRProviderSettings, settings_manager

__all__ = [
    "create_rapidocr_provider",
    "RapidOCRProvider",
    "RapidOCRProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        "create_rapidocr_provider": "._helpers.create_rapidocr_provider",
        "RapidOCRProvider": "._models.rapidocr_provider",
        "RapidOCRProviderSettings": "._settings",
        "settings_manager": "._settings",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
