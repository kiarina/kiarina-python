from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_camera_video_source import create_camera_video_source
    from ._models.camera_video_source import CameraVideoSource
    from ._settings import CameraVideoSourceSettings, settings_manager

__all__ = [
    # ._helpers
    "create_camera_video_source",
    # ._models
    "CameraVideoSource",
    # ._settings
    "CameraVideoSourceSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_camera_video_source": "._helpers.create_camera_video_source",
        # ._models
        "CameraVideoSource": "._models.camera_video_source",
        # ._settings
        "CameraVideoSourceSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
