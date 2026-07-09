from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_stt_audio_event_bundler import (
        create_stt_audio_event_bundler,
    )
    from ._models.stt_audio_event_bundler import STTAudioEventBundler
    from ._settings import STTAudioEventBundlerSettings, settings_manager

__all__ = [
    # ._helpers
    "create_stt_audio_event_bundler",
    # ._models
    "STTAudioEventBundler",
    # ._settings
    "STTAudioEventBundlerSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_stt_audio_event_bundler": "._helpers.create_stt_audio_event_bundler",
        # ._models
        "STTAudioEventBundler": "._models.stt_audio_event_bundler",
        # ._settings
        "STTAudioEventBundlerSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
