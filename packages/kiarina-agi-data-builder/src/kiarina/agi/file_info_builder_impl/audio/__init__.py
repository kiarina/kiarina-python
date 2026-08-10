from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_audio_file_info_builder import create_audio_file_info_builder
    from ._models.audio_file_info_builder import AudioFileInfoBuilder
    from ._settings import AudioFileInfoBuilderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_audio_file_info_builder",
    # ._models
    "AudioFileInfoBuilder",
    # ._settings
    "AudioFileInfoBuilderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_audio_file_info_builder": "._helpers.create_audio_file_info_builder",
        # ._models
        "AudioFileInfoBuilder": "._models.audio_file_info_builder",
        # ._settings
        "AudioFileInfoBuilderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
