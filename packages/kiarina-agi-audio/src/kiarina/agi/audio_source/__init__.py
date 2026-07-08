from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.base_audio_source import BaseAudioSource
    from ._schemas.audio_chunk import AudioChunk
    from ._services.audio_source_registry import audio_source_registry
    from ._settings import AudioSourceSettings, settings_manager
    from ._types.audio_source import AudioSource
    from ._types.audio_source_name import AudioSourceName
    from ._types.audio_source_specifier import AudioSourceSpecifier

__all__ = [
    # ._models
    "BaseAudioSource",
    # ._schemas
    "AudioChunk",
    # ._services
    "audio_source_registry",
    # ._settings
    "AudioSourceSettings",
    "settings_manager",
    # ._types
    "AudioSource",
    "AudioSourceName",
    "AudioSourceSpecifier",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "BaseAudioSource": "._models.base_audio_source",
        # ._schemas
        "AudioChunk": "._schemas.audio_chunk",
        # ._services
        "audio_source_registry": "._services.audio_source_registry",
        # ._settings
        "AudioSourceSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "AudioSource": "._types.audio_source",
        "AudioSourceName": "._types.audio_source_name",
        "AudioSourceSpecifier": "._types.audio_source_specifier",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
