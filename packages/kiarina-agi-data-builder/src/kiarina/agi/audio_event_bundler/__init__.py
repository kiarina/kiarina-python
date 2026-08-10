from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.audio_event_bundler_registry import audio_event_bundler_registry
    from ._models.base_audio_event_bundler import BaseAudioEventBundler
    from ._settings import AudioEventBundlerSettings, settings_manager
    from ._types.audio_event_bundler import AudioEventBundler
    from ._types.audio_event_bundler_name import AudioEventBundlerName
    from ._types.audio_event_bundler_specifier import AudioEventBundlerSpecifier

__all__ = [
    # ._instances
    "audio_event_bundler_registry",
    # ._models
    "BaseAudioEventBundler",
    # ._settings
    "AudioEventBundlerSettings",
    "settings_manager",
    # ._types
    "AudioEventBundler",
    "AudioEventBundlerName",
    "AudioEventBundlerSpecifier",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._instances
        "audio_event_bundler_registry": "._instances.audio_event_bundler_registry",
        # ._models
        "BaseAudioEventBundler": "._models.base_audio_event_bundler",
        # ._settings
        "AudioEventBundlerSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "AudioEventBundler": "._types.audio_event_bundler",
        "AudioEventBundlerName": "._types.audio_event_bundler_name",
        "AudioEventBundlerSpecifier": "._types.audio_event_bundler_specifier",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
