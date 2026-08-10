from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_queue_video_source import create_queue_video_source
    from ._models.queue_video_source import QueueVideoSource
    from ._settings import QueueVideoSourceSettings, settings_manager

__all__ = [
    # ._helpers
    "create_queue_video_source",
    # ._models
    "QueueVideoSource",
    # ._settings
    "QueueVideoSourceSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_queue_video_source": "._helpers.create_queue_video_source",
        # ._models
        "QueueVideoSource": "._models.queue_video_source",
        # ._settings
        "QueueVideoSourceSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
