from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_ambient_audio_event_bundler import (
        create_ambient_audio_event_bundler,
    )
    from ._models.ambient_audio_event_bundler import AmbientAudioEventBundler
    from ._settings import AmbientAudioEventBundlerSettings, settings_manager

__all__ = [
    # ._helpers
    "create_ambient_audio_event_bundler",
    # ._models
    "AmbientAudioEventBundler",
    # ._settings
    "AmbientAudioEventBundlerSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_ambient_audio_event_bundler": "._helpers.create_ambient_audio_event_bundler",
        # ._models
        "AmbientAudioEventBundler": "._models.ambient_audio_event_bundler",
        # ._settings
        "AmbientAudioEventBundlerSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
