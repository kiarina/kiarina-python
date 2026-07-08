from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_numpy_video_source import create_numpy_video_source
    from ._models.numpy_video_source import NumpyVideoSource
    from ._settings import NumpyVideoSourceSettings, settings_manager

__all__ = [
    # ._helpers
    "create_numpy_video_source",
    # ._models
    "NumpyVideoSource",
    # ._settings
    "NumpyVideoSourceSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_numpy_video_source": "._helpers.create_numpy_video_source",
        # ._models
        "NumpyVideoSource": "._models.numpy_video_source",
        # ._settings
        "NumpyVideoSourceSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
