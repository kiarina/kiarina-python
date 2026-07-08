from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.audio_window_buffer import AudioWindowBuffer
    from ._schemas.audio_window import AudioWindow

__all__ = [
    # ._models
    "AudioWindowBuffer",
    # ._schemas
    "AudioWindow",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "AudioWindowBuffer": "._models.audio_window_buffer",
        # ._schemas
        "AudioWindow": "._schemas.audio_window",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
