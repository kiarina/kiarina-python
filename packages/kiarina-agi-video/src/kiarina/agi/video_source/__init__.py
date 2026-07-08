from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.video_source_registry import video_source_registry
    from ._models.base_video_source import BaseVideoSource
    from ._schemas.video_frame import VideoFrame
    from ._settings import VideoSourceSettings, settings_manager
    from ._types.video_source import VideoSource
    from ._types.video_source_name import VideoSourceName
    from ._types.video_source_specifier import VideoSourceSpecifier
    from ._utils.ensure_image_pixels import ensure_image_pixels

__all__ = [
    # ._models
    "BaseVideoSource",
    # ._schemas
    "VideoFrame",
    # ._instances
    "video_source_registry",
    # ._settings
    "VideoSourceSettings",
    "settings_manager",
    # ._types
    "VideoSource",
    "VideoSourceName",
    "VideoSourceSpecifier",
    # ._utils
    "ensure_image_pixels",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "BaseVideoSource": "._models.base_video_source",
        # ._schemas
        "VideoFrame": "._schemas.video_frame",
        # ._instances
        "video_source_registry": "._instances.video_source_registry",
        # ._settings
        "VideoSourceSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "VideoSource": "._types.video_source",
        "VideoSourceName": "._types.video_source_name",
        "VideoSourceSpecifier": "._types.video_source_specifier",
        # ._utils
        "ensure_image_pixels": "._utils.ensure_image_pixels",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
