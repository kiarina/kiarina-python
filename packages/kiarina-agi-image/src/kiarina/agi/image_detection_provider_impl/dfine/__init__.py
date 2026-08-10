from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_dfine_image_detection_provider import (
        create_dfine_image_detection_provider,
    )
    from ._models.dfine_image_detection_provider import DFineImageDetectionProvider
    from ._settings import DFineImageDetectionProviderSettings, settings_manager

__all__ = [
    "create_dfine_image_detection_provider",
    "DFineImageDetectionProvider",
    "DFineImageDetectionProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_dfine_image_detection_provider": "._helpers.create_dfine_image_detection_provider",
        "DFineImageDetectionProvider": "._models.dfine_image_detection_provider",
        "DFineImageDetectionProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
