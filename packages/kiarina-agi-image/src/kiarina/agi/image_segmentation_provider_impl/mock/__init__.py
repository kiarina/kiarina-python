from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_image_segmentation_provider import (
        create_mock_image_segmentation_provider,
    )
    from ._models.mock_image_segmentation_provider import (
        MockImageSegmentationProvider,
    )
    from ._settings import MockImageSegmentationProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_mock_image_segmentation_provider",
    # ._models
    "MockImageSegmentationProvider",
    # ._settings
    "MockImageSegmentationProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        # ._helpers
        "create_mock_image_segmentation_provider": "._helpers.create_mock_image_segmentation_provider",
        # ._models
        "MockImageSegmentationProvider": "._models.mock_image_segmentation_provider",
        # ._settings
        "MockImageSegmentationProviderSettings": "._settings",
        "settings_manager": "._settings",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
