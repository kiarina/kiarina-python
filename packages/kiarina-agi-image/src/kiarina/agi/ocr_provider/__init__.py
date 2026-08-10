from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.ocr_provider_registry import ocr_provider_registry
    from ._models.base_ocr_provider import BaseOCRProvider
    from ._settings import OCRProviderSettings, settings_manager
    from ._types.ocr_provider import OCRProvider
    from ._types.ocr_provider_name import OCRProviderName
    from ._views.ocr_result import OCRResult

__all__ = [
    # ._instances
    "ocr_provider_registry",
    # ._models
    "BaseOCRProvider",
    # ._settings
    "OCRProviderSettings",
    "settings_manager",
    # ._types
    "OCRProvider",
    "OCRProviderName",
    # ._views
    "OCRResult",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        # ._instances
        "ocr_provider_registry": "._instances.ocr_provider_registry",
        # ._models
        "BaseOCRProvider": "._models.base_ocr_provider",
        # ._settings
        "OCRProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "OCRProvider": "._types.ocr_provider",
        "OCRProviderName": "._types.ocr_provider_name",
        # ._views
        "OCRResult": "._views.ocr_result",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
