from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_yamnet_audio_tagging_provider import (
        create_yamnet_audio_tagging_provider,
    )
    from ._models.yamnet_audio_tagging_provider import YamnetAudioTaggingProvider
    from ._settings import YamnetAudioTaggingProviderSettings, settings_manager

__all__ = [
    "create_yamnet_audio_tagging_provider",
    "YamnetAudioTaggingProvider",
    "YamnetAudioTaggingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_yamnet_audio_tagging_provider": "._helpers.create_yamnet_audio_tagging_provider",
        "YamnetAudioTaggingProvider": "._models.yamnet_audio_tagging_provider",
        "YamnetAudioTaggingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
