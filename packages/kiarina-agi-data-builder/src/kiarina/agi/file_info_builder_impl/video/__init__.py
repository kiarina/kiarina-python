from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_video_file_info_builder import create_video_file_info_builder
    from ._models.video_file_info_builder import VideoFileInfoBuilder
    from ._settings import VideoFileInfoBuilderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_video_file_info_builder",
    # ._models
    "VideoFileInfoBuilder",
    # ._settings
    "VideoFileInfoBuilderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_video_file_info_builder": "._helpers.create_video_file_info_builder",
        # ._models
        "VideoFileInfoBuilder": "._models.video_file_info_builder",
        # ._settings
        "VideoFileInfoBuilderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
