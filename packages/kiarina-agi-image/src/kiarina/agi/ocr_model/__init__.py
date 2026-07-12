from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.ocr_image import ocr_image
    from ._instances.ocr_model_registry import ocr_model_registry
    from ._models.ocr_model import OCRModel
    from ._schemas.ocr_model_config import OCRModelConfig
    from ._settings import OCRModelSettings, settings_manager
    from ._types.ocr_model_alias import OCRModelAlias
    from ._types.ocr_model_name import OCRModelName
    from ._types.ocr_model_specifier import OCRModelSpecifier
    from ._types.ocr_options import OCROptions

__all__ = [
    # ._helpers
    "ocr_image",
    # ._instances
    "ocr_model_registry",
    # ._models
    "OCRModel",
    # ._schemas
    "OCRModelConfig",
    # ._settings
    "OCRModelSettings",
    "settings_manager",
    # ._types
    "OCRModelAlias",
    "OCRModelName",
    "OCRModelSpecifier",
    "OCROptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        # ._helpers
        "ocr_image": "._helpers.ocr_image",
        # ._instances
        "ocr_model_registry": "._instances.ocr_model_registry",
        # ._models
        "OCRModel": "._models.ocr_model",
        # ._schemas
        "OCRModelConfig": "._schemas.ocr_model_config",
        # ._settings
        "OCRModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "OCRModelAlias": "._types.ocr_model_alias",
        "OCRModelName": "._types.ocr_model_name",
        "OCRModelSpecifier": "._types.ocr_model_specifier",
        "OCROptions": "._types.ocr_options",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
