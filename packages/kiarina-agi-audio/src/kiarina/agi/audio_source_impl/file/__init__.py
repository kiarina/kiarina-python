from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_file_audio_source import create_file_audio_source
    from ._models.file_audio_source import FileAudioSource
    from ._settings import FileAudioSourceSettings, settings_manager

__all__ = [
    # ._helpers
    "create_file_audio_source",
    # ._models
    "FileAudioSource",
    # ._settings
    "FileAudioSourceSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_file_audio_source": "._helpers.create_file_audio_source",
        # ._models
        "FileAudioSource": "._models.file_audio_source",
        # ._settings
        "FileAudioSourceSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
